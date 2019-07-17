from unittest import TestCase
from daikin.daikin import DaikinMessage, DaikinState


def get_hex(frame):
    return [hex(field) for field in frame]


def skip_header_and_checksum(frame):
    return frame[4:][:-1]


class TestTools(TestCase):
    def test_skip(self):
        frame = [0, 1, 2, 3, 4, 5, 6, 7]
        expected = [4, 5, 6]
        self.assertEqual(skip_header_and_checksum(frame), expected)


class TestDaikinMessage(TestCase):
    def setUp(self):
        self.state = DaikinState()
        self.message = DaikinMessage(self.state)

    def assertFrameData(self, expected, frame):
        trimmed = skip_header_and_checksum(frame)
        hexed = get_hex(trimmed)
        self.assertEqual(expected, hexed)

    def test_frame_one_comfort_off(self):

        expected = [
            '0xc5',
            '0x0',
            '0x0',
        ]
        self.assertFrameData(expected, self.message.frame_one)

    def test_frame_one_comfort_on(self):
        self.state.comfort = True
        expected = [
            '0xc5',
            '0x0',
            '0x10',
        ]
        self.assertFrameData(expected, self.message.frame_one)

    def test_frame_two(self):
        expected = ['0x42', '0x0', '0x0']
        self.assertFrameData(expected, self.message.frame_two)

    def test_frame_three(self):
        expected = [
            '0x0', '0x8', '0x26', '0x0', '0xa0', '0x0', '0x0', '0x6', '0x60',
            '0x0', '0x0', '0xc1', '0x80', '0x0'
        ]
        self.assertFrameData(expected, self.message.frame_three)

    def test_bin_string(self):
        self.assertEqual(8, len(self.message.frame_one))
        self.assertEqual(
            '0001000111011010001001110000000011000101000000000000000011010111',
            "".join(
                [bin(item)[2:].zfill(8) for item in self.message.frame_one]))
