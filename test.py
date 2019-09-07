import unittest
from haikoo import Haikoo

class HaikooTest(unittest.TestCase):

	def test_count_syllables(self):
		haikoo = Haikoo(None, None)
		words = [("food", 1), ("aardvark", 2), ("mountain", 2), ("above", 2), ("the", 1)]

		for w in words:
			print(w)
			self.assertEqual(w[1], haikoo.count_syllables(w[0]))

if __name__ == "__main__":
	unittest.main()

