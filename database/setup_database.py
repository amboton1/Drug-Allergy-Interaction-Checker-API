#!/usr/bin/env python3

import sqlite3
import os
import sys

# Create database directory if it doesn't exist
os.makedirs(os.path.dirname('database/allergy_api.db'), exist_ok=True)

# Connect to SQLite database (will create it if it doesn't exist)
conn = sqlite3.connect('database/allergy_api.db')
cursor = conn.cursor()

print("Creating database schema...")

# Read schema SQL file
with open('database/schema.sql', 'r') as schema_file:
    schema_sql = schema_file.read()
    
    # SQLite doesn't support some PostgreSQL features, so we need to modify the schema
    # Replace SERIAL with INTEGER PRIMARY KEY
    schema_sql = schema_sql.replace('SERIAL PRIMARY KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT')
    
    # Remove TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    schema_sql = schema_sql.replace('TIMESTAMP DEFAULT CURRENT_TIMESTAMP', 'TIMESTAMP DEFAULT (datetime(\'now\',\'localtime\'))')
    
    # Execute schema creation
    cursor.executescript(schema_sql)
    
print("Schema created successfully.")

print("Populating database with initial data...")

# Read initial data SQL file
with open('database/initial_data.sql', 'r') as data_file:
    data_sql = data_file.read()
    
    # Execute data insertion
    try:
        cursor.executescript(data_sql)
        print("Initial data loaded successfully.")
    except sqlite3.Error as e:
        print(f"Error loading initial data: {e}")
        conn.rollback()
        sys.exit(1)

# Commit changes and close connection
conn.commit()
conn.close()

print("Database setup complete.")
