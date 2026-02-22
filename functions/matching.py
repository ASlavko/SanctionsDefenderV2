"""
Advanced name matching logic for sanctions screening.
Implements multiple matching algorithms with weighted scoring.
"""

import unicodedata
import re
from typing import Dict, List, Tuple
from anyascii import anyascii


class NameMatcher:
    """Advanced fuzzy matching for sanctions names"""
    
    def __init__(self):
        # Soundex lookup for phonetic matching
        self.soundex_cache = {}
    
    # ============================================================================
    # NAME NORMALIZATION
    # ============================================================================
    
    @staticmethod
    def normalize_name(name: str) -> str:
        """
        Normalize name by transliterating to Latin, removing diacritics and standardizing format.
        Converts: "Путин" -> "putin", "José García" -> "jose garcia"
        """
        # 1. Transliterate to Latin (Transcription)
        # Handle Russian, Arabic, Chinese, etc.
        name = anyascii(name)
        
        # 2. Convert to NFD (decomposed) form to separate base chars from diacritics
        nfd = unicodedata.normalize('NFD', name)
        # 3. Remove combining characters (diacritics)
        without_diacritics = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
        # 4. Remove extra whitespace and convert to lowercase
        return ' '.join(without_diacritics.lower().split())
    
    @staticmethod
    def remove_prefixes_suffixes(name: str) -> str:
        """
        Remove common name prefixes/suffixes for better matching.
        Examples: "Dr. John Smith" -> "John Smith"
                  "Juan Carlos Lopez Jr." -> "Juan Carlos Lopez"
        """
        name = name.strip()
        
        # Common prefixes to remove
        prefixes = [
            r'^(mr|mrs|ms|dr|prof|sir|dame)\s+',  # Titles
            r'^(van|von|de|da|di|du|la|le|el)(\s|$)',  # Name particles
        ]
        
        # Common suffixes to remove
        suffixes = [
            r'\s+(jr|sr|ii|iii|iv|v)(\s|\.)?$',  # Suffixes
            r'\s+(junior|senior)(\s|\.)?$',  # Written out suffixes
        ]
        
        # Apply replacements (case-insensitive)
        for pattern in prefixes:
            name = re.sub(pattern, '', name, flags=re.IGNORECASE)
        
        for pattern in suffixes:
            name = re.sub(pattern, '', name, flags=re.IGNORECASE)
        
        return ' '.join(name.split())
    
    @staticmethod
    def normalize_company_name(name: str) -> str:
        """
        Normalize company name by removing common business suffixes.
        Examples: "Apple Inc." -> "Apple"
                  "Microsoft Corporation" -> "Microsoft"
        """
        name = name.strip().lower()
        
        company_suffixes = [
            r'\s+(inc|incorporated|corp|corporation|co|company|ltd|limited|llc|llp|pllc)\.?$',
            r'\s+(gmbh|ag|sa|s\.a|s\.a\.s|pty|pty\s+ltd|b\.v|n\.v|plc|s\.l)\.?$',  # International
            r'\s+(as|oas|aka)\.?$',  # Other common endings
        ]
        
        for pattern in company_suffixes:
            name = re.sub(pattern, '', name, flags=re.IGNORECASE)
        
        return ' '.join(name.split())
    
    @staticmethod
    def generate_search_tokens(text: str) -> List[str]:
        """
        Generate search tokens for a given text.
        Splits by whitespace, removes special chars, converts to lowercase.
        Generates tokens and prefixes (length >= 3) for indexed search.
        """
        if not text:
            return []
        
        # Normalize
        normalized = NameMatcher.normalize_name(text)
        
        # Remove non-alphanumeric characters but keep spaces
        cleaned = ''.join(c for c in normalized if c.isalnum() or c.isspace())
        
        tokens = set()
        for word in cleaned.split():
            if len(word) < 2: continue
            
            # Add full word
            tokens.add(word)
            
            # Add prefixes for "starts with" search support
            # Only for words length 3 or more
            for i in range(3, len(word)):
                tokens.add(word[:i])
        
        return list(tokens)

    # ============================================================================
    # EDIT DISTANCE (LEVENSHTEIN)
    # ============================================================================
    
    @staticmethod
    def levenshtein_distance(s1: str, s2: str) -> int:
        """
        Calculate Levenshtein distance (edit distance) between two strings.
        Measures minimum number of single-character edits needed.
        Returns: 0 for identical strings, higher values for more differences
        """
        if len(s1) < len(s2):
            return NameMatcher.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        # Use only two rows for space efficiency
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Cost of insertions, deletions, or substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def levenshtein_ratio(self, s1: str, s2: str) -> float:
        """
        Calculate similarity ratio based on Levenshtein distance (0-100).
        100 = identical, 0 = completely different
        """
        distance = self.levenshtein_distance(s1, s2)
        max_length = max(len(s1), len(s2))
        if max_length == 0:
            return 100.0
        return ((max_length - distance) / max_length) * 100
    
    # ============================================================================
    # SOUNDEX & PHONETIC MATCHING
    # ============================================================================
    
    def soundex(self, name: str) -> str:
        """
        Generate Soundex code for phonetic matching.
        Names that sound similar get the same code.
        Examples: "Smith" and "Smyth" both -> "S530"
        """
        name = name.upper().replace(' ', '')
        
        if not name:
            return ''
        
        # Mapping of letters to digits
        mapping = {
            'B': '1', 'F': '1', 'P': '1', 'V': '1',
            'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
            'D': '3', 'T': '3',
            'L': '4',
            'M': '5', 'N': '5',
            'R': '6'
        }
        
        # First letter stays
        code = name[0]
        prev_code = mapping.get(name[0], '0')
        
        # Process remaining letters
        for letter in name[1:]:
            digit = mapping.get(letter, '0')
            # Skip vowels and duplicates
            if digit != '0' and digit != prev_code:
                code += digit
            if letter not in 'AEIOUYHW':
                prev_code = digit
        
        # Pad or truncate to 4 characters
        return (code + '000')[:4]
    
    def metaphone(self, name: str) -> str:
        """
        Generate Metaphone code for more sophisticated phonetic matching.
        Improved over Soundex for American English pronunciation.
        """
        name = name.upper().replace(' ', '')
        
        if not name:
            return ''
        
        # Drop duplicates and handle initial letters
        previous_was_vowel = False
        code = ''
        
        for i, char in enumerate(name):
            if i == 0:
                # First letter handling
                if char in 'AEIOUWY':
                    code = char
                elif char == 'K' and len(name) > 1 and name[1] == 'N':
                    code = 'N'
                else:
                    code = char
                previous_was_vowel = char in 'AEIOU'
            else:
                # Skip duplicate consonants
                if code and code[-1] == char and char not in 'AEIOU':
                    continue
                
                if char in 'AEIOU':
                    if not previous_was_vowel:
                        code += 'A'
                    previous_was_vowel = True
                else:
                    previous_was_vowel = False
                    
                    # Consonant rules
                    if char == 'B' and i > 0 and name[i-1] == 'M' and i == len(name) - 1:
                        pass  # Skip silent B
                    elif char in 'CGJKQSXZ':
                        code += 'X'
                    elif char == 'D':
                        code += 'T'
                    elif char == 'F' or char == 'V':
                        code += 'F'
                    elif char == 'H' and previous_was_vowel:
                        code += 'H'
                    elif char == 'PH':
                        code += 'F'
                    elif char in 'DT':
                        code += 'T'
                    else:
                        code += char
        
        return code[:4] if code else ''
    
    # ============================================================================
    # TOKEN-BASED MATCHING
    # ============================================================================
    
    @staticmethod
    def token_overlap(s1: str, s2: str) -> float:
        """
        Calculate token overlap ratio (0-100).
        Useful for comparing multi-word names.
        """
        tokens1 = set(s1.lower().split())
        tokens2 = set(s2.lower().split())
        
        if not tokens1 or not tokens2:
            return 0.0
        
        common = len(tokens1 & tokens2)
        total = len(tokens1 | tokens2)
        
        return (common / total) * 100 if total > 0 else 0.0
    
    @staticmethod
    def substring_match(query: str, target: str) -> Tuple[bool, float]:
        """
        Check if query is substring of target or vice versa.
        Returns: (is_match, confidence_score)
        """
        query_lower = query.lower()
        target_lower = target.lower()
        
        # Exact substring match
        if query_lower in target_lower or target_lower in query_lower:
            # Score based on coverage percentage
            longer = max(len(query_lower), len(target_lower))
            shorter = min(len(query_lower), len(target_lower))
            coverage = (shorter / longer) * 100
            return (True, coverage)
        
        return (False, 0.0)
    
    # ============================================================================
    # MAIN MATCHING ALGORITHM
    # ============================================================================
    
    def calculate_match_score(self, query_name: str, record: Dict, 
                             entity_type: str = 'company', 
                             use_phonetic: bool = True) -> float:
        """
        Calculate comprehensive match score (0-100) using multiple algorithms.
        
        Args:
            query_name: Name to search for
            record: Sanctions record with main_name and aliases
            entity_type: 'company' or 'individual' for type-specific normalization
            use_phonetic: Whether to use phonetic matching
        
        Returns:
            Confidence score 0-100
        """
        scores = []
        
        # Normalize names
        query_normalized = self.normalize_name(query_name)
        query_clean = self.remove_prefixes_suffixes(query_normalized)
        
        main_name = record.get('main_name', '')
        main_normalized = self.normalize_name(main_name)
        main_clean = self.remove_prefixes_suffixes(main_normalized)
        
        # Apply entity-specific normalization
        if entity_type == 'company':
            query_clean = self.normalize_company_name(query_clean)
            main_clean = self.normalize_company_name(main_clean)
        
        aliases = [self.normalize_name(a) for a in record.get('aliases', [])]
        
        # -------- EXACT MATCH (Score: 100) --------
        if query_normalized == main_normalized:
            return 100.0
        
        for alias in aliases:
            if query_normalized == alias:
                return 100.0
        
        # -------- EXACT MATCH ON CLEANED (Score: 98) --------
        if query_clean == main_clean:
            return 98.0  # Early return - no need to check other algorithms
        
        # PERFORMANCE: Quick reject if names are very different in length
        # If one name is 3x longer than the other, unlikely to match well
        # BUT: Still check for substring matches (e.g., "Sberbank" in "Sberbank Public Joint Stock Company")
        if max(len(query_clean), len(main_clean)) > 3 * min(len(query_clean), len(main_clean)):
            # IMPORTANT: Check substring match first - handles "Sberbank" matching "Sberbank Public Joint..."
            is_substring, substring_score = self.substring_match(query_clean, main_clean)
            if is_substring:
                # If query is contained in target or vice versa, it's likely a match
                return min(90.0, 70.0 + substring_score * 0.2)
            
            # Check aliases for substring matches
            for alias in aliases:
                is_substring, substring_score = self.substring_match(query_clean, alias)
                if is_substring:
                    return min(85.0, 65.0 + substring_score * 0.2)
            
            # Quick token check - if significant token overlap, still might be a match
            token_score = self.token_overlap(query_clean, main_clean)
            if token_score >= 60:
                return min(75.0, token_score)
            
            return 0.0  # Early exit - too different in length and no overlap
        
        # Continue with normal matching
        else:
            # -------- SUBSTRING MATCH (Score: 90) --------
            is_substring, substring_score = self.substring_match(query_clean, main_clean)
            if is_substring:
                scores.append(min(90.0, 70.0 + substring_score * 0.2))
            
            # Check aliases for substring
            for alias in aliases:
                is_substring, substring_score = self.substring_match(query_clean, alias)
                if is_substring:
                    scores.append(min(85.0, 65.0 + substring_score * 0.2))
        
        # -------- LEVENSHTEIN DISTANCE (Score: 70-85) --------
        lev_ratio = self.levenshtein_ratio(query_clean, main_clean)
        if lev_ratio >= 75:  # Only count if reasonably similar
            scores.append(lev_ratio)
        
        # Check aliases
        for alias in aliases:
            lev_ratio = self.levenshtein_ratio(query_clean, alias)
            if lev_ratio >= 75:
                scores.append(lev_ratio * 0.95)  # Slightly lower for aliases
        
        # -------- PHONETIC MATCHING (Score: 65-80) --------
        if use_phonetic:
            soundex_query = self.soundex(query_clean)
            soundex_main = self.soundex(main_clean)
            
            if soundex_query and soundex_main and soundex_query == soundex_main:
                scores.append(75.0)
            
            # Also check Metaphone
            metaphone_query = self.metaphone(query_clean)
            metaphone_main = self.metaphone(main_clean)
            
            if metaphone_query and metaphone_main and metaphone_query == metaphone_main:
                scores.append(72.0)
        
        # -------- TOKEN-BASED MATCHING (Score: 50-75) --------
        token_score = self.token_overlap(query_clean, main_clean)
        if token_score > 0:
            # Boost if tokens are meaningful
            query_tokens = set(query_clean.split())
            main_tokens = set(main_clean.split())
            common = len(query_tokens & main_tokens)
            
            # Weight by number of common tokens
            adjusted_token_score = token_score * (0.5 + common * 0.1)
            if adjusted_token_score > 0:
                scores.append(min(75.0, adjusted_token_score))
        
        # -------- RETURN BEST SCORE --------
        if scores:
            final_score = max(scores)
            return round(final_score, 2)
        
        return 0.0


# Singleton instance
_matcher = None

def get_matcher() -> NameMatcher:
    """Get or create singleton NameMatcher instance"""
    global _matcher
    if _matcher is None:
        _matcher = NameMatcher()
    return _matcher


def match_name(query_name: str, record: Dict, entity_type: str = 'company', 
              use_phonetic: bool = True) -> float:
    """
    Convenience function to calculate match score.
    
    Usage:
        score = match_name("Putin", {"main_name": "Vladimir Putin", "aliases": []})
    """
    matcher = get_matcher()
    return matcher.calculate_match_score(query_name, record, entity_type, use_phonetic)
