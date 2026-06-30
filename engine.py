import sqlite3
import pandas as pd
from database import DATABASE_NAME

def post_journal_transaction(profile_id, date_str, description, ledger_payload):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO journal_entries (profile_id, date, description)
            VALUES (?, ?, ?)
        """, (profile_id, date_str, description))
        
        journal_id = cursor.lastrowid
        
        for line in ledger_payload:
            cursor.execute("""
                INSERT INTO ledger_entries (journal_id, account_id, amount)
                VALUES (?, ?, ?)
            """, (journal_id, line["account_id"], line["amount"]))
            
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def generate_report_string(profile_id, profile_name):
    conn = sqlite3.connect(DATABASE_NAME)
    
    query = """
        SELECT accounts.type, accounts.name, COALESCE(SUM(ledger_entries.amount), 0) as balance
        FROM accounts
        LEFT JOIN ledger_entries ON accounts.account_id = ledger_entries.account_id
        WHERE accounts.profile_id = ?
        GROUP BY accounts.type, accounts.name
    """
    
    try:
        df = pd.read_sql_query(query, conn, params=(profile_id,))
        
        output = f"Financial Health: {profile_name}\n\n"
        for _, row in df.iterrows():
            output += f"[{row['type']}] {row['name']}: ${row['balance']:,.2f}\n"
            
        conn.close()
        return output
    except Exception as e:
        conn.close()
        return f"Report generation failed: {e}"
