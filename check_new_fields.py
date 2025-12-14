from src.db.session import SessionLocal
from src.db.models import SanctionRecord

def check_data():
    db = SessionLocal()
    try:
        # Check for records with entity_type populated
        count_type = db.query(SanctionRecord).filter(SanctionRecord.entity_type != None).count()
        count_gender = db.query(SanctionRecord).filter(SanctionRecord.gender != None).count()
        count_url = db.query(SanctionRecord).filter(SanctionRecord.url != None).count()
        
        print(f"Records with entity_type: {count_type}")
        print(f"Records with gender: {count_gender}")
        print(f"Records with url: {count_url}")
        
        # Check EU for URL
        eu_url = db.query(SanctionRecord).filter(SanctionRecord.list_type == 'EU', SanctionRecord.url != None).count()
        print(f"EU Records with URL: {eu_url}")
        
        # Check US for Gender
        us_gender = db.query(SanctionRecord).filter(SanctionRecord.list_type == 'US', SanctionRecord.gender != None).count()
        print(f"US Records with Gender: {us_gender}")

        # Check new fields
        count_un = db.query(SanctionRecord).filter(SanctionRecord.un_id != None).count()
        count_remark = db.query(SanctionRecord).filter(SanctionRecord.remark != None).count()
        count_function = db.query(SanctionRecord).filter(SanctionRecord.function != None).count()
        
        print(f"Records with UN ID: {count_un}")
        print(f"Records with Remark: {count_remark}")
        print(f"Records with Function: {count_function}")

        # Sample UK
        sample_uk = db.query(SanctionRecord).filter(SanctionRecord.list_type == 'UK', SanctionRecord.function != None).first()
        if sample_uk:
            print("\nSample UK:")
            print(f"ID: {sample_uk.id}")
            print(f"Function: {sample_uk.function}")
            print(f"Remark: {sample_uk.remark}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_data()
