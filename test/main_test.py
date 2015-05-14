__author__ = 'tomerb'

import unittest
from merger.conf.mergeconf import ARG_CLIENT
from merger.utils.argutils import is_client


class MainTest(unittest.TestCase):

    def test_is_client_sanity(self): self.assertFalse(is_client(['bla']))

    def test_is_client_when_truely_is_client(self):
        self.assertTrue(is_client(['1', ARG_CLIENT]))
