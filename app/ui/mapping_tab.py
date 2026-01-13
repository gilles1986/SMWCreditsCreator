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
        
        # Grid layout (2 Columns) - Increased Col 1 Width (approx 300px)
        self.master.grid_columnconfigure(0, weight=0, minsize=320) # Col 1: Character Map
        self.master.grid_columnconfigure(1, weight=1) # Col 2: Settings + Graphics
        self.master.grid_columnconfigure(2, weight=0) # Remove Col 3
        self.master.grid_rowconfigure(0, weight=1)
        
        
        # --- Column 1: Character Map ---
        char_map_container = ctk.CTkFrame(self.master, fg_color="transparent")
        char_map_container.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Header with info icon and converter button
        header_frame = ctk.CTkFrame(char_map_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(header_frame, text="Character Map (Tile IDs)", font=Theme.FONT_BOLD).pack(side="left")
        
        info_btn = ctk.CTkButton(header_frame, text="ℹ", width=24, height=24, 
                                 font=("Arial", 14, "bold"), 
                                 fg_color="transparent", 
                                 hover_color=Theme.BTN_PRIMARY,
                                 command=self.show_character_map_help)
        info_btn.pack(side="left", padx=5)
        
        # Converter button (dynamic)
        self.btn_converter = ctk.CTkButton(header_frame, text="⇄ BG3", width=70, height=24,
                                          font=("Arial", 12, "bold"),
                                          fg_color=Theme.BTN_INFO,
                                          command=self.convert_mappings)
        self.btn_converter.pack(side="right", padx=5)
        
        self.scroll_frame = ctk.CTkScrollableFrame(char_map_container, width=290)
        self.scroll_frame.pack(fill="both", expand=True)

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
        self.opt_size = ctk.CTkOptionMenu(f1, variable=self.tile_size_var, values=["8x8", "8x16", "16x16"], command=self.on_tile_size_change, height=24)
        self.opt_size.pack(fill="x")
        
        f2 = create_compact_frame(1, 1)
        add_label(f2, "Palette", "Color palette index")
        self.pal_var = ctk.IntVar(value=self.palette)
        self.opt_pal = ctk.CTkOptionMenu(f2, variable=self.pal_var, values=[str(i) for i in range(8)], command=self.save_settings_pal, height=24)
        self.opt_pal.pack(fill="x")


        # Row 2: Action Buttons
        action_frame = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        action_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        
        ctk.CTkButton(action_frame, text="Load Mapping", width=80, command=self.load_mapping).pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(action_frame, text="Save Mapping", width=80, command=self.save_mapping).pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(action_frame, text="Bulk Editor", width=100, fg_color=Theme.BTN_SECONDARY, command=self.open_bulk_editor).pack(side="left", padx=5, expand=True, fill="x")


        # 2. Graphics Section
        self.gfx_frame_container = ctk.CTkFrame(self.middle_frame)
        self.gfx_frame_container.grid(row=1, column=0, sticky="nsew")
        
        # Header Row: Label + Offset + Load Pal + Load Gfx
        gfx_header = ctk.CTkFrame(self.gfx_frame_container, fg_color="transparent")
        gfx_header.pack(fill="x", pady=5, padx=5)
        
        ctk.CTkLabel(gfx_header, text="Graphics (4BPP)", font=Theme.FONT_BOLD).pack(side="left")
        
        # GFX Slot Dropdown (BG2/BG3)
        ctk.CTkLabel(gfx_header, text="GFX Slot:", font=("Arial", 11)).pack(side="left", padx=(10, 5))
        self.gfx_slot_var = ctk.StringVar(value="BG3")
        self.opt_gfx_slot = ctk.CTkOptionMenu(gfx_header, variable=self.gfx_slot_var, values=["BG2", "BG3"], width=70, command=self.refresh_graphics)
        self.opt_gfx_slot.pack(side="left")
        
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
        self.icon_labels = {}
        self.picker_target = None  # Track which entry is waiting for picker selection
        self.picker_sub_index = None # Index of sub-tile being picked (0=Top/TL, 1=Bottom/TR, etc)
        self.picker_sub_vals = [] # List of current tile IDs in composition 
        
        # Auto-load default
        success, msg = self.mapper.load_default_mappings()
        if not success:
            print(f"Auto-load failed: {msg}") 
        
        self.populate_grid()
        
    def open_bulk_editor(self):
        BulkEditorWindow(self.master, self.mapper, self.populate_grid)

    def show_character_map_help(self):
        from tkinter import messagebox
        help_text = (
            "Adding Custom Mappings:\n\n"
            "1. Bulk Editor: Use the 'Bulk Editor' button to map multiple characters at once.\n"
            "   Example: A-Z = 280\n\n"
            "2. mapping.json: Edit the mapping.json file directly and load it via 'Load Mapping'.\n"
            "   The file contains all character-to-tile assignments."
        )
        messagebox.showinfo("Character Map Help", help_text)

    def detect_current_bg(self):
        """Detect current BG slot based on 'A' character mapping"""
        a_mapping = self.mapper.get_mapping('A')
        if not a_mapping:
            return None
        
        try:
            tile_id = int(a_mapping, 16)
            if 0x200 <= tile_id <= 0x27F:
                return "BG2"
            elif 0x280 <= tile_id <= 0x2FF:
                return "BG3"
        except:
            pass
        return None
    
    def update_converter_button(self):
        """Update converter button text based on current BG"""
        current_bg = self.detect_current_bg()
        if current_bg == "BG2":
            self.btn_converter.configure(text="⇄ BG3")
        elif current_bg == "BG3":
            self.btn_converter.configure(text="⇄ BG2")
        else:
            self.btn_converter.configure(text="—", state="disabled")
            return
        self.btn_converter.configure(state="normal")
    
    def convert_mappings(self):
        """Convert all mappings between BG2 and BG3"""
        current_bg = self.detect_current_bg()
        if not current_bg:
            from tkinter import messagebox
            messagebox.showwarning("Conversion Error", "Cannot detect current BG slot from 'A' mapping.")
            return
        
        # Determine offset and target
        if current_bg == "BG2":
            offset = 0x80  # BG2 -> BG3 (+0x80)
            target_bg = "BG3"
        else:
            offset = -0x80  # BG3 -> BG2 (-0x80)
            target_bg = "BG2"
        
        # Convert all mappings
        converted_count = 0
        for char, entry in self.entries.items():
            val = entry.get().strip()
            if val:
                try:
                    tile_id = int(val, 16)
                    new_id = tile_id + offset
                    new_hex = f"{new_id:03X}"
                    entry.delete(0, "end")
                    entry.insert(0, new_hex)
                    self.mapper.set_mapping(char, new_hex)
                    converted_count += 1
                except:
                    pass
        
        # Switch GFX Slot
        self.gfx_slot_var.set(target_bg)
        
        # Update icons and button
        self.update_icons()
        self.update_converter_button()

    def on_tile_size_change(self, _=None):
        """Handle tile size change - update grid and icons"""
        self.save_settings()
        if self.raw_pixels:
            self.refresh_graphics()

    def save_settings(self, _=None):
        self.config.set("tile_size", self.tile_size_var.get())
        
    def save_settings_pal(self, val):
        self.config.set("palette", int(val))
        self.palette = int(val)
        self.refresh_graphics()

    def populate_grid(self):
        # Clear existing
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        # Get characters from mapper
        chars = self.mapper.get_default_characters() 
        for i, char in enumerate(chars):
            # Column 0: Label
            lbl_text = f"'{char}'" if char != ' ' else "'Space'"
            lbl = ctk.CTkLabel(self.scroll_frame, text=lbl_text, width=40, font=Theme.FONT_BOLD)
            lbl.grid(row=i, column=0, padx=5, pady=2, sticky="e")
            
            # Column 1: Entry
            entry = ctk.CTkEntry(self.scroll_frame, placeholder_text="Hex", width=60)
            entry.grid(row=i, column=1, padx=5, pady=2, sticky="w")
            
            # Column 2: Picker Button (skip for Space)
            if char != ' ':
                picker_btn = ctk.CTkButton(self.scroll_frame, text="🎯", width=28, height=28,
                                           font=("Arial", 14),
                                           fg_color=Theme.BTN_PRIMARY,
                                           command=lambda e=entry: self.activate_picker(e))
                picker_btn.grid(row=i, column=2, padx=2, pady=2)
            
            # Column 3: Icon (Visual Feedback)
            icon = ctk.CTkLabel(self.scroll_frame, text="", width=26, height=26)
            icon.grid(row=i, column=3, padx=5, pady=2, sticky="w")
            self.icon_labels[char] = icon

            val = self.mapper.get_mapping(char)
            
            # Set default for Space if not present
            if char == ' ' and not val:
                val = "00F8"
                self.mapper.set_mapping(char, val)
            
            if val:
                entry.insert(0, val)
            
            # Disable Space character input
            if char == ' ':
                entry.configure(state="disabled")
            else:
                entry.bind("<FocusOut>", lambda event, c=char, e=entry: self.update_mapping(c, e))
            
            self.entries[char] = entry
            
        # Update icons if graphics loaded
        if self.raw_pixels:
            self.update_icons()
        
        # Update converter button based on current mappings
        self.update_converter_button()
    
    def activate_picker(self, target_entry):
        """Activate picker mode for selecting a tile from the canvas"""
        self.picker_target = target_entry
        self.picker_sub_index = None
        self.picker_sub_vals = []

        # Visual feedback: highlight the target entry
        target_entry.configure(border_color=Theme.BTN_PRIMARY, border_width=2)
        
        # Change cursor globally
        self.master.configure(cursor="crosshair")
        self.gfx_canvas.configure(cursor="crosshair")
        
        # Bind click outside canvas to cancel
        self.master.bind("<Button-1>", self.on_picker_click, add="+")

        # Check Tile Size for Advanced Picker
        tile_size = self.tile_size_var.get()
        if tile_size == "8x8":
            # Standard single 8x8 picker
            return

        # --- Advanced Picker Setup ---
        
        # 1. Parse current values
        val = target_entry.get().strip()
        try:
             parts = [int(p, 16) for p in val.split(',') if p.strip()]
        except:
             parts = []
             
        # Default fallback if empty
        if not parts:
            parts = [0] * (2 if tile_size == "8x16" else 4)
            
        # Ensure correct length (pad or truncate)
        req_len = 2 if tile_size == "8x16" else 4
        if len(parts) < req_len:
             # Fill with sequential defaults based on first item (or 0)
             start = parts[0] if parts else 0
             if tile_size == "8x16":
                  parts = [start, start + 1]
             else: # 16x16
                  parts = [start, start+1, start+0x10, start+0x11]
        self.picker_sub_vals = parts[:req_len]
        
        # 2. Show Composition UI
        self.show_sub_picker_ui(tile_size)
    
    def show_sub_picker_ui(self, tile_size):
        # Remove existing if any
        if getattr(self, 'sub_picker_frame', None):
             self.sub_picker_frame.destroy()
             
        self.sub_picker_frame = ctk.CTkFrame(self.middle_frame, fg_color=Theme.BG_COLOR_2, border_width=1, border_color="#404040")
        self.sub_picker_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(10, 0)) # Insert between graphics and grid
        
        ctk.CTkLabel(self.sub_picker_frame, text="Composite Picker", font=("Arial", 11, "bold")).pack(pady=2)
        
        # Container for composition buttons
        comp_container = ctk.CTkFrame(self.sub_picker_frame, fg_color="transparent")
        comp_container.pack(pady=5, padx=5)
        
        self.sub_btns = []
        
        def make_btn(idx, txt):
             b = ctk.CTkButton(comp_container, text=txt, width=40, height=30, 
                               font=("Arial", 10),
                               fg_color=Theme.BTN_SECONDARY,
                               hover_color=Theme.BTN_PRIMARY,
                               command=lambda i=idx: self.set_sub_picker_index(i))
             b._sub_idx = idx
             return b

        # "Single" Button (Block Mode) -> Index None
        b_single = make_btn(None, "Block")
        b_single.pack(side="left", padx=5)
        self.sub_btns.append(b_single)
        
        # Separator
        ctk.CTkLabel(comp_container, text="|", text_color="gray").pack(side="left", padx=2)

        if tile_size == "8x16":
             # Vertical Stack
             # Layout: [ Block ] | [ Top ]
             #                   [ Btm ]
             
             stack_frame = ctk.CTkFrame(comp_container, fg_color="transparent")
             stack_frame.pack(side="left", padx=5)
             
             b_top = make_btn(0, "Top")
             b_top.pack(in_=stack_frame, side="top", pady=1)
             b_btm = make_btn(1, "Btm")
             b_btm.pack(in_=stack_frame, side="top", pady=1)
             self.sub_btns.extend([b_top, b_btm])
             
        elif tile_size == "16x16":
             # 2x2 Grid
             grid_frame = ctk.CTkFrame(comp_container, fg_color="transparent")
             grid_frame.pack(side="left", padx=5)
             
             f_top = ctk.CTkFrame(grid_frame, fg_color="transparent")
             f_top.pack()
             f_btm = ctk.CTkFrame(grid_frame, fg_color="transparent")
             f_btm.pack()
             
             b_tl = make_btn(0, "TL")
             b_tl.pack(in_=f_top, side="left", padx=1, pady=1)
             b_tr = make_btn(1, "TR")
             b_tr.pack(in_=f_top, side="left", padx=1, pady=1)
             
             b_bl = make_btn(2, "BL")
             b_bl.pack(in_=f_btm, side="left", padx=1, pady=1)
             b_br = make_btn(3, "BR")
             b_br.pack(in_=f_btm, side="left", padx=1, pady=1)
             self.sub_btns.extend([b_tl, b_tr, b_bl, b_br])

        # Select "Block" (None) by default
        self.set_sub_picker_index(None)

    def set_sub_picker_index(self, idx):
        self.picker_sub_index = idx
        # Update styling
        for btn in self.sub_btns:
             # Check semantic index stored on button
             btn_idx = getattr(btn, '_sub_idx', object())
             if btn_idx == idx:
                  btn.configure(fg_color=Theme.BTN_PRIMARY, border_color="white", border_width=1)
             else:
                  btn.configure(fg_color=Theme.BTN_SECONDARY, border_width=0)
            
    def update_mapping(self, char, entry):
        val = entry.get().strip()
        self.mapper.set_mapping(char, val)
        self.update_icons() # Trigger update

    def update_icons(self):
        if not self.raw_pixels or not getattr(self, 'full_pil_img', None):
             return
             
        slot = self.gfx_slot_var.get()
        base_offset = 0x200 if slot == "BG2" else 0x280
        
        # Get tile size
        tile_size = self.tile_size_var.get()
        scale = self.gfx_scale
        
        # Calculate tile dimensions for final icon
        if tile_size == "8x8":
            icon_w, icon_h = 8 * scale, 8 * scale
        elif tile_size == "8x16":
            icon_w, icon_h = 8 * scale, 16 * scale
        else:  # 16x16
            icon_w, icon_h = 16 * scale, 16 * scale
            
        w_tiles = self.width_in_tiles

        for char, entry in self.entries.items():
             val = entry.get().strip()
             if not val:
                 self.icon_labels[char].configure(image=None)
                 continue

             try:
                 # Parse IDs (handle comma-separation)
                 # e.g. "280,292" -> [280, 292]
                 ids = []
                 parts = val.split(',')
                 for p in parts:
                     if p.strip():
                        ids.append(int(p.strip(), 16))
                 
                 # Create composite image
                 if not ids:
                     self.icon_labels[char].configure(image=None)
                     continue
                     
                 # Determine logic based on tile size
                 # Case 1: 8x8 -> Just take first ID
                 # Case 2: 8x16 -> Expect 2 IDs (Top, Bottom). If 1 ID, calculate bottom = ID+1 (legacy fallback)
                 # Case 3: 16x16 -> Expect 4 IDs (TL, TR, BL, BR). If 1 ID, calculate standard block logic.
                 
                 # Create blank canvas for icon
                 from PIL import Image
                 composite = Image.new("RGB", (icon_w, icon_h), (0, 0, 0))
                 
                 # Helper to get crop
                 def get_crop(tid):
                     local_idx = tid - base_offset
                     if 0 <= local_idx < (len(self.raw_pixels)//64):
                         row = local_idx // w_tiles
                         col = local_idx % w_tiles
                         px = 8 * scale
                         x = col * px
                         y = row * px
                         return self.full_pil_img.crop((x, y, x+px, y+px))
                     return None

                 # Draw Logic
                 draw_success = False
                 px = 8 * scale
                 
                 if tile_size == "8x8":
                     crop = get_crop(ids[0])
                     if crop:
                         composite.paste(crop, (0, 0))
                         draw_success = True
                         
                 elif tile_size == "8x16":
                     # Top Tile
                     t1 = ids[0]
                     crop1 = get_crop(t1)
                     if crop1: composite.paste(crop1, (0, 0))
                     
                     # Bottom Tile
                     if len(ids) >= 2:
                         t2 = ids[1]
                     else:
                         t2 = t1 + 1 # Fallback standard
                     
                     crop2 = get_crop(t2)
                     if crop2: composite.paste(crop2, (0, px))
                     draw_success = True
                     
                 elif tile_size == "16x16":
                     # TL
                     t1 = ids[0]
                     c1 = get_crop(t1)
                     if c1: composite.paste(c1, (0, 0))
                     
                     if len(ids) >= 4:
                         t2, t3, t4 = ids[1], ids[2], ids[3]
                     else:
                         # Fallback standard
                         t2, t3, t4 = t1+1, t1+0x10, t1+0x11
                     
                     c2 = get_crop(t2) # TR
                     if c2: composite.paste(c2, (px, 0))
                     c3 = get_crop(t3) # BL
                     if c3: composite.paste(c3, (0, px))
                     c4 = get_crop(t4) # BR
                     if c4: composite.paste(c4, (px, px))
                     draw_success = True

                 if draw_success:
                      img = ctk.CTkImage(light_image=composite, dark_image=composite, size=(icon_w, icon_h))
                      self.icon_labels[char].configure(image=img)
                      self.icon_labels[char]._image = img 
                 else:
                      self.icon_labels[char].configure(image=None)
                      
             except Exception as e:
                 # Silently fail
                 self.icon_labels[char].configure(image=None)

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

    def refresh_graphics(self, _=None):
        if not self.raw_pixels: return
        
        current_pal = None
        base_idx = self.palette * 16
        
        if self.loaded_palette and len(self.loaded_palette) >= base_idx + 16:
             current_pal = self.loaded_palette[base_idx : base_idx + 16]
        
        pil_img = SNESGraphics.create_image(self.raw_pixels, self.width_in_tiles, palette=current_pal)
        
        scale = self.gfx_scale
        pil_img = pil_img.resize((pil_img.width * scale, pil_img.height * scale), Image.NEAREST)
        self.full_pil_img = pil_img
        
        self.gfx_image_tk = ImageTk.PhotoImage(pil_img)
        self.gfx_canvas.config(width=pil_img.width, height=pil_img.height)
        self.gfx_canvas.create_image(0, 0, anchor="nw", image=self.gfx_image_tk)
        self.gfx_canvas.configure(scrollregion=(0, 0, pil_img.width, pil_img.height))
        
        self.draw_grid(pil_img.width, pil_img.height, scale)
        self.update_icons()  # Update character icons with loaded graphics

    def draw_grid(self, w, h, scale):
        tile_size = self.tile_size_var.get()
        
        # Calculate grid spacing based on tile size
        if tile_size == "8x8":
            tile_w_px, tile_h_px = 8 * scale, 8 * scale
        elif tile_size == "8x16":
            tile_w_px, tile_h_px = 8 * scale, 16 * scale
        else:  # 16x16
            tile_w_px, tile_h_px = 16 * scale, 16 * scale
        
        # Draw vertical lines
        for x in range(0, w + 1, tile_w_px):
             self.gfx_canvas.create_line(x, 0, x, h, fill="#404040", width=1)
        # Draw horizontal lines
        for y in range(0, h + 1, tile_h_px):
             self.gfx_canvas.create_line(0, y, w, y, fill="#404040", width=1)

    def on_picker_click(self, event):
        """Handle clicks during picker mode (cancel if outside canvas)"""
        if not self.picker_target:
            return
        
        # Check if click is on canvas
        widget = event.widget
        if widget == self.gfx_canvas or str(widget).startswith(str(self.gfx_canvas)):
            # Click is on canvas, let on_grid_click handle it
            return
        
        # Click is outside canvas - cancel picker mode
        self.cancel_picker()
    
    def cancel_picker(self):
        """Cancel picker mode and reset UI"""
        if self.picker_target:
            self.picker_target.configure(border_width=1)
            self.picker_target = None
        
        self.picker_sub_index = None
        self.picker_sub_vals = []
        
        if getattr(self, 'sub_picker_frame', None):
             self.sub_picker_frame.destroy()
             self.sub_picker_frame = None

        self.master.configure(cursor="")
        self.gfx_canvas.configure(cursor="")
        self.master.unbind("<Button-1>")
    
    def on_grid_click(self, event):
        if not getattr(self, 'gfx_image_tk', None): return
        
        x = self.gfx_canvas.canvasx(event.x)
        y = self.gfx_canvas.canvasy(event.y)
        scale = self.gfx_scale
        
        # Get tile size
        tile_size = self.tile_size_var.get()
        
        # Calculate which tile grid cell was clicked (always in 8x8 units)
        col_8x8 = int(x // (8 * scale))
        row_8x8 = int(y // (8 * scale))
        
        # Snap to tile grid based on tile size (ONLY IF NOT IN SUB-PICKER MODE)
        if self.picker_sub_index is None:
            if tile_size == "8x16":
                # Snap to 8x16 grid (vertical pairs)
                row_8x8 = (row_8x8 // 2) * 2
            elif tile_size == "16x16":
                # Snap to 16x16 grid (2x2 blocks)
                col_8x8 = (col_8x8 // 2) * 2
                row_8x8 = (row_8x8 // 2) * 2
        
        # Calculate base tile index (top-left 8x8 tile)
        tile_index = row_8x8 * self.width_in_tiles + col_8x8
        
        # Base Offset from Slot
        slot = self.gfx_slot_var.get()
        base_offset = 0x200 if slot == "BG2" else 0x280

        final_id = base_offset + tile_index
        hex_id = f"{final_id:03X}"
        
        # Priority 1: Picker mode (if active)
        if self.picker_target:
            try:
                # ADVANCED PICKER MODE (Sub-Picker)
                if self.picker_sub_index is not None:
                     # Update specific slot
                     idx = self.picker_sub_index
                     if 0 <= idx < len(self.picker_sub_vals):
                          self.picker_sub_vals[idx] = final_id
                     
                     # Construct comma-string
                     new_val = ",".join([f"{x:03X}" for x in self.picker_sub_vals])
                     
                     self.picker_target.delete(0, "end")
                     self.picker_target.insert(0, new_val)
                     self.picker_target.event_generate("<FocusOut>")
                     
                     # Do NOT cancel picker - allow picking next part
                     # Maybe auto-advance? Let's keep it manual for now or user request.
                     self.update_icons()
                     return

                # STANDARD PICKER MODE
                self.picker_target.delete(0, "end")
                self.picker_target.insert(0, hex_id)
                self.picker_target.event_generate("<FocusOut>")
                # Reset picker mode
                self.cancel_picker()
                # Trigger icon update immediately
                self.update_icons()
            except Exception as e:
                print(f"Picker error: {e}")
            return
        
        # Priority 2: Assign to focused entry (fallback)
        focused = self.master.focus_get()
        if focused and (isinstance(focused, ctk.CTkEntry) or "entry" in str(focused).lower()):
             try:
                 focused.delete(0, "end")
                 focused.insert(0, hex_id)
                 focused.event_generate("<FocusOut>")
             except Exception as e:
                 print(f"Could not paste to focused widget: {e}")
