import customtkinter as ctk
import sqlite3
import pandas as pd
from database import DATABASE_NAME, initialize_database
import engine

# Import our modular custom UI panels
from tab_entry import LogTransactionTab
from tab_sheet import InteractiveSheetTab
from tab_reports import ReportsDashboardTab
from tab_settings import SystemSettingsTab
from tab_ledger import GeneralLedgerTab
from tab_invoices import InvoiceTrackerTab

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ModernAccountingApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        initialize_database()
        
        self.title("B.O.Y.O.U.N.G. Financial Suite")
        self.geometry("950x700")
        self.current_profile_id = 1
        
        # --- PATH 3: CENTRAL HIGH-SPEED MEMORY CACHE STORE ---
        self._cache = {
            "ledger": None,
            "invoices": None
        }
        
        # --- TOP HEADER BAR ---
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.top_bar.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(self.top_bar, text="Portfolio Context:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        self.profile_menu = ctk.CTkOptionMenu(self.top_bar, values=self.get_profile_names(), command=self.switch_profile, width=200)
        self.profile_menu.pack(side="left", padx=10)
        
        # Sync configuration state rules
        self.sync_accounts()
        
        # Prime the cache memory structures for the initial profile context
        self.invalidate_and_prime_cache()
        
        # --- TAB CONTAINER HUB ---
        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Mount the specialized external tabs directly onto container frame elements
        self.tab1 = LogTransactionTab(self.tabs.add("📝 Log Transaction"), self)
        self.tab1.pack(fill="both", expand=True)
        
        self.tab2 = InteractiveSheetTab(self.tabs.add("📊 Interactive Sheet"), self)
        self.tab2.pack(fill="both", expand=True)
        
        self.tab3 = ReportsDashboardTab(self.tabs.add("📈 View Dashboard"), self)
        self.tab3.pack(fill="both", expand=True)
        
        self.tab4 = SystemSettingsTab(self.tabs.add("⚙️ Manage System"), self)
        self.tab4.pack(fill="both", expand=True)

        self.tab5 = GeneralLedgerTab(self.tabs.add("📜 View Ledger"), self)
        self.tab5.pack(fill="both", expand=True)

        self.tab6 = InvoiceTrackerTab(self.tabs.add("🧾 Track Invoices"), self)
        self.tab6.pack(fill="both", expand=True)

        # --- MOUNT THE B.O.Y.O.U.N.G. RESET ENGINE PANEL ---
        self.mount_nuke_control()

        self.refresh_reports()

    # --- PATH 3: INTELLIGENT CACHE MANAGEMENT ENGINE ---
    def invalidate_and_prime_cache(self):
        """Pre-fetches data tables completely into fast system memory structures"""
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        try:
            # 1. Cache the Ledger Query
            cursor.execute("PRAGMA table_info(journal_entries);")
            columns = [col[1] for col in cursor.fetchall()]
            date_col = "date" if "date" in columns else ("transaction_date" if "transaction_date" in columns else columns[2])
            
            ledger_query = f"""
                SELECT j.{date_col} as record_date, j.description, a.name as account_name, le.amount
                FROM journal_entries j
                JOIN ledger_entries le ON j.journal_id = le.journal_id
                JOIN accounts a ON le.account_id = a.account_id
                WHERE j.profile_id = ?
                ORDER BY j.journal_id DESC, le.amount DESC
            """
            self._cache["ledger"] = pd.read_sql_query(ledger_query, conn, params=(self.current_profile_id,))
            
            # 2. Cache the Invoice Pipeline Query
            invoice_query = "SELECT invoice_id, customer_name, amount, due_date, status FROM invoices WHERE profile_id = ?"
            self._cache["invoices"] = pd.read_sql_query(invoice_query, conn, params=(self.current_profile_id,))
            
        except Exception as e:
            print(f"🎯 Cache Pre-fetch Failure: {e}")
        finally:
            conn.close()

    def get_cached_data(self, key):
        """Returns hot memory data instantly; if cache dropped, re-fetches gracefully"""
        if self._cache.get(key) is None:
            self.invalidate_and_prime_cache()
        return self._cache[key]

    # --- PRESERVED: SYSTEM RESET CONTROL ENGINE FUNCTIONS ---
    def mount_nuke_control(self):
        nuke_frame = ctk.CTkFrame(self.tab4, fg_color="#2b2b2b", border_color="#8B0000", border_width=1)
        nuke_frame.pack(fill="x", padx=20, pady=20, side="bottom")
        
        ctk.CTkLabel(
            nuke_frame, 
            text="⚠️ SYSTEM RESET CONTROL ENGINE", 
            font=ctk.CTkFont(weight="bold", size=13), 
            text_color="#ff6b6b"
        ).pack(anchor="w", padx=15, pady=8)
        
        ctk.CTkLabel(
            nuke_frame, 
            text="Clicking this button will completely nuke the active database binary tables and hot-reload blank production schemas.\nAll testing portfolios, spreadsheet states, and invoice lines will be cleared instantly.",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            justify="left"
        ).pack(anchor="w", padx=15, pady=2)
        
        self.nuke_btn = ctk.CTkButton(
            nuke_frame, 
            text="Nuke & Reset Local Engine", 
            fg_color="#8B0000", 
            hover_color="#550000",
            width=200,
            command=self.trigger_system_nuke
        )
        self.nuke_btn.pack(anchor="w", padx=15, pady=15)

    def trigger_system_nuke(self):
        import database
        from tkinter import messagebox
        
        confirm = messagebox.askyesno("Confirm Core Reset", "Are you absolutely sure you want to nuke the database?\nThis action will delete all portfolio lines permanently.")
        if not confirm:
            return
            
        try:
            database.reset_and_reinitialize_database()
            
            self.current_profile_id = 1
            profiles = self.get_profile_names()
            self.profile_menu.configure(values=profiles)
            self.profile_menu.set(profiles[0])
            self.tab4.delete_menu.configure(values=profiles)
            self.tab4.delete_menu.set(profiles[0])
            
            self.sync_accounts()
            self.tab1.acct1_menu.configure(values=self.account_options)
            self.tab1.acct1_menu.set(self.account_options[0] if self.account_options else "")
            self.tab1.acct2_menu.configure(values=self.account_options)
            self.tab1.acct2_menu.set(self.account_options[0] if self.account_options else "")

            # Clear cache entirely so nuke values drop instantly from RAM memory
            self.invalidate_and_prime_cache()

            self.tab2.load_grid_from_db()  
            self.tab5.reload_ledger()      
            self.tab6.load_invoices()      
            self.refresh_reports()         
            
            messagebox.showinfo("Reset Complete", "B.O.Y.O.U.N.G. Engine database hot-reloaded successfully!")
        except Exception as e:
            messagebox.showerror("Reset Failure", f"An error occurred during teardown: {e}")

    # --- SHARED SYSTEM DATA CORE UTILITIES ---
    def get_profile_names(self):
        conn = sqlite3.connect(DATABASE_NAME)
        df = pd.read_sql_query("SELECT name FROM business_profiles", conn)
        conn.close()
        return df['name'].tolist()

    def sync_accounts(self):
        conn = sqlite3.connect(DATABASE_NAME)
        df = pd.read_sql_query("SELECT account_id, name FROM accounts WHERE profile_id = ?", conn, params=(self.current_profile_id,))
        conn.close()
        self.account_map = {row['name']: row['account_id'] for _, row in df.iterrows()}
        self.account_options = list(self.account_map.keys()) if self.account_map else ["No Accounts Found"]

    def switch_profile(self, selection):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT profile_id FROM business_profiles WHERE name = ?", (selection,))
        self.current_profile_id = cursor.fetchone()[0]
        conn.close()
        
        self.sync_accounts()
        self.tab1.acct1_menu.configure(values=self.account_options)
        self.tab1.acct1_menu.set(self.account_options[0] if self.account_options else "")
        self.tab1.acct2_menu.configure(values=self.account_options)
        self.tab1.acct2_menu.set(self.account_options[0] if self.account_options else "")
        
        # Force memory cache to drop and pre-fetch the newly selected profile data instantly
        self.invalidate_and_prime_cache()
        
        self.tab2.load_grid_from_db()
        self.tab5.reload_ledger()
        self.tab6.load_invoices()
        self.refresh_reports()

    def execute_entry(self):
        try:
            val = float(self.tab1.amount_entry.get())
            a1 = self.account_map[self.tab1.acct1_menu.get()]
            a2 = self.account_map[self.tab1.acct2_menu.get()]
            payload = [{"account_id": a1, "amount": val}, {"account_id": a2, "amount": -val}]
            
            engine.post_journal_transaction(self.current_profile_id, "2026-06-27", self.tab1.desc_entry.get(), payload)
            self.tab1.status_label.configure(text="🟢 Entry Posted Successfully!", text_color="green")
            self.tab1.amount_entry.delete(0, 'end')
            self.tab1.desc_entry.delete(0, 'end')
            
            # HOT REFRESH SPEED TRICK: Wipe cache memory records so the UI forces a hot refresh
            self.invalidate_and_prime_cache()
            
            self.tab5.reload_ledger()
            self.refresh_reports()
        except Exception as e:
            self.tab1.status_label.configure(text=f"Error: {e}", text_color="red")

    def refresh_reports(self):
        data = engine.generate_report_string(self.current_profile_id, self.profile_menu.get())
        self.tab3.bi_box.delete("1.0", "end")
        self.tab3.bi_box.insert("1.0", data)

    def add_profile(self):
        name = self.tab4.new_profile_entry.get().strip()
        if not name: return
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO business_profiles (name) VALUES (?)", (name,))
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
            
            profiles = self.get_profile_names()
            self.profile_menu.configure(values=profiles)
            self.tab4.delete_menu.configure(values=profiles)
            self.tab4.new_profile_entry.delete(0, 'end')
        except Exception as e:
            print(e)
        finally:
            conn.close()

    def delete_profile(self):
        target_name = self.tab4.delete_menu.get()
        profiles = self.get_profile_names()
        if len(profiles) <= 1: return
            
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM business_profiles WHERE name = ?", (target_name,))
            conn.commit()
            
            if target_name == self.profile_menu.get():
                remaining_profiles = self.get_profile_names()
                self.switch_profile(remaining_profiles[0])
                self.profile_menu.set(remaining_profiles[0])
            
            updated_profiles = self.get_profile_names()
            self.profile_menu.configure(values=updated_profiles)
            self.tab4.delete_menu.configure(values=updated_profiles)
        except Exception as e:
            print(e)
        finally:
            conn.close()

if __name__ == "__main__":
    app = ModernAccountingApp()
    app.mainloop()