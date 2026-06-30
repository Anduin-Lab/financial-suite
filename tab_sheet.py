import customtkinter as ctk
import sqlite3
import pandas as pd
from database import DATABASE_NAME

class InteractiveSheetTab(ctk.CTkFrame):
    def __init__(self, master, master_app):
        super().__init__(master, fg_color="transparent")
        self.master_app = master_app
        
        self.total_rows = 15
        self.widgets = {}  

        control_bar = ctk.CTkFrame(self, fg_color="transparent")
        control_bar.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(control_bar, text="Ledger Spreadsheet Workspace", font=ctk.CTkFont(weight="bold", size=14)).pack(side="left")
        ctk.CTkButton(control_bar, text="Save Changes", fg_color="#1f538d", hover_color="#14375e", width=120, command=self.save_grid_to_db).pack(side="right", padx=5)
        ctk.CTkButton(control_bar, text="Recalculate Sheet", fg_color="#3a3a3a", hover_color="#2b2b2b", width=140, command=self.load_grid_from_db).pack(side="right", padx=5)

        self.sheet_container = ctk.CTkScrollableFrame(self)
        self.sheet_container.pack(fill="both", expand=True, padx=20, pady=5)

        headers = ["Row", "Item / Expense Description", "Quantity", "Unit Rate ($)", "Line Total ($)"]
        widths = [50, 320, 100, 120, 140]
        
        for col_idx, text in enumerate(headers):
            lbl = ctk.CTkLabel(self.sheet_container, text=text, font=ctk.CTkFont(weight="bold"), width=widths[col_idx], anchor="w" if col_idx < 4 else "e")
            lbl.grid(row=0, column=col_idx, padx=5, pady=5, sticky="ew")

        for r in range(1, self.total_rows + 1):
            ctk.CTkLabel(self.sheet_container, text=str(r), width=50, anchor="center").grid(row=r, column=0, padx=5, pady=2)
            
            desc_field = ctk.CTkEntry(self.sheet_container, placeholder_text="Enter description...", width=320)
            desc_field.grid(row=r, column=1, padx=5, pady=2, sticky="w")
            
            qty_field = ctk.CTkEntry(self.sheet_container, placeholder_text="0", width=100)
            qty_field.grid(row=r, column=2, padx=5, pady=2, sticky="w")
            
            rate_field = ctk.CTkEntry(self.sheet_container, placeholder_text="0.00", width=120)
            rate_field.grid(row=r, column=3, padx=5, pady=2, sticky="w")
            
            total_label = ctk.CTkLabel(self.sheet_container, text="$0.00", font=ctk.CTkFont(family="Courier"), width=140, anchor="e")
            total_label.grid(row=r, column=4, padx=5, pady=2, sticky="e")
            
            qty_field.bind("<KeyRelease>", lambda e, r_idx=r: self.compute_row_total(r_idx))
            rate_field.bind("<KeyRelease>", lambda e, r_idx=r: self.compute_row_total(r_idx))
            
            self.widgets[r] = {
                "desc": desc_field,
                "qty": qty_field,
                "rate": rate_field,
                "total": total_label
            }

        self.summary_strip = ctk.CTkFrame(self, fg_color="#1e1e1e", height=35, corner_radius=6)
        self.summary_strip.pack(fill="x", side="bottom", pady=10, padx=20)
        
        self.grand_total_lbl = ctk.CTkLabel(self.summary_strip, text="Grand Aggregate Value: $0.00", font=ctk.CTkFont(weight="bold", size=13), text_color="#40ff40")
        self.grand_total_lbl.pack(side="right", padx=20, pady=5)

        self.load_grid_from_db()

    def compute_row_total(self, r):
        try:
            qty_val = self.widgets[r]["qty"].get().strip()
            rate_val = self.widgets[r]["rate"].get().strip()
            
            qty = float(qty_val) if qty_val else 0.0
            rate = float(rate_val) if rate_val else 0.0
            
            line_total = qty * rate
            self.widgets[r]["total"].configure(text=f"${line_total:,.2f}")
        except ValueError:
            self.widgets[r]["total"].configure(text="$0.00")
            
        self.compute_grand_total()

    def compute_grand_total(self):
        grand_total = 0.0
        for r in range(1, self.total_rows + 1):
            txt = self.widgets[r]["total"].cget("text")
            try:
                val = float(txt.replace("$", "").replace(",", ""))
                grand_total += val
            except ValueError:
                pass
        self.grand_total_lbl.configure(text=f"Grand Aggregate Value: ${grand_total:,.2f}")

    def save_grid_to_db(self):
        if self.master_app.is_simulation_mode:
            print("Spreadsheet saving skipped while in simulation mode.")
            return

        pid = self.master_app.current_profile_id
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM grid_items WHERE profile_id = ?", (pid,))
            
            payload = []
            for r in range(1, self.total_rows + 1):
                desc = self.widgets[r]["desc"].get().strip()
                qty_str = self.widgets[r]["qty"].get().strip()
                rate_str = self.widgets[r]["rate"].get().strip()
                
                if desc or qty_str or rate_str:
                    qty = float(qty_str) if qty_str else 0.0
                    rate = float(rate_str) if rate_str else 0.0
                    payload.append((pid, r, desc, qty, rate))
                    
            if payload:
                cursor.executemany("INSERT INTO grid_items (profile_id, row_index, description, quantity, rate) VALUES (?,?,?,?,?)", payload)
            conn.commit()
        except Exception as e:
            print(f"Spreadsheet persistence error: {e}")
        finally:
            conn.close()

    def load_grid_from_db(self):
        pid = self.master_app.current_profile_id
        
        for r in range(1, self.total_rows + 1):
            self.widgets[r]["desc"].delete(0, 'end')
            self.widgets[r]["desc"]._activate_placeholder()  
            
            self.widgets[r]["qty"].delete(0, 'end')
            self.widgets[r]["qty"]._activate_placeholder()
            
            self.widgets[r]["rate"].delete(0, 'end')
            self.widgets[r]["rate"]._activate_placeholder()
            
            self.widgets[r]["total"].configure(text="$0.00")

        conn = sqlite3.connect(DATABASE_NAME)
        try:
            df = pd.read_sql_query("SELECT row_index, description, quantity, rate FROM grid_items WHERE profile_id = ?", conn, params=(pid,))
            for _, row in df.iterrows():
                r = int(row['row_index'])
                if r in self.widgets:
                    self.widgets[r]["desc"].insert(0, str(row['description'] or ""))
                    self.widgets[r]["qty"].insert(0, str(int(row['quantity']) if row['quantity'].is_integer() else row['quantity']))
                    self.widgets[r]["rate"].insert(0, f"{row['rate']:.2f}")
                    
                    line_total = float(row['quantity'] or 0.0) * float(row['rate'] or 0.0)
                    self.widgets[r]["total"].configure(text=f"${line_total:,.2f}")
        except Exception as e:
            print(f"Spreadsheet load error: {e}")
        finally:
            conn.close()
            
        self.compute_grand_total()
