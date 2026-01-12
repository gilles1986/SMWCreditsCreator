import customtkinter as ctk
from tkinter import filedialog
import threading
import os # Added
from app.core.validator import Validator
from app.core.config_manager import ConfigManager
from app.core.app_config import AppConfig # Added
from app.ui.theme import Theme

class ProjectTab:
    def __init__(self, master):
        self.master = master
        self.project_path = None
        self.rhr_version = None
        self.config = AppConfig() # Added
        
        # UI Setup
        self.setup_ui() # Added
        
        # Load Last Project
        last_proj = self.config.get("last_project") # Added
        if last_proj and os.path.exists(last_proj): # Added
            self.load_project(last_proj) # Added

    def setup_ui(self): # Added method
        # Grid layout
        self.master.grid_columnconfigure(0, weight=1)
        
        # 1. Folder Selection
        self.sel_frame = ctk.CTkFrame(self.master) # Changed from path_frame
        self.sel_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew") # Changed row and pady
        self.sel_frame.grid_columnconfigure(0, weight=1)
        
        self.lbl_path = ctk.CTkLabel(self.sel_frame, text="No Project Selected", font=Theme.FONT_BOLD, text_color=Theme.TEXT_ERROR) # Changed from path_entry and label
        self.lbl_path.grid(row=0, column=0, padx=10, pady=10, sticky="w") # Changed from path_entry grid
        
        self.btn_browse = ctk.CTkButton(self.sel_frame, text="Select RHR Folder", command=self.browse_folder, fg_color=Theme.BTN_PRIMARY, text_color=Theme.BTN_PRIMARY_TEXT) # Changed from browse_button
        self.btn_browse.grid(row=0, column=1, padx=10, pady=10) # Changed from browse_button grid

        # Status Area
        self.status_frame = ctk.CTkFrame(self.master)
        self.status_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew") # Changed row from 2 to 1
        self.status_frame.grid_columnconfigure(1, weight=1)

        self.lbl_valid = ctk.CTkLabel(self.status_frame, text="Project Status:", font=Theme.FONT_BOLD)
        self.lbl_valid.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.status_valid_val = ctk.CTkLabel(self.status_frame, text="N/A", text_color=Theme.TEXT_STATUS_NEUTRAL)
        self.status_valid_val.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.lbl_version = ctk.CTkLabel(self.status_frame, text="RHR Version:", font=Theme.FONT_BOLD)
        self.lbl_version.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.status_version_val = ctk.CTkLabel(self.status_frame, text="N/A", text_color=Theme.TEXT_STATUS_NEUTRAL)
        self.status_version_val.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.lbl_config = ctk.CTkLabel(self.status_frame, text="Config Status:", font=Theme.FONT_BOLD)
        self.lbl_config.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.status_config_val = ctk.CTkLabel(self.status_frame, text="N/A", text_color=Theme.TEXT_STATUS_NEUTRAL)
        self.status_config_val.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        # Action Buttons
        self.fix_button = ctk.CTkButton(self.master, text="Fix exports.toml", state="disabled", command=self.fix_config, fg_color=Theme.BTN_WARNING, text_color=Theme.BTN_WARNING_TEXT)
        # self.fix_button.grid(row=3, column=0, padx=20, pady=10, sticky="w") # Hidden by default


    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.load_project(folder)
            
    def load_project(self, folder):
        self.project_path = folder
        self.lbl_path.configure(text=folder, text_color=Theme.TEXT_NORMAL)
        self.validate_project()
        # Save to config
        self.config.set("last_project", folder)

    def validate_project(self):
        if not self.project_path:
            return

        # 1. Validate RHR Project
        is_valid, msg = Validator.validate_folder(self.project_path)
        self.status_valid_val.configure(text=msg, text_color=Theme.TEXT_STATUS_SUCCESS if is_valid else Theme.TEXT_STATUS_ERROR)
        
        if not is_valid:
            self.rhr_version = None
            self.status_version_val.configure(text="N/A", text_color=Theme.TEXT_STATUS_NEUTRAL)
            self.status_config_val.configure(text="N/A", text_color=Theme.TEXT_STATUS_NEUTRAL)
            self.fix_button.grid_forget() # Hide
            return

        # 2. Get Version
        self.rhr_version = Validator.get_rhr_version(self.project_path)
        self.status_version_val.configure(text=self.rhr_version, text_color=Theme.TEXT_STATUS_INFO)

        # 3. Check Config
        self.check_config()

    def check_config(self):
        if not self.project_path or not self.rhr_version:
            return

        is_good, msg = ConfigManager.check_exports_toml(self.project_path, self.rhr_version)
        self.status_config_val.configure(text=msg, text_color=Theme.TEXT_STATUS_SUCCESS if is_good else Theme.TEXT_STATUS_ERROR)

        if not is_good and "Found" not in msg and "not found" not in msg: # Allow fix if file exists but invalid? 
            # Actually if file missing, we can probably not fix it easily without knowning where to put it or creating default.
            # But specific error "use_text_map16_format is False" is fixable.
            if "False" in msg or "not found" in msg: 
                 self.fix_button.grid(row=3, column=0, padx=20, pady=10, sticky="w") # Show
                 self.fix_button.configure(state="normal")
            else:
                 self.fix_button.grid_forget() # Hide
        else:
            self.fix_button.grid_forget() # Hide

    def fix_config(self):
        if not self.project_path or not self.rhr_version:
            return
            
        success, msg = ConfigManager.fix_exports_toml(self.project_path, self.rhr_version)
        if success:
            self.check_config() # Re-check
        else:
            self.status_config_val.configure(text=f"Fix Failed: {msg}", text_color=Theme.TEXT_STATUS_ERROR)
