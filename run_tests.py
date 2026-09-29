import unittest

from processor import process_file

VALID_STATUSES = {
    "Valid",
    "Missing",
    "Unsigned",
    "Expired",
    "Flagged",
    "Needs Review",
    "Mismatch",
    "Late",
    "Notary Invalid",
    "Unreadable",
    "Duplicate",
    "Version Mismatch",
    "Cleared",
}


class ProcessorTests(unittest.TestCase):
    def test_csv_fallback(self):
        test_bytes = b"supplier,product,price\nAcme,Widget,9.99"
        results = process_file(test_bytes)

        self.assertIsInstance(results, list)
        self.assertTrue(results)
        self.assertEqual(results[0]["title"], "Acme")
        self.assertIn(results[0]["status"], VALID_STATUSES)
        self.assertEqual(results[0]["details"]["product"], "Widget")

    def test_due_date_is_top_level_and_not_in_details(self):
        test_bytes = b"borrower_name,due_date,amount\nJane Doe,2025-01-31,100"
        results = process_file(test_bytes)

        self.assertEqual(results[0]["due_date"], "2025-01-31")
        self.assertNotIn("due_date", results[0]["details"])

    def test_unreadable_empty_bytes(self):
        results = process_file(b"")

        self.assertIsInstance(results, list)
        self.assertEqual(results[0]["status"], "Unreadable")

    def test_details_is_dict(self):
        results = process_file(b"borrower_name,signed\nBob,true")

        self.assertIsInstance(results[0]["details"], dict)
        self.assertEqual(results[0]["details"]["signed"], "true")


if __name__ == "__main__":
    unittest.main()
