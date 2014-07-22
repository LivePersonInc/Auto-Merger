__author__ = 'tomerb'

import unittest

class MultiReposTest(unittest.TestCase):

    def setUp(self):
        self.branches_map_as_str = """aaa"""

    def test_extract_branch_with_repo_from_look__base_build_xml(self):
        self.assertEquals("a", "a")