import toml
import os
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    @staticmethod
    def get_config_path(project_path, version):
        if version == ">=5.13":
            return os.path.join(project_path, "tools", "Callisto", "exports.toml")
        else:
            return os.path.join(project_path, "buildtool", "exports.toml")

    @staticmethod
    def check_exports_toml(project_path, version):
        """
        Checks if use_text_map16_format is True in exports.toml.
        Returns:
            (bool) True if config is correct (or doesn't need fix), False if it needs fixing.
            (str) Status message or error.
        """
        config_path = ConfigManager.get_config_path(project_path, version)
        
        if not os.path.exists(config_path):
            return False, f"Config file not found at {config_path}"

        try:
            config = toml.load(config_path)
            # Assuming structure [resources] use_text_map16_format based on context, 
            # OR top level if not specified. Usually Callisto configs are structured.
            # Let's search recursively or check common locations.
            # In RHR/Callisto, it's typically under a specific section or root. 
            # I'll check root first, then 'resources' if that's a thing.
            # UPDATE: Callisto usually uses `[resources]` or `[settings]`. 
            # Let's try to find the key `use_text_map16_format`.
            
            # Simple recursive search helper
            def find_key(data, key):
                if key in data:
                    return data[key]
                for k, v in data.items():
                    if isinstance(v, dict):
                        res = find_key(v, key)
                        if res is not None:
                            return res
                return None

            val = find_key(config, "use_text_map16_format")
            
            if val is True:
                return True, "Config is correct."
            elif val is False:
                return False, "use_text_map16_format is False."
            else:
                # Key not found, might default to False?
                # User said: "checken, ob use_text_map16_format auf false ist".
                # If missing, it's likely using default which might be binary (False).
                return False, "use_text_map16_format not found (Default used?)."

        except Exception as e:
            logger.error(f"Error reading config: {e}")
            return False, f"Error reading config: {e}"

    @staticmethod
    def fix_exports_toml(project_path, version):
        config_path = ConfigManager.get_config_path(project_path, version)
        
        try:
            with open(config_path, 'r') as f:
                config = toml.load(f)

            # We need to set it. Where? 
            # If we didn't find it before, we might need to know where to add it.
            # Usually it's in the root for some Callisto versions OR specific table.
            # Safest is to find it and update, or Append if missing?
            # User instructions "exports.toml ... checken ...".
            # For now, let's look for the key to update, if not found, add to root?
            # Or asking USER might be better if I am unsure of structure.
            # But I need to be proactive. 
            # Let's assume top level or [resources] if [resources] exists.
            
            updated = False
            
            def update_key(data, key, value):
                if key in data:
                    data[key] = value
                    return True
                for k, v in data.items():
                    if isinstance(v, dict):
                        if update_key(v, key, value):
                            return True
                return False

            if not update_key(config, "use_text_map16_format", True):
                # If not found, add it.
                # If [resources] exists, add there.
                if "resources" in config:
                     config["resources"]["use_text_map16_format"] = True
                else:
                    config["use_text_map16_format"] = True

            with open(config_path, 'w') as f:
                toml.dump(config, f)
            
            return True, "Config updated."

        except Exception as e:
            logger.error(f"Error fixing config: {e}")
            return False, f"Error fixing config: {e}"
