# Loan Data Analysis Project

This project implements a normalized database for loan data analysis. The database follows the Third Normal Form (3NF) to ensure data integrity and minimize redundancy.

## Project Structure

```
loan_project/
├── README.md
├── requirements.txt
├── src/
│   ├── database.py
│   └── main.py
├── data/
└── loan_database.db
```

## Database Schema

The database is structured in Third Normal Form (3NF) with the following tables:

1. `person`
   - Primary information about loan applicants
   - Includes demographics and credit information

2. `education_level` (lookup table)
   - Education levels of applicants

3. `home_ownership` (lookup table)
   - Types of home ownership

4. `loan_intent` (lookup table)
   - Purpose of the loan

5. `loan`
   - Loan-specific information
   - Connected to person and lookup tables

## Setup and Usage

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the main script:
   ```bash
   python src/main.py
   ```

## Features

- Normalized database structure (3NF)
- CSV data import
- Lookup tables for categorical data
- Easy data retrieval with SQL joins
- Pandas DataFrame integration

## Data Analysis

The database can be used for various analyses:
- Loan approval patterns
- Credit score analysis
- Demographics study
- Risk assessment
- Interest rate analysis
