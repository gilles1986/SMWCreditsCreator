import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import logging
import pyperclip
from app.core.credits_parser import CreditsParser
from app.core.map16_handler import Map16Generator, Map16Handler
from app.core.clipboard_handler import ClipboardHandler
from app.ui.theme import Theme
from app.core.app_config import AppConfig
from app.core.validator import Validator
from app.core.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class CreditsTab:
    def __init__(self, master, mapper, on_mapping_change=None):
        self.master = master
        self.mapper = mapper
        self.on_mapping_change = on_mapping_change # Callback
        self.credits_path = None
        self.current_mapping_name = None # Track filename
        self.config = AppConfig()
        self.log_history = ["Ready."] 

        # Main Grid Config
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=1) 
        
        # Central View Container
        self.view_container = ctk.CTkFrame(self.master, fg_color="transparent")
        self.view_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.view_container.grid_columnconfigure(0, weight=1)
        
        self.show_view_main()

    # ... (skipping clear_view/show_view_main) ...

    def load_custom_mapping(self):
        file = filedialog.askopenfilename(filetypes=[("JSON Mapping", "*.json")])
        if file:
            success, msg = self.mapper.load_mappings(file)
            if success:
                self.current_mapping_name = os.path.basename(file)
                self.log(f"Loaded mapping from {self.current_mapping_name}")
                self._update_mapping_status("Custom")
                # Trigger external sync
                if self.on_mapping_change:
                     self.on_mapping_change(filename=self.current_mapping_name)
            else:
                messagebox.showerror("Error", msg)
                self.log(f"Error loading mapping: {msg}")

    def reset_mapping_rhr(self):
        if messagebox.askyesno("Confirm Reset", "Reset font mapping to RHR Defaults (A-Z -> 0x280)?\nThis will clear current mappings."):
            success, msg = self.mapper.reset_defaults_rhr()
            self.current_mapping_name = None
            self._update_mapping_status("Default (RHR)")
            self.log(msg)
            # Trigger external sync
            if self.on_mapping_change:
                 self.on_mapping_change(status="Default (RHR)")

    def _update_mapping_status(self, status=None):
        # Infer status if not provided
        if status is None:
            val_a = self.mapper.get_mapping('A')
            if val_a == "280" or val_a == "0280":
                status = "Default (RHR)"
            elif val_a:
                status = "Custom"
            else:
                status = "Empty / Unknown"
        
        # Display filename if custom and available
        display_text = status
        if status == "Custom" and self.current_mapping_name:
            display_text = self.current_mapping_name
        
        self.lbl_mapping_status.configure(text=display_text)
        
        if "Default" in status:
            self.lbl_mapping_status.configure(text_color=Theme.TEXT_SUCCESS) 
        elif "Custom" in status:
            self.lbl_mapping_status.configure(text_color=Theme.BTN_PRIMARY) 
        else:
            self.lbl_mapping_status.configure(text_color=Theme.BTN_DANGER)

    def clear_view(self):
        for widget in self.view_container.winfo_children():
            widget.destroy()

    def show_view_main(self):
        logger.debug("Loading CreditsTab Layout Fix V2")
        self.clear_view()

        # Layout: Top (Split Column), Bottom (Settings + Log)
        
        # Container for Top Sections (Content + Visuals)
        top_container = ctk.CTkFrame(self.view_container, fg_color="transparent")
        top_container.pack(fill="x", pady=(0, 10))
        top_container.grid_columnconfigure(0, weight=1)
        top_container.grid_columnconfigure(1, weight=1)
        
        # --- Section 1: Credits Content ("What") ---
        # Left Column (Spans 2 rows)
        sec1 = self._create_section_frame(top_container, "1. Credits Content")
        sec1.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 5))
        
        sec1.grid_rowconfigure(1, weight=1) # Content area grows
        # Toolbar Header (Toggle + File Input)
        toolbar = ctk.CTkFrame(sec1, fg_color="transparent")
        toolbar.pack(fill="x", padx=10, pady=(5, 5))
        toolbar.grid_columnconfigure(0, weight=1)
        
        # Toggle
        self.src_mode_var = ctk.StringVar(value="file")
        self.seg_mode = ctk.CTkSegmentedButton(toolbar, values=["File", "Direct Text"], 
                                               variable=self.src_mode_var, 
                                               command=self.toggle_source_mode)
        self.seg_mode.grid(row=0, column=0, sticky="ew")
        self.seg_mode.set("File")

        # File Inputs (Grouped for hiding)
        self.frm_file_inputs = ctk.CTkFrame(toolbar, fg_color="transparent")
        self.frm_file_inputs.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        self.frm_file_inputs.grid_columnconfigure(0, weight=1)

        self.path_entry = ctk.CTkEntry(self.frm_file_inputs, placeholder_text="Path to credits file (.txt or .json)")
        self.path_entry.grid(row=0, column=0, sticky="ew", pady=(8, 0))
        ctk.CTkButton(self.frm_file_inputs, text="Browse...", width=100, command=self.browse_file).grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        if self.credits_path:
            self.path_entry.insert(0, self.credits_path)

        # Content Area
        self.content_area = ctk.CTkFrame(sec1, fg_color="transparent")
        self.content_area.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

        # Direct Text Input (Initially hidden)
        self.txt_credits_input = ctk.CTkTextbox(self.content_area)
        # Note: We grid/pack this in toggle

        # Hints - Supported Formats
        self.hint_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")

        ctk.CTkLabel(self.hint_frame, text="💡 Supported Formats:",
                     text_color=Theme.TEXT_DIM, font=("Arial", 13, "bold")).pack(anchor="w", pady=(0, 3))

        ctk.CTkLabel(self.hint_frame, text="  •  Textfile (.txt)",
                     text_color=Theme.TEXT_DIM, font=("Arial", 12)).pack(anchor="w")

        hint_json_row = ctk.CTkFrame(self.hint_frame, fg_color="transparent")
        hint_json_row.pack(anchor="w", fill="x")
        ctk.CTkLabel(hint_json_row, text="  •  ",
                     text_color=Theme.TEXT_DIM, font=("Arial", 12)).pack(side="left")
        self.lbl_link = ctk.CTkLabel(hint_json_row, text="SMW Credits Manager json-File",
                                     text_color="#4A9EFF", font=("Arial", 12, "underline"),
                                     cursor="hand2")
        self.lbl_link.pack(side="left")
        self.lbl_link.bind("<Button-1>", lambda e: self.open_credits_manager_link())

        
        self.toggle_source_mode("File")

        # --- Section 2: Appearance & Font ("How") ---
        # Right Column
        sec2 = self._create_section_frame(top_container, "2. Appearance & Font")
        sec2.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=(0, 5))
        
        # Font Mapping Control Area
        font_frame = ctk.CTkFrame(sec2, fg_color="transparent")
        font_frame.pack(fill="x", padx=10, pady=5)
        
        # Row 1: Label + Status
        status_row = ctk.CTkFrame(font_frame, fg_color="transparent")
        status_row.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(status_row, text="Font Mapping:", font=Theme.FONT_BOLD).pack(side="left", padx=(0, 10))
        self.lbl_mapping_status = ctk.CTkLabel(status_row, text="Unknown", text_color=Theme.TEXT_DIM)
        self.lbl_mapping_status.pack(side="left")
        
        # Row 2: Buttons
        btn_row = ctk.CTkFrame(font_frame, fg_color="transparent")
        btn_row.pack(fill="x")
        
        ctk.CTkButton(btn_row, text="Load Mapping (.json)", width=140, height=24, 
                      fg_color=Theme.BTN_SECONDARY, command=self.load_custom_mapping).pack(side="left", padx=(0, 5))
        
        # Reset Icon Button
        ctk.CTkButton(btn_row, text="↺", width=24, height=24, 
                      font=("Arial", 16, "bold"),
                      fg_color=Theme.BTN_DANGER, 
                      command=self.reset_mapping_rhr,
                      hover_color="#B71C1C").pack(side="left") # Dark red hover

        self._update_mapping_status()

        # Visual Options Grid
        vis_grid = ctk.CTkFrame(sec2, fg_color="transparent")
        vis_grid.pack(fill="x", padx=10, pady=10)
        
        # Load Defaults
        opt_def = self.config.get("optimize_columns", True)
        empty_def = self.config.get("add_empty_line", False)
        font_size_def = self.config.get("tile_size", "8x8")

        self.chk_capitalize_var = ctk.BooleanVar(value=self.config.get("capitalize", False))
        ctk.CTkCheckBox(vis_grid, text="Capitalize Text (UPPERCASE)", variable=self.chk_capitalize_var, command=self.save_config).grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.chk_optimize_var = ctk.BooleanVar(value=opt_def)
        ctk.CTkCheckBox(vis_grid, text="Optimize Columns (2 Names/Row)", variable=self.chk_optimize_var, command=self.save_config).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        self.chk_empty_var = ctk.BooleanVar(value=empty_def)
        ctk.CTkCheckBox(vis_grid, text="Add Empty Line After Section", variable=self.chk_empty_var, command=self.save_config).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        
        frame_size = ctk.CTkFrame(vis_grid, fg_color="transparent")
        frame_size.grid(row=0, column=1, rowspan=3, sticky="ne", padx=20)
        ctk.CTkLabel(frame_size, text="Font Size:").pack(side="left", padx=5)
        self.font_size_var = ctk.StringVar(value=font_size_def)
        self.opt_font_size = ctk.CTkOptionMenu(frame_size, variable=self.font_size_var, values=["8x8", "8x16", "16x16"], command=lambda _: self.save_config(), width=80)
        self.opt_font_size.pack(side="left", padx=5)

        # --- Section 3: Map16 Settings ("Settings") ---
        sec3 = self._create_section_frame(top_container, "3. Map16 Settings")
        sec3.grid(row=1, column=1, sticky="nsew", padx=(5, 0), pady=(5, 0))
        
        map16_grid = ctk.CTkFrame(sec3, fg_color="transparent")
        map16_grid.pack(fill="x", padx=10, pady=5)
        
        # Row 1: Blank Tile + Act As
        blank_def = self.config.get("blank_tile_id", "0F8")
        ctk.CTkLabel(map16_grid, text="Blank Tile ID:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.ent_blank = ctk.CTkEntry(map16_grid, width=60)
        self.ent_blank.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.ent_blank.insert(0, blank_def)

        act_as_def = self.config.get("act_as", "0025")
        # Normalize: strip any trailing description like "0025 (Air)" -> "0025"
        if isinstance(act_as_def, str) and " " in act_as_def:
            act_as_def = act_as_def.split()[0]
        ctk.CTkLabel(map16_grid, text="Act As:").grid(row=0, column=2, sticky="e", padx=10, pady=5)
        act_as_frame = ctk.CTkFrame(map16_grid, fg_color="transparent")
        act_as_frame.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        self.ent_act_as = ctk.CTkEntry(act_as_frame, width=70, placeholder_text="0025")
        self.ent_act_as.insert(0, act_as_def)
        self.ent_act_as.pack(side="left")
        ctk.CTkLabel(act_as_frame, text="(0025=Air  0130=Cement  002B=Coin)",
                     text_color=Theme.TEXT_DIM, font=("Arial", 10)).pack(side="left", padx=(5, 0))
        self.ent_act_as.bind("<FocusOut>", lambda _: self.save_config())

        # Row 1 (right): Start Page under Act As
        ctk.CTkLabel(map16_grid, text="Start Page (Hex):").grid(row=1, column=2, sticky="e", padx=10, pady=5)
        start_page_def = self.config.get("start_page", 0x60)
        page_frame = ctk.CTkFrame(map16_grid, fg_color="transparent")
        page_frame.grid(row=1, column=3, sticky="w", padx=5, pady=5)
        self.ent_start_page = ctk.CTkEntry(page_frame, width=60)
        self.ent_start_page.pack(side="left")
        ctk.CTkLabel(page_frame, text="(hex)",
                     text_color=Theme.TEXT_DIM, font=("Arial", 10)).pack(side="left", padx=(5, 0))
        self.ent_start_page.insert(0, f"{start_page_def:02X}")
        self.ent_start_page.bind("<FocusOut>", lambda _: self.save_config())
        self.ent_start_page.bind("<KeyRelease>", lambda _: self._validate_start_page())

        # Row 1 (left): Priority
        priority_def = self.config.get("priority", False)
        self.priority_var = ctk.BooleanVar(value=priority_def)
        ctk.CTkCheckBox(map16_grid, text="Priority (On Top)", variable=self.priority_var, command=self.save_config).grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=5)

        # Row 2: Section Order
        sort_mode_def = self.config.get("sort_mode", "predefined")
        ctk.CTkLabel(map16_grid, text="Section Order:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.sort_mode_var = ctk.StringVar(value=sort_mode_def)
        self.opt_sort_mode = ctk.CTkOptionMenu(
            map16_grid, variable=self.sort_mode_var,
            values=["predefined", "alphabetical", "none"],
            command=lambda _: self.save_config(), width=120)
        self.opt_sort_mode.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Row 3: Section Order info text
        ctk.CTkLabel(map16_grid, text="(predefined = Sprites/UberASM/…, alphabetical, none = file order)",
                     text_color=Theme.TEXT_DIM, font=("Arial", 10)).grid(row=3, column=0, columnspan=4, sticky="w", padx=20, pady=(0, 5))

        # 3. Actions & Log
        action_frame = ctk.CTkFrame(self.view_container)
        action_frame.pack(fill="both", expand=True, pady=10)
        
        # Grid for Actions
        act_grid = ctk.CTkFrame(action_frame, fg_color="transparent")
        act_grid.pack(fill="x", padx=20, pady=10)
        
        # self.btn_generate_proj = ctk.CTkButton(act_grid, text="Export as Text File (.txt)", 
        #                                   command=self.generate_text_file, 
        #                                   height=40, font=('Arial', 13, 'bold'),
        #                                   fg_color=Theme.BTN_PRIMARY)
        # self.btn_generate_proj.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn_save_bin = ctk.CTkButton(act_grid, text="Save .map16", 
                                          command=self.save_as_file, 
                                          height=40, font=('Arial', 13, 'bold'),
                                          fg_color=Theme.BTN_SUCCESS)
        self.btn_save_bin.pack(side="left", fill="x", expand=True, padx=5)

        # self.btn_clipboard = ctk.CTkButton(act_grid, text="Copy to Clipboard", 
        #                                   command=self.copy_to_clipboard, 
        #                                   height=40, font=('Arial', 13, 'bold'), # Standard color
        #                                   )
        # self.btn_clipboard.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        # Log Pane
        ctk.CTkLabel(action_frame, text="Output Log:", text_color=Theme.TEXT_DIM, font=("Arial", 11)).pack(anchor="w", padx=20, pady=(0, 5))
        
        self.txt_log = ctk.CTkTextbox(action_frame, 
                                      text_color=Theme.TEXT_NORMAL, 
                                      fg_color=Theme.BG_COLOR_2,
                                      corner_radius=6,
                                      padx=10, pady=10,
                                      font=("Consolas", 12))
        self.txt_log.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.txt_log.insert("0.0", "\n".join(self.log_history))
        self.txt_log.configure(state="disabled") # Read-only but selectable

    # ... (rest) ...

    def _create_section_frame(self, parent, title):
        frame = ctk.CTkFrame(parent)
        # Note: We do NOT pack here, allowing grid/pack by caller
        ctk.CTkLabel(frame, text=title, font=Theme.FONT_BOLD).pack(anchor="w", padx=15, pady=5)
        return frame



    def save_config(self):
        act_as_val = self.ent_act_as.get().strip().split()[0] if self.ent_act_as.get().strip() else "0025"
        updates = {
            "optimize_columns": self.chk_optimize_var.get(),
            "add_empty_line": self.chk_empty_var.get(),
            "blank_tile_id": self.ent_blank.get(),
            "tile_size": self.font_size_var.get(),
            "capitalize": self.chk_capitalize_var.get(),
            "act_as": act_as_val,
            "priority": self.priority_var.get(),
            "sort_mode": self.sort_mode_var.get(),
        }
        try:
            updates["start_page"] = int(self.ent_start_page.get(), 16)
        except ValueError:
            pass  # Keep previous valid start_page
        self.config.set_many(updates)

    def _validate_start_page(self):
        """Visual feedback for start page hex entry."""
        val = self.ent_start_page.get().strip()
        try:
            if val:
                int(val, 16)
            self.ent_start_page.configure(border_color=Theme.TEXT_SUCCESS)
        except ValueError:
            self.ent_start_page.configure(border_color="#FF4444")

    def browse_file(self):
        file = filedialog.askopenfilename(filetypes=[("Credits File", "*.json *.txt")])
        if file:
            self.credits_path = file
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, file)
            
    def open_credits_manager_link(self):
        """Opens the Saphros SMW Credits Manager website in the default browser."""
        import webbrowser
        webbrowser.open("https://saphros.de/smwcredits/")
        self.log("Opened Saphros SMW Credits Manager in browser.")
    
    def toggle_source_mode(self, mode):
        # inputs are: self.frm_file_inputs (grid in toolbar), self.txt_credits_input (pack in content), self.hint_frame (pack in content)
        
        if mode == "File":
            self.frm_file_inputs.grid() # Restore
            self.txt_credits_input.pack_forget()
            self.hint_frame.pack(anchor="nw", pady=(10, 0), padx=5)
        else:
            self.frm_file_inputs.grid_remove()
            self.hint_frame.pack_forget()
            self.txt_credits_input.pack(fill="both", expand=True, pady=(10, 0))

    def log(self, message):
        # Helper to log safely even if view changed (though usually log is in main view)
        self.log_history.append(message)
        
        if hasattr(self, 'txt_log') and self.txt_log.winfo_exists():
            self.txt_log.configure(state="normal")
            self.txt_log.insert("end", message + "\n")
            self.txt_log.see("end")
            self.txt_log.configure(state="disabled")
        else:
            logger.info(message)

    def _generate_tiles_internal(self):
        """Helper to generate tiles based on current settings."""

        act_raw = self.ent_act_as.get().strip()
        act_val = act_raw.split()[0] if act_raw else "0025"
        
        # Options
        options = {
            "optimize_columns": self.chk_optimize_var.get(),
            "add_empty_line": self.chk_empty_var.get(),
            "blank_tile": self.ent_blank.get(),
            "act_as": act_val,
            "palette": self.config.get("palette", 0),
            "priority": self.config.get("priority", False),
            "font_size": self.config.get("tile_size", "8x8"),
            "sort_mode": self.config.get("sort_mode", "predefined")
        }
        
        try:
            # Check Mapping Exist
            if not self.mapper.mappings:
                if messagebox.askyesno("No Mapping", "No font mapping loaded. Load default (RHR)?"):
                    self.mapper.reset_defaults_rhr()
                    self._update_mapping_status("Default (RHR)")
                else:
                    return None, None

            # Validate all mappings before generating
            valid, errors = Validator.validate_all_mappings(self.mapper.mappings)
            if not valid:
                error_list = [f"  '{e[0]}' = '{e[1]}': {e[2]}" for e in errors[:10]]
                suffix = f"\n  (and {len(errors) - 10} more)" if len(errors) > 10 else ""
                warn_msg = f"{len(errors)} invalid tile mapping(s) found:\n" + "\n".join(error_list) + suffix
                warn_msg += "\n\nInvalid values will produce garbled tile data.\nGenerate anyway?"
                self.log(f"Warning: {len(errors)} invalid mapping(s) detected.")
                if not messagebox.askyesno("Mapping Validation Warning", warn_msg, icon="warning"):
                    return None, None

            credits_data = None
            mode = self.src_mode_var.get()
            
            if mode == "File":
                if not self.credits_path:
                     self.log("Error: No credits file selected.")
                     messagebox.showerror("Error", "Please select a credits file.")
                     return None, None
                self.log(f"Parsing file: {os.path.basename(self.credits_path)}")
                try:
                    credits_data = CreditsParser.parse_file(self.credits_path)
                except ValueError as e:
                    self.log(f"Error: {e}")
                    messagebox.showerror("Parse Error", str(e))
                    return None, None
            else:
                # Text Input
                content = self.txt_credits_input.get("1.0", "end").strip()
                if not content:
                     self.log("Error: Credits text is empty.")
                     messagebox.showerror("Error", "Please enter names in the text box.")
                     return None, None
                
                # Check if JSON
                is_json = content.strip().startswith(("[", "{"))
                try:
                    credits_data = CreditsParser.parse_content(content, is_json=is_json)
                except ValueError as e:
                    self.log(f"Error: {e}")
                    messagebox.showerror("Parse Error", str(e))
                    return None, None
                self.log("Parsed text content.")

            if not credits_data:
                 self.log("Error: No credits data found. The file may be empty or in an unrecognized format.")
                 messagebox.showerror("Parse Error",
                     "No credits data found.\n\n"
                     "Expected JSON format:\n"
                     '[{"section": "...", "authors": [{"name": "..."}]}]\n\n'
                     "Or plain text with one name per line.")
                 return None, None

            # Apply Capitalization (Uppercase all content)
            if self.config.get("capitalize", False) and credits_data:
                new_data = {}
                for sec, names in credits_data.items():
                     # Uppercase Header
                     new_sec = sec.upper()
                     # Uppercase Names
                     new_names = [n.upper() for n in names]
                     new_data[new_sec] = new_names
                credits_data = new_data

            generator = Map16Generator(self.mapper)
            tiles = generator.generate_credits_tiles(credits_data, options)
            self.log(f"Generated {len(tiles)} tiles.")
            
            # Map16 Page
            try: page_val = int(self.ent_start_page.get(), 16)
            except ValueError: page_val = 0
            
            return tiles, page_val
            
        except Exception as e:
            self.log(f"Error generating tiles: {e}")
            logger.exception("Error generating tiles")
            messagebox.showerror("Generation Error", str(e))
            return None, None

    def generate_text_file(self):
        """Generates text file export."""
        tiles, page_val = self._generate_tiles_internal()
        if not tiles: return # Error logged already
        
        self.log(f"Generating Text Export... ({len(tiles)} tiles)")
        
        text_content = Map16Handler.generate_map16_text(page_val, tiles)
        
        f = filedialog.asksaveasfilename(defaultextension=".txt", 
                                         filetypes=[("Text File", "*.txt"), ("All Files", "*.*")],
                                         initialfile=f"page_{page_val:02X}.txt")
                                         
        if f:
            try:
                with open(f, "w", encoding="utf-8") as file:
                    file.write(text_content)
                self.log(f"Saved text export to {f}")
                messagebox.showinfo("Success", f"Saved text file:\n{os.path.basename(f)}")
            except Exception as e:
                 self.log(f"Error saving text file: {e}")
                 messagebox.showerror("Error", f"Failed to save text file: {e}")

    def save_as_file(self):
        """Export as binary .map16 file."""
        tiles, page_val = self._generate_tiles_internal()
        if not tiles: return
        
        data = Map16Handler.generate_map16_binary(page_val, tiles)
        f = filedialog.asksaveasfilename(defaultextension=".map16", filetypes=[("Lunar Magic Map16", "*.map16")])
        if f:
             try:
                 with open(f, "wb") as file:
                     file.write(data)
                 self.log(f"Saved binary .map16 to {f}")
                 messagebox.showinfo("Success", f"Saved .map16 file.")
             except Exception as e:
                 self.log(f"Error saving binary: {e}")
                 messagebox.showerror("Error", str(e))

    def copy_to_clipboard(self):
         try:
             tiles, page_val = self._generate_tiles_internal()
             if not tiles: 
                 self.log("Warning: No tiles generated (0).")
                 return
             
             # Generate Binary Data for Clipboard (Selection Format)
             binary_data = Map16Handler.generate_map16_selection(tiles)
             self.log(f"Clipboard Binary Size: {len(binary_data)} bytes")
             
             # Copy to Clipboard (Native)
             if ClipboardHandler.copy_map16(binary_data):
                 self.log(f"Copied {len(tiles)} tiles to clipboard (Binary Format).")
             else:
                 self.log("Error: Failed to register or set clipboard data.")
                 
         except Exception as e:
             self.log(f"Clipboard Error: {e}")
             import traceback
             traceback.print_exc()

    def generate(self):
        # Legacy stub
        self.generate_text_file()
