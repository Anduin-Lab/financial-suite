import customtkinter as ctk
import sqlite3
import pandas as pd
from database import DATABASE_NAME, initialize_database
import engine
import designs

from tab_entry import LogTransactionTab
from tab_sheet import InteractiveSheetTab
from tab_reports import ReportsDashboardTab
from tab_settings import SystemSettingsTab
from tab_ledger import GeneralLedgerTab
from tab_invoices import InvoiceTrackerTab
from tab_reconciliation import BankReconciliationTab
from audit_engine import AuditEngine

ctk.set_appearance_mode("Dark")

class ModernAccountingApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        initialize_database()
        
        self.title("Financial Suite HUD — Mark VII")
        self.geometry("1020x780")
        self.configure(fg_color=designs.BG_WINDOW)
        
        self.current_profile_id = 1
        self._cache = {"ledger": None, "invoices": None}
        
        self.top_bar = ctk.CTkFrame(self, fg_color=designs.BG_PANEL, height=55, corner_radius=8, border_color=designs.BORDER_COLOR, border_width=1)
        self.top_bar.pack(pady=(15, 10), padx=20, fill="x")
        self.top_bar.pack_propagate(False)
        
        profile_lbl = ctk.CTkLabel(self.top_bar, text="OPERATIONAL SCOPE:", font=ctk.CTkFont(family=designs.FONT_HUD_TITLE[0], size=designs.FONT_HUD_TITLE[1], weight=designs.FONT_HUD_TITLE[2]), text_color=designs.COLOR_ACCENT)
        profile_lbl.pack(side="left", padx=(20, 5), pady=12)
        
        self.profile_menu = ctk.CTkOptionMenu(
            self.top_bar, 
            values=self.get_profile_names(), 
            command=self.switch_profile, 
            width=200,
            font=ctk.CTkFont(family=designs.FONT_HUD_REGULAR[0], size=designs.FONT_HUD_REGULAR[1], weight=designs.FONT_HUD_REGULAR[2]),
            **designs.OPTIONMENU_STYLE
        )
        self.profile_menu.pack(side="left", padx=10, pady=12)
        
        self.sync_accounts()
        self.invalidate_and_prime_cache()

        self.footer_bar = ctk.CTkFrame(self, height=35, fg_color=designs.BG_SUBPANEL, corner_radius=0, border_color=designs.BORDER_COLOR, border_width=1)
        self.footer_bar.pack(fill="x", side="bottom", ipady=2)
        
        self.error_icon_lbl = ctk.CTkLabel(
            self.footer_bar, 
            text="SYSTEM INTEGRITY: SECURE", 
            font=ctk.CTkFont(family=designs.FONT_HUD_CONSOLE[0], size=designs.FONT_HUD_CONSOLE[1], weight=designs.FONT_HUD_CONSOLE[2]),
            text_color=designs.COLOR_SUCCESS, 
            cursor="hand2"
        )
        self.error_icon_lbl.pack(side="left", padx=20, pady=5)
        self.error_icon_lbl.bind("<Button-1>", lambda e: self.show_audit_console_popup())
        
        self.detected_errors = []
        
        self.tabs = ctk.CTkTabview(
            self,
            **designs.TABVIEW_STYLE
        )
        self.tabs.pack(padx=20, pady=(5, 15), fill="both", expand=True)
        

        self.tabs._segmented_button.configure(font=ctk.CTkFont(family=designs.FONT_HUD_REGULAR[0], size=designs.FONT_HUD_REGULAR[1], weight=designs.FONT_HUD_REGULAR[2]))
        
        self.tab1 = LogTransactionTab(self.tabs.add("Log Transaction"), self)
        self.tab1.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab2 = InteractiveSheetTab(self.tabs.add("Interactive Sheet"), self)
        self.tab2.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab3 = ReportsDashboardTab(self.tabs.add("View Dashboard"), self)
        self.tab3.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab4 = SystemSettingsTab(self.tabs.add("Manage System"), self)
        self.tab4.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab5 = GeneralLedgerTab(self.tabs.add("View Ledger"), self)
        self.tab5.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab6 = InvoiceTrackerTab(self.tabs.add("Track Invoices"), self)
        self.tab6.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab7 = BankReconciliationTab(self.tabs.add("Reconcile Accounts"), self)
        self.tab7.pack(fill="both", expand=True, padx=10, pady=10)

        self.mount_reset_control()
        self.refresh_reports()
        self.refresh_system_health_status()

    def invalidate_and_prime_cache(self):
        conn = sqlite3.connect(DATABASE_NAME)
        try:
            self._cache["ledger"] = pd.read_sql_query("SELECT * FROM ledger_entries WHERE profile_id = ?", conn, params=(self.current_profile_id,))
            self._cache["invoices"] = pd.read_sql_query("SELECT * FROM invoices WHERE profile_id = ?", conn, params=(self.current_profile_id,))
        except Exception:
            self._cache["ledger"] = pd.DataFrame()
            self._cache["invoices"] = pd.DataFrame()
        finally:
            conn.close()

    def get_cached_data(self, key):
        if self._cache.get(key) is None:
            self.invalidate_and_prime_cache()
        return self._cache[key]

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
        
        self.invalidate_and_prime_cache()
        self.tab2.load_grid_from_db()
        self.tab5.reload_ledger()
        self.tab6.load_invoices()
        self.refresh_reports()
        self.refresh_system_health_status()

    def execute_entry(self):
        try:
            val = float(self.tab1.amount_entry.get())
            a1 = self.account_map[self.tab1.acct1_menu.get()]
            a2 = self.account_map[self.tab1.acct2_menu.get()]
            payload = [{"account_id": a1, "amount": val}, {"account_id": a2, "amount": -val}]
            
            engine.post_journal_transaction(self.current_profile_id, "2026-06-27", self.tab1.desc_entry.get(), payload)
            self.tab1.status_label.configure(text="Transaction posted successfully", text_color=designs.COLOR_SUCCESS)
            self.invalidate_and_prime_cache()
                
            self.tab1.amount_entry.delete(0, 'end')
            self.tab1.desc_entry.delete(0, 'end')
            self.tab5.reload_ledger()
            self.refresh_reports()
            self.refresh_system_health_status()
        except Exception as e:
            self.tab1.status_label.configure(text=f"Error: {e}", text_color=designs.COLOR_CRITICAL)

    def refresh_reports(self):
        data = engine.generate_report_string(self.current_profile_id, self.profile_menu.get())
        self.tab3.bi_box.delete("1.0", "end")
        self.tab3.bi_box.insert("1.0", data)

    def mount_reset_control(self):
        reset_frame = ctk.CTkFrame(self.tab4, fg_color=designs.COLOR_CRITICAL_BG, border_color=designs.COLOR_CRITICAL, border_width=1, corner_radius=6)
        reset_frame.pack(fill="x", padx=20, pady=20, side="bottom")
        ctk.CTkLabel(reset_frame, text="CRITICAL DESTRUCTION PROTOCOL", font=ctk.CTkFont(family=designs.FONT_HUD_ALERT_TITLE[0], size=designs.FONT_HUD_ALERT_TITLE[1], weight=designs.FONT_HUD_ALERT_TITLE[2]), text_color=designs.COLOR_CRITICAL).pack(anchor="w", padx=15, pady=8)
        self.reset_btn = ctk.CTkButton(reset_frame, text="WIPE SOFTWARE DATA", fg_color=designs.COLOR_CRITICAL_ALERT, hover_color=designs.COLOR_CRITICAL, text_color="#ffffff", font=ctk.CTkFont(weight="bold"), width=200, command=self.trigger_system_reset)
        self.reset_btn.pack(anchor="w", padx=15, pady=15)

    def trigger_system_reset(self):
        import database
        from tkinter import messagebox
        if not messagebox.askyesno("Confirm Reset", "Are you sure you want to reset the local database?"): return
        try:
            database.reset_and_reinitialize_database()
            self.current_profile_id = 1
            profiles = self.get_profile_names()
            self.profile_menu.configure(values=profiles)
            self.profile_menu.set(profiles[0])
            self.sync_accounts()
            self.invalidate_and_prime_cache()
            self.tab2.load_grid_from_db()  
            self.tab5.reload_ledger()      
            self.tab6.load_invoices()      
            self.refresh_reports()         
            self.refresh_system_health_status()
            messagebox.showinfo("Success", "Database successfully reinitialized.")
        except Exception as e: messagebox.showerror("Error", f"Reset failed: {e}")

    def refresh_system_health_status(self):
        self.detected_errors = AuditEngine.run_system_audit(self.current_profile_id)
        err_count = len(self.detected_errors)
        
        if err_count > 0:
            self.error_icon_lbl.configure(text=f"⚠️ METRIC ANOMALIES DETECTED: {err_count}", text_color=designs.COLOR_CRITICAL)
        else:
            self.error_icon_lbl.configure(text="✅ CORE SYSTEM INTEGRITY: OPTIMAL", text_color=designs.COLOR_SUCCESS)

    def show_audit_console_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("System Integrity Console Log")
        popup.geometry("600x400")
        popup.configure(fg_color=designs.BG_WINDOW)
        popup.attributes("-topmost", True)
        
        ctk.CTkLabel(popup, text="CRITICAL SYSTEM METRIC AUDIT", font=ctk.CTkFont(family=designs.FONT_HUD_REGULAR[0], weight="bold", size=14), text_color=designs.COLOR_ACCENT).pack(pady=15)
        
        log_view = ctk.CTkScrollableFrame(popup, fg_color=designs.BG_PANEL, border_color=designs.BORDER_COLOR, border_width=1)
        log_view.pack(fill="both", expand=True, padx=20, pady=10)
        
        if not self.detected_errors:
            ctk.CTkLabel(log_view, text="No anomalies registered in workspace structures.", text_color=designs.COLOR_SUCCESS, font=ctk.CTkFont(family=designs.FONT_HUD_CONSOLE[0], size=13)).pack(pady=60)
            return
            
        for err in self.detected_errors:
            error_text = f"• [{err['type'].upper()}] Found in '{err['tab']}' tab:\n  {err['msg']}\n"
            lbl = ctk.CTkLabel(log_view, text=error_text, font=ctk.CTkFont(family=designs.FONT_HUD_ALERT_BODY[0], size=designs.FONT_HUD_ALERT_BODY[1]), text_color=designs.COLOR_CRITICAL, justify="left", anchor="w", wraplength=520)
            lbl.pack(fill="x", anchor="w", pady=6, padx=10)

    def add_profile(self):
        name = self.tab4.new_profile_entry.get().strip()
        if not name: return
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO business_profiles (name) VALUES (?)", (name,))
            pid = cursor.lastrowid
            accounts = [(pid, '1000', 'Cash / Bank', 'Asset'), (pid, '1200', 'Accounts Receivable', 'Asset'), (pid, '2000', 'Payables', 'Liability'), (pid, '3000', 'Owner Equity', 'Equity'), (pid, '4000', 'Revenue', 'Revenue'), (pid, '5000', 'Software Expenses', 'Expense'), (pid, '5100', 'Rent Expense', 'Expense')]
            cursor.executemany("INSERT INTO accounts (profile_id, account_number, name, type) VALUES (?,?,?,?)", accounts)
            conn.commit()
            self.profile_menu.configure(values=self.get_profile_names())
            self.tab4.new_profile_entry.delete(0, 'end')
        except Exception as e: print(e)
        finally: conn.close()

    def delete_profile(self):
        target_name = self.tab4.delete_menu.get()
        if len(self.get_profile_names()) <= 1: return
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM business_profiles WHERE name = ?", (target_name,))
            conn.commit()
            if target_name == self.profile_menu.get():
                self.switch_profile(self.get_profile_names()[0])
                self.profile_menu.set(self.get_profile_names()[0])
            self.profile_menu.configure(values=self.get_profile_names())
        except Exception as e: print(e)
        finally: conn.close()

if __name__ == "__main__":
    app = ModernAccountingApp()
    app.mainloop()
