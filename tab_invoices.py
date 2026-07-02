import customtkinter as ctk
import sqlite3
import pandas as pd
from datetime import date, datetime
from database import DATABASE_NAME

class InvoiceTrackerTab(ctk.CTkFrame):
    def __init__(self, master, master_app):
        super().__init__(master, fg_color="transparent")
        self.master_app = master_app
        
        self.current_page = 1
        self.items_per_page = 10  

        self.form_panel = ctk.CTkFrame(self, width=280)
        self.form_panel.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.form_panel, text="Create Customer Invoice", font=ctk.CTkFont(weight="bold", size=14)).pack(pady=10, padx=10)
        
        self.cust_entry = ctk.CTkEntry(self.form_panel, placeholder_text="Customer / Client Name", width=220)
        self.cust_entry.pack(pady=6, padx=10)

        self.amt_entry = ctk.CTkEntry(self.form_panel, placeholder_text="Invoice Amount ($)", width=220)
        self.amt_entry.pack(pady=6, padx=10)

        self.date_entry = ctk.CTkEntry(self.form_panel, placeholder_text="Due Date (YYYY-MM-DD)", width=220)
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        self.date_entry.pack(pady=6, padx=10)

        ctk.CTkButton(self.form_panel, text="Issue Invoice", fg_color="#1f538d", hover_color="#14375e", command=self.create_invoice, width=150).pack(pady=15, padx=10)
        
        self.status_lbl = ctk.CTkLabel(self.form_panel, text="", font=ctk.CTkFont(size=12))
        self.status_lbl.pack(pady=5, padx=10)

        self.right_panel = ctk.CTkFrame(self)
        self.right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.pipeline_container = ctk.CTkScrollableFrame(self.right_panel)
        self.pipeline_container.pack(fill="both", expand=True, padx=10, pady=10)

        self.pagination_bar = ctk.CTkFrame(self.right_panel, fg_color="transparent", height=40)
        self.pagination_bar.pack(fill="x", side="bottom", padx=10, pady=5)

        self.load_invoices()

    def create_invoice(self):
        pid = self.master_app.current_profile_id
        cust = self.cust_entry.get().strip()
        amt_raw = self.amt_entry.get().strip()
        due = self.date_entry.get().strip()

        if not cust or not amt_raw or not due:
            self.status_lbl.configure(text="❌ All invoice fields required.", text_color="red")
            return

        try:
            amt = float(amt_raw)
            
            if self.master_app.is_simulation_mode:
                sim_inv = pd.DataFrame([{
                    "invoice_id": 9999, 
                    "customer_name": cust, 
                    "amount": amt, 
                    "due_date": due, 
                    "status": "Unpaid"
                }])
                self.master_app._sim_cache["invoices"] = pd.concat([sim_inv, self.master_app._sim_cache["invoices"]], ignore_index=True)
                self.status_lbl.configure(text="Simulated Invoice Added to RAM!", text_color="#ffb84d")
            else:
                conn = sqlite3.connect(DATABASE_NAME)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO invoices (profile_id, customer_name, amount, due_date)
                    VALUES (?, ?, ?, ?)
                """, (pid, cust, amt, due))
                conn.commit()
                conn.close()
                self.master_app.invalidate_and_prime_cache()
                self.status_lbl.configure(text="Invoice Issued Safely!", text_color="green")

            self.cust_entry.delete(0, 'end')
            self.amt_entry.delete(0, 'end')
            self.load_invoices()
        except ValueError:
            self.status_lbl.configure(text="❌ Value must be numeric.", text_color="red")

    def load_invoices(self):
        for widget in self.pipeline_container.winfo_children():
            widget.destroy()
        for widget in self.pagination_bar.winfo_children():
            widget.destroy()

        headers = ["ID", "Customer", "Amount", "Due Date", "Status", "Actions"]
        header_frame = ctk.CTkFrame(self.pipeline_container, fg_color="#2b2b2b", height=30)
        header_frame.pack(fill="x", padx=5, pady=2)
        
        for col_idx, text in enumerate(headers):
            w = 50 if col_idx == 0 else (130 if col_idx in [1, 5] else 100)
            anchor_pos = "w" if col_idx in [1, 3] else ("e" if col_idx == 2 else "center")
            ctk.CTkLabel(header_frame, text=text, font=ctk.CTkFont(weight="bold"), width=w, anchor=anchor_pos).pack(side="left", padx=10)

        df = self.master_app.get_cached_data("invoices")
        if df is None or df.empty:
            ctk.CTkLabel(self.pipeline_container, text="No open invoices found for this profile portfolio.", text_color="gray").pack(pady=40)
            return

        total_records = len(df)
        total_pages = max(1, (total_records + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page > total_pages:
            self.current_page = total_pages

        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_df = df.iloc[start_idx:end_idx]

        for _, row in page_df.iterrows():
            row_frame = ctk.CTkFrame(self.pipeline_container, fg_color="#1e1e1e", height=35)
            row_frame.pack(fill="x", padx=5, pady=2)

            inv_id = row['invoice_id']
            status = row['status']
            
            ctk.CTkLabel(row_frame, text=f"#{inv_id}", width=50, text_color="gray").pack(side="left", padx=10)
            ctk.CTkLabel(row_frame, text=str(row['customer_name']), width=130, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(row_frame, text=f"${float(row['amount']):,.2f}", font=ctk.CTkFont(family="Courier"), width=100, anchor="e").pack(side="left", padx=10)
            ctk.CTkLabel(row_frame, text=str(row['due_date']), width=100, anchor="w").pack(side="left", padx=10)

            status_color = "#40ff40" if status == "Paid" else "#ff6b6b"
            ctk.CTkLabel(row_frame, text=status, text_color=status_color, font=ctk.CTkFont(weight="bold"), width=100).pack(side="left", padx=10)

            act_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            act_frame.pack(side="right", padx=10)

            if status == "Unpaid":
                ctk.CTkButton(act_frame, text="Mark Paid", width=75, height=22, fg_color="#228B22", hover_color="#122416", command=lambda i=inv_id: self.mark_invoice_paid(i)).pack(side="left", padx=2)
            
            ctk.CTkButton(act_frame, text="Delete", width=55, height=22, fg_color="#8B0000", hover_color="#550000", command=lambda i=inv_id: self.delete_invoice(i)).pack(side="left", padx=2)

        if total_pages > 1:
            footer_frame = ctk.CTkFrame(self.pagination_bar, fg_color="transparent")
            footer_frame.pack(anchor="center")
            for p in range(1, total_pages + 1):
                is_current = (p == self.current_page)
                b_color = "#1f538d" if is_current else "#3a3a3a"
                p_btn = ctk.CTkButton(footer_frame, text=str(p), width=30, height=24, fg_color=b_color, command=lambda target_p=p: self.change_page(target_p))
                p_btn.pack(side="left", padx=3)

    def change_page(self, page_number):
        self.current_page = page_number
        self.load_invoices()

    def mark_invoice_paid(self, invoice_id):
        if self.master_app.is_simulation_mode:
            df = self.master_app._sim_cache["invoices"]
            df.loc[df['invoice_id'] == invoice_id, 'status'] = 'Paid'
            self.status_lbl.configure(text="Simulated Invoice Marked Paid!", text_color="#ffb84d")
        else:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("UPDATE invoices SET status = 'Paid' WHERE invoice_id = ?", (invoice_id,))
            conn.commit()
            conn.close()
            self.master_app.invalidate_and_prime_cache()

        self.load_invoices()
        self.master_app.refresh_reports()

    def delete_invoice(self, invoice_id):
        if self.master_app.is_simulation_mode:
            df = self.master_app._sim_cache["invoices"]
            self.master_app._sim_cache["invoices"] = df[df['invoice_id'] != invoice_id]
            self.status_lbl.configure(text="Simulated Invoice Deleted from RAM!", text_color="#ffb84d")
        else:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM invoices WHERE invoice_id = ?", (invoice_id,))
            conn.commit()
            conn.close()
            self.master_app.invalidate_and_prime_cache()

        self.load_invoices()
        self.master_app.refresh_reports()
