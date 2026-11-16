"""
Synthetic Phishing Domain Dataset Generator.

Generates a realistic dataset of legitimate and phishing domains with
associated metadata including registrar, IP address, nameservers,
creation dates, country codes, and SSL certificate information.

Phishing domains are generated using real-world attack techniques:
- Typosquatting (character substitution / transposition)
- Homograph attacks (lookalike characters)
- Subdomain abuse (prepending brand names)
- Random / algorithmically generated strings
"""

import csv
import logging
import random
import string
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants – realistic pools for metadata generation
# ---------------------------------------------------------------------------

LEGIT_DOMAINS_BASE: List[str] = [
    # Tech giants
    "google.com", "amazon.com", "microsoft.com", "apple.com", "facebook.com",
    "netflix.com", "twitter.com", "linkedin.com", "github.com", "stackoverflow.com",
    "dropbox.com", "slack.com", "zoom.us", "salesforce.com", "adobe.com",
    "oracle.com", "ibm.com", "intel.com", "nvidia.com", "amd.com",
    "spotify.com", "reddit.com", "pinterest.com", "tumblr.com", "quora.com",
    # E-commerce
    "ebay.com", "walmart.com", "target.com", "bestbuy.com", "etsy.com",
    "shopify.com", "aliexpress.com", "wayfair.com", "costco.com", "homedepot.com",
    # Finance
    "chase.com", "bankofamerica.com", "wellsfargo.com", "citibank.com",
    "paypal.com", "stripe.com", "squareup.com", "venmo.com", "robinhood.com",
    "fidelity.com", "schwab.com", "tdameritrade.com", "etrade.com",
    # Media / news
    "cnn.com", "bbc.com", "nytimes.com", "washingtonpost.com", "reuters.com",
    "bloomberg.com", "forbes.com", "theguardian.com", "usatoday.com",
    # Universities
    "mit.edu", "stanford.edu", "harvard.edu", "yale.edu", "princeton.edu",
    "caltech.edu", "columbia.edu", "uchicago.edu", "upenn.edu", "cornell.edu",
    "berkeley.edu", "ucla.edu", "umich.edu", "cmu.edu", "gatech.edu",
    "nyu.edu", "usc.edu", "duke.edu", "northwestern.edu", "jhu.edu",
    # Government
    "irs.gov", "ssa.gov", "usa.gov", "nasa.gov", "cdc.gov", "nih.gov",
    "whitehouse.gov", "fbi.gov", "sec.gov", "fda.gov",
    # Misc popular
    "wikipedia.org", "archive.org", "mozilla.org", "wordpress.org",
    "apache.org", "python.org", "nodejs.org", "rust-lang.org",
    "medium.com", "substack.com", "notion.so", "figma.com", "canva.com",
    "airbnb.com", "uber.com", "lyft.com", "doordash.com", "grubhub.com",
]

LEGIT_TLDS: List[str] = [
    "com", "org", "net", "edu", "gov", "io", "co", "us", "uk", "de",
    "ca", "au", "fr", "jp", "in", "it", "es", "nl", "se", "ch",
]

PHISHING_TLDS: List[str] = [
    "tk", "ml", "ga", "cf", "gq", "xyz", "top", "club", "online",
    "site", "info", "pw", "cc", "buzz", "work", "click", "link",
    "space", "fun", "icu", "monster", "rest",
]

BRAND_TARGETS: List[str] = [
    "google", "facebook", "apple", "microsoft", "amazon", "paypal",
    "netflix", "chase", "bankofamerica", "wellsfargo", "instagram",
    "whatsapp", "dropbox", "linkedin", "twitter", "coinbase",
    "binance", "outlook", "office365", "icloud",
]

REGISTRARS_LEGIT: List[str] = [
    "MarkMonitor Inc.", "CSC Corporate Domains", "Gandi SAS",
    "Google LLC", "Amazon Registrar", "Network Solutions LLC",
    "GoDaddy.com LLC", "Tucows Domains Inc.", "Namecheap Inc.",
    "Cloudflare Inc.",
]

REGISTRARS_PHISHING: List[str] = [
    "Namecheap Inc.", "PDR Ltd.", "Alibaba Cloud Computing",
    "GoDaddy.com LLC", "Tucows Domains Inc.", "NameSilo LLC",
    "Dynadot LLC", "Eranet International Limited",
    "Web Commerce Communications Limited", "Shinjiru Technology",
]

