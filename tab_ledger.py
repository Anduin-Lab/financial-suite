import customtkinter as ctk
import sqlite3
import pandas as pd
from database import DATABASE_NAME

class GeneralLedgerTab(ctk.CTkFrame):
    def __init__(self, master, master_app):
        super().__init__(master, fg_color="transparent")
        self.master_app = master_app

        # --- CONTROL MENU BAR ---
        control_bar = ctk.CTkFrame(self, fg_color="transparent")
        control_bar.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(control_bar, text="📜 Historical Transaction Journal", font=ctk.CTkFont(weight="bold", size=15)).pack(side="left", padx=5)
        ctk.CTkButton(control_bar, text="🔄 Refresh Ledger", command=self.reload_ledger, width=120).pack(side="right", padx=5)

        # --- DATA CANVAS MATRIX ---
        self.table_container = ctk.CTkScrollableFrame(self)
        self.table_container.pack(pady=10, padx=10, fill="both", expand=True)

        # Build column header structures
        self.headers = ["Transaction Date", "Memo / Narrative", "Target Account", "Amount ($)"]
        self.reload_ledger()

    def reload_ledger(self):
        # 🔥 FORCED SYNC UPGRADE: Re-prime core app data cache completely when manually refreshing
        self.master_app.invalidate_and_prime_cache()

        # Clear out previous widgets
        for widget in self.table_container.winfo_children():
            widget.destroy()

        # Render Table Headers
        for col_idx, text in enumerate(self.headers):
            lbl = ctk.CTkLabel(self.table_container, text=text, font=ctk.CTkFont(weight="bold"), width=180, anchor="w" if col_idx < 3 else "e")
            lbl.grid(row=0, column=col_idx, padx=15, pady=8, sticky="ew")

        conn = sqlite3.connect(DATABASE_NAME)
        
        try:
            # Read directly from central fast runtime storage cache array
            df = self.master_app.get_cached_data("ledger")
            
            if df.empty:
                empty_lbl = ctk.CTkLabel(self.table_container, text="No transactions logged yet for this portfolio profile context.", font=ctk.CTkFont(slant="italic"), text_color="gray")
                empty_lbl.grid(row=1, column=0, columnspan=4, pady=30, padx=20)
                return

            for row_idx, row in df.iterrows():
                grid_row = row_idx + 1
                
                amt = row['amount']
                amt_str = f"${amt:,.2f}" if amt >= 0 else f"-${abs(amt):,.2f}"
                
                # --- TRAFFIC LIGHT COLORING ASSIGNMENTS ---
                if amt >= 0:
                    text_color = "#40ff40"   # Pastel green text
                    bg_row_color = "#122416" # Muted green background row block
                else:
                    text_color = "#ff6b6b"   # Soft warning red text
                    bg_row_color = "#2b1616" # Muted red background row block

                # Create an entry row background container strip to give the structural "traffic light grid" effect
                row_strip = ctk.CTkFrame(self.table_container, fg_color=bg_row_color, height=28, corner_radius=4)
                row_strip.grid(row=grid_row, column=0, columnspan=4, padx=5, pady=2, sticky="ew")
                row_strip.grid_columnconfigure((0,1,2,3), weight=1)

                # Generate clean visual grid items attached inside the background container frame
                ctk.CTkLabel(row_strip, text=str(row['record_date']), width=180, anchor="w").grid(row=0, column=0, padx=10, pady=2, sticky="w")
                ctk.CTkLabel(row_strip, text=str(row['description']), width=180, anchor="w").grid(row=0, column=1, padx=10, pady=2, sticky="w")
                ctk.CTkLabel(row_strip, text=str(row['account_name']), width=180, anchor="w").grid(row=0, column=2, padx=10, pady=2, sticky="w")
                ctk.CTkLabel(row_strip, text=amt_str, font=ctk.CTkFont(family="Courier"), text_color=text_color, width=180, anchor="e").grid(row=0, column=3, padx=10, pady=2, sticky="e")

        except Exception as e:
            err_lbl = ctk.CTkLabel(self.table_container, text=f"Ledger pipeline reading error: {e}", text_color="red")
            err_lbl.grid(row=1, column=0, columnspan=4, pady=20)
        finally:
            conn.close()