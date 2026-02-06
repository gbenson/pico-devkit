from picoscroll import PicoScroll

scroll = PicoScroll()
scroll.show_bitmap_1d(bytearray(b"^E^@>*\x14\x00A\x006\x086\x01]Q="), 128, 0)
scroll.show()
