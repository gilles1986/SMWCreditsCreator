import customtkinter as ctk
from tkinter import filedialog
from app.core.mapper import Mapper
from app.ui.theme import Theme
from app.core.app_config import AppConfig

class MappingTab:
    def __init__(self, master):
        self.master = master
        self.mapper = Mapper()
        self.config = AppConfig()
        
        # Load Settings from Config
        self.act_as = self.config.get("act_as", "0025 (Air)")
        self.palette = self.config.get("palette", 0)
        self.priority = self.config.get("priority", False)
        self.start_page = self.config.get("start_page", 0x60)
        self.tile_size = self.config.get("tile_size", "8x8")
        
        # Grid layout (3 Columns)
        self.master.grid_columnconfigure(0, weight=0, minsize=250) # Col 1: Character Map
        self.master.grid_columnconfigure(1, weight=1) # Col 2: Settings
        self.master.grid_columnconfigure(2, weight=1) # Col 3: Bulk Tools
        self.master.grid_rowconfigure(0, weight=1)
        
        # --- Column 1: Character Map ---
        self.scroll_frame = ctk.CTkScrollableFrame(self.master, label_text="Character Map (Tile IDs)", width=220)
        self.scroll_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # --- Column 2: Configuration ---
        self.config_frame = ctk.CTkFrame(self.master)
        self.config_frame.grid(row=0, column=1, padx=5, pady=10, sticky="nsew")
        
        self.lbl_config_title = ctk.CTkLabel(self.config_frame, text="Configuration", font=Theme.FONT_BOLD)
        self.lbl_config_title.pack(pady=10)

        # Helper to create config rows
        def add_config_item(parent, label, help_text, widget):
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            frame.pack(fill="x", padx=10, pady=5)
            
            lbl = ctk.CTkLabel(frame, text=label, anchor="w")
            lbl.pack(fill="x")
            
            if help_text:
                lbl_help = ctk.CTkLabel(frame, text=help_text, text_color=Theme.TEXT_DIM, font=("Arial", 11), anchor="w")
                lbl_help.pack(fill="x")
            
            widget.pack(fill="x", pady=(2, 5))
            return widget

        # 1. Tile Size
        self.tile_size_var = ctk.StringVar(value=self.tile_size)
        self.opt_size = ctk.CTkOptionMenu(self.config_frame, variable=self.tile_size_var, values=["8x8", "8x16", "16x16"], command=self.save_settings)
        add_config_item(self.config_frame, "Tile Size:", "Size of each character tile.", self.opt_size)

        # 2. Act As
        self.act_as_var = ctk.StringVar(value=self.act_as)
        self.opt_act = ctk.CTkOptionMenu(self.config_frame, variable=self.act_as_var, values=["0025 (Air)", "0130 (Cement)", "002B (Coin)"], command=self.save_settings)
        add_config_item(self.config_frame, "Act As:", "Map16 behavior (solidity, interaction).", self.opt_act)

        # 3. Palette
        self.pal_var = ctk.IntVar(value=self.palette)
        self.opt_pal = ctk.CTkOptionMenu(self.config_frame, variable=self.pal_var, values=[str(i) for i in range(8)], command=self.save_settings_pal)
        add_config_item(self.config_frame, "Palette:", "Color palette index for the tiles.", self.opt_pal)

        # 4. Start Page
        self.ent_page = ctk.CTkEntry(self.config_frame)
        self.ent_page.insert(0, f"{self.start_page:02X}")
        self.ent_page.bind("<FocusOut>", self.save_settings_page)
        add_config_item(self.config_frame, "Start Page (Hex):", "Map16 page number to start generating from.", self.ent_page)

        # 5. Priority
        self.prio_var = ctk.BooleanVar(value=self.priority)
        self.chk_prio = ctk.CTkCheckBox(self.config_frame, text="Priority (On Top)", variable=self.prio_var, command=self.save_settings)
        # Checkbox is its own widget/label combo
        frame_prio = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        frame_prio.pack(fill="x", padx=10, pady=10)
        self.chk_prio.pack(anchor="w")
        ctk.CTkLabel(frame_prio, text="Draw tiles on top of other sprites.", text_color=Theme.TEXT_DIM, font=("Arial", 11)).pack(anchor="w", padx=25)


        # --- Column 3: Bulk Tools & Actions ---
        self.bulk_frame = ctk.CTkFrame(self.master)
        self.bulk_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        self.lbl_bulk_title = ctk.CTkLabel(self.bulk_frame, text="Bulk Tools", font=Theme.FONT_BOLD)
        self.lbl_bulk_title.pack(pady=10)
        
        # Bulk Editor Header
        self.bulk_header = ctk.CTkFrame(self.bulk_frame, fg_color="transparent")
        self.bulk_header.pack(fill="x", padx=10)
        ctk.CTkLabel(self.bulk_header, text="Rules:").pack(side="left")
        ctk.CTkButton(self.bulk_header, text="?", width=25, height=25, command=self.show_bulk_help).pack(side="right")

        self.txt_bulk = ctk.CTkTextbox(self.bulk_frame, height=200)
        self.txt_bulk.pack(padx=10, pady=5, fill="both", expand=True)

        default_bulk = """# Example Bulk Rules
A-Z = 280
a-z = 2B0
[:'"/°-] = 29A 
0-9 = 2A0
[.&*,!?] = 2AA
"""
        self.txt_bulk.insert("0.0", default_bulk)
        
        self.btn_apply_bulk = ctk.CTkButton(self.bulk_frame, text="Apply Rules", command=self.apply_bulk)
        self.btn_apply_bulk.pack(pady=10, padx=10, fill="x")

        # Separator (Visual)
        ctk.CTkFrame(self.bulk_frame, height=2, fg_color="gray30").pack(fill="x", padx=20, pady=10)

        # Actions
        self.btn_save = ctk.CTkButton(self.bulk_frame, text="Save Mapping (JSON)", command=self.save_mapping, fg_color=Theme.BTN_PRIMARY, text_color=Theme.BTN_PRIMARY_TEXT)
        self.btn_save.pack(pady=5, padx=10, fill="x")
        
        self.btn_load = ctk.CTkButton(self.bulk_frame, text="Load Mapping (JSON)", command=self.load_mapping)
        self.btn_load.pack(pady=5, padx=10, fill="x")

        self.entries = {}
        # Auto-load default
        success, msg = self.mapper.load_default_mappings()
        if not success:
            print(f"Auto-load failed: {msg}") 
        
        self.populate_grid()
        
    def show_bulk_help(self):
        from tkinter import messagebox
        help_text = """Bulk Editor Syntax Guide:

1. Ranges:
   A-Z = 280
   (Maps A to 280, B to 281, ..., Z to 299)

2. Single Characters:
   ! = 100
   (Maps '!' to tile 100)

3. Sets (Bracket Groups):
   [ABC] = 200
   (Maps A to 200, B to 201, C to 202)

4. Comments:
   Lines starting with # are ignored.

Note: All tile IDs are in Hexadecimal.
"""
        messagebox.showinfo("Bulk Editor Help", help_text)
        
    def save_settings(self, _=None):
        self.config.set("act_as", self.act_as_var.get())
        self.config.set("priority", self.prio_var.get())
        self.config.set("tile_size", self.tile_size_var.get())
        
    def save_settings_pal(self, val):
        self.config.set("palette", int(val))
        
    def save_settings_page(self, _=None):
        try:
            val = int(self.ent_page.get(), 16)
            self.config.set("start_page", val)
        except:
            pass # Ignore invalid

    def populate_grid(self):
        # Clear existing
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        # Get characters from mapper
        chars = self.mapper.get_default_characters() 
        for i, char in enumerate(chars):
            lbl_text = f"'{char}'" if char != ' ' else "'Space'"
            lbl = ctk.CTkLabel(self.scroll_frame, text=lbl_text, width=60, font=Theme.FONT_BOLD)
            lbl.grid(row=i, column=0, padx=5, pady=2, sticky="e")
            
            entry = ctk.CTkEntry(self.scroll_frame, placeholder_text="Hex", width=70)
            entry.grid(row=i, column=1, padx=5, pady=2, sticky="w")
            val = self.mapper.get_mapping(char)
            if val:
                entry.insert(0, val) 
            entry.bind("<FocusOut>", lambda event, c=char, e=entry: self.update_mapping(c, e))
            self.entries[char] = entry
            
    def update_mapping(self, char, entry):
        val = entry.get().strip()
        self.mapper.set_mapping(char, val)

    def apply_bulk(self):
        rules = self.txt_bulk.get("1.0", "end")
        success, msg = self.mapper.apply_bulk_rules(rules)
        if success:
            self.populate_grid()
        else:
            print(msg) # TODO: Visual Feedback

    def save_mapping(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if filepath:
            self.mapper.save_mappings(filepath)

    def load_mapping(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if filepath:
            success, msg = self.mapper.load_mappings(filepath)
            if success:
                self.populate_grid()
