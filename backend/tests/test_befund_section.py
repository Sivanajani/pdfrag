import os
import sys
import unittest

# Prevent import-time RuntimeError in gemini_client
os.environ.setdefault("GOOGLE_API_KEY", "test-key")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.gemini_client import extract_befund_section


class TestBefundSectionExtraction(unittest.TestCase):
    def test_extracts_befund_until_next_heading(self):
        text = (
            "Klinik: Schmerzen seit 2 Wochen\n"
            "Befund:\n"
            "Im linken Oberschenkel zeigt sich eine suspekte Raumforderung von 5 cm.\n"
            "Weitere Beschreibung und Messwerte im Verlauf.\n"
            "Beurteilung:\n"
            "V. a. Sarkom.\n"
        )

        extracted = extract_befund_section(text)

        self.assertIn("linken Oberschenkel", extracted)
        self.assertNotIn("Beurteilung", extracted)
        self.assertNotIn("V. a. Sarkom", extracted)

    def test_returns_full_text_if_no_befund_heading(self):
        text = "Kein expliziter Abschnittstitel vorhanden. Nur Freitext."

        extracted = extract_befund_section(text)

        self.assertEqual(extracted, text)


if __name__ == "__main__":
    unittest.main()
