import os
import unittest
from haikoo.haikoo import Haikoo
from haikoo.haikoo import MockImageDescriber

class HaikooTest(unittest.TestCase):

	def test_count_syllables(self):
		haikoo = Haikoo(None, None)
		words = [("food", 1), ("aardvark", 2), ("mountain", 2), ("above", 2), ("the", 1)]

		for w in words:
			print(w)
			self.assertEqual(w[1], haikoo.count_syllables(w[0]))

	def test_create_image(self):
		describer = MockImageDescriber()
		haikoo = Haikoo(describer, "fusion")
		result = haikoo.create_image("./fixtures/image.jpeg", "./test/test_create_image.png")

		print(result)
		self.assertTrue(os.path.exists(result.image))
		os.remove(result.image)

	def test_create_thumbnail(self):
		haikoo = Haikoo(None, None)
		thumbnail_image = haikoo.create_thumbnail("./fixtures/image.jpeg", "./test/thumbnail.jpeg", 128, 128)

		self.assertTrue(os.path.exists(thumbnail_image))
		os.remove(thumbnail_image)

