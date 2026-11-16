"""
Dataset collector module for phishing domain detection.

Collects real phishing and benign domain datasets from online sources:
- PhishTank (phishing)
- OpenPhish (phishing fallback)
- Tranco (benign)

Provides fallback to synthetic generation if real sources fail.
"""

import io
import json
import logging
import os
import pathlib
import urllib.parse
import zipfile

import pandas as pd
import requests

from src.data.dataset_generator import PhishingDatasetGenerator

# Configure logging
logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 30


class PhishTankCollector:
    """Collects phishing domains from PhishTank."""

    URL = "http://data.phishtank.com/data/online-valid.json"

    def collect(self, max_domains: int = 5000) -> pd.DataFrame:
        """
        Collects verified phishing URLs from PhishTank.

        Args:
            max_domains: Maximum number of domains to collect.

        Returns:
            DataFrame with columns: domain, label, source.
        """
        logger.info(f"Collecting up to {max_domains} domains from PhishTank...")
        try:
            response = requests.get(self.URL, timeout=TIMEOUT_SECONDS)
            response.raise_for_status()
            data = response.json()

            domains = set()
            for item in data:
                url = item.get('url', '')
                if url:
                    try:
                        parsed_url = urllib.parse.urlparse(url)
                        domain = parsed_url.netloc
                        if domain and domain not in domains:
                            domains.add(domain)
                            if len(domains) >= max_domains:
                                break
                    except Exception as parse_err:
                        logger.debug(f"Error parsing URL {url}: {parse_err}")

            df = pd.DataFrame({
                'domain': list(domains),
                'label': 1,
                'source': 'phishtank'
            })
            logger.info(f"Successfully collected {len(df)} domains from PhishTank.")
            return df
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch data from PhishTank: {e}")
            return pd.DataFrame(columns=['domain', 'label', 'source'])
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse PhishTank JSON data: {e}")
            return pd.DataFrame(columns=['domain', 'label', 'source'])
        except Exception as e:
            logger.error(f"Unexpected error in PhishTankCollector: {e}")
            return pd.DataFrame(columns=['domain', 'label', 'source'])


class TrancoCollector:
    """Collects benign domains from the Tranco list."""

    URL = "https://tranco-list.eu/top-1m.csv.zip"

    def collect(self, max_domains: int = 5000) -> pd.DataFrame:
        """
        Collects top benign domains from Tranco.

        Args:
            max_domains: Maximum number of domains to collect.

        Returns:
            DataFrame with columns: domain, label, source.
        """
        logger.info(f"Collecting up to {max_domains} benign domains from Tranco...")
        try:
            response = requests.get(self.URL, timeout=TIMEOUT_SECONDS)
            response.raise_for_status()

            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                # Tranco zip usually contains a single csv file
                csv_filename = z.namelist()[0]
                with z.open(csv_filename) as f:
                    # Tranco CSV format: rank,domain
                    df_tranco = pd.read_csv(f, header=None, names=['rank', 'domain'], nrows=max_domains)
            
            domains = df_tranco['domain'].dropna().unique()
            df = pd.DataFrame({
                'domain': list(domains)[:max_domains],
                'label': 0,
                'source': 'tranco'
            })
            logger.info(f"Successfully collected {len(df)} domains from Tranco.")
            return df
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch data from Tranco: {e}")
            return pd.DataFrame(columns=['domain', 'label', 'source'])
        except zipfile.BadZipFile as e:
            logger.error(f"Failed to extract Tranco zip file: {e}")
            return pd.DataFrame(columns=['domain', 'label', 'source'])
        except Exception as e:
            logger.error(f"Unexpected error in TrancoCollector: {e}")
            return pd.DataFrame(columns=['domain', 'label', 'source'])


class OpenPhishCollector:
    """Collects phishing domains from OpenPhish feed."""

    URL = "https://openphish.com/feed.txt"

    def collect(self, max_domains: int = 2000) -> pd.DataFrame:
        """
        Collects phishing URLs from OpenPhish.

        Args:
            max_domains: Maximum number of domains to collect.

        Returns:
            DataFrame with columns: domain, label, source.
        """
        logger.info(f"Collecting up to {max_domains} domains from OpenPhish...")
        try:
            response = requests.get(self.URL, timeout=TIMEOUT_SECONDS)
            response.raise_for_status()
            
            domains = set()
            for line in response.text.splitlines():
                url = line.strip()
                if url:
                    try:
                        parsed_url = urllib.parse.urlparse(url)
                        domain = parsed_url.netloc
                        if domain and domain not in domains:
                            domains.add(domain)
                            if len(domains) >= max_domains:
                                break
                    except Exception as parse_err:
                        logger.debug(f"Error parsing URL {url}: {parse_err}")

            df = pd.DataFrame({
                'domain': list(domains),
                'label': 1,
                'source': 'openphish'
            })
            logger.info(f"Successfully collected {len(df)} domains from OpenPhish.")
            return df
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch data from OpenPhish: {e}")
            return pd.DataFrame(columns=['domain', 'label', 'source'])
        except Exception as e:
            logger.error(f"Unexpected error in OpenPhishCollector: {e}")
            return pd.DataFrame(columns=['domain', 'label', 'source'])


