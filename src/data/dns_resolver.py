import dns.resolver
import dns.exception
import sqlite3
import json
import time
import logging
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any

logger = logging.getLogger(__name__)

class DNSResolver:
    """DNS Resolver with SQLite caching."""
    
    def __init__(self, cache_db: str = 'data/dns_cache.db', timeout: float = 1.5,
                 max_retries: int = 1, nameservers: Optional[List[str]] = None,
                 rate_limit: int = 50):
        """Initialize the DNSResolver.
        
        Args:
            cache_db: Path to the SQLite cache database.
            timeout: DNS query timeout in seconds.
            max_retries: Maximum number of retries for DNS queries.
            nameservers: Optional list of nameservers to use.
            rate_limit: Queries per second limit.
        """
        self.cache_db = Path(cache_db)
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limit = rate_limit
        
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = timeout
        self.resolver.lifetime = timeout
        if nameservers:
            self.resolver.nameservers = nameservers
            
        # Ensure directory exists if not memory
        if str(self.cache_db) != ':memory:':
            self.cache_db.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(str(self.cache_db))
        self.conn.row_factory = sqlite3.Row
        self._init_db()
        
    def _init_db(self) -> None:
        """Initialize the SQLite database schema."""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dns_cache (
                domain TEXT PRIMARY KEY,
                ip_addresses TEXT,
                nameservers TEXT,
                dns_status TEXT,
                resolved_at REAL,
                ttl INTEGER DEFAULT 86400
            )
        ''')
        self.conn.commit()
        
    def __enter__(self) -> 'DNSResolver':
        """Context manager entry."""
        return self
        
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
        
    def close(self) -> None:
        """Close the SQLite connection."""
        self.conn.close()
        
    def clear_cache(self) -> None:
        """Drop and recreate the cache table."""
        cursor = self.conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS dns_cache')
        self.conn.commit()
        self._init_db()
        logger.info("Cache cleared.")
        
    def get_cached_count(self) -> int:
        """Return number of cached entries.
        
        Returns:
            Number of entries in the cache.
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM dns_cache')
        return cursor.fetchone()[0]
        
    def resolve_domain(self, domain: str) -> Dict[str, Any]:
        """Resolve A and NS records for a domain.
        
        Args:
            domain: Domain to resolve.
            
        Returns:
            Dict containing domain, ip_addresses, nameservers, and dns_status.
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM dns_cache WHERE domain = ?', (domain,))
        row = cursor.fetchone()
        
        current_time = time.time()
        
        if row:
            resolved_at = row['resolved_at']
            ttl = row['ttl']
            if current_time - resolved_at < ttl:
                # Valid cache entry
                return {
                    'domain': domain,
                    'ip_addresses': json.loads(row['ip_addresses']),
                    'nameservers': json.loads(row['nameservers']),
                    'dns_status': row['dns_status'],
                    'from_cache': True,
                }
                
        ip_addresses: List[str] = []
        nameservers: List[str] = []
        
        # Resolve A records
        for _ in range(self.max_retries):
            try:
                answers = self.resolver.resolve(domain, 'A')
                ip_addresses = [rdata.to_text() for rdata in answers]
                break
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                break
            except (dns.resolver.Timeout, dns.exception.DNSException) as e:
                logger.debug("A record resolution error for %s: %s", domain, e)
                
        # Resolve NS records
        for _ in range(self.max_retries):
            try:
                answers = self.resolver.resolve(domain, 'NS')
                nameservers = [rdata.to_text().rstrip('.') for rdata in answers]
                break
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                break
            except (dns.resolver.Timeout, dns.exception.DNSException) as e:
                logger.debug("NS record resolution error for %s: %s", domain, e)
                
        if ip_addresses and nameservers:
            dns_status = 'resolved'
        elif ip_addresses or nameservers:
            dns_status = 'partial'
        else:
            dns_status = 'failed'
            
        # Save to cache
        cursor.execute('''
            INSERT OR REPLACE INTO dns_cache 
            (domain, ip_addresses, nameservers, dns_status, resolved_at, ttl)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            domain,
            json.dumps(ip_addresses),
            json.dumps(nameservers),
            dns_status,
            current_time,
            86400
        ))
        self.conn.commit()
        
        return {
            'domain': domain,
            'ip_addresses': ip_addresses,
            'nameservers': nameservers,
            'dns_status': dns_status,
            'from_cache': False,
        }
        
    def resolve_batch(self, domains: List[str], batch_size: int = 100) -> pd.DataFrame:
        """Resolves a list of domains with progress logging.
        
        Args:
            domains: List of domains to resolve.
            batch_size: Number of domains between progress logs.
            
        Returns:
            DataFrame containing resolved data.
        """
        results = []
        total = len(domains)
        sleep_time = 1.0 / self.rate_limit if self.rate_limit > 0 else 0
        
        for i, domain in enumerate(domains):
            if i > 0 and i % batch_size == 0:
                logger.info("Resolved %d/%d domains...", i, total)
                
            result = self.resolve_domain(domain)
            results.append({
                'domain': result['domain'],
                'ip_addresses': json.dumps(result['ip_addresses']),
                'nameservers': json.dumps(result['nameservers']),
                'dns_status': result['dns_status']
            })
            
            if sleep_time > 0 and not result.get('from_cache', False):
                time.sleep(sleep_time)
                
        logger.info("Finished resolving %d domains.", total)
        return pd.DataFrame(results)


def explode_dns_records(dns_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Explode DNS records into separate DataFrames for IPs and NS.
    
    Args:
        dns_df: DataFrame containing DNS resolution results.
        
    Returns:
        Tuple of (domain_ip_df, domain_ns_df).
    """
    records_ip = []
    records_ns = []
    
    for _, row in dns_df.iterrows():
        domain = row['domain']
        
        ip_addresses = json.loads(row['ip_addresses'])
        for ip in ip_addresses:
            records_ip.append({'domain': domain, 'ip': ip})
            
        nameservers = json.loads(row['nameservers'])
        for ns in nameservers:
            records_ns.append({'domain': domain, 'nameserver': ns})
            
    domain_ip_df = pd.DataFrame(records_ip)
    domain_ns_df = pd.DataFrame(records_ns)
    
    return domain_ip_df, domain_ns_df


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    test_domains = ['google.com', 'github.com', 'example.com', 'facebook.com', 'microsoft.com']
    
    # Use memory db for testing
    with DNSResolver(cache_db=':memory:', rate_limit=5) as resolver:
        logger.info("Resolving domains...")
        df = resolver.resolve_batch(test_domains, batch_size=2)
        
        logger.info("DNS DataFrame:")
        print(df.to_string())
        
        logger.info("Exploding records...")
        ip_df, ns_df = explode_dns_records(df)
        
        logger.info("IP Records:")
        print(ip_df.to_string())
        
        logger.info("NS Records:")
        print(ns_df.to_string())
        
        count = resolver.get_cached_count()
        logger.info("Cached entries: %d", count)
