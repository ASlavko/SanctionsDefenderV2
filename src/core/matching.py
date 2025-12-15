import re
import unicodedata

class NameMatcher:
    @staticmethod
    def normalize_name(name: str) -> str:
        if not name:
            return ""
        
        # 1. Lowercase
        name = name.lower()
        
        # 2. Remove accents (keep non-Latin characters)
        name = unicodedata.normalize('NFKD', name)
        name = "".join([c for c in name if not unicodedata.combining(c)])
        
        # 3. Remove special chars (keep alphanumeric and spaces)
        # Replace with space to avoid merging words (e.g. "Vladimir-Putin" -> "Vladimir Putin")
        name = re.sub(r'[^\w\s]', ' ', name)
        
        # 4. Remove extra spaces
        name = re.sub(r'\s+', ' ', name).strip()
        
        # 5. Remove common corporate suffixes (optional, can be expanded)
        suffixes = [' ltd', ' limited', ' inc', ' incorporated', ' llc', ' sa', ' gmbh']
        for suffix in suffixes:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
                break
                
        return name