NAMESERVERS_LEGIT: List[str] = [
    "ns1.google.com", "ns1.amazon.com", "ns1.cloudflare.com",
    "ns1.digitalocean.com", "ns1.dnsimple.com", "pdns1.ultradns.net",
    "a1-67.akam.net", "ns-cloud-d1.googledomains.com",
    "ns1.awsdns-01.com", "ns1.p16.dynect.net",
]

NAMESERVERS_PHISHING: List[str] = [
    "ns1.hostinger.com", "ns1.registrar-servers.com",
    "dns1.namecheaphosting.com", "ns1.dns-parking.com",
    "ns1.sedoparking.com", "ns1.suspended-domain.com",
    "ns1.above.com", "ns1.bodis.com",
    "ns1.undeveloped.com", "ns1.parkingcrew.net",
]

SSL_ISSUERS_LEGIT: List[str] = [
    "DigiCert Inc", "Comodo CA Limited", "GlobalSign nv-sa",
    "Sectigo Limited", "Amazon", "Google Trust Services LLC",
    "Let's Encrypt", "Entrust Inc.",
]

SSL_ISSUERS_PHISHING: List[str] = [
    "Let's Encrypt", "cPanel Inc.", "ZeroSSL",
    "Sectigo Limited", "Cloudflare Inc.",
]

COUNTRIES_LEGIT: List[str] = [
    "US", "US", "US", "US",  # weighted heavier
    "GB", "DE", "CA", "AU", "FR", "JP", "NL", "SE", "CH", "IE",
]

COUNTRIES_PHISHING: List[str] = [
    "RU", "CN", "BR", "NG", "IN", "ID", "UA", "VN", "PH", "TR",
    "PA", "US", "NL", "RO", "BG", "HK", "MY",
]

HOMOGRAPH_MAP: Dict[str, str] = {
    "a": "а",  # Cyrillic а
    "e": "е",  # Cyrillic е
    "o": "о",  # Cyrillic о
    "p": "р",  # Cyrillic р
    "c": "с",  # Cyrillic с
    "i": "і",  # Ukrainian і
}

LOGIN_KEYWORDS: List[str] = [
    "login", "secure", "account", "verify", "update",
    "confirm", "banking", "signin", "auth", "validate",
    "support", "help", "service", "alert", "notification",
]


# ---------------------------------------------------------------------------
# Generator class
# ---------------------------------------------------------------------------


