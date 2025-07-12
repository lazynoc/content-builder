#!/usr/bin/env python3
"""
Script to check the current database schema
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from parent directory
load_dotenv('../.env')

# Database configuration
DB_URL = os.getenv('SUPABASE_DB_URL')

def check_schema():
    """Check the current database schema"""
    
    # Connect to database
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    
    # Get table schema
    cursor.execute("""
        SELECT column_name, data_type, character_maximum_length, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'questions'
        ORDER BY ordinal_position;
    """)
    
    columns = cursor.fetchall()
    
    print("📋 CURRENT DATABASE SCHEMA:")
    print("=" * 80)
    print(f"{'Column Name':<30} {'Data Type':<20} {'Max Length':<12} {'Nullable':<10}")
    print("-" * 80)
    
    for column in columns:
        col_name, data_type, max_length, nullable = column
        max_len = str(max_length) if max_length else 'N/A'
        print(f"{col_name:<30} {data_type:<20} {max_len:<12} {nullable:<10}")
    
    # Close connection
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_schema() 