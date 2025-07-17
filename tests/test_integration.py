
import unittest
from unittest.mock import patch, MagicMock
import os
import requests
import speech_recognition as sr
from src.tesla_grok_integration import TeslaGrokIntegration

class TestTeslaGrokIntegration(unittest.TestCase):
    integration: TeslaGrokIntegration

    @patch.dict(os.environ, {"API_KEY": "test_api_key"})
    def setUp(self) -> None:
        self.integration = TeslaGrokIntegration()

    @patch('src.tesla_grok_integration.sr.Recognizer.recognize_google', autospec=True)
    @patch('src.tesla_grok_integration.sr.Recognizer.listen', autospec=True)
    def test_recognize_speech_success(self, mock_listen: MagicMock, mock_recognize_google: MagicMock) -> None:
        mock_listen.return_value = MagicMock(spec=sr.AudioData)
        mock_recognize_google.return_value = "test query"
        result = self.integration.recognize_speech()
        self.assertEqual(result, "test query")

    @patch('src.tesla_grok_integration.sr.Recognizer.listen', autospec=True)
    def test_recognize_speech_error(self, mock_listen: MagicMock) -> None:
        mock_listen.side_effect = sr.UnknownValueError("Speech recognition error")
        result = self.integration.recognize_speech()
        self.assertIsNone(result)

    @patch('src.iot_client.requests.post', autospec=True)
    def test_process_grok_query_success(self, mock_post: MagicMock) -> None:
        mock_post.return_value.json.return_value = {"response": "Test response"}
        mock_post.return_value.raise_for_status.return_value = None
        result = self.integration.process_grok_query("test query")
        self.assertEqual(result, "Test response")

    @patch('src.iot_client.requests.post', autospec=True)
    def test_process_grok_query_error(self, mock_post: MagicMock) -> None:
        mock_post.side_effect = requests.RequestException("API error")
        result = self.integration.process_grok_query("test query")
        self.assertEqual(result, "Πρόβλημα σύνδεσης με το Grok. Δοκίμασε ξανά.")

if __name__ == '__main__':
    unittest.main()
