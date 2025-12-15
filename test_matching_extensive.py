import unittest
import sys
import os
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.api.services.engine import SearchEngine
from src.db.models import SanctionRecord, MatchDecision, MatchStatus
from src.core.matching import NameMatcher

class TestMatchingEngineExtensive(unittest.TestCase):
    def setUp(self):
        # Reset Singleton state or just clear data manually for the test
        self.engine = SearchEngine()
        self.engine.names = []
        self.engine.ids = []
        self.engine.records = {}
        self.engine.decisions = {}
        
        # --- POPULATE TEST DATA ---
        # 1. Standard Latin Name
        self.add_record("1", "Vladimir Putin", ["Vladimir Vladimirovich Putin"], list_type="EU")
        
        # 2. Latin Name with different casing/spacing in DB
        self.add_record("2", "Bashar Al-Assad", ["Bashar Hafez al-Assad"], list_type="US")
        
        # 3. Arabic Name with Latin Alias (The fix verification)
        self.add_record("3", "بشارالاسد", ["Bashar AL-ASSAD"], list_type="EU") 
        
        # 4. Standard Name for Logic Tests
        self.add_record("4", "Osama Bin Laden", [], list_type="UN")
        
        # 5. Corporate Entity
        self.add_record("5", "Gazprom Neft", ["Gazprom Neft PJSC", "Open Joint Stock Company Gazprom Neft"], list_type="UK")
        
        # 6. Greek Name with Latin Alias
        self.add_record("6", "Χαμάς", ["Hamas", "Harakat al-Muqawama al-Islamiya"], list_type="EU")
        
        # 7. Cyrillic Name
        self.add_record("7", "Сбербанк", ["Sberbank"], list_type="EU")

    def add_record(self, id, name, aliases, list_type="EU"):
        # Create record object
        rec = SanctionRecord(
            id=id, 
            original_name=name, 
            normalized_name=NameMatcher.normalize_name(name),
            alias_names=aliases, # In real DB this might be JSON string, but engine handles list too if mocked
            list_type=list_type
        )
        self.engine.records[id] = rec
        
        # Index primary name
        if rec.normalized_name:
            self.engine.names.append(rec.normalized_name)
            self.engine.ids.append(id)
            
        # Index aliases (Simulating the logic in engine.load_data)
        for alias in aliases:
            norm = NameMatcher.normalize_name(alias)
            if norm and norm != rec.normalized_name:
                self.engine.names.append(norm)
                self.engine.ids.append(id)

    # --- BASIC MATCHING TESTS ---

    def test_exact_match(self):
        """Test exact string match."""
        results = self.engine.search("Vladimir Putin")
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]['record'].id, "1")
        self.assertEqual(results[0]['score'], 100)

    def test_case_insensitivity(self):
        """Test mixed case input."""
        results = self.engine.search("vLaDiMiR pUtIn")
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]['score'], 100)

    def test_punctuation_noise(self):
        """Test input with extra punctuation."""
        results = self.engine.search("Vladimir-Putin!")
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]['score'], 100)

    def test_word_reordering(self):
        """Test 'Last, First' format."""
        results = self.engine.search("Putin, Vladimir")
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]['score'], 100)

    def test_typo_tolerance(self):
        """Test small typos."""
        # "Vladimyr" instead of "Vladimir"
        results = self.engine.search("Vladimyr Putin")
        self.assertTrue(len(results) > 0)
        self.assertTrue(results[0]['score'] > 85)

    # --- ALIAS & NON-LATIN TESTS ---

    def test_alias_search(self):
        """Test searching by a known alias."""
        results = self.engine.search("Vladimir Vladimirovich Putin")
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]['record'].id, "1")

    def test_non_latin_direct_search(self):
        """Test searching using the original Arabic script."""
        results = self.engine.search("بشارالاسد")
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]['record'].id, "3")

    def test_non_latin_via_latin_alias(self):
        """Test finding an Arabic record by searching its Latin alias."""
        results = self.engine.search("Bashar AL-ASSAD")
        # Should match record 3 (Arabic) because we indexed the alias
        matches = [r['record'].id for r in results]
        self.assertIn("3", matches)

    def test_greek_search(self):
        """Test searching using Greek script."""
        results = self.engine.search("Χαμάς")
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]['record'].id, "6")

    def test_greek_via_alias(self):
        """Test finding Greek record via Latin alias."""
        results = self.engine.search("Hamas")
        matches = [r['record'].id for r in results]
        self.assertIn("6", matches)

    def test_cyrillic_search(self):
        """Test searching using Cyrillic script."""
        results = self.engine.search("Сбербанк")
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]['record'].id, "7")

    # --- LOGIC & DECISION TESTS ---

    def test_false_positive_logic(self):
        """Test that FALSE_POSITIVE decision blocks a match."""
        # 1. Verify match exists initially
        results = self.engine.search("Osama Bin Laden")
        self.assertTrue(len(results) > 0)
        
        # 2. Add False Positive decision
        norm_query = NameMatcher.normalize_name("Osama Bin Laden")
        decision = MatchDecision(
            search_term_normalized=norm_query,
            decision=MatchStatus.FALSE_POSITIVE
        )
        self.engine.decisions[norm_query] = decision
        
        # 3. Verify match is now blocked
        results = self.engine.search("Osama Bin Laden")
        self.assertEqual(len(results), 0)

    def test_true_match_logic(self):
        """Test that TRUE_MATCH decision forces 100% score."""
        # 1. Add True Match decision for a partial match query
        query = "Osama B. Laden" # Partial
        norm_query = NameMatcher.normalize_name(query)
        
        decision = MatchDecision(
            search_term_normalized=norm_query,
            decision=MatchStatus.TRUE_MATCH,
            sanction_id="4"
        )
        self.engine.decisions[norm_query] = decision
        
        # 2. Verify it returns 100% score
        results = self.engine.search(query)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]['record'].id, "4")
        self.assertEqual(results[0]['score'], 100.0)
        self.assertEqual(results[0]['status'], MatchStatus.TRUE_MATCH)

    # --- EDGE CASES ---

    def test_corporate_suffix_handling(self):
        """Test corporate suffix handling."""
        # "Gazprom Neft PJSC" is an alias. 
        # Searching "Gazprom Neft" should match it.
        results = self.engine.search("Gazprom Neft")
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]['record'].id, "5")

    def test_empty_query(self):
        """Test empty string search."""
        results = self.engine.search("")
        self.assertEqual(len(results), 0)

    def test_special_chars_only(self):
        """Test search with only special characters."""
        results = self.engine.search("!!!")
        self.assertEqual(len(results), 0)

    def test_threshold_filtering(self):
        """Test that low scores are filtered out."""
        # "Vladimir Putin" vs "John Doe" -> Should be low score
        results = self.engine.search("John Doe")
        self.assertEqual(len(results), 0)

    def test_very_long_string(self):
        """Test extremely long input string."""
        long_str = "A" * 1000
        results = self.engine.search(long_str)
        self.assertEqual(len(results), 0)

if __name__ == "__main__":
    unittest.main()
