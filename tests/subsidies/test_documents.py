import unittest

import tests.test_environment  # noqa: F401

from apps.subsidies.services.document_checker import find_missing_documents, parse_required_documents


class DocumentCheckerTests(unittest.TestCase):
    def test_parse_required_documents(self):
        docs = parse_required_documents({"required_documents": "Aadhaar Card, Land Record , Bank Passbook"})
        self.assertEqual(docs, ["aadhaar card", "land record", "bank passbook"])

    def test_no_missing_when_all_uploaded(self):
        missing = find_missing_documents(
            {"required_documents": "Aadhaar Card, Land Record"},
            [{"document_type": "Aadhaar Card"}, {"document_type": "Land Record"}],
        )
        self.assertEqual(missing, [])

    def test_missing_document_detected(self):
        missing = find_missing_documents(
            {"required_documents": "Aadhaar Card, Bank Passbook"},
            [{"document_type": "Aadhaar Card"}],
        )
        self.assertEqual(missing, ["bank passbook"])

    def test_combined_upload_satisfies_both(self):
        missing = find_missing_documents(
            {"required_documents": "Aadhaar Card, Land Record"},
            [{"document_type": "Aadhaar Card & Land Certificate"}],
        )
        self.assertEqual(missing, [])

    def test_empty_upload_list_reports_all_missing(self):
        missing = find_missing_documents(
            {"required_documents": "Aadhaar Card, Land Record"},
            [],
        )
        self.assertEqual(len(missing), 2)


if __name__ == "__main__":
    unittest.main()