class PhishingDatasetGenerator:
    """Generate a synthetic dataset of legitimate and phishing domains.

    Attributes:
        seed: Random seed for reproducibility.
        num_legit: Number of legitimate domains to generate.
        num_phishing: Number of phishing domains to generate.
    """

    def __init__(
        self,
        num_legit: int = 2000,
        num_phishing: int = 2000,
        seed: int = 42,
    ) -> None:
        self.num_legit = num_legit
        self.num_phishing = num_phishing
        self.seed = seed
        random.seed(seed)
        logger.info(
            "DatasetGenerator initialised (legit=%d, phishing=%d, seed=%d)",
            num_legit, num_phishing, seed,
        )

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _random_ip(prefix: Optional[str] = None) -> str:
        """Generate a random IPv4 address, optionally with a fixed prefix."""
        if prefix:
            parts = prefix.split(".")
            remaining = 4 - len(parts)
            parts.extend(str(random.randint(1, 254)) for _ in range(remaining))
            return ".".join(parts)
        return ".".join(str(random.randint(1, 254)) for _ in range(4))

    @staticmethod
    def _random_date(start_year: int, end_year: int) -> str:
        """Return a random date string between *start_year* and *end_year*."""
        start = datetime(start_year, 1, 1)
        end = datetime(end_year, 12, 31)
        delta = end - start
        random_days = random.randint(0, delta.days)
        return (start + timedelta(days=random_days)).strftime("%Y-%m-%d")

    @staticmethod
    def _typosquat(domain: str) -> str:
        """Create a typosquatted variant of *domain*."""
        name, tld = domain.rsplit(".", 1)
        technique = random.choice(["swap", "drop", "double", "replace", "insert"])

        if len(name) < 3:
            technique = "insert"

        if technique == "swap" and len(name) >= 2:
            idx = random.randint(0, len(name) - 2)
            name = name[:idx] + name[idx + 1] + name[idx] + name[idx + 2:]
        elif technique == "drop":
            idx = random.randint(0, len(name) - 1)
            name = name[:idx] + name[idx + 1:]
        elif technique == "double":
            idx = random.randint(0, len(name) - 1)
            name = name[:idx] + name[idx] * 2 + name[idx + 1:]
        elif technique == "replace":
            replacements = {"o": "0", "l": "1", "i": "1", "e": "3", "a": "4", "s": "5"}
            candidates = [(i, c) for i, c in enumerate(name) if c in replacements]
            if candidates:
                idx, ch = random.choice(candidates)
                name = name[:idx] + replacements[ch] + name[idx + 1:]
        elif technique == "insert":
            idx = random.randint(0, len(name))
            char = random.choice(string.ascii_lowercase)
            name = name[:idx] + char + name[idx:]

        phish_tld = random.choice(PHISHING_TLDS + [tld, tld])
        return f"{name}.{phish_tld}"

    @staticmethod
    def _homograph(domain: str) -> str:
        """Create a homograph attack variant using lookalike characters."""
        name, tld = domain.rsplit(".", 1)
        candidates = [(i, c) for i, c in enumerate(name) if c in HOMOGRAPH_MAP]
        if candidates:
            idx, ch = random.choice(candidates)
            name = name[:idx] + HOMOGRAPH_MAP[ch] + name[idx + 1:]
        phish_tld = random.choice(PHISHING_TLDS + [tld])
        return f"{name}.{phish_tld}"

    @staticmethod
    def _subdomain_abuse(brand: str) -> str:
        """Generate subdomain-abuse phishing domain."""
        keyword = random.choice(LOGIN_KEYWORDS)
        random_part = "".join(random.choices(string.ascii_lowercase, k=random.randint(4, 8)))
        tld = random.choice(PHISHING_TLDS)
        patterns = [
            f"{brand}-{keyword}.{random_part}.{tld}",
            f"{keyword}.{brand}.{random_part}.{tld}",
            f"{brand}.{keyword}-{random_part}.{tld}",
            f"{keyword}-{brand}.{random_part}.{tld}",
            f"{brand}{keyword}.{random_part}.{tld}",
        ]
        return random.choice(patterns)

    @staticmethod
    def _random_string_domain() -> str:
        """Generate a random/algorithmically-generated domain name."""
        length = random.randint(8, 24)
        chars = string.ascii_lowercase + string.digits
        name = "".join(random.choices(chars, k=length))
        tld = random.choice(PHISHING_TLDS)
        return f"{name}.{tld}"

    # ------------------------------------------------------------------ #
    # Domain generators
    # ------------------------------------------------------------------ #

    def _generate_legit_domains(self) -> List[str]:
        """Generate *num_legit* legitimate domain names."""
        domains: List[str] = list(LEGIT_DOMAINS_BASE)

        # Add subdomains of known domains
        subdomains = ["www", "mail", "blog", "api", "docs", "app", "cdn",
                       "dev", "staging", "support", "shop", "store", "help"]
        for _ in range(300):
            base = random.choice(LEGIT_DOMAINS_BASE)
            sub = random.choice(subdomains)
            domains.append(f"{sub}.{base}")

        # Generate plausible company domains
        prefixes = [
            "tech", "cloud", "data", "smart", "cyber", "net", "web", "app",
            "digital", "info", "core", "soft", "sys", "dev", "inno",
        ]
        suffixes = [
            "solutions", "labs", "works", "hub", "ware", "logic", "base",
            "flow", "point", "stack", "mind", "craft", "forge", "sync",
        ]
        for _ in range(500):
            name = random.choice(prefixes) + random.choice(suffixes)
            tld = random.choice(LEGIT_TLDS)
            domains.append(f"{name}.{tld}")

        # Regional / country-specific domains
        country_tlds = ["co.uk", "com.au", "co.jp", "de", "fr", "ca",
                        "com.br", "co.in", "co.kr", "com.mx"]
        words = ["shop", "market", "service", "group", "online", "world",
                 "global", "city", "express", "connect"]
        for _ in range(400):
            word = random.choice(words) + random.choice(suffixes[:7])
            tld = random.choice(country_tlds)
            domains.append(f"{word}.{tld}")

        # University-style domains
        for _ in range(100):
            abbr = "".join(random.choices(string.ascii_lowercase, k=random.randint(3, 5)))
            domains.append(f"{abbr}.edu")

        random.shuffle(domains)
        return domains[: self.num_legit]

    def _generate_phishing_domains(self) -> List[str]:
        """Generate *num_phishing* phishing domain names using multiple techniques."""
        domains: List[str] = []
        per_technique = self.num_phishing // 4

        # 1. Typosquatting
        for _ in range(per_technique):
            target = random.choice(LEGIT_DOMAINS_BASE[:30])
            domains.append(self._typosquat(target))

        # 2. Homograph attacks
        for _ in range(per_technique):
            target = random.choice(LEGIT_DOMAINS_BASE[:30])
            domains.append(self._homograph(target))

        # 3. Subdomain abuse
        for _ in range(per_technique):
            brand = random.choice(BRAND_TARGETS)
            domains.append(self._subdomain_abuse(brand))

        # 4. Random string / DGA-style
        remaining = self.num_phishing - len(domains)
        for _ in range(remaining):
            domains.append(self._random_string_domain())

        random.shuffle(domains)
        return domains[: self.num_phishing]

    # ------------------------------------------------------------------ #
    # Metadata generation
    # ------------------------------------------------------------------ #

    def _generate_metadata(
        self, domain: str, label: int
    ) -> Dict[str, Any]:
        """Generate realistic metadata for a single domain.

        Args:
            domain: The domain name.
            label: 0 for legitimate, 1 for phishing.

        Returns:
            Dictionary with metadata fields.
        """
        is_phishing = label == 1

        registrar = random.choice(
            REGISTRARS_PHISHING if is_phishing else REGISTRARS_LEGIT
        )

        # IP – phishing domains are more likely to share IPs (hosting clusters)
        if is_phishing:
            ip_prefix = random.choice(
                [f"{random.randint(100, 200)}.{random.randint(1, 254)}.{random.randint(1, 254)}"]
                * 3 + [None]
            )
            ip_address = self._random_ip(ip_prefix)
        else:
            ip_address = self._random_ip()

        nameserver = random.choice(
            NAMESERVERS_PHISHING if is_phishing else NAMESERVERS_LEGIT
        )

        # Phishing domains tend to be very recently created
        if is_phishing:
            creation_date = self._random_date(2024, 2026)
        else:
            creation_date = self._random_date(1995, 2024)

        country = random.choice(
            COUNTRIES_PHISHING if is_phishing else COUNTRIES_LEGIT
        )

        # SSL – most legit sites have SSL; phishing sites increasingly use free certs
        has_ssl: bool
        ssl_issuer: str
        if is_phishing:
            has_ssl = random.random() < 0.65
            ssl_issuer = random.choice(SSL_ISSUERS_PHISHING) if has_ssl else "None"
        else:
            has_ssl = random.random() < 0.96
            ssl_issuer = random.choice(SSL_ISSUERS_LEGIT) if has_ssl else "None"

        return {
            "domain": domain,
            "label": label,
            "registrar": registrar,
            "ip_address": ip_address,
            "nameserver": nameserver,
            "creation_date": creation_date,
            "country": country,
            "has_ssl": int(has_ssl),
            "ssl_issuer": ssl_issuer,
        }

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def generate(self) -> pd.DataFrame:
        """Generate the complete dataset and return it as a DataFrame.

        Returns:
            pandas DataFrame with columns:
                domain, label, registrar, ip_address, nameserver,
                creation_date, country, has_ssl, ssl_issuer
        """
        logger.info("Generating legitimate domains …")
        legit_domains = self._generate_legit_domains()

        logger.info("Generating phishing domains …")
        phishing_domains = self._generate_phishing_domains()

        records: List[Dict[str, Any]] = []
        for domain in legit_domains:
            records.append(self._generate_metadata(domain, label=0))
        for domain in phishing_domains:
            records.append(self._generate_metadata(domain, label=1))

        df = pd.DataFrame(records)
        # Shuffle the entire dataset
        df = df.sample(frac=1, random_state=self.seed).reset_index(drop=True)

        logger.info(
            "Dataset generated: %d rows (%d legit, %d phishing)",
            len(df),
            (df["label"] == 0).sum(),
            (df["label"] == 1).sum(),
        )
        return df

    def save(
        self,
        df: pd.DataFrame,
        output_path: str = "data/domains_dataset.csv",
    ) -> Path:
        """Save the dataset DataFrame to a CSV file.

        Args:
            df: The dataset DataFrame.
            output_path: Relative or absolute path for the output CSV.

        Returns:
            Resolved *Path* of the saved file.
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False, quoting=csv.QUOTE_NONNUMERIC)
        logger.info("Dataset saved to %s", path.resolve())
        return path.resolve()


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def main() -> None:
    """Generate and save the synthetic dataset."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )
    generator = PhishingDatasetGenerator(num_legit=2000, num_phishing=2000, seed=42)
    df = generator.generate()
    output = generator.save(df, output_path="data/domains_dataset.csv")
    print(f"\n[+] Dataset saved to {output}")
    print(df.head(10).to_string(index=False))
    print(f"\nLabel distribution:\n{df['label'].value_counts().to_string()}")


if __name__ == "__main__":
    main()
