import customtkinter as ctk
from app.ui.project_tab import ProjectTab
from app.ui.mapping_tab import MappingTab

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SMW Credits Creator")
        self.geometry("800x600")

        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create Tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Add Tabs
        self.tabview.add("Project")
        self.tabview.add("Mapping")

        # Initialize Tabs
        self.project_tab = ProjectTab(self.tabview.tab("Project"))
        self.mapping_tab = MappingTab(self.tabview.tab("Mapping"))
