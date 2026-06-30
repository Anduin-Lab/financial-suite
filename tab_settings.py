import customtkinter as ctk

class SystemSettingsTab(ctk.CTkFrame):
    def __init__(self, master, master_app):
        super().__init__(master, fg_color="transparent")
        self.master_app = master_app
        
        self.settings_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.settings_frame.pack(pady=30, padx=40, fill="both", expand=True)
        
        create_box = ctk.CTkFrame(self.settings_frame)
        create_box.pack(fill="x", pady=10, ipady=15, ipadx=15)
        
        ctk.CTkLabel(create_box, text="Add New Business Profile:", font=ctk.CTkFont(weight="bold", size=14)).pack(anchor="w", pady=2, padx=15)
        self.new_profile_entry = ctk.CTkEntry(create_box, placeholder_text="e.g., Global Assets LLC", width=300)
        self.new_profile_entry.pack(side="left", pady=5, padx=15)
        
        ctk.CTkButton(create_box, text="Create Profile", command=self.master_app.add_profile, width=120).pack(side="left", pady=5, padx=5)
        
        delete_box = ctk.CTkFrame(self.settings_frame)
        delete_box.pack(fill="x", pady=10, ipady=15, ipadx=15)
        
        ctk.CTkLabel(delete_box, text="Delete Business Profile:", text_color="#ff6b6b", font=ctk.CTkFont(weight="bold", size=14)).pack(anchor="w", pady=2, padx=15)
        ctk.CTkLabel(delete_box, text="Warning: This permanently purges all data and accounts associated with this profile.", text_color="gray", font=ctk.CTkFont(size=11)).pack(anchor="w", pady=2, padx=15)
        
        self.delete_menu = ctk.CTkOptionMenu(delete_box, values=self.master_app.get_profile_names(), width=300)
        self.delete_menu.pack(side="left", pady=10, padx=15)
        
        ctk.CTkButton(delete_box, text="Delete Profile", fg_color="#8B0000", hover_color="#550000", command=self.master_app.delete_profile, width=120).pack(side="left", pady=10, padx=5)
