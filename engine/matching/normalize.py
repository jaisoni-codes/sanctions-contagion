import unicodedata
from unidecode import unidecode
import re
import jellyfish

COMPANY_SUFFIXES = {'ltd', 'llc', 'pvt', 'jsc', 'gmbh', 'inc', 'co', 'corp', 'limited', 'corporation', 'plc', 'holdings'}
HONORIFICS = {'mr', 'mrs', 'dr', 'shri', 'sheikh', 'ms'}
ALIAS_MAP = {
    'mohd': 'mohammad',
    'md': 'mohammad',
    'muhd': 'mohammad',
    'mohammed': 'mohammad',
    'muhammad': 'mohammad',
    'intl': 'international',
    'tech': 'technology'
}

def clean_text(text: str) -> str:
    if not text:
        return ""
    # Unicode NFKD, casefold
    text = unicodedata.normalize('NFKD', str(text)).casefold()
    # Transliterate non-Latin
    text = unidecode(text)
    # Strip diacritics and punctuation
    text = re.sub(r'[^\w\s]', ' ', text)
    # Extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def normalize_party(name: str, kind: str) -> dict:
    cleaned = clean_text(name)
    tokens = cleaned.split()
    
    # Remove honorifics
    if kind == 'INDIVIDUAL':
        tokens = [t for t in tokens if t not in HONORIFICS]
    
    company_suffix = None
    if kind == 'COMPANY':
        # Remove all trailing company suffixes
        while tokens and tokens[-1] in COMPANY_SUFFIXES:
            company_suffix = tokens.pop()
            
    # Alias canonicalization
    tokens = [ALIAS_MAP.get(t, t) for t in tokens]
    
    # Let's create a single string without spaces for brand matching (e.g. Sam Soong -> samsoong)
    joined_name = "".join(tokens)
    phonetic_joined = jellyfish.metaphone(joined_name) if joined_name else ""
    
    sorted_tokens = sorted(tokens)
    phonetics = [jellyfish.metaphone(t) for t in tokens]
    
    return {
        "norm_name": " ".join(tokens),
        "joined_name": joined_name,
        "phonetic_joined": phonetic_joined,
        "sorted_tokens": sorted_tokens,
        "phonetics": phonetics,
        "company_suffix": company_suffix
    }
