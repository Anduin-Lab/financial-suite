import sqlite3
import pandas as pd
from database import DATABASE_NAME

def post_journal_transaction(profile_id, date_str, description, ledger_payload):
    import sqlite3
    from database import DATABASE_NAME
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    try:
        # 1. Insert the parent Journal Header record
        cursor.execute("""
            INSERT INTO journal_entries (profile_id, date, description)
            VALUES (?, ?, ?)
        """, (profile_id, date_str, description))
        
        # Get the unique ID assigned to this specific transaction header
        journal_id = cursor.lastrowid
        
        # 2. Insert the balanced Double-Entry Ledger split rows
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
    import sqlite3
    import pandas as pd
    from database import DATABASE_NAME
    
    conn = sqlite3.connect(DATABASE_NAME)
    
    # FIXED QUERY: Connects accounts to ledger entries to calculate balances accurately
    query = """
        SELECT accounts.type, accounts.name, COALESCE(SUM(ledger_entries.amount), 0) as balance
        FROM accounts
        LEFT JOIN ledger_entries ON accounts.account_id = ledger_entries.account_id
        WHERE accounts.profile_id = ?
        GROUP BY accounts.type, accounts.name
    """
    
    try:
        df = pd.read_sql_query(query, conn, params=(profile_id,))
        
        # --- (Keep the rest of your formatting code underneath this the same) ---
        # (The logic where it loops through the dataframe and builds the text report string)
        
        # Simple placeholder assembly example if you want to overwrite cleanly:
        output = f"=== Financial Health: {profile_name} ===\n\n"
        for _, row in df.iterrows():
            output += f"[{row['type']}] {row['name']}: ${row['balance']:,.2f}\n"
            
        conn.close()
        return output
    except Exception as e:
        conn.close()
        return f"Report generation engine failure: {e}"