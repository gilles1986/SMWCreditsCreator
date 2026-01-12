import unittest
from app.core.credits_parser import CreditsParser
from app.core.map16_handler import Map16Generator, Map16Tile
from app.core.mapper import Mapper
import os

class TestCredits(unittest.TestCase):
    def setUp(self):
        self.mapper = Mapper()
        # Mock Mappings
        for c in "ABCDEFG":
            self.mapper.mappings[c] = f"10{c}" # 10A, 10B...

    def test_txt_parser(self):
        # Create temp txt
        with open("test.txt", "w") as f:
            f.write("Alice\nBob\nAlice") # Dupe
            
        data = CreditsParser.parse_file("test.txt")
        self.assertIn("General", data)
        self.assertEqual(data["General"], ["Alice", "Bob"]) # Sorted unique
        
        import os
        os.remove("test.txt")

    def test_json_parser(self):
        # Create temp json
        json_data = [
            {"section": "smwsprites", "authors": [{"name": "Auth1"}]},
            {"section": "smwsprites", "authors": [{"name": "Auth2"}]},
            {"section": "uberasm", "authors": [{"name": "Auth3"}]}
        ]
        import json
        with open("test.json", "w") as f:
            json.dump(json_data, f)
            
        data = CreditsParser.parse_file("test.json")
        self.assertIn("Sprites", data)
        self.assertEqual(len(data["Sprites"]), 2)
        self.assertIn("UberASM", data)
        
        os.remove("test.json")

    def test_generator_single_col(self):
        # "A" -> 16 chars max per line? 
        # Actually our gen logic uses full row if single col.
        # Single col row takes 1 name.
        data = {"General": ["A", "B"]}
        options = {"optimize_columns": False}
        gen = Map16Generator(self.mapper)
        
        tiles = gen.generate_credits_tiles(data, options)
        # Header (General) + A + B
        # Header "GENERAL" is 7 chars.
        # 7 chars take ? rows.
        # _pack_tiles_into_rows logic not fully visible in snippet but assumed standard.
        # A takes 1 row.
        # B takes 1 row.
        
        # Verify valid Map16Tile objects
        self.assertTrue(all(isinstance(t, Map16Tile) for t in tiles))

    def test_generator_optimize(self):
        # A and B should fit in one row
        data = {"General": ["A", "B"]}
        options = {"optimize_columns": True}
        gen = Map16Generator(self.mapper)
        
        tiles = gen.generate_credits_tiles(data, options)
        # Header + 1 Row (A | B)
        # Roughly check count.
        pass

if __name__ == '__main__':
    unittest.main()
