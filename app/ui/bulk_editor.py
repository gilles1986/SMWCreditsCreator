import customtkinter as ctk
from app.ui.theme import Theme

class BulkEditorWindow(ctk.CTkToplevel):
    def __init__(self, parent, mapper, on_apply_callback):
        super().__init__(parent)
        self.mapper = mapper
        self.on_apply_callback = on_apply_callback
        
        self.title("Bulk Mapping Editor")
        self.geometry("400x500")
        
        # Make modal-ish
        self.transient(parent) 
        # self.grab_set() # Disabled to allow checking tooltips in main window 
        
        self.lbl_title = ctk.CTkLabel(self, text="Bulk Rules", font=Theme.FONT_BOLD)
        self.lbl_title.pack(pady=10)
        
        # Header text
        ctk.CTkLabel(self, text="Enter mapping rules below.", text_color=Theme.TEXT_DIM).pack(pady=(0,5))
        
        # Text Area
        self.txt_bulk = ctk.CTkTextbox(self)
        self.txt_bulk.pack(padx=10, pady=5, fill="both", expand=True)

        default_bulk = """# Example Bulk Rules
A-Z = 280
a-z = 2B0
[:'"/°-] = 29A 
0-9 = 2A0
[.&*,!?] = 2AA
"""
        self.txt_bulk.insert("0.0", default_bulk)
        
        # Buttons
        curr_frame = ctk.CTkFrame(self, fg_color="transparent")
        curr_frame.pack(fill="x", pady=5, padx=10)
        
        self.var_clear = ctk.BooleanVar(value=False)
        self.chk_clear = ctk.CTkCheckBox(self, text="Clear existing mappings first", variable=self.var_clear)
        self.chk_clear.pack(pady=(0, 10))
        
        ctk.CTkButton(curr_frame, text="?", width=40, command=self.show_help).pack(side="left")
        ctk.CTkButton(curr_frame, text="Apply Rules", command=self.apply_bulk).pack(side="left", padx=10, fill="x", expand=True)
        ctk.CTkButton(curr_frame, text="Close", width=60, fg_color="gray", command=self.destroy).pack(side="right")

    def show_help(self):
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

    def apply_bulk(self):
        rules = self.txt_bulk.get("1.0", "end")
        clear_val = self.var_clear.get()
        success, msg = self.mapper.apply_bulk_rules(rules, clear_first=clear_val)
        if success:
            if self.on_apply_callback:
                self.on_apply_callback()
            self.destroy()
        else:
             from tkinter import messagebox
             messagebox.showerror("Error", msg)
