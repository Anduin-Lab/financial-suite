import customtkinter as ctk

class ReportsDashboardTab(ctk.CTkFrame):
    def __init__(self, master, master_app):
        super().__init__(master, fg_color="transparent")
        self.master_app = master_app
        
        self.bi_box = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Courier", size=13))
        self.bi_box.pack(padx=10, pady=10, fill="both", expand=True)