import unittest
import glob
import sys

sys.path.append(".")

import regex2dfa

class AllTests(unittest.TestCase):
    def test_all_regexes(self):
        regexes = glob.glob("tests/*.regex")
        for filepath in regexes:
            self._test_regex_file(filepath)

    def _test_regex_file(self, filepath):
        with open(filepath) as fh:
            regex = fh.read()

        actual_dfa = regex2dfa.regex2dfa(regex)

        filepath_dfa = filepath[:-5] + "dfa"
        with open(filepath_dfa) as fh:
            expected_dfa = fh.read()
 
        actual_dfa = actual_dfa.strip()
        expected_dfa = expected_dfa.strip()

        self.assertEquals(expected_dfa, actual_dfa)

def suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(AllTests))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
