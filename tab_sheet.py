import customtkinter as ctk
import sqlite3
import pandas as pd
from database import DATABASE_NAME

class InteractiveSheetTab(ctk.CTkFrame):
    def __init__(self, master, master_app):
        super().__init__(master, fg_color="transparent")
        self.master_app = master_app
        
        # Grid Configuration Rules
        self.total_rows = 15
        self.widgets = {}  # Format: {row -> {"desc": widget, "qty": widget, ...}}

        # Control Panel Bar
        control_bar = ctk.CTkFrame(self, fg_color="transparent")
        control_bar.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(control_bar, text="📊 Live Ledger Spreadsheet Engine", font=ctk.CTkFont(weight="bold", size=14)).pack(side="left")
        ctk.CTkButton(control_bar, text="💾 Save Changes", fg_color="#1f538d", hover_color="#14375e", width=120, command=self.save_grid_to_db).pack(side="right", padx=5)
        ctk.CTkButton(control_bar, text="🔄 Recalculate Sheet", fg_color="#3a3a3a", hover_color="#2b2b2b", width=140, command=self.load_grid_from_db).pack(side="right", padx=5)

        # Scrollable Sheet Workspace Canvas
        self.sheet_container = ctk.CTkScrollableFrame(self)
        self.sheet_container.pack(fill="both", expand=True, padx=20, pady=10)

        # Draw Table Headers
        headers = ["Row", "Description / Account Link", "Quantity", "Rate ($)", "Line Total ($)"]
        for col_idx, text in enumerate(headers):
            ctk.CTkLabel(self.sheet_container, text=text, font=ctk.CTkFont(weight="bold")).grid(row=0, column=col_idx, padx=10, pady=5, sticky="ew")

        # Draw Input Matrix Rows
        for r in range(1, self.total_rows + 1):
            ctk.CTkLabel(self.sheet_container, text=str(r), text_color="gray").grid(row=r, column=0, padx=10, pady=2)

            desc = ctk.CTkEntry(self.sheet_container, width=280, placeholder_text="Freeform entry...")
            qty = ctk.CTkEntry(self.sheet_container, width=100, placeholder_text="0", justify="right")
            rate = ctk.CTkEntry(self.sheet_container, width=120, placeholder_text="0.00", justify="right")
            total_lbl = ctk.CTkLabel(self.sheet_container, text="$0.00", font=ctk.CTkFont(family="Courier", weight="bold"))

            desc.grid(row=r, column=1, padx=5, pady=2)
            qty.grid(row=r, column=2, padx=5, pady=2)
            rate.grid(row=r, column=3, padx=5, pady=2)
            total_lbl.grid(row=r, column=4, padx=15, pady=2, sticky="e")

            self.widgets[r] = {"desc": desc, "qty": qty, "rate": rate, "total": total_lbl}

            # --- EXCEL KEYBOARD BINDINGS ---
            desc.bind("<Key>", lambda e, row=r: self.navigate_keyboard(e, row, "desc"))
            qty.bind("<Key>", lambda e, row=r: self.navigate_keyboard(e, row, "qty"))
            rate.bind("<Key>", lambda e, row=r: self.navigate_keyboard(e, row, "rate"))

            # --- FORMULA EVALUATION TRIGGERS ---
            qty.bind("<FocusOut>", lambda e, row=r: self.evaluate_and_update_row(row))
            rate.bind("<FocusOut>", lambda e, row=r: self.evaluate_and_update_row(row))

        # --- GRAND TOTAL FOOTER BLOCK ---
        self.total_row_frame = ctk.CTkFrame(self.sheet_container, fg_color="#1a1a1a", height=35, corner_radius=4)
        self.total_row_frame.grid(row=self.total_rows + 1, column=0, columnspan=5, padx=5, pady=15, sticky="ew")
        
        self.grand_total_label = ctk.CTkLabel(
            self.total_row_frame, 
            text="Grand Sheet Total: $0.00", 
            font=ctk.CTkFont(weight="bold", size=13),
            text_color="#228B22"
        )
        self.grand_total_label.pack(side="right", padx=20, pady=5)

        self.load_grid_from_db()

    def evaluate_expression(self, text):
        cleaned = text.strip()
        if not cleaned:
            return 0.0
        if cleaned.startswith("="):
            cleaned = cleaned[1:]
        if not all(char in "0123456789+-*/.()" for char in cleaned):
            try: return float(cleaned)
            except ValueError: return 0.0
        try:
            result = eval(cleaned, {"__builtins__": None}, {})
            return float(result)
        except Exception:
            return 0.0

    def calculate_grand_total(self):
        """Scans all displayed line items and aggregates the sheet matrix total"""
        grand_total = 0.0
        for r in range(1, self.total_rows + 1):
            qty_val = self.evaluate_expression(self.widgets[r]["qty"].get())
            rate_val = self.evaluate_expression(self.widgets[r]["rate"].get())
            grand_total += (qty_val * rate_val)
        self.grand_total_label.configure(text=f"Grand Sheet Total: ${grand_total:,.2f}")

    def evaluate_and_update_row(self, row):
        qty_box = self.widgets[row]["qty"]
        rate_box = self.widgets[row]["rate"]

        qty_val = self.evaluate_expression(qty_box.get())
        rate_val = self.evaluate_expression(rate_box.get())

        if qty_box.get().strip().startswith("="):
            qty_box.delete(0, 'end')
            qty_box.insert(0, str(int(qty_val) if qty_val.is_integer() else qty_val))
            
        if rate_box.get().strip().startswith("="):
            rate_box.delete(0, 'end')
            rate_box.insert(0, f"{rate_val:.2f}")

        line_total = qty_val * rate_val
        self.widgets[row]["total"].configure(text=f"${line_total:,.2f}")
        
        # Recalculate whole sheet aggregate on any value edit event
        self.calculate_grand_total()

    def navigate_keyboard(self, event, row, field):
        if event.keysym in ["Return", "Down", "Up", "Tab", "Right", "Left"]:
            self.evaluate_and_update_row(row)

        fields_order = ["desc", "qty", "rate"]
        col_idx = fields_order.index(field)
        
        target_row = row
        target_field = field

        if event.keysym in ["Return", "Down"]:
            if row < self.total_rows:
                target_row = row + 1
        elif event.keysym == "Up":
            if row > 1:
                target_row = row - 1
        elif event.keysym in ["Tab", "Right"]:
            if col_idx < len(fields_order) - 1:
                target_field = fields_order[col_idx + 1]
                if event.keysym == "Tab":
                    self.widgets[target_row][target_field].focus()
                    return "break"
            elif row < self.total_rows:
                target_row = row + 1
                target_field = fields_order[0]
        elif event.keysym == "Left":
            if col_idx > 0:
                target_field = fields_order[col_idx - 1]

        if target_row != row or target_field != field:
            self.widgets[target_row][target_field].focus()
            if event.keysym == "Return":
                return "break"

    def save_grid_to_db(self):
        pid = self.master_app.current_profile_id
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM grid_items WHERE profile_id = ?", (pid,))
            for r in range(1, self.total_rows + 1):
                desc_text = self.widgets[r]["desc"].get().strip()
                qty_raw = self.widgets[r]["qty"].get().strip()
                rate_raw = self.widgets[r]["rate"].get().strip()

                if desc_text or qty_raw or rate_raw:
                    qty_val = self.evaluate_expression(qty_raw)
                    rate_val = self.evaluate_expression(rate_raw)
                    cursor.execute("""
                        INSERT INTO grid_items (profile_id, row_index, description, quantity, rate)
                        VALUES (?, ?, ?, ?, ?)
                    """, (pid, r, desc_text, qty_val, rate_val))
            conn.commit()
        except Exception as e:
            print(f"Spreadsheet save error: {e}")
        finally:
            conn.close()
        self.load_grid_from_db()

    def load_grid_from_db(self):
        pid = self.master_app.current_profile_id
        
        for r in range(1, self.total_rows + 1):
            self.widgets[r]["desc"].delete(0, 'end')
            self.widgets[r]["desc"]._activate_placeholder()  # <-- FIXED: Using proper customtkinter attribute token
            
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
            
        # Run a global calculation check right after database numbers pour in
        self.calculate_grand_total()