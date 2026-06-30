import customtkinter as ctk
import sqlite3
import pandas as pd
from datetime import datetime
from database import DATABASE_NAME

class InvoiceTrackerTab(ctk.CTkFrame):
    def __init__(self, master, master_app):
        super().__init__(master, fg_color="transparent")
        self.master_app = master_app
        
        # Pagination Tracking States
        self.current_page = 1
        self.items_per_page = 10  # Upgraded to 10 rows per viewport frame context

        # Left Column: Input Form Panel
        self.form_panel = ctk.CTkFrame(self, width=280)
        self.form_panel.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.form_panel, text="➕ Create Customer Invoice", font=ctk.CTkFont(weight="bold", size=14)).pack(pady=10, padx=10)
        
        self.cust_entry = ctk.CTkEntry(self.form_panel, placeholder_text="Customer / Client Name", width=220)
        self.cust_entry.pack(pady=6, padx=10)

        self.amt_entry = ctk.CTkEntry(self.form_panel, placeholder_text="Invoice Amount ($)", width=220)
        self.amt_entry.pack(pady=6, padx=10)

        self.date_entry = ctk.CTkEntry(self.form_panel, placeholder_text="Due Date (YYYY-MM-DD)", width=220)
        self.date_entry.insert(0, "2026-07-15")
        self.date_entry.pack(pady=6, padx=10)

        ctk.CTkButton(self.form_panel, text="🧾 Issue Invoice", fg_color="#228B22", hover_color="#006400", command=self.create_invoice, width=180).pack(pady=15, padx=10)
        self.status_lbl = ctk.CTkLabel(self.form_panel, text="", font=ctk.CTkFont(size=12))
        self.status_lbl.pack(pady=5)

        # Right Column: Visual Ledger / Pipeline Tracker
        self.display_panel = ctk.CTkFrame(self)
        self.display_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Control Bar for Right Side
        top_bar = ctk.CTkFrame(self.display_panel, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(top_bar, text="💳 Accounts Receivable Aging Pipeline", font=ctk.CTkFont(weight="bold", size=14)).pack(side="left", pady=5)
        ctk.CTkButton(top_bar, text="🔄 Sync Pipeline", command=self.load_invoices, width=100).pack(side="right", pady=5)

        # Container for entries
        self.table_scroll = ctk.CTkScrollableFrame(self.display_panel)
        self.table_scroll.pack(fill="both", expand=True, padx=10, pady=5)

        # --- LIVE REAL-TIME FINANCIAL SUMMARY STRIP ---
        self.summary_strip = ctk.CTkFrame(self.display_panel, fg_color="#1e1e1e", height=32, corner_radius=6)
        self.summary_strip.pack(fill="x", side="bottom", pady=(5, 5), padx=10)
        
        self.unpaid_summary_lbl = ctk.CTkLabel(self.summary_strip, text="Total Unpaid: $0.00", font=ctk.CTkFont(weight="bold", size=12), text_color="#D2691E")
        self.unpaid_summary_lbl.pack(side="left", padx=20, pady=5)
        
        self.paid_summary_lbl = ctk.CTkLabel(self.summary_strip, text="Total Paid: $0.00", font=ctk.CTkFont(weight="bold", size=12), text_color="#228B22")
        self.paid_summary_lbl.pack(side="right", padx=20, pady=5)

        # Pagination Control Bar Footer
        self.pagination_bar = ctk.CTkFrame(self.display_panel, fg_color="transparent")
        self.pagination_bar.pack(fill="x", side="bottom", pady=(5, 5), padx=10)

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
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO invoices (profile_id, customer_name, amount, due_date)
                VALUES (?, ?, ?, ?)
            """, (pid, cust, amt, due))
            conn.commit()
            conn.close()

            # 🔥 CACHE UPDATE: Force database changes into high-speed memory immediately
            self.master_app.invalidate_and_prime_cache()

            self.status_lbl.configure(text="🟢 Invoice Issued Safely!", text_color="green")
            self.cust_entry.delete(0, 'end')
            self.amt_entry.delete(0, 'end')
            self.load_invoices()
        except ValueError:
            self.status_lbl.configure(text="❌ Value must be numeric.", text_color="red")

    def load_invoices(self):
        # Wipe out old table items and page layouts cleanly
        for widget in self.table_scroll.winfo_children():
            widget.destroy()
        for widget in self.pagination_bar.winfo_children():
            widget.destroy()

        headers = ["Customer Client", "Amount Due", "Deadline Date", "Status", "Action Switch"]
        for col, text in enumerate(headers):
            ctk.CTkLabel(self.table_scroll, text=text, font=ctk.CTkFont(weight="bold")).grid(row=0, column=col, padx=12, pady=6, sticky="ew")

        conn = sqlite3.connect(DATABASE_NAME)
        today_str = datetime.now().strftime("%Y-%m-%d")

        try:
            # Hot rendering from runtime RAM cache
            df = self.master_app.get_cached_data("invoices")
            
            if df.empty:
                ctk.CTkLabel(self.table_scroll, text="No accounts receivable invoices tracked currently.", font=ctk.CTkFont(slant="italic"), text_color="gray").grid(row=1, column=0, columnspan=5, pady=20)
                self.unpaid_summary_lbl.configure(text="Total Unpaid: $0.00")
                self.paid_summary_lbl.configure(text="Total Paid: $0.00")
                return

            # --- CALCULATE LIVE METRICS ---
            total_unpaid = df[df['status'] == 'Unpaid']['amount'].sum()
            total_paid = df[df['status'] == 'Paid']['amount'].sum()
            
            self.unpaid_summary_lbl.configure(text=f"Total Unpaid: ${total_unpaid:,.2f}")
            self.paid_summary_lbl.configure(text=f"Total Paid: ${total_paid:,.2f}")

            # --- PAGINATION ENGINE ---
            total_items = len(df)
            total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
            
            if self.current_page > total_pages:
                self.current_page = total_pages

            start_idx = (self.current_page - 1) * self.items_per_page
            end_idx = start_idx + self.items_per_page
            page_df = df.iloc[start_idx:end_idx]

            # Render Page Rows Loop
            for loop_idx, (_, row) in enumerate(page_df.iterrows()):
                grid_row = loop_idx + 1
                inv_id = int(row['invoice_id'])
                
                status_str = row['status']
                due_date_str = str(row['due_date'])
                
                # --- TRAFFIC LIGHT CONDITIONAL EVALUATION ENGINE ---
                if status_str == "Paid":
                    status_display = "Paid"
                    status_color = "#228B22"  # Bright corporate green
                    row_bg_color = "transparent"
                else:
                    if due_date_str < today_str:
                        status_display = "⚠️ OVERDUE"
                        status_color = "#FF4500"  # Intense alerting orange-red
                        row_bg_color = "#2d1a15"  # Faint alert tint row wrap
                    else:
                        status_display = "Unpaid"
                        status_color = "#D2691E"  # Standard warning gold/amber
                        row_bg_color = "transparent"

                # Structural row background coloring tint setup
                row_frame = ctk.CTkFrame(self.table_scroll, fg_color=row_bg_color, corner_radius=4)
                row_frame.grid(row=grid_row, column=0, columnspan=5, padx=2, pady=2, sticky="ew")
                row_frame.grid_columnconfigure((0,1,2,3,4), weight=1)

                ctk.CTkLabel(row_frame, text=str(row['customer_name'])).grid(row=0, column=0, padx=12, pady=4)
                ctk.CTkLabel(row_frame, text=f"${row['amount']:,.2f}", font=ctk.CTkFont(family="Courier")).grid(row=0, column=1, padx=12, pady=4)
                ctk.CTkLabel(row_frame, text=due_date_str).grid(row=0, column=2, padx=12, pady=4)
                ctk.CTkLabel(row_frame, text=status_display, text_color=status_color, font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=12, pady=4)

                if status_str == "Unpaid":
                    btn = ctk.CTkButton(row_frame, text="Mark Paid", width=90, height=24, fg_color="#4682B4", hover_color="#2b506f", command=lambda i=inv_id: self.mark_invoice_paid(i))
                    btn.grid(row=0, column=4, padx=12, pady=4)
                else:
                    del_btn = ctk.CTkButton(row_frame, text="❌ Delete", width=90, height=24, fg_color="#8B0000", hover_color="#550000", command=lambda i=inv_id: self.delete_invoice(i))
                    del_btn.grid(row=0, column=4, padx=12, pady=4)

            # Render Pagination Footer
            if total_pages > 1:
                footer_frame = ctk.CTkFrame(self.pagination_bar, fg_color="transparent")
                footer_frame.pack(anchor="center")
                
                for p in range(1, total_pages + 1):
                    is_current = (p == self.current_page)
                    b_color = "#1f538d" if is_current else "#3a3a3a"
                    
                    p_btn = ctk.CTkButton(footer_frame, text=str(p), width=30, height=24, fg_color=b_color, command=lambda target_p=p: self.change_page(target_p))
                    p_btn.pack(side="left", padx=3)

        except Exception as e:
            print(f"Pipeline render error: {e}")
        finally:
            conn.close()

    def change_page(self, page_number):
        self.current_page = page_number
        self.load_invoices()

    def mark_invoice_paid(self, invoice_id):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE invoices SET status = 'Paid' WHERE invoice_id = ?", (invoice_id,))
        conn.commit()
        conn.close()
        
        # 🔥 CACHE UPDATE: Refresh memory block metrics on modification
        self.master_app.invalidate_and_prime_cache()
        self.load_invoices()
        self.master_app.refresh_reports()

    def delete_invoice(self, invoice_id):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM invoices WHERE invoice_id = ?", (invoice_id,))
        conn.commit()
        conn.close()
        
        # 🔥 CACHE UPDATE: Remove record from memory block metrics instantly
        self.master_app.invalidate_and_prime_cache()
        self.load_invoices()
        self.master_app.refresh_reports()