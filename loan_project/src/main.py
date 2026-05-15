from pathlib import Path
from database import LoanDatabase

def main():
    # Setup paths
    project_root = Path(__file__).parent.parent
    data_dir = project_root / 'data'
    data_dir.mkdir(exist_ok=True)
    
    # Initialize database
    db = LoanDatabase(str(project_root / 'loan_database.db'))
    db.connect()
    db.create_tables()
    
    # Load data
    csv_path = '/Users/dhinakaryalla/Downloads/loan_data.csv'
    db.load_data_from_csv(csv_path)
    
    # Fetch and display sample data
    df = db.fetch_complete_loan_data()
    print("Database created and data loaded successfully!")
    print("\nSample of the normalized data:")
    print(df.head())
    
    # Close database connection
    db.close()

if __name__ == "__main__":
    main()
