import unittest


class TestClass01(unittest.TestCase):
    def test_case01(self):
        self.my_str = 'ASHWIN'
        self.my_int = 999
        self.assertTrue(isinstance(self.my_str, str))
        self.assertTrue(isinstance(self.my_int, int))

    def test_case02(self):
        my_pi = 3.14
        self.assertFalse(isinstance(my_pi, int))


if __name__ == '__main__':
    unittest.main()
