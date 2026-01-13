import customtkinter as ctk
from tkinter import filedialog
from app.core.mapper import Mapper
from app.ui.theme import Theme
from app.core.app_config import AppConfig
from app.core.snes_graphics import SNESGraphics
from PIL import Image, ImageTk
from app.ui.bulk_editor import BulkEditorWindow

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
        
        # Grid layout (2 Columns)
        self.master.grid_columnconfigure(0, weight=0, minsize=250) # Col 1: Character Map
        self.master.grid_columnconfigure(1, weight=1) # Col 2: Settings + Graphics
        self.master.grid_columnconfigure(2, weight=0) # Remove Col 3
        self.master.grid_rowconfigure(0, weight=1)
        
        # --- Column 1: Character Map ---
        self.scroll_frame = ctk.CTkScrollableFrame(self.master, label_text="Character Map (Tile IDs)", width=220)
        self.scroll_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # --- Column 2: Configuration & Graphics (Compact) ---
        self.middle_frame = ctk.CTkFrame(self.master, fg_color="transparent")
        self.middle_frame.grid(row=0, column=1, padx=5, pady=10, sticky="nsew")
        self.middle_frame.grid_rowconfigure(1, weight=1) # Graphics expand
        self.middle_frame.grid_columnconfigure(0, weight=1)

        # 1. Config Section
        self.config_frame = ctk.CTkFrame(self.middle_frame)
        self.config_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.config_frame.grid_columnconfigure(0, weight=1)
        self.config_frame.grid_columnconfigure(1, weight=1)
        
        self.lbl_config_title = ctk.CTkLabel(self.config_frame, text="Configuration", font=Theme.FONT_BOLD)
        self.lbl_config_title.grid(row=0, column=0, columnspan=2, pady=(5, 5))

        def create_compact_frame(row, col):
            f = ctk.CTkFrame(self.config_frame, fg_color="transparent")
            f.grid(row=row, column=col, padx=4, pady=2, sticky="ew")
            return f

        def add_label(frame, label, help_text):
            l = ctk.CTkLabel(frame, text=label, anchor="w", font=("Arial", 12, "bold"))
            l.pack(fill="x")
            if help_text:
                ctk.CTkLabel(frame, text=help_text, text_color=Theme.TEXT_DIM, font=("Arial", 10), anchor="w").pack(fill="x")

        # Row 1: Tile Size | Palette
        f1 = create_compact_frame(1, 0)
        add_label(f1, "Tile Size", "Size of char tile")
        self.tile_size_var = ctk.StringVar(value=self.tile_size)
        self.opt_size = ctk.CTkOptionMenu(f1, variable=self.tile_size_var, values=["8x8", "8x16", "16x16"], command=self.save_settings, height=24)
        self.opt_size.pack(fill="x")
        
        f2 = create_compact_frame(1, 1)
        add_label(f2, "Palette", "Color palette index")
        self.pal_var = ctk.IntVar(value=self.palette)
        self.opt_pal = ctk.CTkOptionMenu(f2, variable=self.pal_var, values=[str(i) for i in range(8)], command=self.save_settings_pal, height=24)
        self.opt_pal.pack(fill="x")

        # Row 2: Act As | Start Page
        f3 = create_compact_frame(2, 0)
        add_label(f3, "Act As", "Map16 behavior")
        self.act_as_var = ctk.StringVar(value=self.act_as)
        self.opt_act = ctk.CTkOptionMenu(f3, variable=self.act_as_var, values=["0025 (Air)", "0130 (Cement)", "002B (Coin)"], command=self.save_settings, height=24)
        self.opt_act.pack(fill="x")

        f4 = create_compact_frame(2, 1)
        add_label(f4, "Start Page (Hex)", "Map16 page number")
        self.ent_page = ctk.CTkEntry(f4, height=24)
        self.ent_page.insert(0, f"{self.start_page:02X}")
        self.ent_page.bind("<FocusOut>", self.save_settings_page)
        self.ent_page.pack(fill="x")

        # Row 3: Priority (Full)
        self.prio_var = ctk.BooleanVar(value=self.priority)
        self.chk_prio = ctk.CTkCheckBox(self.config_frame, text="Priority (On Top)", variable=self.prio_var, command=self.save_settings)
        self.chk_prio.grid(row=3, column=0, columnspan=2, padx=10, pady=(10,5), sticky="w")
        
        # Row 4: Action Buttons (New)
        action_frame = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        action_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)
        
        ctk.CTkButton(action_frame, text="Load JSON", width=80, command=self.load_mapping).pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(action_frame, text="Save JSON", width=80, command=self.save_mapping).pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(action_frame, text="Bulk Editor", width=100, fg_color=Theme.BTN_SECONDARY, command=self.open_bulk_editor).pack(side="left", padx=5, expand=True, fill="x")


        # 2. Graphics Section (New)
        self.gfx_frame_container = ctk.CTkFrame(self.middle_frame)
        self.gfx_frame_container.grid(row=1, column=0, sticky="nsew")
        
        # Header Row: Label + Offset + Load Pal + Load Gfx
        gfx_header = ctk.CTkFrame(self.gfx_frame_container, fg_color="transparent")
        gfx_header.pack(fill="x", pady=5, padx=5)
        
        ctk.CTkLabel(gfx_header, text="Graphics (4BPP)", font=Theme.FONT_BOLD).pack(side="left")
        
        ctk.CTkLabel(gfx_header, text="Offset (Hex):", font=("Arial", 11)).pack(side="left", padx=(10, 5))
        self.ent_gfx_offset = ctk.CTkEntry(gfx_header, width=50, height=24)
        self.ent_gfx_offset.insert(0, "0")
        self.ent_gfx_offset.pack(side="left")
        
        self.btn_load_pal = ctk.CTkButton(gfx_header, text="Load Palette (.bin)", width=120, command=self.load_palette, fg_color=Theme.BTN_INFO)
        self.btn_load_pal.pack(side="right", padx=5)
        
        self.btn_load_gfx = ctk.CTkButton(gfx_header, text="Load Graphics (.bin)", width=120, command=self.load_graphics)
        self.btn_load_gfx.pack(side="right", padx=5)

        # Scrollable Canvas area
        self.gfx_scroll = ctk.CTkScrollableFrame(self.gfx_frame_container, label_text="Preview")
        self.gfx_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.gfx_canvas = ctk.CTkCanvas(self.gfx_scroll, bg="#202020", highlightthickness=0, width=256, height=256)
        self.gfx_canvas.pack(anchor="nw", expand=True, fill="both")
        self.gfx_canvas.bind("<Button-1>", self.on_grid_click) # Left click
        
        self.width_in_tiles = 16
        self.gfx_scale = 3
        self.loaded_palette = None # List of (r,g,b)
        self.raw_pixels = None # Store raw pixels (0-15)

        self.entries = {}
        # Auto-load default
        success, msg = self.mapper.load_default_mappings()
        if not success:
            print(f"Auto-load failed: {msg}") 
        
        self.populate_grid()
        
    def open_bulk_editor(self):
        BulkEditorWindow(self.master, self.mapper, self.populate_grid)

    def save_settings(self, _=None):
        self.config.set("act_as", self.act_as_var.get())
        self.config.set("priority", self.prio_var.get())
        self.config.set("tile_size", self.tile_size_var.get())
        
    def save_settings_pal(self, val):
        self.config.set("palette", int(val))
        self.palette = int(val)
        self.refresh_graphics()
        
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

    def load_palette(self):
        filename = filedialog.askopenfilename(filetypes=[("SNES Palette", "*.bin;*.pal;*.tpl")])
        if not filename: return
        
        try:
             with open(filename, "rb") as f:
                 data = f.read()
             
             self.loaded_palette = SNESGraphics.decode_palette(data)
             
             if self.raw_pixels:
                 self.refresh_graphics()
                 
             from tkinter import messagebox
             messagebox.showinfo("Success", f"Loaded palette with {len(self.loaded_palette)} colors.")
             
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Failed to load palette: {e}")

    def load_graphics(self):
        filename = filedialog.askopenfilename(filetypes=[("SNES Graphics", "*.bin;*.gfx")])
        if not filename: return
        
        try:
            with open(filename, "rb") as f:
                data = f.read()
            
            pixels, num_tiles = SNESGraphics.decode_4bpp(data)
            
            if num_tiles == 0:
                 return

            self.width_in_tiles = 16 
            self.raw_pixels = pixels
            self.refresh_graphics()
            
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Failed to load graphics: {e}")

    def refresh_graphics(self):
        if not self.raw_pixels: return
        
        current_pal = None
        base_idx = self.palette * 16
        
        if self.loaded_palette and len(self.loaded_palette) >= base_idx + 16:
             current_pal = self.loaded_palette[base_idx : base_idx + 16]
        
        pil_img = SNESGraphics.create_image(self.raw_pixels, self.width_in_tiles, palette=current_pal)
        
        scale = self.gfx_scale
        pil_img = pil_img.resize((pil_img.width * scale, pil_img.height * scale), Image.NEAREST)
        
        self.gfx_image_tk = ImageTk.PhotoImage(pil_img)
        self.gfx_canvas.config(width=pil_img.width, height=pil_img.height)
        self.gfx_canvas.create_image(0, 0, anchor="nw", image=self.gfx_image_tk)
        self.gfx_canvas.configure(scrollregion=(0, 0, pil_img.width, pil_img.height))
        
        self.draw_grid(pil_img.width, pil_img.height, scale)

    def draw_grid(self, w, h, scale):
        tile_px = 8 * scale
        for x in range(0, w + 1, tile_px):
             self.gfx_canvas.create_line(x, 0, x, h, fill="#404040", width=1)
        for y in range(0, h + 1, tile_px):
             self.gfx_canvas.create_line(0, y, w, y, fill="#404040", width=1)

    def on_grid_click(self, event):
        if not getattr(self, 'gfx_image_tk', None): return
        
        x = self.gfx_canvas.canvasx(event.x)
        y = self.gfx_canvas.canvasy(event.y)
        scale = self.gfx_scale
        
        col = int(x // (8 * scale))
        row = int(y // (8 * scale))
        
        tile_index = row * self.width_in_tiles + col
        
        # Base Offset
        base_offset = 0
        try:
             base_offset = int(self.ent_gfx_offset.get(), 16)
        except: pass
        
        final_id = base_offset + tile_index
        hex_id = f"{final_id:03X}"
        
        # Assign to focused entry
        focused = self.master.focus_get()
        if focused and (isinstance(focused, ctk.CTkEntry) or "entry" in str(focused).lower()):
             try:
                 focused.delete(0, "end")
                 focused.insert(0, hex_id)
                 focused.event_generate("<FocusOut>")
             except Exception as e:
                 print(f"Could not paste to focused widget: {e}")
