import customtkinter as ctk

class LogTransactionTab(ctk.CTkFrame):
    def __init__(self, master, master_app):
        super().__init__(master, fg_color="transparent")
        self.master_app = master_app  # Reference to main core app
        
        # Grid frame setup
        self.entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.entry_frame.pack(pady=20, padx=20, fill="both")
        
        ctk.CTkLabel(self.entry_frame, text="Counterparty Name:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.desc_entry = ctk.CTkEntry(self.entry_frame, placeholder_text="e.g., Supplier Invoice", width=250)
        self.desc_entry.grid(row=0, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(self.entry_frame, text="Inbound Account:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.acct1_menu = ctk.CTkOptionMenu(self.entry_frame, values=self.master_app.account_options, width=250)
        self.acct1_menu.grid(row=1, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(self.entry_frame, text="Outbound Account:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.acct2_menu = ctk.CTkOptionMenu(self.entry_frame, values=self.master_app.account_options, width=250)
        self.acct2_menu.grid(row=2, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(self.entry_frame, text="Value Amount ($):").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.amount_entry = ctk.CTkEntry(self.entry_frame, placeholder_text="0.00", width=120)
        self.amount_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        
        self.status_label = ctk.CTkLabel(self, text="Ready to write securely.", text_color="gray")
        self.status_label.pack(pady=10)
        
        ctk.CTkButton(self, text="Commit Entry", command=self.master_app.execute_entry).pack(pady=5)