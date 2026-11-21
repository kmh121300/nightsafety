import unittest
from error_recovery_smoke import failure_message, mock_is_default


class ErrorRecoveryEvidenceTest(unittest.TestCase):
    def test_effective_mock_default_accepts_both_android_forms(self):
        self.assertTrue(mock_is_default('No operations.\nDefault mode: deny'))
        self.assertTrue(mock_is_default('MOCK_LOCATION: default\n'))
        self.assertTrue(mock_is_default('MOCK_LOCATION: default; time=+20s ago'))
        self.assertFalse(mock_is_default('MOCK_LOCATION: allow'))
        self.assertFalse(mock_is_default('MOCK_LOCATION: allow; time=+20s ago'))

    def test_empty_assertion_still_has_a_reportable_failure(self):
        self.assertEqual(failure_message(AssertionError()), 'AssertionError')
        self.assertEqual(failure_message(ValueError('first\nsecond')), 'first')


if __name__ == '__main__':
    unittest.main()
