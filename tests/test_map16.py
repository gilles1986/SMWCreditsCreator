import unittest
from app.core.map16_handler import Map16Handler, Map16Tile, Map16SubTile

class TestMap16(unittest.TestCase):
    def test_subtile_tostring(self):
        st = Map16SubTile("287", 0, False, False, False)
        self.assertEqual(st.to_string(), "287 0 ---")
        
        st2 = Map16SubTile("123", 4, True, True, True)
        self.assertEqual(st2.to_string(), "123 4 xyp")

    def test_tile_tostring_empty(self):
        t = Map16Tile("6006")
        t.is_empty = True
        self.assertEqual(t.to_line(), "6006: ~\n")

    def test_tile_tostring_full(self):
        # 6000: 0130 { 287 0 ---  0F8 2 ---  2B0 0 ---  0F8 2 --- }
        st1 = Map16SubTile("287", 0)
        st2 = Map16SubTile("0F8", 2)
        st3 = Map16SubTile("2B0", 0)
        st4 = Map16SubTile("0F8", 2)
        
        t = Map16Tile("6000", "0130", [st1, st2, st3, st4])
        expected = "6000: 0130 { 287 0 ---  0F8 2 ---  2B0 0 ---  0F8 2 --- }\n"
        self.assertEqual(t.to_line(), expected)

    def test_parse_line_full(self):
        line = "6000: 0130 { 287 0 ---  0F8 2 x--  2B0 0 -y-  0F8 2 --p }"
        tile = Map16Handler.parse_line(line)
        self.assertIsNotNone(tile)
        self.assertEqual(tile.tile_number, "6000")
        self.assertEqual(tile.act_as, "0130")
        self.assertEqual(len(tile.sub_tiles), 4)
        
        self.assertEqual(tile.sub_tiles[0].tile_id, "287")
        self.assertFalse(tile.sub_tiles[0].flip_x)
        
        self.assertEqual(tile.sub_tiles[1].palette, 2)
        self.assertTrue(tile.sub_tiles[1].flip_x)
        
        self.assertTrue(tile.sub_tiles[2].flip_y)
        self.assertTrue(tile.sub_tiles[3].priority)

    def test_parse_line_empty(self):
        line = "6006: ~"
        tile = Map16Handler.parse_line(line)
        self.assertIsNotNone(tile)
        self.assertTrue(tile.is_empty)
        self.assertEqual(tile.tile_number, "6006")

if __name__ == '__main__':
    unittest.main()