class DatasetCollector:
    """Main orchestrator for collecting phishing and benign datasets."""

    def __init__(self):
        """Initializes the DatasetCollector with its sub-collectors."""
        self.phishtank = PhishTankCollector()
        self.openphish = OpenPhishCollector()
        self.tranco = TrancoCollector()

    def collect(self, num_malicious: int = 5000, num_benign: int = 5000) -> pd.DataFrame:
        """
        Collects a balanced dataset of malicious and benign domains.

        Args:
            num_malicious: Target number of malicious domains.
            num_benign: Target number of benign domains.

        Returns:
            DataFrame containing the combined dataset.
        """
        logger.info("Starting dataset collection...")
        
        # Collect malicious domains
        df_malicious = self.phishtank.collect(max_domains=num_malicious)
        
        if len(df_malicious) < num_malicious:
            logger.info(f"PhishTank only provided {len(df_malicious)} domains. Falling back to OpenPhish...")
            remaining = num_malicious - len(df_malicious)
            df_openphish = self.openphish.collect(max_domains=remaining)
            if not df_openphish.empty:
                df_malicious = pd.concat([df_malicious, df_openphish], ignore_index=True)
                df_malicious = df_malicious.drop_duplicates(subset=['domain'])

        if len(df_malicious) < num_malicious:
            logger.warning(f"Could not collect enough real malicious domains ({len(df_malicious)}/{num_malicious}). Generating synthetic data...")
            try:
                remaining = num_malicious - len(df_malicious)
                generator = PhishingDatasetGenerator(num_legit=0, num_phishing=remaining, seed=42)
                df_synth = generator.generate()
                df_synth_malicious = df_synth[df_synth['label'] == 1].copy()
                df_synth_malicious['source'] = 'synthetic_malicious'
                df_malicious = pd.concat([df_malicious, df_synth_malicious[['domain', 'label', 'source']]], ignore_index=True)
            except Exception as e:
                logger.error(f"Failed to generate synthetic malicious domains: {e}")

        # Collect benign domains
        df_benign = self.tranco.collect(max_domains=num_benign)

        if len(df_benign) < num_benign:
            logger.warning(f"Could not collect enough real benign domains ({len(df_benign)}/{num_benign}). Generating synthetic data...")
            try:
                remaining = num_benign - len(df_benign)
                generator = PhishingDatasetGenerator(num_legit=remaining, num_phishing=0, seed=42)
                df_synth = generator.generate()
                df_synth_benign = df_synth[df_synth['label'] == 0].copy()
                df_synth_benign['source'] = 'synthetic_benign'
                df_benign = pd.concat([df_benign, df_synth_benign[['domain', 'label', 'source']]], ignore_index=True)
            except Exception as e:
                logger.error(f"Failed to generate synthetic benign domains: {e}")

        # Combine datasets
        df_combined = pd.concat([df_malicious, df_benign], ignore_index=True)
        df_combined = df_combined.drop_duplicates(subset=['domain'])
        
        logger.info(f"Collection complete. Total domains: {len(df_combined)} (Target malicious: {num_malicious}, Target benign: {num_benign})")
        return df_combined

    def save(self, df: pd.DataFrame, output_path: str) -> str:
        """
        Saves the DataFrame to a CSV file.

        Args:
            df: The DataFrame to save.
            output_path: Path to save the CSV file.

        Returns:
            The absolute path to the saved file.
        """
        path = pathlib.Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        abs_path = str(path.absolute())
        df.to_csv(abs_path, index=False)
        logger.info(f"Dataset saved to {abs_path}")
        return abs_path

    def load(self, path: str) -> pd.DataFrame:
        """
        Loads the dataset from a CSV file.

        Args:
            path: Path to the CSV file.

        Returns:
            DataFrame containing the dataset.
        """
        logger.info(f"Loading dataset from {path}")
        return pd.read_csv(path)


if __name__ == '__main__':
    # Test collection with small sample sizes
    logger.info("Running DatasetCollector tests...")
    collector = DatasetCollector()
    
    # Try collecting 10 malicious and 10 benign
    df = collector.collect(num_malicious=10, num_benign=10)
    
    print("Collected Dataset:")
    print(df.head(20))
    
    # Test saving and loading
    test_path = "test_dataset.csv"
    collector.save(df, test_path)
    loaded_df = collector.load(test_path)
    print(f"Loaded {len(loaded_df)} rows from {test_path}")
    
    # Cleanup
    if os.path.exists(test_path):
        os.remove(test_path)
