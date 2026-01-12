import unittest
from app.core.mapper import Mapper

class TestMapperBulk(unittest.TestCase):
    def setUp(self):
        self.mapper = Mapper()

    def test_single_mapping(self):
        rule = "! = 100"
        success, msg = self.mapper.apply_bulk_rules(rule)
        self.assertTrue(success)
        self.assertEqual(self.mapper.get_mapping("!"), "100")

    def test_range_mapping(self):
        self.mapper.mappings.clear()
        rule = "A-C = 100"
        # Expect A=100, B=101, C=102
        success, msg = self.mapper.apply_bulk_rules(rule)
        self.assertTrue(success)
        self.assertEqual(self.mapper.get_mapping("A"), "100")
        self.assertEqual(self.mapper.get_mapping("B"), "101")
        self.assertEqual(self.mapper.get_mapping("C"), "102")

    def test_range_hex_math(self):
        self.mapper.mappings.clear()
        rule = "A-B = 109"
        # Expect A=109, B=10A
        success, msg = self.mapper.apply_bulk_rules(rule)
        self.assertTrue(success)
        self.assertEqual(self.mapper.get_mapping("A"), "109")
        self.assertEqual(self.mapper.get_mapping("B"), "10A")

    def test_overlap_overwrite(self):
        self.mapper.mappings.clear()
        rules = "A-B = 100\nB = 200"
        # Expect A=100, B=200
        success, msg = self.mapper.apply_bulk_rules(rules)
        self.assertTrue(success)
        self.assertEqual(self.mapper.get_mapping("A"), "100")
        self.assertEqual(self.mapper.get_mapping("B"), "200")

    def test_invalid_syntax_recovery(self):
        rules = "InvalidLine\nA = 100"
        success, msg = self.mapper.apply_bulk_rules(rules)
        self.assertTrue(success) # Should succeed partially
        self.assertIn("Skipped invalid line", msg)
        self.assertEqual(self.mapper.get_mapping("A"), "100")

    def test_bracket_set(self):
        self.mapper.mappings.clear()
        rule = "[ABC] = 100"
        success, msg = self.mapper.apply_bulk_rules(rule)
        self.assertTrue(success)
        self.assertEqual(self.mapper.get_mapping("A"), "100")
        self.assertEqual(self.mapper.get_mapping("B"), "101")
        self.assertEqual(self.mapper.get_mapping("C"), "102")

    def test_bracket_escaping(self):
        self.mapper.mappings.clear()
        rule = r"[\[\]\\] = 200" # Maps [, ], \
        success, msg = self.mapper.apply_bulk_rules(rule)
        self.assertTrue(success)
        self.assertEqual(self.mapper.get_mapping("["), "200")
        self.assertEqual(self.mapper.get_mapping("]"), "201")
        self.assertEqual(self.mapper.get_mapping("\\"), "202")

if __name__ == '__main__':
    unittest.main()
