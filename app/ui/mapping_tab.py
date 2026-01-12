import customtkinter as ctk
from tkinter import filedialog
from app.core.mapper import Mapper
from app.ui.theme import Theme

class MappingTab:
    def __init__(self, master):
        self.master = master
        self.mapper = Mapper()
        
        # Grid layout
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(1, weight=1)
        
        # Controls Frame
        self.controls_frame = ctk.CTkFrame(self.master)
        self.controls_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        
        self.btn_load = ctk.CTkButton(self.controls_frame, text="Load Mapping", command=self.load_mapping, fg_color=Theme.BTN_PRIMARY, text_color=Theme.BTN_PRIMARY_TEXT)
        self.btn_load.pack(side="left", padx=10, pady=10)
        
        self.btn_save = ctk.CTkButton(self.controls_frame, text="Save Mapping", command=self.save_mapping, fg_color=Theme.BTN_PRIMARY, text_color=Theme.BTN_PRIMARY_TEXT)
        self.btn_save.pack(side="left", padx=10, pady=10)
        
        self.tile_size_var = ctk.StringVar(value="8x8")
        self.opt_tile_size = ctk.CTkOptionMenu(self.controls_frame, variable=self.tile_size_var, values=["8x8", "16x16"], fg_color=Theme.BTN_PRIMARY, text_color=Theme.BTN_PRIMARY_TEXT)
        self.opt_tile_size.pack(side="left", padx=10, pady=10)

        # Mapping Grid (Scrollable)
        self.scroll_frame = ctk.CTkScrollableFrame(self.master, label_text="Character Mappings")
        self.scroll_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(1, weight=1)
        
        self.entries = {}
        self.populate_grid()

    def populate_grid(self):
        # Clear existing
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        chars = self.mapper.get_default_characters()
        for i, char in enumerate(chars):
            lbl_text = f"'{char}'" if char != ' ' else "'Space'"
            lbl = ctk.CTkLabel(self.scroll_frame, text=lbl_text, width=30, font=Theme.FONT_BOLD)
            lbl.grid(row=i, column=0, padx=5, pady=2, sticky="e")
            
            entry = ctk.CTkEntry(self.scroll_frame, placeholder_text="Tile ID (hex)")
            entry.grid(row=i, column=1, padx=5, pady=2, sticky="ew")
            
            # Pre-fill if exists
            val = self.mapper.get_mapping(char)
            if val:
                entry.insert(0, val)
                
            self.entries[char] = entry

    def save_mapping(self):
        # Update mapper from UI
        for char, entry in self.entries.items():
            self.mapper.set_mapping(char, entry.get().strip())
        self.mapper.tile_size = self.tile_size_var.get()
        
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if filepath:
            self.mapper.save_mappings(filepath)

    def load_mapping(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if filepath:
            success, msg = self.mapper.load_mappings(filepath)
            if success:
                self.tile_size_var.set(self.mapper.tile_size)
                self.populate_grid()
