import os
import unittest
from haikoo.haikoo import Haikoo
from haikoo.haikoo import MockImageDescriber
from haikoo.syllable_counter import SyllableCounter

class HaikooTest(unittest.TestCase):

	def test_count_syllables_word(self):
		counter = SyllableCounter()
		words = [("food", 1), ("aardvark", 2), ("mountain", 2), ("above", 2), ("the", 1), ("consequence", 3)]

		for w in words:
			print(w)
			self.assertEqual(w[1], counter.count(w[0]))

	def test_count_syllables_sentence(self):
		counter = SyllableCounter()
		sentences = [("The quick brown fox jumps over the lazy dog.", 11), ("an ancient pond / a frog jumps in / the splash of water", 13)]

		for s in sentences:
			print(s)
			self.assertEqual(s[1], counter.count(s[0]))

	def test_split_sentence(self):
		counter = SyllableCounter()
		sentence = "The quick brown fox jumps over the lazy dog."
		halves = counter.split_sentence(sentence, 5)

		self.assertEqual("The quick brown fox jumps", halves[0])
		# punctuation/special characters should be removed (when not part of a word)
		self.assertEqual("over the lazy dog", halves[1])

		# 
		sentence = "Torches are made to light, jewels to wear, Dainties to taste, fresh beauty for the use"
		halves = counter.split_sentence(sentence, 7)

		# syllable 7 is in the middle of "jewels", so we should break at the end of the word
		self.assertEqual("Torches are made to light jewels", halves[0])
		self.assertEqual("to wear Dainties to taste fresh beauty for the use", halves[1])

	def test_create_text(self):
		describer = MockImageDescriber()
		haikoo = Haikoo(describer, "fusion")
		result = haikoo.create_text("./fixtures/image.jpeg")

		print(result)

	def test_create_image(self):
		describer = MockImageDescriber()
		haikoo = Haikoo(describer, "fusion")
		result = haikoo.create_image("./fixtures/image.jpeg", "./test/test_create_image.png")

		print(result)
		self.assertTrue(os.path.exists(result.image))
		self.assertIsNotNone(result.text)
		self.assertIsNotNone(result.keywords)
		os.remove(result.image)

	def test_create_thumbnail(self):
		haikoo = Haikoo(None, None)
		thumbnail_image = haikoo.create_thumbnail("./fixtures/image.jpeg", "./test/thumbnail.jpeg", 128, 128)

		self.assertTrue(os.path.exists(thumbnail_image))
		os.remove(thumbnail_image)

