
import requests
import json
from typing import Dict
from .type_defs import GrokResponse

class IoTClient:
    """Κλάση για τη διαχείριση της IoT επικοινωνίας με το API του Grok."""
    
    def __init__(self, api_url: str, api_key: str, timeout: int = 10):
        """Αρχικοποίηση του IoT client."""
        if not api_key:
            raise ValueError("Το API key δεν έχει οριστεί.")
        self.api_url: str = api_url
        self.api_key: str = api_key
        self.timeout: int = timeout
        self.headers: Dict[str, str] = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def send_query(self, query: str) -> str:
        """Αποστολή ερωτήματος στο API του Grok."""
        payload: Dict[str, str] = {
            "query": query,
            "language": "el",
            "context": "tesla_vehicle"
        }
        try:
            response: requests.Response = requests.post(
                self.api_url,
                headers=self.headers,
                data=json.dumps(payload),
                timeout=self.timeout
            )
            response.raise_for_status()
            response_json: GrokResponse = response.json()
            return response_json.get("response", "Καμία απάντηση από το Grok.")
        except requests.RequestException as e:
            raise Exception(f"Σφάλμα σύνδεσης με το API: {e}")
