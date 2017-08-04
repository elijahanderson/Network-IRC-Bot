import os

from twisted.trial import unittest

from talkback.response_picker import ResponsePicker

# TestResponsePicker will inherit twisted's unittest.TestCase class
# TestCase will run every function that starts with test
class TestResponsePicker(unittest.TestCase) :

    RESPONSE1 = 'response1'
    RESPONSE2 = 'response2'

    def test_pick(self) :
        picker = ResponsePicker

        response = picker.pick()
        self.assertIn(response, (self.RESPONSE1, self.RESPONSE2),
                      "Got unexpected response: '%s'" % (response))