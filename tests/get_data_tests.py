import unittest
import get_data


class GetDataTests(unittest.TestCase):

    def test_check_should_capture(self):
        result = get_data.check_should_capture("20100501123456", "20100123123456")
        self.assertEqual(True, result)

        result = get_data.check_should_capture("20100501123456", "20090123123456")
        self.assertEqual(True, result)

        result = get_data.check_should_capture("20100201123456", "20091023123456")
        self.assertEqual(True, result)

        result = get_data.check_should_capture("20100101123456", "20091223123456")
        self.assertEqual(False, result)

        result = get_data.check_should_capture("20101201123456", "20101123123456")
        self.assertEqual(False, result)        
