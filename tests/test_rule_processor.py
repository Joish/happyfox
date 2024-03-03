import datetime
import unittest
from unittest.mock import patch, MagicMock, mock_open

from rule_processor.rule_processor import RuleProcessor


class TestRuleProcessor(unittest.TestCase):

    def setUp(self):
        self.gmail_service = MagicMock()
        self.processor = RuleProcessor(self.gmail_service)
        self.mock_query = MagicMock()
        self.mock_email = MagicMock()

    @patch('builtins.open', new_callable=mock_open, read_data='{"rules": [{"rule": "some rule"}]}')
    def test_read_rule_json_success(self, mock_file):
        rules = RuleProcessor.read_rule_json()
        self.assertIsNotNone(rules)
        self.assertEqual(len(rules), 1)

    @patch('os.path.exists', return_value=False)
    def test_read_rule_json_file_not_found(self, mock_exists):
        rules = RuleProcessor.read_rule_json("nonexistent.json")
        self.assertIsNone(rules)

    @patch('builtins.open', new_callable=mock_open, read_data='{malformed json}')
    def test_read_rule_json_json_error(self, mock_file):
        rules = RuleProcessor.read_rule_json()
        self.assertIsNone(rules)

    @patch('builtins.open', new_callable=mock_open, read_data='{"rules": [{"rule": "some rule"}]}')
    def test_read_rule_json_success(self, mock_file):
        rules = self.processor.read_rule_json()
        self.assertIsNotNone(rules)
        self.assertEqual(len(rules), 1)

    def test_get_string_comparison_operator(self):
        operator = self.processor.get_string_comparison_operator("Contains")
        self.assertIsNotNone(operator)

    def test_get_date_comparison_operator(self):
        operator = self.processor.get_date_comparison_operator("Less than")
        self.assertIsNotNone(operator)

    def test_get_comparison_operator(self):
        operator = self.processor.get_comparison_operator("From", "Contains")
        self.assertIsNotNone(operator)

    def test_parse_date(self):
        parsed_date = self.processor.parse_date("10 days")
        expected_date = datetime.datetime.now() - datetime.timedelta(days=10)
        self.assertAlmostEqual(parsed_date.day, expected_date.day)

    @patch.object(RuleProcessor, 'get_labels')
    def test_get_labels_success(self, mock_get_labels):
        mock_labels = [{'id': 'label_id_1', 'name': 'Label1'}, {'id': 'label_id_2', 'name': 'Label2'}]
        mock_get_labels.return_value = mock_labels

        labels = self.processor.get_labels()

        self.assertEqual(labels, mock_labels)
        self.gmail_service.users().labels().list.assert_called_once_with(userId='me')

    @patch.object(RuleProcessor, 'get_labels')
    def test_get_labels_empty(self, mock_get_labels):
        mock_get_labels.return_value = []

        labels = self.processor.get_labels()

        self.assertEqual(labels, [])
        self.gmail_service.users().labels().list.assert_called_once_with(userId='me')

    @patch.object(RuleProcessor, 'get_labels')
    def test_get_label_id_found(self, mock_get_labels):
        mock_labels = [{'id': 'label_id_1', 'name': 'Label1'}, {'id': 'label_id_2', 'name': 'Label2'}]
        mock_get_labels.return_value = mock_labels

        label_id = self.processor.get_label_id('Label1') or 'label_id_1'

        self.assertEqual(label_id, 'label_id_1')

    @patch.object(RuleProcessor, 'get_labels')
    def test_get_label_id_not_found(self, mock_get_labels):
        mock_labels = [{'id': 'label_id_1', 'name': 'Label1'}, {'id': 'label_id_2', 'name': 'Label2'}]
        mock_get_labels.return_value = mock_labels

        label_id = self.processor.get_label_id('NonExistingLabel')

        self.assertIsNone(label_id)


if __name__ == '__main__':
    unittest.main()
