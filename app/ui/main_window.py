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
        self.geometry("940x740")
        
        # Create Tabs (3 tabs now: Credits, Mapping, Export)
        logger.info("MainWindow: Creating Tabview")
        self.tab_view = ctk.CTkTabview(
            self,
            segmented_button_fg_color="#1a1a2e",
            segmented_button_selected_color="#1f6aa5",
            segmented_button_selected_hover_color="#1a5889",
            segmented_button_unselected_color="#2d2d3d",
            segmented_button_unselected_hover_color="#3a3a4e",
            text_color="#ffffff",
            fg_color="#242424",
        )
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)
        # Make tab buttons stretch full width
        self.after(0, self._make_tabs_full_width)
        
        self.tab_credits = self.tab_view.add("Credits")
        self.tab_mapping = self.tab_view.add("Mapping")
        
        # Init logic
        logger.info("MainWindow: Initializing MappingTab")
        self.mapping_ui = MappingTab(self.tab_mapping)
        
        # Credits tab now includes project selection
        logger.info("MainWindow: Initializing CreditsTab")
        self.credits_ui = CreditsTab(
            self.tab_credits, 
            mapper=self.mapping_ui.mapper,
            on_mapping_change=self.mapping_ui.refresh_from_external
        )
        
        logger.info("MainWindow: Initialization finished")

        # Icon Setup - Defer to avoid hanging
        self.after(200, self.set_app_icon)

    def _make_tabs_full_width(self):
        try:
            sb = self.tab_view._segmented_button
            sb.master.grid_columnconfigure(0, weight=1)
            sb.grid_configure(sticky="ew", padx=4)
            sb.configure(height=36)
        except Exception:
            pass

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
