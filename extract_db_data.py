#!/usr/bin/env python3
"""Extract current DB data for migration"""
import psycopg2
import json
from datetime import datetime

def serialize_value(val):
    """Serialize values for SQL INSERT"""
    if val is None:
        return 'NULL'
    elif isinstance(val, bool):
        return 'TRUE' if val else 'FALSE'
    elif isinstance(val, (int, float)):
        return str(val)
    elif isinstance(val, datetime):
        return f"'{val.isoformat()}'"
    elif isinstance(val, str):
        # Escape single quotes
        escaped = val.replace("'", "''")
        return f"'{escaped}'"
    else:
        return f"'{str(val)}'"

def extract_data():
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='matchit_db',
            user='postgres',
            password='password'
        )
        cur = conn.cursor()
        
        output = []
        output.append("-- Extracted data from Docker DB")
        output.append(f"-- Generated: {datetime.now().isoformat()}\n")
        
        # Extract each table
        tables_to_export = [
            'careerlevels',
            'experienceranges',
            'platforms',
            'jobcategories',
            'skills',
            'desiredjobs',
            'users',
            'sociallogins',
            'jobposts',
            'jobpostskills',
            'bootcampposts',
            'userskills',
            'userdesiredjobs',
            'userscraps',
            'usernotificationsettings',
        ]
        
        for table in tables_to_export:
            try:
                cur.execute(f"SELECT * FROM {table};")
                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                
                if rows:
                    col_str = ', '.join(columns)
                    output.append(f"\n-- {table.upper()} ({len(rows)} rows)")
                    output.append(f"INSERT INTO {table} ({col_str}) VALUES")
                    
                    values_list = []
                    for row in rows:
                        values = [serialize_value(v) for v in row]
                        values_list.append(f"({', '.join(values)})")
                    
                    output.append(',\n'.join(values_list) + ";")
                else:
                    output.append(f"\n-- {table} is empty")
            except Exception as e:
                output.append(f"\n-- Error extracting {table}: {e}")
        
        conn.close()
        
        result = '\n'.join(output)
        print(result)
        
        # Also save to file
        with open('extracted_db_data.sql', 'w', encoding='utf-8') as f:
            f.write(result)
        
        print("\n✓ Data extraction successful. Saved to extracted_db_data.sql")
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == '__main__':
    extract_data()
