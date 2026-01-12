import unittest
import os
import json
from app.core.app_config import AppConfig

class TestPersistence(unittest.TestCase):
    def setUp(self):
        # Reset singleton and file
        if AppConfig._instance:
            AppConfig._instance = None
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")
            
        # Patch CONFIG_FILE for test
        AppConfig.CONFIG_FILE = "test_config.json"

    def tearDown(self):
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")

    def test_save_load(self):
        cfg = AppConfig()
        cfg.set("key", "value")
        
        # New instance should reload
        AppConfig._instance = None
        cfg2 = AppConfig()
        self.assertEqual(cfg2.get("key"), "value")

    def test_defaults(self):
        cfg = AppConfig()
        self.assertIsNone(cfg.get("nonexistent"))
        self.assertEqual(cfg.get("nonexistent", "default"), "default")

if __name__ == '__main__':
    unittest.main()
