import re
import unicodedata
from anyascii import anyascii

class NameMatcher:
    @staticmethod
    def normalize_name(name: str) -> str:
        if not name:
            return ""
        
        # 1. Transliterate to Latin (Transcription)
        # Handle Russian, Arabic, Chinese, etc.
        name = anyascii(name)
        
        # 2. Lowercase
        name = name.lower()
        
        # 3. Remove accents (keep non-Latin characters - though anyascii already handled them)
        name = unicodedata.normalize('NFKD', name)
        name = "".join([c for c in name if not unicodedata.combining(c)])
        
        # 4. Remove special chars (keep alphanumeric and spaces)
        # Replace with space to avoid merging words (e.g. "Vladimir-Putin" -> "Vladimir Putin")
        name = re.sub(r'[^\w\s]', ' ', name)
        
        # 5. Remove extra spaces
        name = re.sub(r'\s+', ' ', name).strip()
        
        # 6. Remove common corporate suffixes (optional, can be expanded)
        suffixes = [' ltd', ' limited', ' inc', ' incorporated', ' llc', ' sa', ' gmbh']
        for suffix in suffixes:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
                break
                
        return name
