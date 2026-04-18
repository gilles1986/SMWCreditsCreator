import unittest
from app.core.validator import Validator
from app.core.mapper import Mapper


class TestValidateTileId(unittest.TestCase):
    """Tests for Validator.validate_tile_id()"""

    def test_valid_3digit_hex(self):
        self.assertTrue(Validator.validate_tile_id("280")[0])
        self.assertTrue(Validator.validate_tile_id("0F8")[0])
        self.assertTrue(Validator.validate_tile_id("3FF")[0])
        self.assertTrue(Validator.validate_tile_id("000")[0])

    def test_valid_1digit_hex(self):
        self.assertTrue(Validator.validate_tile_id("0")[0])
        self.assertTrue(Validator.validate_tile_id("F")[0])

    def test_valid_lowercase_hex(self):
        self.assertTrue(Validator.validate_tile_id("2b0")[0])
        self.assertTrue(Validator.validate_tile_id("0f8")[0])

    def test_valid_with_flags(self):
        self.assertTrue(Validator.validate_tile_id("280:xy")[0])
        self.assertTrue(Validator.validate_tile_id("280:x")[0])
        self.assertTrue(Validator.validate_tile_id("280:yp")[0])

    def test_invalid_empty(self):
        valid, msg = Validator.validate_tile_id("")
        self.assertFalse(valid)
        self.assertIn("Empty", msg)

    def test_invalid_none(self):
        valid, msg = Validator.validate_tile_id(None)
        self.assertFalse(valid)

    def test_invalid_non_hex_chars(self):
        valid, msg = Validator.validate_tile_id("sssss")
        self.assertFalse(valid)
        self.assertIn("invalid hex", msg.lower())

    def test_invalid_partial_hex(self):
        valid, msg = Validator.validate_tile_id("28G")
        self.assertFalse(valid)

    def test_invalid_random_string(self):
        valid, msg = Validator.validate_tile_id("ll")
        self.assertFalse(valid)

    def test_out_of_range_high(self):
        valid, msg = Validator.validate_tile_id("400")
        self.assertFalse(valid)
        self.assertIn("out of range", msg.lower())

    def test_out_of_range_very_high(self):
        valid, msg = Validator.validate_tile_id("FFFF")
        self.assertFalse(valid)

    def test_boundary_max(self):
        self.assertTrue(Validator.validate_tile_id("3FF")[0])

    def test_boundary_just_over(self):
        self.assertFalse(Validator.validate_tile_id("400")[0])

    def test_whitespace_handling(self):
        self.assertTrue(Validator.validate_tile_id("  280  ")[0])

    def test_with_0x_prefix_invalid(self):
        valid, msg = Validator.validate_tile_id("0x280")
        self.assertFalse(valid)
        self.assertIn("invalid hex", msg.lower())


class TestValidateMappingValue(unittest.TestCase):
    """Tests for Validator.validate_mapping_value()"""

    def test_simple_valid(self):
        self.assertTrue(Validator.validate_mapping_value("280")[0])

    def test_with_flags_valid(self):
        self.assertTrue(Validator.validate_mapping_value("280:xy")[0])

    def test_comma_separated_valid(self):
        self.assertTrue(Validator.validate_mapping_value("280, 290")[0])

    def test_comma_with_flags_valid(self):
        self.assertTrue(Validator.validate_mapping_value("280:x, 290:y")[0])

    def test_four_part_composite_valid(self):
        self.assertTrue(Validator.validate_mapping_value("280, 281, 290, 291")[0])

    def test_invalid_single(self):
        valid, msg = Validator.validate_mapping_value("sssss")
        self.assertFalse(valid)

    def test_invalid_in_composite(self):
        valid, msg = Validator.validate_mapping_value("280, ZZZ")
        self.assertFalse(valid)

    def test_empty_string(self):
        valid, msg = Validator.validate_mapping_value("")
        self.assertFalse(valid)

    def test_none(self):
        valid, msg = Validator.validate_mapping_value(None)
        self.assertFalse(valid)

    def test_out_of_range_composite(self):
        valid, msg = Validator.validate_mapping_value("280, FFF")
        self.assertFalse(valid)


class TestValidateAllMappings(unittest.TestCase):
    """Tests for Validator.validate_all_mappings()"""

    def test_all_valid(self):
        mappings = {"A": "280", "B": "281", "C": "282"}
        valid, errors = Validator.validate_all_mappings(mappings)
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)

    def test_one_invalid(self):
        mappings = {"A": "280", "B": "sssss", "C": "282"}
        valid, errors = Validator.validate_all_mappings(mappings)
        self.assertFalse(valid)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0][0], "B")

    def test_empty_value_ok(self):
        mappings = {"A": "280", "B": "", "C": "282"}
        valid, errors = Validator.validate_all_mappings(mappings)
        self.assertTrue(valid)

    def test_space_skipped(self):
        mappings = {" ": "bad_value", "A": "280"}
        valid, errors = Validator.validate_all_mappings(mappings)
        self.assertTrue(valid)

    def test_multiple_invalid(self):
        mappings = {"A": "GGG", "B": "HHH", "C": "282"}
        valid, errors = Validator.validate_all_mappings(mappings)
        self.assertFalse(valid)
        self.assertEqual(len(errors), 2)


class TestMapperValidation(unittest.TestCase):
    """Tests for validation integrated into Mapper"""

    def test_validate_mapping_valid(self):
        m = Mapper()
        valid, msg = m.validate_mapping("A", "280")
        self.assertTrue(valid)

    def test_validate_mapping_invalid(self):
        m = Mapper()
        valid, msg = m.validate_mapping("A", "sssss")
        self.assertFalse(valid)

    def test_validate_mapping_empty_ok(self):
        m = Mapper()
        valid, msg = m.validate_mapping("A", "")
        self.assertTrue(valid)

    def test_bulk_rules_invalid_hex(self):
        m = Mapper()
        success, msg = m.apply_bulk_rules("A = ZZZ")
        self.assertTrue(success)  # apply_bulk_rules returns True even with skipped lines
        self.assertIn("Invalid hex", msg)
        self.assertEqual(m.get_mapping("A"), "")  # Should not be mapped

    def test_bulk_rules_out_of_range(self):
        m = Mapper()
        success, msg = m.apply_bulk_rules("A = FFF")
        self.assertTrue(success)
        self.assertIn("out of range", msg.lower())

    def test_bulk_range_overflow(self):
        m = Mapper()
        success, msg = m.apply_bulk_rules("A-Z = 3F0")
        self.assertTrue(success)
        self.assertIn("overflow", msg.lower())

    def test_bulk_comma_invalid(self):
        m = Mapper()
        success, msg = m.apply_bulk_rules("A = ZZZ, 280")
        self.assertTrue(success)
        self.assertIn("Invalid hex", msg)

    def test_bulk_valid_range(self):
        m = Mapper()
        m.mappings.clear()
        success, msg = m.apply_bulk_rules("A-C = 280")
        self.assertTrue(success)
        self.assertEqual(m.get_mapping("A"), "280")
        self.assertEqual(m.get_mapping("B"), "281")
        self.assertEqual(m.get_mapping("C"), "282")


if __name__ == '__main__':
    unittest.main()
