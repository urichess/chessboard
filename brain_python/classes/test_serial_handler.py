import unittest
from unittest.mock import MagicMock, patch
from SerialHandler import SerialHandler
import time

class TestSerialHandler(unittest.TestCase):

    @patch('serial.Serial')  # Mock pyserial
    def test_callback_invoked_on_board_message(self, mock_serial_class):
        mock_serial = MagicMock()
        mock_serial.readline.side_effect = [
            b'BOARD:FF-FF-00-00-00-00-FF-FF\n',
            b''  # Simulate end of input
        ]
        mock_serial_class.return_value = mock_serial

        received_data = []

        def fake_callback(data):
            received_data.append(data)

        handler = SerialHandler('/dev/fake')
        handler.set_callback(fake_callback)
        handler.start()
        time.sleep(0.1)
        handler.stop()

        self.assertEqual(len(received_data), 1)
        self.assertEqual(received_data[0], 'BOARD:FF-FF-00-00-00-00-FF-FF')

    @patch('serial.Serial')  # Second test
    def test_ignores_non_board_messages(self, mock_serial_class):
        mock_serial = MagicMock()
        mock_serial.readline.side_effect = [
            b'HELLO:Something else\n',
            b''  # End
        ]
        mock_serial_class.return_value = mock_serial

        received_data = []

        def fake_callback(data):
            received_data.append(data)

        handler = SerialHandler('/dev/fake')
        handler.set_callback(fake_callback)
        handler.start()
        time.sleep(0.1)
        handler.stop()

        # Callback should not be triggered
        self.assertEqual(received_data, [])


