import unittest
import os
import shutil
import tempfile
import json
import toml
from app.core.validator import Validator
from app.core.config_manager import ConfigManager
from app.core.mapper import Mapper

class TestCore(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.project_path = os.path.join(self.test_dir, "MyProject")
        os.makedirs(self.project_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_validator_valid(self):
        # Create changelog.txt
        with open(os.path.join(self.project_path, "changelog.txt"), "w") as f:
            f.write("Some text\nv5.10\nSome more text")
        
        valid, msg = Validator.validate_folder(self.project_path)
        self.assertTrue(valid)
        self.assertIn("Detected: v5.10", msg)

    def test_validator_invalid_missing_file(self):
        valid, msg = Validator.validate_folder(self.project_path)
        self.assertFalse(valid)
        self.assertIn("changelog.txt", msg)

    def test_validator_invalid_version(self):
        with open(os.path.join(self.project_path, "changelog.txt"), "w") as f:
            f.write("v5.09")
        valid, msg = Validator.validate_folder(self.project_path)
        self.assertFalse(valid)

    def test_rhr_version(self):
        # Test Callisto check
        tools_dir = os.path.join(self.project_path, "tools", "Callisto")
        os.makedirs(tools_dir)
        version = Validator.get_rhr_version(self.project_path)
        self.assertEqual(version, ">=5.13")

    def test_rhr_version_old(self):
        version = Validator.get_rhr_version(self.project_path)
        self.assertEqual(version, "<5.13")

    def test_config_check_and_fix(self):
        # Setup config
        buildtool = os.path.join(self.project_path, "buildtool")
        os.makedirs(buildtool)
        config_path = os.path.join(buildtool, "exports.toml")
        
        data = {"resources": {"use_text_map16_format": False}}
        with open(config_path, "w") as f:
            toml.dump(data, f)

        # Check
        valid, msg = ConfigManager.check_exports_toml(self.project_path, "<5.13")
        self.assertFalse(valid)
        
        # Fix
        success, msg = ConfigManager.fix_exports_toml(self.project_path, "<5.13")
        self.assertTrue(success)

        # Re-check
        valid, msg = ConfigManager.check_exports_toml(self.project_path, "<5.13")
        self.assertTrue(valid)

    def test_mapper(self):
        m = Mapper()
        m.set_mapping("A", "80")
        self.assertEqual(m.get_mapping("A"), "80")
        
        # Save load
        save_path = os.path.join(self.test_dir, "map.json")
        m.save_mappings(save_path)
        
        m2 = Mapper()
        m2.load_mappings(save_path)
        self.assertEqual(m2.get_mapping("A"), "80")

if __name__ == '__main__':
    unittest.main()
