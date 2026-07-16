import customtkinter as ctk
from datetime import datetime
import config.designs as designs

class LogTransactionTab(ctk.CTkFrame):
    def __init__(self, parent, master_app=None):
        super().__init__(parent, fg_color="transparent")
        self.master_app = master_app  
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        self.title_label = ctk.CTkLabel(
            self, 
            text="Log Financial Transaction", 
            font=designs.FONT_HUD_TITLE
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        self.mode_toggle = ctk.CTkSegmentedButton(
            self,
            values=["Smart Guide", "Advanced Ledger"],
            command=self.toggle_input_mode,
            selected_color=designs.COLOR_ACCENT,
            selected_hover_color=designs.COLOR_ACCENT_HOVER
        )
        self.mode_toggle.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.mode_toggle.set("Smart Guide")
        
        self.smart_frame = ctk.CTkFrame(self, fg_color=designs.BG_PANEL)
        self.advanced_frame = ctk.CTkFrame(self, fg_color=designs.BG_PANEL)
        
        self.build_smart_guide()
        self.build_advanced_ledger()
        
        self.smart_frame.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")

    def toggle_input_mode(self, mode):
        """Toggles view layout visibility profiles dynamically"""
        if mode == "Smart Guide":
            self.advanced_frame.grid_forget()
            self.smart_frame.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")
        else:
            self.smart_frame.grid_forget()
            self.advanced_frame.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")

    def build_smart_guide(self):
        """Simplified natural language framework mapping directly to core variables"""
        self.smart_frame.grid_columnconfigure((0, 1), weight=1)
        
        lbl_type = ctk.CTkLabel(self.smart_frame, text="What kind of transaction is this?", font=designs.FONT_HUD_REGULAR)
        lbl_type.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        self.smart_type = ctk.CTkComboBox(
            self.smart_frame, 
            values=["💸 Expense / Vendor Payment", "💰 Invoice Revenue / Asset Increase"],
            command=self.auto_map_smart_accounts
        )
        self.smart_type.grid(row=1, column=0, columnspan=2, padx=20, pady=5, sticky="ew")

        self.lbl_inbound = ctk.CTkLabel(self.smart_frame, text="Target (Inbound Account):", font=designs.FONT_HUD_REGULAR)
        self.lbl_inbound.grid(row=2, column=0, padx=20, pady=(15, 2), sticky="w")
        
        self.smart_inbound = ctk.CTkOptionMenu(self.smart_frame, values=self.master_app.account_options if self.master_app else ["Default"], width=250)
        self.smart_inbound.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        self.lbl_outbound = ctk.CTkLabel(self.smart_frame, text="Source (Outbound Account):", font=designs.FONT_HUD_REGULAR)
        self.lbl_outbound.grid(row=2, column=1, padx=20, pady=(15, 2), sticky="w")
        
        self.smart_outbound = ctk.CTkOptionMenu(self.smart_frame, values=self.master_app.account_options if self.master_app else ["Default"], width=250)
        self.smart_outbound.grid(row=3, column=1, padx=20, pady=5, sticky="ew")

        lbl_party = ctk.CTkLabel(self.smart_frame, text="Counterparty Name / Description:", font=designs.FONT_HUD_REGULAR)
        lbl_party.grid(row=4, column=0, padx=20, pady=(15, 2), sticky="w")
        
        self.smart_desc = ctk.CTkEntry(self.smart_frame, placeholder_text="e.g., Supplier Invoice")
        self.smart_desc.grid(row=5, column=0, padx=20, pady=5, sticky="ew")

        lbl_amt = ctk.CTkLabel(self.smart_frame, text="Value Amount ($):", font=designs.FONT_HUD_REGULAR)
        lbl_amt.grid(row=4, column=1, padx=20, pady=(15, 2), sticky="w")
        
        self.smart_amt = ctk.CTkEntry(self.smart_frame, placeholder_text="0.00")
        self.smart_amt.grid(row=5, column=1, padx=20, pady=5, sticky="ew")

        btn_smart_submit = ctk.CTkButton(
            self.smart_frame, 
            text="Commit Smart Entry", 
            fg_color=designs.COLOR_ACCENT,
            hover_color=designs.COLOR_ACCENT_HOVER,
            command=self.execute_smart_pipeline
        )
        btn_smart_submit.grid(row=6, column=0, columnspan=2, padx=20, pady=30, sticky="ew")

    def auto_map_smart_accounts(self, selection):
        if "Expense" in selection:
            self.lbl_inbound.configure(text="Where did the value go? (Expense Category):")
            self.lbl_outbound.configure(text="Where did the money come from? (Payment Asset):")
        else:
            self.lbl_inbound.configure(text="Where did the money land? (Receiving Asset):")
            self.lbl_outbound.configure(text="What generated this income? (Revenue Stream):")

    def build_advanced_ledger(self):
        self.advanced_frame.grid_columnconfigure((0, 1), weight=1)
        
        for r in range(8):
            self.advanced_frame.grid_rowconfigure(r, weight=0)
        self.advanced_frame.grid_rowconfigure(8, weight=1)
        
        lbl_date = ctk.CTkLabel(self.advanced_frame, text="Transaction Date:", font=designs.FONT_HUD_REGULAR)
        lbl_date.grid(row=0, column=0, padx=20, pady=(15, 2), sticky="w")
        self.date_entry = ctk.CTkEntry(self.advanced_frame, placeholder_text="YYYY-MM-DD")
        self.date_entry.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        lbl_ref = ctk.CTkLabel(self.advanced_frame, text="Reference / Invoice ID:", font=designs.FONT_HUD_REGULAR)
        lbl_ref.grid(row=0, column=1, padx=20, pady=(15, 2), sticky="w")
        self.ref_entry = ctk.CTkEntry(self.advanced_frame, placeholder_text="e.g., INV-2026-001")
        self.ref_entry.grid(row=1, column=1, padx=20, pady=5, sticky="ew")

        ctk.CTkLabel(self.advanced_frame, text="Counterparty Name:", font=designs.FONT_HUD_REGULAR).grid(row=2, column=0, padx=20, pady=(15, 2), sticky="w")
        self.desc_entry = ctk.CTkEntry(self.advanced_frame, placeholder_text="e.g., Supplier Invoice")
        self.desc_entry.grid(row=3, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
        
        ctk.CTkLabel(self.advanced_frame, text="Inbound Account (Debit):", font=designs.FONT_HUD_REGULAR).grid(row=4, column=0, padx=20, pady=(15, 2), sticky="w")
        self.acct1_menu = ctk.CTkOptionMenu(self.advanced_frame, values=self.master_app.account_options if self.master_app else ["Default"])
        self.acct1_menu.grid(row=5, column=0, padx=20, pady=5, sticky="ew")
        
        ctk.CTkLabel(self.advanced_frame, text="Outbound Account (Credit):", font=designs.FONT_HUD_REGULAR).grid(row=4, column=1, padx=20, pady=(15, 2), sticky="w")
        self.acct2_menu = ctk.CTkOptionMenu(self.advanced_frame, values=self.master_app.account_options if self.master_app else ["Default"])
        self.acct2_menu.grid(row=5, column=1, padx=20, pady=5, sticky="ew")
        
        ctk.CTkLabel(self.advanced_frame, text="Value Amount ($):", font=designs.FONT_HUD_REGULAR).grid(row=6, column=0, padx=20, pady=(15, 2), sticky="w")
        self.amount_entry = ctk.CTkEntry(self.advanced_frame, placeholder_text="0.00", width=200)
        self.amount_entry.grid(row=7, column=0, padx=20, pady=5, sticky="w")
        
        self.status_label = ctk.CTkLabel(
            self.advanced_frame, 
            text="Ready to save transaction.", 
            text_color="gray", 
            font=designs.FONT_HUD_REGULAR
        )
        self.status_label.grid(row=7, column=1, padx=20, pady=5, sticky="e")
        
        self.amount_entry.bind("<KeyRelease>", self.realtime_balancing_engine)

        self.btn_commit = ctk.CTkButton(
            self.advanced_frame, 
            text="Commit Entry", 
            fg_color=designs.COLOR_ACCENT,
            hover_color=designs.COLOR_ACCENT_HOVER,
            command=self.execute_advanced_pipeline
        )
        self.btn_commit.grid(row=8, column=0, columnspan=2, padx=20, pady=25, sticky="ew")

    def realtime_balancing_engine(self, event=None):
        raw_val = self.amount_entry.get().strip()
        if not raw_val:
            self.status_label.configure(text="Ready to save transaction.", text_color="gray")
            self.btn_commit.configure(state="normal")
            return
            
        try:
            val = float(raw_val)
            if val <= 0:
                self.status_label.configure(text="Error: Value must be greater than 0", text_color="#ff3333")
                self.btn_commit.configure(state="disabled")
            else:
                self.status_label.configure(text="Ledger Status: Balanced and Validated", text_color="#39ff14")
                self.btn_commit.configure(state="normal")
        except ValueError:
            self.status_label.configure(text="Error: Invalid Number", text_color="#ff3333")
            self.btn_commit.configure(state="disabled")

    def execute_advanced_pipeline(self):
        ref_id = self.ref_entry.get().strip()
        tx_date = self.date_entry.get().strip()
        base_desc = self.desc_entry.get().strip()
        
        meta_stamp = f"[{tx_date}] Ref:{ref_id if ref_id else 'N/A'} | {base_desc}"
        
        self.desc_entry.delete(0, 'end')
        self.desc_entry.insert(0, meta_stamp)
        
        if self.master_app:
            self.master_app.execute_entry()
            
        self.ref_entry.delete(0, 'end')
        self.desc_entry.delete(0, 'end')
        self.amount_entry.delete(0, 'end')
        self.date_entry.delete(0, 'end')
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.status_label.configure(text="Transaction saved successfully.", text_color="#39ff14")

    def execute_smart_pipeline(self):
        """Passes variables into working advanced targets inside hidden system flow"""
        self.desc_entry.delete(0, 'end')
        self.desc_entry.insert(0, f"[Smart Entry] {self.smart_desc.get()}")
        
        self.amount_entry.delete(0, 'end')
        self.amount_entry.insert(0, self.smart_amt.get())
        
        self.acct1_menu.set(self.smart_inbound.get())
        self.acct2_menu.set(self.smart_outbound.get())
        
        if self.master_app:
            self.master_app.execute_entry()
            
        self.smart_desc.delete(0, 'end')
        self.smart_amt.delete(0, 'end')
