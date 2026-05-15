import csv
import sqlite3
import pandas as pd
from pathlib import Path

class LoanDatabase:
    def __init__(self, db_path='loan_database.db'):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        """Connect to the SQLite database"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        """Create all necessary tables in the database"""
        # Person table (1NF -> 2NF -> 3NF)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS person (
            person_id INTEGER PRIMARY KEY AUTOINCREMENT,
            age INTEGER,
            gender TEXT,
            education_level_id INTEGER,
            income FLOAT,
            employment_experience INTEGER,
            home_ownership_id INTEGER,
            credit_history_length INTEGER,
            credit_score INTEGER,
            has_previous_defaults BOOLEAN,
            FOREIGN KEY (education_level_id) REFERENCES education_level(education_id),
            FOREIGN KEY (home_ownership_id) REFERENCES home_ownership(ownership_id)
        )''')

        # Education Level table (lookup table)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS education_level (
            education_id INTEGER PRIMARY KEY,
            education_name TEXT UNIQUE
        )''')

        # Home Ownership table (lookup table)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS home_ownership (
            ownership_id INTEGER PRIMARY KEY,
            ownership_type TEXT UNIQUE
        )''')

        # Loan Intent table (lookup table)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS loan_intent (
            intent_id INTEGER PRIMARY KEY,
            intent_name TEXT UNIQUE
        )''')

        # Loan table (1NF -> 2NF -> 3NF)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS loan (
            loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER,
            loan_amount FLOAT,
            intent_id INTEGER,
            interest_rate FLOAT,
            percent_income FLOAT,
            loan_status BOOLEAN,
            FOREIGN KEY (person_id) REFERENCES person(person_id),
            FOREIGN KEY (intent_id) REFERENCES loan_intent(intent_id)
        )''')

        self.conn.commit()

    def load_lookup_data(self, table_name, values):
        """Load data into lookup tables"""
        column_mappings = {
            'education_level': 'education_name',
            'home_ownership': 'ownership_type',
            'loan_intent': 'intent_name'
        }
        for value in values:
            self.cursor.execute(f'''
            INSERT OR IGNORE INTO {table_name} ({column_mappings[table_name]})
            VALUES (?)
            ''', (value,))
        self.conn.commit()

    def get_id_from_lookup(self, table_name, value):
        """Get ID from lookup tables"""
        id_mappings = {
            'education_level': 'education_id',
            'home_ownership': 'ownership_id',
            'loan_intent': 'intent_id'
        }
        column_mappings = {
            'education_level': 'education_name',
            'home_ownership': 'ownership_type',
            'loan_intent': 'intent_name'
        }
        self.cursor.execute(f'''
        SELECT {id_mappings[table_name]} 
        FROM {table_name} 
        WHERE {column_mappings[table_name]} = ?
        ''', (value,))
        return self.cursor.fetchone()[0]

    def load_data_from_csv(self, csv_path):
        """Load data from CSV file into the database"""
        # Read CSV file
        with open(csv_path, 'r') as file:
            csv_reader = csv.DictReader(file)
            
            # Extract unique values for lookup tables
            education_levels = set()
            home_ownership_types = set()
            loan_intents = set()
            
            data = []
            for row in csv_reader:
                education_levels.add(row['person_education'])
                home_ownership_types.add(row['person_home_ownership'])
                loan_intents.add(row['loan_intent'])
                data.append(row)

            # Populate lookup tables
            self.load_lookup_data('education_level', education_levels)
            self.load_lookup_data('home_ownership', home_ownership_types)
            self.load_lookup_data('loan_intent', loan_intents)
            
            # Insert data into main tables
            for row in data:
                # Insert person data
                self.cursor.execute('''
                INSERT INTO person (
                    age, gender, education_level_id, income, 
                    employment_experience, home_ownership_id,
                    credit_history_length, credit_score, has_previous_defaults
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    int(float(row['person_age'])),
                    row['person_gender'],
                    self.get_id_from_lookup('education_level', row['person_education']),
                    float(row['person_income']),
                    int(float(row['person_emp_exp'])),
                    self.get_id_from_lookup('home_ownership', row['person_home_ownership']),
                    int(float(row['cb_person_cred_hist_length'])),
                    int(float(row['credit_score'])),
                    row['previous_loan_defaults_on_file'] == 'Yes'
                ))
                
                person_id = self.cursor.lastrowid
                
                # Insert loan data
                self.cursor.execute('''
                INSERT INTO loan (
                    person_id, loan_amount, intent_id,
                    interest_rate, percent_income, loan_status
                ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    person_id,
                    float(row['loan_amnt']),
                    self.get_id_from_lookup('loan_intent', row['loan_intent']),
                    float(row['loan_int_rate']),
                    float(row['loan_percent_income']),
                    int(row['loan_status'])
                ))
            
            self.conn.commit()

    def fetch_complete_loan_data(self):
        """Fetch complete loan data as a pandas DataFrame"""
        query = '''
        SELECT 
            p.person_id,
            p.age,
            p.gender,
            el.education_name as education,
            p.income,
            p.employment_experience,
            ho.ownership_type as home_ownership,
            p.credit_history_length,
            p.credit_score,
            p.has_previous_defaults,
            l.loan_amount,
            li.intent_name as loan_intent,
            l.interest_rate,
            l.percent_income,
            l.loan_status
        FROM person p
        JOIN loan l ON p.person_id = l.person_id
        JOIN education_level el ON p.education_level_id = el.education_id
        JOIN home_ownership ho ON p.home_ownership_id = ho.ownership_id
        JOIN loan_intent li ON l.intent_id = li.intent_id
        '''
        return pd.read_sql_query(query, self.conn)

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
