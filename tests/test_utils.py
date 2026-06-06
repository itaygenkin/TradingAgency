import unittest
from src.utils.utils import clean_report


class TestCleanReport(unittest.TestCase):
    
    def test_escapes_dollar_signs(self):
        result = clean_report("$100 and $200")
        self.assertEqual(result, "\\$100 and \\$200")
    
    def test_removes_data_summary_and_following_content(self):
        report = "Content\nDATA_SUMMARY\nMore content with $ sign and \\$ sign as well."
        result = clean_report(report)
        self.assertEqual(result, "Content\n")
        self.assertNotIn("DATA_SUMMARY", result)
        self.assertNotIn("More content", result)
    
    def test_data_summary_not_found_keeps_full_report(self):
        report = "Just normal report"
        result = clean_report(report)
        self.assertEqual(result, "Just normal report")
    
    def test_escapes_dollars_and_removes_summary(self):
        report = "Price: $50\nDATA_SUMMARY\nExtra: $100"
        result = clean_report(report)
        self.assertEqual(result, "Price: \\$50\n")
        self.assertNotIn("$100", result)
    
    def test_empty_string(self):
        result = clean_report("")
        self.assertEqual(result, "")

    def test_only_data_summary_marker(self):
        result = clean_report("DATA_SUMMARY")
        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
