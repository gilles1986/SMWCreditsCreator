import json
import os
import logging

logger = logging.getLogger(__name__)

class AppConfig:
    CONFIG_FILE = "config.json"
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
            cls._instance.data = {}
            cls._instance.load()
        return cls._instance

    TEMPLATE_FILE = "config.template.json"

    def load(self):
        # Initial template copy if missing
        if not os.path.exists(self.CONFIG_FILE):
             if os.path.exists(self.TEMPLATE_FILE):
                 import shutil
                 try:
                     shutil.copy(self.TEMPLATE_FILE, self.CONFIG_FILE)
                     logger.info(f"Initialized {self.CONFIG_FILE} from template.")
                 except Exception as e:
                     logger.error(f"Could not copy template: {e}")

        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    self.data = json.load(f)
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                self.data = {}
        else:
            self.data = {}

    def save(self):
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving config: {e}")

    # Accessors
    def get(self, key, default=None):
        return self.data.get(key, default)
        
    def set(self, key, value):
        self.data[key] = value
        self.save() # Auto-save on set

    def set_many(self, updates):
        """Set multiple keys at once with a single disk write."""
        self.data.update(updates)
        self.save()
