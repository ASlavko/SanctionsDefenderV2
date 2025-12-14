from src.etl.parsers import EUParser, UKParser, USParser
import os

def test_parsers():
    base_path = os.path.join(os.getcwd(), "data", "sanctions")
    
    # Test EU
    print("--- Testing EU Parser ---")
    eu_path = os.path.join(base_path, "EU.xml")
    if os.path.exists(eu_path):
        parser = EUParser()
        count = 0
        for rec in parser.parse(eu_path):
            print(f"Parsed EU: {rec['id']} - {rec['original_name']}")
            count += 1
            if count >= 3: break
    else:
        print("EU.xml not found")

    # Test UK
    print("\n--- Testing UK Parser ---")
    uk_path = os.path.join(base_path, "UK.xml")
    if os.path.exists(uk_path):
        parser = UKParser()
        count = 0
        for rec in parser.parse(uk_path):
            print(f"Parsed UK: {rec['id']} - {rec['original_name']}")
            count += 1
            if count >= 3: break
    else:
        print("UK.xml not found")

    # Test US
    print("\n--- Testing US Parser ---")
    us_path = os.path.join(base_path, "US_SDN_SIMPLE.xml")
    if os.path.exists(us_path):
        parser = USParser()
        count = 0
        for rec in parser.parse(us_path):
            print(f"Parsed US: {rec['id']} - {rec['original_name']}")
            count += 1
            if count >= 3: break
    else:
        print("US_SDN_SIMPLE.xml not found")

if __name__ == "__main__":
    test_parsers()
