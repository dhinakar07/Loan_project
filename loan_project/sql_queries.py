import pandas as pd
import sqlite3

def fetch_complete_loan_data():
    """
    Fetch complete loan data using SQL joins and load into a pandas DataFrame
    """
    # Connect to the database
    conn = sqlite3.connect('loan_database.db')
    
    # SQL query with all necessary joins
    query = '''
    SELECT 
        -- Person Information
        p.person_id,
        p.age,
        p.gender,
        el.education_name as education_level,
        p.income,
        p.employment_experience,
        ho.ownership_type as home_ownership,
        p.credit_history_length,
        p.credit_score,
        p.has_previous_defaults,
        
        -- Loan Information
        l.loan_id,
        l.loan_amount,
        li.intent_name as loan_purpose,
        l.interest_rate,
        l.percent_income,
        l.loan_status,
        
        -- Additional Calculated Fields
        CASE 
            WHEN p.credit_score >= 700 THEN 'Excellent'
            WHEN p.credit_score >= 650 THEN 'Good'
            WHEN p.credit_score >= 600 THEN 'Fair'
            ELSE 'Poor'
        END as credit_category,
        
        CASE 
            WHEN l.loan_status = 1 THEN 'Approved'
            ELSE 'Denied'
        END as loan_status_desc
        
    FROM person p
    -- Join with loan table
    JOIN loan l 
        ON p.person_id = l.person_id
    
    -- Join with education_level lookup table
    JOIN education_level el 
        ON p.education_level_id = el.education_id
    
    -- Join with home_ownership lookup table
    JOIN home_ownership ho 
        ON p.home_ownership_id = ho.ownership_id
    
    -- Join with loan_intent lookup table
    JOIN loan_intent li 
        ON l.intent_id = li.intent_id
    
    -- Optional: Add WHERE clause for filtering
    -- WHERE p.credit_score >= 600
    
    -- Optional: Add ORDER BY clause
    ORDER BY p.person_id
    '''
    
    # Execute query and load into DataFrame
    df = pd.read_sql_query(query, conn)
    
    # Close the connection
    conn.close()
    
    return df

def get_loan_statistics():
    """
    Get detailed loan statistics using SQL
    """
    conn = sqlite3.connect('loan_database.db')
    
    statistics_query = '''
    SELECT 
        -- Loan Amount Statistics
        COUNT(*) as total_loans,
        AVG(l.loan_amount) as avg_loan_amount,
        MIN(l.loan_amount) as min_loan_amount,
        MAX(l.loan_amount) as max_loan_amount,
        
        -- Interest Rate Statistics
        AVG(l.interest_rate) as avg_interest_rate,
        
        -- Approval Statistics
        SUM(CASE WHEN l.loan_status = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as approval_rate,
        
        -- Credit Score Statistics
        AVG(p.credit_score) as avg_credit_score
        
    FROM loan l
    JOIN person p ON l.person_id = p.person_id
    '''
    
    stats_df = pd.read_sql_query(statistics_query, conn)
    conn.close()
    
    return stats_df

def get_loan_purpose_distribution():
    """
    Get distribution of loans by purpose
    """
    conn = sqlite3.connect('loan_database.db')
    
    purpose_query = '''
    SELECT 
        li.intent_name as loan_purpose,
        COUNT(*) as loan_count,
        AVG(l.loan_amount) as avg_amount,
        AVG(l.interest_rate) as avg_interest_rate,
        SUM(CASE WHEN l.loan_status = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as approval_rate
    FROM loan l
    JOIN loan_intent li ON l.intent_id = li.intent_id
    GROUP BY li.intent_name
    ORDER BY loan_count DESC
    '''
    
    purpose_df = pd.read_sql_query(purpose_query, conn)
    conn.close()
    
    return purpose_df

def get_education_loan_analysis():
    """
    Analyze loan patterns by education level
    """
    conn = sqlite3.connect('loan_database.db')
    
    education_query = '''
    SELECT 
        el.education_name,
        COUNT(*) as total_applications,
        AVG(l.loan_amount) as avg_loan_amount,
        AVG(l.interest_rate) as avg_interest_rate,
        AVG(p.credit_score) as avg_credit_score,
        SUM(CASE WHEN l.loan_status = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as approval_rate
    FROM person p
    JOIN loan l ON p.person_id = l.person_id
    JOIN education_level el ON p.education_level_id = el.education_id
    GROUP BY el.education_name
    ORDER BY avg_loan_amount DESC
    '''
    
    education_df = pd.read_sql_query(education_query, conn)
    conn.close()
    
    return education_df

# Example usage:
if __name__ == "__main__":
    # Fetch complete loan data
    loan_df = fetch_complete_loan_data()
    print("\nComplete Loan Data Sample:")
    print(loan_df.head())
    
    # Get loan statistics
    stats_df = get_loan_statistics()
    print("\nLoan Statistics:")
    print(stats_df)
    
    # Get loan purpose distribution
    purpose_df = get_loan_purpose_distribution()
    print("\nLoan Purpose Distribution:")
    print(purpose_df)
    
    # Get education level analysis
    education_df = get_education_loan_analysis()
    print("\nEducation Level Analysis:")
    print(education_df)
