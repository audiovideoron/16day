import unittest
from unittest.mock import patch
import contacts  # replace with the name of your actual file

class TestFuncs(unittest.TestCase):
    def test_is_valid_phone_number(self):
        self.assertTrue(contacts.is_valid_phone_number('(123) 345-6789'))
        self.assertFalse(contacts.is_valid_phone_number('123-345-6789'))

    def test_calculate_weight(self):
        self.assertEqual(contacts.calculate_weight(["a1", "v2"], 1, 0, 1, 0), 6)

    def test_generate_unique_id(self):
        test_contacts = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
        self.assertEqual(contacts.generate_unique_id(test_contacts), "4")

    def test_get_position_key(self):
        self.assertEqual(contacts.get_position_key("Audio Level 1"), "a1")

    @patch('builtins.input', side_effect=['Steve', 'Jobs', '(123) 345-6789', 'a1', 'y', 'n', 'y', 'n', '100', 'q'])
    def test_gather_contact_info(self, mock):
        self.assertEqual(contacts.gather_contact_info([]), [{'id': '1', 'first_name': 'Steve', 'last_name': 'Jobs', 'phone': '(123) 345-6789', 'position': ['a1'], 'weight': 3, 'rate': '100', 'reliable': True, 'flexible': False, 'client_relations': True, 'preferred': False}])

if __name__ == "__main__":
    unittest.main()
