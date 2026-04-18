import logging
import sys
import traceback
import customtkinter as ctk
from tkinter import messagebox

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='app.log',
                    filemode='a')

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        from app.ui.main_window import MainWindow
        logger.info("Starting SMW Credits Creator")
        app = MainWindow()
        app.mainloop()
    except Exception as e:
        logger.critical("Fatal Error", exc_info=True)
        # Show error window
        root = None
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
        except Exception:
             pass
        
        err_msg = "".join(traceback.format_exception(None, e, e.__traceback__))
        messagebox.showerror("Critical Error", f"Failed to start:\n{err_msg}")
        if root: root.destroy()
