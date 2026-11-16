"""
Feature Extractor Module (v2.0)
================================
Extracts structural, lexical, and DNS-aware features from domain names
for phishing detection.

Features:
- Lexical: length, entropy, digit ratio, hyphens, consonant sequences
- Brand: leet-speak aware brand similarity (Levenshtein distance)
- DNS-aware: number of A-records, NS-records, shared IP/NS flags
- TLD: suspicious TLD detection via tldextract

Uses tldextract for accurate subdomain/domain/suffix parsing.
"""

import re
import math
import logging
from typing import List, Dict, Optional, Set

import numpy as np
import pandas as pd

try:
    import tldextract
    HAS_TLDEXTRACT = True
except ImportError:
    HAS_TLDEXTRACT = False

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────

# Top brands commonly targeted by phishing attacks
TOP_BRANDS = [
    'google', 'facebook', 'apple', 'microsoft', 'amazon',
    'paypal', 'netflix', 'bank', 'chase', 'wellsfargo',
    'instagram', 'twitter', 'linkedin', 'dropbox', 'adobe',
    'yahoo', 'outlook', 'office365', 'icloud', 'whatsapp',
    'steam', 'roblox', 'coinbase', 'binance', 'metamask',
    'spotify', 'twitch', 'discord', 'telegram', 'signal',
]

# TLDs commonly abused by phishing domains
SUSPICIOUS_TLDS: Set[str] = {
    'tk', 'ml', 'ga', 'cf', 'gq', 'xyz', 'top', 'club',
    'online', 'site', 'info', 'pw', 'cc', 'buzz', 'work',
    'icu', 'cam', 'bid', 'stream', 'download', 'racing',
    'win', 'gdn', 'loan', 'men', 'click', 'link', 'space',
    'surf', 'rest', 'fit', 'monster', 'sbs', 'cfd',
}

# Keywords that indicate phishing intent
LOGIN_KEYWORDS = [
    'login', 'secure', 'account', 'verify', 'update', 'confirm',
    'banking', 'signin', 'sign-in', 'password', 'credential',
    'authenticate', 'validation', 'suspend', 'restrict', 'unlock',
    'alert', 'notification', 'security', 'wallet', 'recover',
]

# Leet-speak mapping for brand impersonation detection
LEET_MAP = str.maketrans({
    '0': 'o', '1': 'l', '3': 'e', '4': 'a',
    '5': 's', '7': 't', '8': 'b', '9': 'g',
})


# ── Core Functions ─────────────────────────────────────────────────────────

