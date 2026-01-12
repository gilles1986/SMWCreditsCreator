import customtkinter as ctk
from app.ui.mapping_tab import MappingTab
from app.ui.credits_tab import CreditsTab

VERSION = "1.0.0"

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title(f"SMW Credits Creator v{VERSION} - by Saphros © 2026")
        self.geometry("900x700")
        
        # Create Tabs (2 tabs now: Credits and Mapping)
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_credits = self.tab_view.add("Credits")
        self.tab_mapping = self.tab_view.add("Mapping")
        
        # Init logic
        self.mapping_ui = MappingTab(self.tab_mapping)
        
        # Credits tab now includes project selection
        self.credits_ui = CreditsTab(
            self.tab_credits, 
            mapper=self.mapping_ui.mapper
        )
