import os
import unittest
from dotenv import load_dotenv

# Test Upbit Class
from upbit import Upbit


class TestUpbit(unittest.TestCase):
    def setUp(self):
        load_dotenv(verbose=True)
        self.upbit = Upbit(
            access_key=os.getenv('UPBIT_ACCESS_KEY'),
            secret_key=os.getenv('UPBIT_SECRET_KEY'),
            debug=True,
        )

    def test_get_deposit_history(self):
        h1 = sum(self.upbit.get_deposit_history())
        h2 = sum(self.upbit.get_withdraws_history())
        h3 = self.upbit.get_net_deposit_of_krw()
        self.assertEqual(h1 - h2, h3)


if __name__ == '__main__':
    unittest.main()
