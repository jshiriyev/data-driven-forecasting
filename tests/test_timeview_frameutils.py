import unittest

import pandas as pd

from prodpy.timeview import FrameUtils

class TestFrameUtils(unittest.TestCase):

	def test_heads(self):

		frame = {"name":["john","smith","python"],"age":[32,47,23]}

		frame = pd.DataFrame(frame)

		utils = FrameUtils()

		self.assertEqual(utils(frame).heads(),[])

if __name__ == "__main__":

    unittest.main()

    # Test the commitments (python -m unittest discover -v)