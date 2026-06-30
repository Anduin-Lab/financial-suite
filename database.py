import sqlite3

DATABASE_NAME = "accounting.db"

def initialize_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Enable foreign keys for cascading deletes
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 1. Profiles Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS business_profiles (
            profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)
    
    # 2. Accounts Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            account_id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER,
            account_number TEXT NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            FOREIGN KEY(profile_id) REFERENCES business_profiles(profile_id) ON DELETE CASCADE
        )
    """)
    
    # 3. Spreadsheet Grid Storage Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grid_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER,
            row_index INTEGER NOT NULL,
            description TEXT,
            quantity REAL DEFAULT 0.0,
            rate REAL DEFAULT 0.0,
            FOREIGN KEY(profile_id) REFERENCES business_profiles(profile_id) ON DELETE CASCADE
        )
    """)

    # 4. Journal Headers Table (Tracks the date and description of transactions)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS journal_entries (
            journal_id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER,
            date TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY(profile_id) REFERENCES business_profiles(profile_id) ON DELETE CASCADE
        )
    """)

    # 5. Ledger Lines Table (Tracks individual debits and credits for each account)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ledger_entries (
            entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
            journal_id INTEGER,
            account_id INTEGER,
            amount REAL NOT NULL,
            FOREIGN KEY(journal_id) REFERENCES journal_entries(journal_id) ON DELETE CASCADE,
            FOREIGN KEY(account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
        )
    """)

    # 6. Accounts Receivable / Invoice Tracking Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER,
            customer_name TEXT NOT NULL,
            amount REAL NOT NULL,
            due_date TEXT NOT NULL,
            status TEXT DEFAULT 'Unpaid',
            FOREIGN KEY(profile_id) REFERENCES business_profiles(profile_id) ON DELETE CASCADE
        )
    """)
    
    # Seed default profile if empty
    cursor.execute("SELECT COUNT(*) FROM business_profiles")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO business_profiles (name) VALUES ('Default Corporation')")
        pid = cursor.lastrowid
        accounts = [
            (pid, '1000', 'Cash / Bank', 'Asset'),
            (pid, '1200', 'Accounts Receivable', 'Asset'),
            (pid, '2000', 'Payables', 'Liability'),
            (pid, '3000', 'Owner Equity', 'Equity'),
            (pid, '4000', 'Revenue', 'Revenue'),
            (pid, '5000', 'Software Expenses', 'Expense'),
            (pid, '5100', 'Rent Expense', 'Expense')
        ]
        cursor.executemany("INSERT INTO accounts (profile_id, account_number, name, type) VALUES (?,?,?,?)", accounts)
        
    conn.commit()
    conn.close()

def reset_and_reinitialize_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Disable foreign keys temporarily so we can drop tables cleanly without blockages
    cursor.execute("PRAGMA foreign_keys = OFF;")
    
    # Fetch all custom table names inside the engine database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]
    
    # Nuke every table
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table};")
        
    conn.commit()
    conn.close()
    
    # Reinitialize empty production-ready structures instantly
    initialize_database()