def levenshtein_distance(s1: str, s2: str) -> int:
    """Compute the Levenshtein (edit) distance between two strings.

    Args:
        s1: First string.
        s2: Second string.

    Returns:
        Integer edit distance.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    prev_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row

    return prev_row[-1]


def calculate_entropy(text: str) -> float:
    """Calculate Shannon entropy of a string.

    Higher entropy suggests more randomness (common in malicious domains).

    Args:
        text: Input string.

    Returns:
        Shannon entropy value.
    """
    if not text:
        return 0.0

    freq: Dict[str, int] = {}
    for char in text:
        freq[char] = freq.get(char, 0) + 1

    length = len(text)
    entropy = 0.0
    for count in freq.values():
        probability = count / length
        if probability > 0:
            entropy -= probability * math.log2(probability)

    return round(entropy, 4)


def get_longest_consonant_sequence(text: str) -> int:
    """Find the longest consecutive sequence of consonants.

    Random-string domains tend to have longer consonant sequences.

    Args:
        text: Input string.

    Returns:
        Length of longest consonant sequence.
    """
    max_seq = 0
    current_seq = 0
    for char in text.lower():
        if char in 'bcdfghjklmnpqrstvwxyz':
            current_seq += 1
            max_seq = max(max_seq, current_seq)
        else:
            current_seq = 0
    return max_seq


def _parse_domain(domain: str) -> Dict[str, str]:
    """Parse a domain into subdomain, registered domain, and suffix.

    Uses tldextract when available, falls back to manual splitting.

    Args:
        domain: Raw domain string.

    Returns:
        Dict with keys: subdomain, domain_body, suffix, fqdn.
    """
    # Clean the input
    clean = domain.lower().strip()
    clean = re.sub(r'^https?://', '', clean)
    clean = clean.rstrip('/')
    # Remove path/query
    clean = clean.split('/')[0].split('?')[0].split('#')[0]

    if HAS_TLDEXTRACT:
        ext = tldextract.extract(clean)
        return {
            'subdomain': ext.subdomain,
            'domain_body': ext.domain,
            'suffix': ext.suffix,
            'fqdn': clean,
        }
    else:
        # Manual fallback
        parts = clean.split('.')
        suffix = parts[-1] if parts else ''
        domain_body = parts[-2] if len(parts) >= 2 else clean
        subdomain = '.'.join(parts[:-2]) if len(parts) > 2 else ''
        return {
            'subdomain': subdomain,
            'domain_body': domain_body,
            'suffix': suffix,
            'fqdn': clean,
        }


def _brand_similarity(domain_body: str, fqdn: str) -> int:
    """Compute minimum edit distance to any known brand.

    Includes leet-speak normalization and hyphen-segment splitting
    to catch impersonation like 'g00gle-login'.

    Args:
        domain_body: The registered domain name (without TLD).
        fqdn: Full domain for segment splitting.

    Returns:
        Minimum edit distance (0 = exact brand match). Capped at 20.
    """
    parts = fqdn.split('.')
    segments: Set[str] = set()

    for part in parts[:-1]:  # Exclude TLD
        low = part.lower()
        segments.add(low)
        # Split by hyphens to check individual words
        segments.update(low.split('-'))

    # Remove empty strings
    segments.discard('')

    min_dist = 20  # Cap value

    for brand in TOP_BRANDS:
        for segment in segments:
            # Raw distance
            dist = levenshtein_distance(segment, brand)
            min_dist = min(min_dist, dist)

            # Leet-normalized distance
            normalized = segment.translate(LEET_MAP)
            if normalized != segment:
                dist_norm = levenshtein_distance(normalized, brand)
                min_dist = min(min_dist, dist_norm)

            if min_dist == 0:
                return 0  # Can't get better than exact match

    return min_dist


# ── Main Feature Extraction ───────────────────────────────────────────────

def extract_domain_features(
    domain: str,
    dns_info: Optional[Dict] = None,
) -> Dict[str, float]:
    """Extract all structural, lexical, and DNS-aware features from a domain.

    Args:
        domain: Domain name string (e.g., 'example.com').
        dns_info: Optional dict with DNS resolution data:
            {'ip_addresses': List[str], 'nameservers': List[str],
             'dns_status': str}

    Returns:
        Dictionary of feature names to numeric values.
    """
    parsed = _parse_domain(domain)
    fqdn = parsed['fqdn']
    domain_body = parsed['domain_body']
    subdomain = parsed['subdomain']
    suffix = parsed['suffix']

    parts = fqdn.split('.')

    features: Dict[str, float] = {}

    # ── Lexical Features ───────────────────────────────────────────────

    # 1. Domain length
    features['domain_length'] = len(fqdn)

    # 2. Subdomain count
    features['subdomain_count'] = len(subdomain.split('.')) if subdomain else 0

    # 3. Dot count
    features['dot_count'] = fqdn.count('.')

    # 4. Hyphen count
    features['hyphen_count'] = fqdn.count('-')

    # 5. Digit count
    features['digit_count'] = sum(c.isdigit() for c in fqdn)

    # 6. Special character count (non-alphanumeric, non-dot, non-hyphen)
    features['special_char_count'] = sum(
        1 for c in fqdn if not c.isalnum() and c not in '.-'
    )

    # 7. Shannon entropy (of domain body, excluding TLD)
    body_for_entropy = '.'.join(parts[:-1]) if len(parts) > 1 else fqdn
    features['entropy'] = calculate_entropy(body_for_entropy)

    # 8. Has IP address pattern
    ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    features['has_ip'] = 1.0 if re.search(ip_pattern, fqdn) else 0.0

    # 9. Vowel ratio
    alpha_chars = [c for c in domain_body if c.isalpha()]
    vowel_count = sum(1 for c in alpha_chars if c.lower() in 'aeiou')
    features['vowel_ratio'] = round(
        vowel_count / max(len(alpha_chars), 1), 4
    )

    # 10. Digit ratio
    features['digit_ratio'] = round(
        features['digit_count'] / max(len(fqdn), 1), 4
    )

    # 11. Is Punycode (internationalized domain name)
    features['is_punycode'] = 1.0 if 'xn--' in fqdn else 0.0

    # 12. TLD length
    features['tld_length'] = len(suffix)

    # 13. Longest word length (between dots)
    features['longest_word_length'] = max(
        (len(p) for p in parts), default=0
    )

    # 14. Suspicious TLD
    features['suspicious_tld'] = 1.0 if suffix in SUSPICIOUS_TLDS else 0.0

    # 15. Brand similarity (leet-speak aware)
    features['brand_similarity'] = float(
        _brand_similarity(domain_body, fqdn)
    )

    # 16. Longest consonant sequence
    features['consonant_sequence'] = get_longest_consonant_sequence(
        body_for_entropy
    )

    # 17. Contains login/security keywords
    features['contains_login_keywords'] = 1.0 if any(
        kw in fqdn for kw in LOGIN_KEYWORDS
    ) else 0.0

    # ── DNS-Aware Features ─────────────────────────────────────────────

    if dns_info is not None:
        ip_list = dns_info.get('ip_addresses', [])
        ns_list = dns_info.get('nameservers', [])
        status = dns_info.get('dns_status', 'failed')

        features['num_a_records'] = float(len(ip_list))
        features['num_ns_records'] = float(len(ns_list))
        features['dns_resolved'] = 1.0 if status in ('resolved', 'partial') else 0.0
        features['dns_failed'] = 1.0 if status == 'failed' else 0.0
    else:
        features['num_a_records'] = 0.0
        features['num_ns_records'] = 0.0
        features['dns_resolved'] = 0.0
        features['dns_failed'] = 1.0

    return features


def extract_features_batch(
    domains: List[str],
    dns_records: Optional[Dict[str, Dict]] = None,
) -> pd.DataFrame:
    """Extract features from a batch of domain names.

    Args:
        domains: List of domain name strings.
        dns_records: Optional mapping of domain -> dns_info dict.

    Returns:
        DataFrame with one row per domain and feature columns.
    """
    logger.info("Extracting features from %d domains...", len(domains))

    features_list = []
    for i, domain in enumerate(domains):
        try:
            dns_info = dns_records.get(domain) if dns_records else None
            features = extract_domain_features(domain, dns_info=dns_info)
            features['domain'] = domain
            features_list.append(features)
        except Exception as e:
            logger.warning("Failed to extract features for '%s': %s", domain, e)
            continue

        if (i + 1) % 500 == 0:
            logger.info("  Processed %d/%d domains", i + 1, len(domains))

    df = pd.DataFrame(features_list)

    # Reorder columns with 'domain' first
    if 'domain' in df.columns:
        cols = ['domain'] + [c for c in df.columns if c != 'domain']
        df = df[cols]

    logger.info("Feature extraction complete. Shape: %s", df.shape)
    return df


# ── Feature Metadata ──────────────────────────────────────────────────────

def get_feature_names() -> List[str]:
    """Get the ordered list of all feature names.

    Returns:
        List of feature name strings.
    """
    return [
        'domain_length', 'subdomain_count', 'dot_count', 'hyphen_count',
        'digit_count', 'special_char_count', 'entropy', 'has_ip',
        'vowel_ratio', 'digit_ratio', 'is_punycode', 'tld_length',
        'longest_word_length', 'suspicious_tld', 'brand_similarity',
        'consonant_sequence', 'contains_login_keywords',
        # DNS-aware features
        'num_a_records', 'num_ns_records', 'dns_resolved', 'dns_failed',
    ]


def get_feature_descriptions() -> Dict[str, str]:
    """Get human-readable descriptions for each feature.

    Returns:
        Dictionary mapping feature names to descriptions.
    """
    return {
        'domain_length': 'Total length of the domain name',
        'subdomain_count': 'Number of subdomains (e.g., a.b.example.com has 2)',
        'dot_count': 'Number of dots in the domain',
        'hyphen_count': 'Number of hyphens in the domain',
        'digit_count': 'Number of numeric digits',
        'special_char_count': 'Count of special characters (excluding dots/hyphens)',
        'entropy': 'Shannon entropy measuring string randomness',
        'has_ip': 'Whether the domain contains an IP address pattern',
        'vowel_ratio': 'Ratio of vowels to total alphabetic characters',
        'digit_ratio': 'Ratio of digits to total characters',
        'is_punycode': 'Whether the domain uses Punycode encoding (IDN)',
        'tld_length': 'Length of the top-level domain',
        'longest_word_length': 'Length of the longest segment between dots',
        'suspicious_tld': 'Whether TLD is commonly abused for phishing',
        'brand_similarity': 'Min edit distance to known brand (lower = suspicious)',
        'consonant_sequence': 'Longest consecutive consonant run',
        'contains_login_keywords': 'Presence of login/security-related keywords',
        'num_a_records': 'Number of DNS A-records (IP addresses) resolved',
        'num_ns_records': 'Number of DNS NS-records (nameservers) resolved',
        'dns_resolved': 'Whether DNS resolution succeeded (fully or partially)',
        'dns_failed': 'Whether DNS resolution failed completely',
    }


if __name__ == '__main__':
    # Quick test
    test_domains = [
        'google.com',
        'g00gle-login.xyz',
        'paypa1-update.ml',
        'github.com',
        'secure-login-portal.net',
    ]

    print("\n  Feature Extraction Test")
    print("  " + "=" * 60)

    for domain in test_domains:
        features = extract_domain_features(domain)
        brand = features['brand_similarity']
        tld = features['suspicious_tld']
        kw = features['contains_login_keywords']
        ent = features['entropy']
        print(
            f"  {domain:35s}  brand={brand:2.0f}  "
            f"tld={tld:.0f}  kw={kw:.0f}  entropy={ent:.2f}"
        )

    print("  " + "=" * 60)
    print(f"  Total features: {len(get_feature_names())}")
    print()
