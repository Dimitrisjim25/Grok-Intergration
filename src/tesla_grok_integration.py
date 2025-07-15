
import json
import logging
import os
import speech_recognition as sr
from speech_recognition import AudioData, Recognizer, Microphone
from typing import Optional
from .iot_client import IoTClient
from .logger import setup_logger
from .type_defs import Config

class TeslaGrokIntegration:
    """Κλάση για την ενσωμάτωση του Grok στο infotainment σύστημα ενός Tesla."""
    
    def __init__(self, config_path: str = "config/config.json"):
        """Αρχικοποίηση του συστήματος με ρυθμίσεις από config.json."""
        self.logger: logging.Logger = setup_logger("TeslaGrokIntegration")
        self.logger.info("Αρχικοποίηση του Tesla Grok Integration...")
        
        # Φόρτωση ρυθμίσεων
        try:
            with open(config_path, 'r') as f:
                self.config: Config = json.load(f)
        except FileNotFoundError:
            self.logger.error("Το αρχείο config.json δεν βρέθηκε!")
            raise
        
        # Λήψη API key από environment variable
        api_key: Optional[str] = os.environ.get("API_KEY")
        if not api_key:
            self.logger.error("Το API key δεν έχει οριστεί στο environment variable 'API_KEY'.")
            raise ValueError("Δεν βρέθηκε το API key.")

        # Αρχικοποίηση IoT client
        self.iot_client: IoTClient = IoTClient(
            api_url=self.config["api_url"],
            api_key=api_key,
            timeout=self.config.get("timeout", 10)
        )
        
        # Αρχικοποίηση speech recognizer
        self.recognizer: Recognizer = Recognizer()
        self.microphone: Microphone = Microphone()
        
    def recognize_speech(self) -> Optional[str]:
        """Αναγνώριση φωνής από το μικρόφωνο του οχήματος."""
        self.logger.info("Αναμονή για φωνητική είσοδο...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio: AudioData = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text: str = self.recognizer.recognize_google(audio, language="el-GR")
                self.logger.info(f"Αναγνωρίστηκε κείμενο: {text}")
                return text
            except sr.WaitTimeoutError:
                self.logger.warning("Χρονικό όριο φωνητικής εισόδου.")
                return None
            except sr.UnknownValueError:
                self.logger.warning("Δεν αναγνωρίστηκε η φωνή.")
                return None
            except sr.RequestError as e:
                self.logger.error(f"Σφάλμα speech recognition: {e}")
                return None
            except Exception as e:
                self.logger.error(f"Απρόσμενο σφάλμα στο recognize_speech: {e}")
                return None

    def process_grok_query(self, query: str) -> str:
        """Αποστολή ερωτήματος στο Grok API και λήψη απάντησης."""
        self.logger.info(f"Αποστολή ερωτήματος στο Grok: {query}")
        try:
            response: str = self.iot_client.send_query(query)
            self.logger.info(f"Απάντηση Grok: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Σφάλμα κατά την αποστολή ερωτήματος: {e}")
            return "Πρόβλημα σύνδεσης με το Grok. Δοκίμασε ξανά."

    def run(self) -> None:
        """Κύρια λειτουργία του συστήματος."""
        self.logger.info("Εκκίνηση του Tesla Grok Integration...")
        print("Tesla Grok Integration - Πες κάτι ή πες 'έξοδος' για τερματισμό.")
        
        while True:
            user_input: Optional[str] = self.recognize_speech()
            if user_input:
                if user_input.lower() == "έξοδος":
                    self.logger.info("Τερματισμός του συστήματος.")
                    print("Αντίο!")
                    break
                response: str = self.process_grok_query(user_input)
                print(f"Grok: {response}")
            else:
                print("Δεν κατάλαβα, δοκίμασε ξανά.")

if __name__ == "__main__":
    try:
        integration: TeslaGrokIntegration = TeslaGrokIntegration()
        integration.run()
    except KeyboardInterrupt:
        print("Τερματισμός από τον χρήστη.")
    except (ValueError, FileNotFoundError) as e:
        logging.basicConfig()
        logging.error(f"Σφάλμα αρχικοποίησης: {e}")
    except Exception as e:
        logging.basicConfig()
        logging.error(f"Κρίσιμο σφάλμα: {e}")
