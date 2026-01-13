import customtkinter as ctk
from app.ui.mapping_tab import MappingTab
from app.ui.credits_tab import CreditsTab
import os
import sys
import logging

VERSION = "1.0.0"

logger = logging.getLogger(__name__)

class MainWindow(ctk.CTk):
    def __init__(self):
        logger.info("MainWindow: initializing super()")
        super().__init__()
        
        logger.info("MainWindow: setting title/geometry")
        self.title(f"SMW Credits Creator v{VERSION} - by Saphros © 2026")
        self.geometry("940x700")
        
        # Create Tabs (2 tabs now: Credits and Mapping)
        logger.info("MainWindow: Creating Tabview")
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_credits = self.tab_view.add("Credits")
        self.tab_mapping = self.tab_view.add("Mapping")
        
        # Init logic
        logger.info("MainWindow: Initializing MappingTab")
        self.mapping_ui = MappingTab(self.tab_mapping)
        
        # Credits tab now includes project selection
        logger.info("MainWindow: Initializing CreditsTab")
        self.credits_ui = CreditsTab(
            self.tab_credits, 
            mapper=self.mapping_ui.mapper
        )
        logger.info("MainWindow: Initialization finished")

        # Icon Setup - Defer to avoid hanging
        self.after(200, self.set_app_icon)

    def set_app_icon(self):
        logger.info("MainWindow: setting icon (deferred)")
        try:
            icon_path = self.resource_path("icon.ico")
            logger.info(f"Icon path resolved to: {icon_path}")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
                logger.info("Icon set successfully.")
            else:
                 logger.warning("Icon file not found at path.")
        except Exception as e:
            logger.error(f"Warning: Could not set icon: {e}")

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)
