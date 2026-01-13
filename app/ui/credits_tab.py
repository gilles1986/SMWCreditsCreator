import customtkinter as ctk
from tkinter import filedialog
from app.core.credits_parser import CreditsParser
from app.core.map16_handler import Map16Generator
from app.ui.theme import Theme
from app.core.app_config import AppConfig
from app.core.validator import Validator
from app.core.config_manager import ConfigManager
import os

class CreditsTab:
    def __init__(self, master, mapper):
        self.master = master
        self.mapper = mapper
        self.credits_path = None
        self.project_path = None
        self.rhr_version = None
        self.config = AppConfig()
        self.log_history = ["Ready."] # Persistent log history

        # Main Grid Config
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(1, weight=1) # Content area expands
        
        # --- 1. Project Bar (Persistent Top) ---
        self.bar_frame = ctk.CTkFrame(self.master, height=50, fg_color=Theme.BG_COLOR_2) # Darker header
        self.bar_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.bar_frame.grid_columnconfigure(1, weight=1)
        
        self.lbl_proj_title = ctk.CTkLabel(self.bar_frame, text="Active Project:", font=Theme.FONT_BOLD, text_color=Theme.TEXT_DIM)
        self.lbl_proj_title.grid(row=0, column=0, padx=(20, 10), pady=10)
        
        self.lbl_proj_path = ctk.CTkLabel(self.bar_frame, text="No Project Selected", text_color=Theme.TEXT_NORMAL)
        self.lbl_proj_path.grid(row=0, column=1, padx=0, pady=10, sticky="w")
        
        self.btn_change = ctk.CTkButton(self.bar_frame, text="Change Folder", width=100, command=self.browse_project, fg_color=Theme.BTN_PRIMARY, text_color=Theme.BTN_PRIMARY_TEXT)
        self.btn_change.grid(row=0, column=2, padx=10, pady=10)
        
        self.btn_unload = ctk.CTkButton(self.bar_frame, text="x", width=30, command=self.unload_project, fg_color=Theme.BTN_WARNING, hover_color=Theme.BTN_WARNING_HOVER, text_color=Theme.BTN_WARNING_TEXT, state="disabled")
        self.btn_unload.grid(row=0, column=3, padx=(0, 20), pady=10)

        # --- 2. Central View Container ---
        self.view_container = ctk.CTkFrame(self.master, fg_color="transparent")
        self.view_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.view_container.grid_columnconfigure(0, weight=1)
        self.view_container.grid_rowconfigure(0, weight=1)
        
        # Load last project
        last_proj = self.config.get("last_project")
        if last_proj and os.path.exists(last_proj):
            self.load_project(last_proj)
        else:
            self.show_view_no_project()
    # --- Project Management ---

    def browse_project(self):
        # Open directory dialog
        folder = filedialog.askdirectory(title="Select Project Folder")
        if folder:
            self.load_project(folder)

    def load_project(self, path):
        # 1. Detect Version
        version = self.detect_version(path)
        if not version:
             self.show_view_invalid_project("Could not detect a valid RHR or Callisto project structure.\n(Expected 'buildtool' or 'tools/Callisto' folder)")
             return

        self.project_path = path
        self.rhr_version = version

        # 2. Check Config
        ok, msg = ConfigManager.check_exports_toml(path, version)
        if not ok:
             self.show_view_setup_needed(msg)
             return

        # 3. Success
        self.config.set("last_project", path)
        self.lbl_proj_path.configure(text=path)
        self.btn_change.configure(text="Change")
        self.btn_unload.configure(state="normal")
        
        self.show_view_main()
        self.log(f"Project loaded: {path} (v{version[0]}.{version[1]})")

    def detect_version(self, path):
        # Check high version first
        if os.path.exists(os.path.join(path, "tools", "Callisto", "callisto.exe")):
             return (5, 13) # or newer
        elif os.path.exists(os.path.join(path, "buildtool", "callisto.exe")):
             return (5, 10)
        elif os.path.exists(os.path.join(path, "buildtool", "project.toml")):
             # Old RHR
             return (5, 0)
        return None

    def unload_project(self):
        self.project_path = None
        self.rhr_version = None
        self.config.set("last_project", "")
        self.lbl_proj_path.configure(text="No Project Selected")
        self.btn_change.configure(text="Change Folder")
        self.btn_unload.configure(state="disabled")
        self.show_view_no_project()
        
    def fix_config(self):
        if not self.project_path or not self.rhr_version:
             return
        
        ok, msg = ConfigManager.fix_exports_toml(self.project_path, self.rhr_version)
        if ok:
             self.log("Configuration fixed.")
             self.load_project(self.project_path) # Reload
        else:
             from tkinter import messagebox
             messagebox.showerror("Error", f"Failed to fix config: {msg}")

    def clear_view(self):
        for widget in self.view_container.winfo_children():
            widget.destroy()

    def show_view_no_project(self):
        self.clear_view()
        
        # Center Content
        center_frame = ctk.CTkFrame(self.view_container, fg_color="transparent")
        center_frame.grid(row=0, column=0)
        
        ctk.CTkLabel(center_frame, text="No Project Loaded", font=("Arial", 20, "bold"), text_color=Theme.TEXT_DIM).pack(pady=10)
        ctk.CTkLabel(center_frame, text="Please select a valid RHR project folder to begin.", text_color=Theme.TEXT_DIM).pack(pady=5)
        ctk.CTkButton(center_frame, text="Select RHR Folder", command=self.browse_project, width=200, height=40, font=Theme.FONT_BOLD).pack(pady=20)

    def show_view_setup_needed(self, check_msg):
        self.clear_view()
        
        # Warning Card
        card = ctk.CTkFrame(self.view_container, border_width=2, border_color=Theme.BTN_WARNING)
        card.grid(row=0, column=0)
        
        config_path = ConfigManager.get_config_path(self.project_path, self.rhr_version)
        config_file = os.path.basename(config_path) if config_path else "Config file"

        ctk.CTkLabel(card, text="⚠️ Configuration Update Required", font=("Arial", 16, "bold"), text_color=Theme.BTN_WARNING).pack(pady=(20, 10), padx=40)
        ctk.CTkLabel(card, text=f"{config_file} needs to be modified to make this tool work.", text_color=Theme.TEXT_NORMAL, font=("Arial", 12)).pack(pady=10, padx=20)
        
        ctk.CTkButton(card, text="Fix Configuration", command=self.fix_config, fg_color=Theme.BTN_WARNING, hover_color=Theme.BTN_WARNING_HOVER, text_color=Theme.BTN_WARNING_TEXT, width=200, height=35).pack(pady=20)

    def show_view_invalid_project(self, message):
        self.clear_view()
        
        # Error Card
        card = ctk.CTkFrame(self.view_container, border_width=2, border_color=Theme.BTN_WARNING, width=400) # Explicit width
        card.grid(row=0, column=0)
        
        ctk.CTkLabel(card, text="⚠️ Invalid Project", font=("Arial", 16, "bold"), text_color=Theme.BTN_WARNING).pack(pady=(20, 10), padx=40)
        
        # Wrapped Message
        lbl_msg = ctk.CTkLabel(card, text=message, text_color=Theme.TEXT_NORMAL, wraplength=400, justify="center")
        lbl_msg.pack(pady=10, padx=20)
        
        ctk.CTkButton(card, text="Select Different Folder", command=self.browse_project, fg_color=Theme.BTN_WARNING, hover_color=Theme.BTN_WARNING_HOVER, text_color=Theme.BTN_WARNING_TEXT, width=200, height=35).pack(pady=20)

    def show_view_main(self):
        self.clear_view()

        # Layout: Top (Source), Middle (Options), Bottom (Log)
        
        # 1. Source Panel
        src_frame = ctk.CTkFrame(self.view_container)
        src_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(src_frame, text="Credits Source", font=Theme.FONT_BOLD).pack(anchor="w", padx=15, pady=10)
        
        file_row = ctk.CTkFrame(src_frame, fg_color="transparent")
        file_row.pack(fill="x", padx=10, pady=(0, 15))
        
        self.path_entry = ctk.CTkEntry(file_row, placeholder_text="Path to credits file (.txt or .json)")
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        if self.credits_path:
            self.path_entry.insert(0, self.credits_path)
            
        ctk.CTkButton(file_row, text="Browse File...", width=100, command=self.browse_file).pack(side="right")
        
        ctk.CTkLabel(src_frame, text="💡 Supports: .txt (1 author/line) or .json (SMW Credits Manager)", text_color=Theme.TEXT_DIM, font=("Arial", 11)).pack(anchor="w", padx=15, pady=(0, 10))

        # 2. Options Panel
        opt_frame = ctk.CTkFrame(self.view_container)
        opt_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(opt_frame, text="Generation Options", font=Theme.FONT_BOLD).pack(anchor="w", padx=15, pady=10)
        
        # Grid for options
        opt_grid = ctk.CTkFrame(opt_frame, fg_color="transparent")
        opt_grid.pack(fill="x", padx=10, pady=(0, 15))
        
        # Load Defaults
        opt_def = self.config.get("optimize_columns", True)
        empty_def = self.config.get("add_empty_line", False)
        blank_def = self.config.get("blank_tile_id", "0F8")
        font_size_def = self.config.get("tile_size", "8x8") # Use tile_size

        self.chk_optimize_var = ctk.BooleanVar(value=opt_def)
        ctk.CTkCheckBox(opt_grid, text="Optimize Columns (2 Names/Row)", variable=self.chk_optimize_var, command=self.save_config).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.chk_empty_var = ctk.BooleanVar(value=empty_def)
        ctk.CTkCheckBox(opt_grid, text="Add Empty Line After Section", variable=self.chk_empty_var, command=self.save_config).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        # Blank Tile & Font Size
        blank_row = ctk.CTkFrame(opt_grid, fg_color="transparent")
        blank_row.grid(row=0, column=1, rowspan=2, sticky="e", padx=20)
        
        ctk.CTkLabel(blank_row, text="Blank Tile ID:").pack(side="left", padx=5)
        self.ent_blank = ctk.CTkEntry(blank_row, width=50)
        self.ent_blank.pack(side="left", padx=5)
        self.ent_blank.insert(0, blank_def)
        
        ctk.CTkLabel(blank_row, text="Font Size:").pack(side="left", padx=(15, 5))
        self.font_size_var = ctk.StringVar(value=font_size_def)
        self.opt_font_size = ctk.CTkOptionMenu(blank_row, variable=self.font_size_var, values=["8x8", "8x16", "16x16"], command=lambda _: self.save_config(), width=80)
        self.opt_font_size.pack(side="left", padx=5)
        
        # Map16 Settings Row
        map16_row = ctk.CTkFrame(opt_grid, fg_color="transparent")
        map16_row.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))
        
        # Act As
        ctk.CTkLabel(map16_row, text="Act As:").pack(side="left", padx=5)
        act_as_def = self.config.get("act_as", "0025 (Air)")
        self.act_as_var = ctk.StringVar(value=act_as_def)
        self.opt_act_as = ctk.CTkOptionMenu(map16_row, variable=self.act_as_var, 
                                            values=["0025 (Air)", "0130 (Cement)", "002B (Coin)"], 
                                            command=lambda _: self.save_config(), width=120)
        self.opt_act_as.pack(side="left", padx=5)
        
        # Priority
        priority_def = self.config.get("priority", False)
        self.priority_var = ctk.BooleanVar(value=priority_def)
        ctk.CTkCheckBox(map16_row, text="Priority (On Top)", variable=self.priority_var, 
                       command=self.save_config).pack(side="left", padx=15)
        
        # Start Page
        ctk.CTkLabel(map16_row, text="Start Page (Hex):").pack(side="left", padx=(15, 5))
        start_page_def = self.config.get("start_page", 0x60)
        self.ent_start_page = ctk.CTkEntry(map16_row, width=50)
        self.ent_start_page.pack(side="left", padx=5)
        self.ent_start_page.insert(0, f"{start_page_def:02X}")
        self.ent_start_page.bind("<FocusOut>", lambda _: self.save_config())
        
        # ... (rest of method) ...

    # ... (rest) ...

    def save_config(self):
        self.config.set("optimize_columns", self.chk_optimize_var.get())
        self.config.set("add_empty_line", self.chk_empty_var.get())
        self.config.set("blank_tile_id", self.ent_blank.get())
        self.config.set("tile_size", self.font_size_var.get()) # Save as tile_size
        # Map16 Settings
        self.config.set("act_as", self.act_as_var.get())
        self.config.set("priority", self.priority_var.get())
        try:
            start_page = int(self.ent_start_page.get(), 16)
            self.config.set("start_page", start_page)
        except:
            pass  # Ignore invalid hex

    def browse_file(self):
        file = filedialog.askopenfilename(filetypes=[("Credits File", "*.json *.txt")])
        if file:
            self.credits_path = file
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, file)

    def log(self, message):
        # Helper to log safely even if view changed (though usually log is in main view)
        if hasattr(self, 'lbl_log') and self.lbl_log.winfo_exists():
            current = self.lbl_log.cget("text")
            self.lbl_log.configure(text=current + "\n" + message)
        else:
            print(f"[LOG] {message}")

    def generate(self):
        self.save_config() 
        # 1. Validation
        if not self.credits_path:
            self.log("Error: No credits file selected.")
            return
            
        if not self.project_path:
             self.log("Error: No Project selected.")
             return
             
        # 1.5 Safety Save - Ensure Map16 files exist in text format
        from app.core.callisto_handler import CallistoHandler
        self.log("Running safety 'callisto save'...")
        ok, msg = CallistoHandler.save(self.project_path, self.rhr_version)
        if not ok:
             self.log(f"Error executing save: {msg}")
             self.log("Aborting to prevent data corruption. Please check Callisto.")
             return

        # 2. Parse Credits
        self.log(f"Parsing {os.path.basename(self.credits_path)}...")
        credits_data = CreditsParser.parse_file(self.credits_path)
        
        total_names = sum(len(v) for v in credits_data.values())
        self.log(f"Found {total_names} authors in {len(credits_data)} sections.")
        
        # 3. Generate Tiles
        self.log("Generating Map16 Data...")
        generator = Map16Generator(self.mapper)
        
        # Parse Act As string "0025 (Air)" -> "0025"
        act_raw = self.config.get("act_as", "0025")
        act_val = act_raw.split()[0]
        
        options = {
            "optimize_columns": self.chk_optimize_var.get(),
            "add_empty_line": self.chk_empty_var.get(),
            "blank_tile": self.ent_blank.get(),
            "act_as": act_val,
            "palette": self.config.get("palette", 0),
            "priority": self.config.get("priority", False),
            "font_size": self.config.get("tile_size", "8x8")
        }
        
        tiles = generator.generate_credits_tiles(credits_data, options)
        self.log(f"Generated {len(tiles)} Map16 tiles.")
        
        # 4. Preview / Export
        tiles_per_page = 16 * 16 # 256
        pages_needed = (len(tiles) + tiles_per_page - 1) // tiles_per_page
        self.log(f"Requires {pages_needed} Map16 Pages.")
        
        # Determine output directory based on version
        # < v5.10: resources/map16/All.map16/global_pages/FG_pages
        # >= v5.10: export/all_map16.map16/global_pages/FG_pages
        
        is_legacy_path = False
        if self.rhr_version and self.rhr_version < (5, 10):
            is_legacy_path = True
            
        if is_legacy_path:
             export_dir = os.path.join(self.project_path, "resources", "map16", "All.map16", "global_pages", "FG_pages")
        else:
             export_dir = os.path.join(self.project_path, "export", "all_map16.map16", "global_pages", "FG_pages")

        if not os.path.exists(export_dir):
            try:
                os.makedirs(export_dir, exist_ok=True)
            except:
                pass
                
        if not os.path.exists(export_dir):
             self.log(f"Error: Could not locate map16 export folder at {export_dir}")
             return
             
        from app.core.map16_handler import Map16Handler
        
        # Calculate which pages we'll be generating
        current_page = self.config.get("start_page", 0x60)
        pages_to_generate = []
        for i in range(pages_needed):
            page_hex = f"{current_page + i:02X}"
            pages_to_generate.append(f"page_{page_hex}.txt")
        
        # Only delete the pages we're about to regenerate
        self.log(f"Cleaning up {len(pages_to_generate)} page(s) that will be regenerated...")
        try:
            for fname in pages_to_generate:
                fpath = os.path.join(export_dir, fname)
                if os.path.exists(fpath):
                    os.remove(fpath)
                    self.log(f"Deleted: {fname}")
        except Exception as e:
            self.log(f"Warning: Could not clean files: {e}")
        
        for i in range(pages_needed):
            start_index = i * tiles_per_page
            end_index = start_index + tiles_per_page
            chunk = tiles[start_index:end_index]
            
            page_hex = f"{current_page:02X}"
            filename = f"page_{page_hex}.txt"
            output_path = os.path.join(export_dir, filename)
            
            # Start Hex for this page
            start_tile_hex = f"{page_hex}00"
            
            try:
                lines = Map16Handler.generate_page_content(start_tile_hex, chunk)
                # UTF-8 without BOM, but explicit CRLF for Windows compatibility
                with open(output_path, 'w', encoding='utf-8', newline='\r\n') as f:
                    f.writelines(lines)
                self.log(f"Generated: {filename} ({len(lines)} tiles)")
            except Exception as e:
                self.log(f"Error writing {filename}: {e}")
                
            current_page += 1

        self.log("Done. Files generated.")
        
        # 5. Callisto Update
        from app.core.callisto_handler import CallistoHandler
        self.log("Running 'callisto update'...")
        ok, msg = CallistoHandler.update(self.project_path, self.rhr_version)
        if ok:
             self.log(f"Success: {msg}")
        else:
             self.log(f"Warning: {msg}")
