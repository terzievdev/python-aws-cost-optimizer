import unittest
from src.scanner import AWSResourceScanner
import json


class TestScanner(unittest.TestCase):

    def setUp(self):
        self.scanner = AWSResourceScanner()

    def test_scanner_initialization(self):
        """Test scanner initializes correctly"""
        self.assertIsNotNone(self.scanner.results)
        self.assertIn('scan_time', self.scanner.results)
        self.assertIn('regions', self.scanner.results)

    def test_scan_ec2_instances(self):
        """Test EC2 scanning (mocked)"""
        # This would require mocking boto3
        # For now, just test the method exists
        self.assertTrue(hasattr(self.scanner, 'scan_ec2_instances'))

    def test_results_structure(self):
        """Test results have correct structure"""
        self.assertIsInstance(self.scanner.results, dict)
        self.assertIsInstance(self.scanner.results['regions'], dict)


if __name__ == '__main__':
    unittest.run()

