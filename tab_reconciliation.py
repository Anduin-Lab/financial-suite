import customtkinter as ctk
import sqlite3
import pandas as pd
from tkinter import filedialog
from database import DATABASE_NAME
import engine

class BankReconciliationTab(ctk.CTkFrame):
    def __init__(self, master, master_app):
        super().__init__(master, fg_color="transparent")
        self.master_app = master_app
        self.csv_data = None

        control_bar = ctk.CTkFrame(self, fg_color="transparent")
        control_bar.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(control_bar, text="Bank Statement Matching", font=ctk.CTkFont(weight="bold", size=15)).pack(side="left", padx=5)
        ctk.CTkButton(control_bar, text="Import CSV File", command=self.import_statement, fg_color="#1f538d", hover_color="#14375e").pack(side="right", padx=5)

        self.table_container = ctk.CTkScrollableFrame(self)
        self.table_container.pack(pady=10, padx=10, fill="both", expand=True)

        self.status_lbl = ctk.CTkLabel(self, text="Upload a standard bank statement CSV to reconcile.", font=ctk.CTkFont(size=12))
        self.status_lbl.pack(pady=5)

    def import_statement(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return
        try:
            self.csv_data = pd.read_csv(file_path)
            self.render_reconciliation_grid()
        except Exception as e:
            self.status_lbl.configure(text=f"Error reading CSV: {e}", text_color="red")

    def render_reconciliation_grid(self):
        for widget in self.table_container.winfo_children():
            widget.destroy()

        headers = ["Date", "Description", "Amount", "Action"]
        for col_idx, text in enumerate(headers):
            ctk.CTkLabel(self.table_container, text=text, font=ctk.CTkFont(weight="bold"), width=180, anchor="w").grid(row=0, column=col_idx, padx=10, pady=5)

        required_cols = ['date', 'description', 'amount']
        if not all(col in [c.lower() for c in self.csv_data.columns] for col in required_cols):
            self.status_lbl.configure(text="CSV must contain 'date', 'description', and 'amount' headers.", text_color="red")
            return

        self.csv_data.columns = [c.lower() for c in self.csv_data.columns]

        for idx, row in self.csv_data.iterrows():
            grid_row = idx + 1
            date_str = str(row['date'])
            desc_str = str(row['description'])
            try:
                amt_val = float(row['amount'])
            except ValueError:
                amt_val = 0.0

            ctk.CTkLabel(self.table_container, text=date_str, width=180, anchor="w").grid(row=grid_row, column=0, padx=10, pady=2)
            ctk.CTkLabel(self.table_container, text=desc_str, width=180, anchor="w").grid(row=grid_row, column=1, padx=10, pady=2)
            ctk.CTkLabel(self.table_container, text=f"${amt_val:,.2f}", font=ctk.CTkFont(family="Courier"), width=180, anchor="w").grid(row=grid_row, column=2, padx=10, pady=2)

            btn = ctk.CTkButton(self.table_container, text="Match Split", width=90, height=22, command=lambda d=date_str, desc=desc_str, a=amt_val, r=grid_row: self.post_reconciled_split(d, desc, a, r))
            btn.grid(row=grid_row, column=3, padx=10, pady=2)

    def post_reconciled_split(self, date_str, description, amount, row_idx):
        pid = self.master_app.current_profile_id
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT account_id FROM accounts WHERE profile_id = ? AND account_number = '1000' LIMIT 1", (pid,))
        bank_acct = cursor.fetchone()
        cursor.execute("SELECT account_id FROM accounts WHERE profile_id = ? AND account_number = '4000' LIMIT 1", (pid,))
        rev_acct = cursor.fetchone()
        conn.close()

        if not bank_acct or not rev_acct:
            self.status_lbl.configure(text="Default accounts (1000/4000) are missing.", text_color="red")
            return

        payload = [
            {"account_id": bank_acct[0], "amount": amount},
            {"account_id": rev_acct[0], "amount": -amount}
        ]

        try:
            engine.post_journal_transaction(pid, date_str, f"Reconciled: {description}", payload)
            for widget in self.table_container.grid_slaves(row=row_idx):
                if isinstance(widget, ctk.CTkButton):
                    widget.configure(text="✅ Matched", state="disabled", fg_color="green")
            self.master_app.invalidate_and_prime_cache()
            self.status_lbl.configure(text="Transaction posted directly into ledger records.", text_color="green")
        except Exception as e:
            self.status_lbl.configure(text=f"Posting failed: {e}", text_color="red")
