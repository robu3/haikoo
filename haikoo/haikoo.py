import sys, os, re, urllib.request, shutil
import markovify
from random import shuffle
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from .image_describer import ImageDescriber
from .mock_image_describer import MockImageDescriber
from .haikoo_model_config import HaikooModelConfig
from .haikoo_result import HaikooResult
from .haiku_text import HaikuText
from .haiku_chain import HaikuChain
from .syllable_counter import SyllableCounter
from . import __path__ as ROOT_PATH

class Haikoo:
	"""
	A haiku poem generator.
	"""
	VOWELS = ["a", "e", "i", "o", "u", "y"]
	LINE_SYLLABLES = [5, 7, 5]
	HAIKU_SYLLABLES = 17
	MODEL_CONFIGS = {
			"classic": HaikooModelConfig(["models/classic_haiku_model.json"], [1]),
			"frost": HaikooModelConfig(["models/robert_frost.json"], [1]),
			"shakespeare": HaikooModelConfig([
				ROOT_PATH[0] + "/models/shakespeare_sonnets.json",
				ROOT_PATH[0] + "/models/shakespeare_romeo_and_juliet.json",
				ROOT_PATH[0] + "/models/shakespeare_hamlet.json"
				],
				[1, 1, 1]),
			"fusion": HaikooModelConfig([
				ROOT_PATH[0] + "/models/classic_haiku_model.json",
				ROOT_PATH[0] + "/models/robert_frost.json",
				ROOT_PATH[0] + "/models/shakespeare_sonnets.json",
				ROOT_PATH[0] + "/models/shakespeare_romeo_and_juliet.json",
				ROOT_PATH[0] + "/models/shakespeare_hamlet.json"
				],
				[1, 1, 1, 1, 1])
	}

	def __init__(self, image_describer, model, max_retries = 5, retry_score = 0.1):
		self.image_describer = image_describer
		self.syllable_counter = SyllableCounter() 
		self.max_retries = max_retries
		self.retry_score = retry_score
		self.model = model

	def trim_line(self, line, line_number):
		"""
		Trims the specified line to the correct number of syllables per its line number.
		Returns a tuple of (trimmed_line, syllable_count)
		"""
		if line_number > len(self.LINE_SYLLABLES) or line_number < 0:
			raise Exception("Invalid line number: " + line_number)

		# remove punctation
		line = re.sub(r"[\.!,]", "", line)

		# iterate over each word
		# build a new line and cut it once we've met or exceeded the syllable count
		words = line.split(" ")
		trimmed = ""
		max_count = self.LINE_SYLLABLES[line_number]
		count = 0

		for w in words:
			count += self.syllable_counter.count(w)

			trimmed += w

			if count >= max_count:
				break
			else:
				trimmed += " "

		return (trimmed, count)

	def format(self, haiku):
		"""
		Formats the haiku text.
		"""
		haiku = haiku.lower()
		return haiku

	def load_markov_model(self, model_name, keywords):
		"""
		Loads our haiku Markov model.
		"""
		model_config = self.MODEL_CONFIGS[model_name]
		models = []

		# load each model file
		for m in model_config.models:
			with open(m) as f:
				json_text = f.read()

			models.append(HaikuText.from_json(json_text))

		# combine the models and return result
		combined_model = self.combine(models, model_config.weights)
		combined_model.keywords = keywords
		return combined_model

	def combine(self, models, weights=None):
		"""
		Combine multiple Markov text models into a single on.
		Modified version of implementation in markovify's utils.py
		"""
		if weights == None:
			weights = [ 1 for _ in range(len(models)) ]

		if len(models) != len(weights):
			raise ValueError("`models` and `weights` lengths must be equal.")

		model_dicts = list(map(markovify.utils.get_model_dict, models))
		state_sizes = [ len(list(md.keys())[0])
			for md in model_dicts ]

		if len(set(state_sizes)) != 1:
			raise ValueError("All `models` must have the same state size.")

		if len(set(map(type, models))) != 1:
			raise ValueError("All `models` must be of the same type.")

		c = {}

		for m, w in zip(model_dicts, weights):
			for state, options in m.items():
				current = c.get(state, {})
				for subseq_k, subseq_v in options.items():
					subseq_prev = current.get(subseq_k, [0, 0])
					current[subseq_k] = [subseq_prev[0] + (subseq_v[0] * w), subseq_v[1]]
				c[state] = current

		ret_inst = models[0]

		if isinstance(ret_inst, HaikuChain):
			return HaikuChain.from_json(c)
		if isinstance(ret_inst, HaikuText):
			if any(m.retain_original for m in models):
				combined_sentences = []
				for m in models:
					if m.retain_original:
						combined_sentences += m.parsed_sentences
				return ret_inst.from_chain(c, parsed_sentences=combined_sentences)
			else:
				return ret_inst.from_chain(c)
		if isinstance(ret_inst, list):
			return list(c.items())
		if isinstance(ret_inst, dict):
			return c

	def generate_text(self, description, markov_model, retry_count):
		"""
		Generates haiku text using the descriptive keywords and Markov model.
		Returns an array of lines.
		"""
		lines = []
		keywords = []
		syllable_counts = [12, 5]
		total_syllable_count = 0

		for i in range(len(description)):
			word = description[i]

			markov_model.syllable_count = syllable_counts[len(lines)]
			line = markov_model.make_sentence_with_start(word, test_output=False, strict=False)

			if line != None:
				lines.append(line)
				total_syllable_count += markov_model.chain.num_syllables
				keywords.append(word)

			if len(lines) == 2:
				break

		print(keywords)
		print(f"Total syllables {total_syllable_count}")

		# retry if total syllable count is more than 2 off
		if abs(total_syllable_count - self.HAIKU_SYLLABLES) > 2 and retry_count < self.max_retries:
			return self.generate_text(description, markov_model, retry_count + 1)

		# split 12 syllable line into 5-7
		final_lines = list(self.syllable_counter.split_sentence(lines[0], 5))

		# add a 切れ字-like punctionation (--) at the end of the second line
		final_lines[1] += " --"

		# then add the final line
		final_lines.append(lines[1])

		return (final_lines, keywords)

	def generate_text_original(self, description, markov_model, retry_count):
		"""
		Generates haiku text using the descriptive keywords and Markov model.
		Returns an array of lines.
		"""
		lines = []
		keywords = []
		syllables = []
		final_score = 0

		for i in range(len(description)):
			word = description[i]

			line_number = len(lines)
			markov_model.syllable_count = self.LINE_SYLLABLES[line_number]

			try:
				# attempt to create a line starting with the desired word
				line = markov_model.make_sentence_with_start(word, test_output=False, strict=False)
				#line = markov_model.make_sentence(test_output=True)
			except:
				# handle exceptions; generate a sentence that simply contains the word
				line = markov_model.make_sentence(test_output=True)
				pass

			if line != None:
				# trim the line and add it to our haiku
				trimmed = self.trim_line(line, line_number)

				lines.append(trimmed[0])
				keywords.append(word)

				# score is difference in syllables
				# lower is better (0 == perfect)
				score = abs(trimmed[1] - self.LINE_SYLLABLES[line_number]) / self.LINE_SYLLABLES[line_number]
				final_score += score
				syllables.append(trimmed[1])

			if len(lines) == 3:
				break

		# add random lines if ones based on keywords were not enough
		while len(lines) < 3:
			line = markov_model.make_sentence(test_output=True)
			# trim the line and add it to our haiku
			line_number = len(lines)
			trimmed = self.trim_line(line, line_number)

			lines.append(trimmed[0])
			keywords.append(None)

			# score is % difference in syllables
			# lower is better (0 == perfect)
			score = abs(trimmed[1] - self.LINE_SYLLABLES[line_number]) / self.LINE_SYLLABLES[line_number]
			final_score += score
			syllables.append(trimmed[1])


		# retry if the syllable count is too far off
		final_score /= 3

		if final_score > self.retry_score and retry_count < self.max_retries:
			return self.generate_text(description, markov_model, retry_count + 1)

		print(syllables)
		print(final_score)
		print(keywords)

		return (lines, keywords)


	def create_text(self, file_path):
		"""
		Creates a new haiku from the specified image file.

		:return: Tuple containing (the text of the haiku, descriptive keywords used).
		"""
		# get a text description of the image (list of words)
		description = self.image_describer.describe_file(file_path)
		#print(f"description: {description}")

		# cap descriptive words to most relevant
		# description = description[0:(6 if len(description) >= 6 else len(description))]

		#shuffle(description)

		if len(description) < 3:
			raise Exception("Description needs to include at least 3 words.")

		# then generate a haiku line for each word
		markov_model = self.load_markov_model(self.model, description)
		text = self.generate_text(description, markov_model, 0)
		#print(f"keywords: {text[1]}")

		haiku = "\n".join(text[0])
		return (self.format(haiku), text[1])

	def create_image_file(self, file_path, out_file_path, retry_count = 0, text = None):
		"""
		Creates a haiku of the specified image and then overlays the text on top.
		"""
		# generate haiku if not already provided
		if text == None:
			text = self.create_text(file_path)[0]

		# size of the image (will be square-cropped)
		size = 512
		font_size = int(size / 16)
		shadow_size = 1

		img = Image.open(file_path)
		font = ImageFont.truetype("impact.ttf", font_size - shadow_size)

		# resize and crop image
		# resize to smallest dimension
		if img.size[0] < img.size[1]:
			resize_factor = size / img.size[0]
		else:
			resize_factor = size / img.size[1]

		resize = (img.size[0] * resize_factor, img.size[1] * resize_factor)
		img.thumbnail(resize)

		# then crop to a square
		if img.size[0] > img.size[1]:
			# landscape orientation
			left = (img.size[0] - size) / 2
			right = left + size
			img = img.crop((left, 0, right, size))
		else:
			top = (img.size[1] - size) / 2
			bottom = top + size
			img = img.crop((0, top, size, bottom))

		textX = font_size
		textY = font_size

		draw = ImageDraw.Draw(img)

		# draw the text shadow
		draw.text((textX - shadow_size, textY - shadow_size), text, (0, 0, 0), font=font)
		draw.text((textX - shadow_size, textY + shadow_size), text, (0, 0, 0), font=font)
		draw.text((textX + shadow_size, textY - shadow_size), text, (0, 0, 0), font=font)
		draw.text((textX + shadow_size, textY + shadow_size), text, (0, 0, 0), font=font)
		draw.text((textX, textY), text, (255, 255, 255), font=font)
		img.save(out_file_path)

	def create_image_file_error(self, out_file_path, text = None):
		if text is None:
			text = "an error occurs\nas frustrated you may be\nmy heart weeps more so"

		self.create_image_file(ROOT_PATH[0] + "/fixtures/bsod.png", out_file_path, text)

	def download_image(self, image_url):
		"""
		Downloads an image.

		:return: The full local path of the file downloaded.
		"""
		# download the file
		url = urllib.parse.urlparse(image_url)
		temp_file = "TEMP-" + os.path.basename(url.path)

		req = urllib.request.Request(image_url)
		with urllib.request.urlopen(req) as res:
			with open(temp_file, "wb") as f:
				shutil.copyfileobj(res, f)

		return os.path.abspath(temp_file)

	def create_image_url(self, image_url, out_file_path, retry_count = 0, text = None):
		"""
		Creates a haiku of the specified image at the specified URL and then overlays the text on top.

		:return: The full path of the new image file generated.
		"""
		# download the file
		url = urllib.parse.urlparse(image_url)
		temp_file = "TEMP-" + os.path.basename(url.path)

		req = urllib.request.Request(image_url)
		with urllib.request.urlopen(req) as res:
			with open(temp_file, "wb") as f:
				shutil.copyfileobj(res, f)

		# create haiku and remove temp file
		self.create_image_file(temp_file, out_file_path, retry_count, text)
		os.remove(temp_file)

	def create_image(self, file_path, out_file_path, retry_count = 0, text = None):
		"""
		Creates a haiku of the specified image and then overlays the text on top.
		If the file path appears to be URL, the file will be downloaded.

		:return: A HaikooResult instance containing the haiku text, keywords used to generate it, and the generated image file ("haikoo").
		"""
		try:
			is_url = False

			# download the file if necessary
			if re.match("http[s]+://", file_path):
				file_path = self.download_image(file_path)
				is_url = True

			# generate haiku text
			if text == None:
				haiku = self.create_text(file_path)
				text = haiku[0]
				keywords = haiku[1]

			# create image
			self.create_image_file(file_path, out_file_path, retry_count, text)
			result = HaikooResult(text=text, image=os.path.abspath(out_file_path), keywords=keywords) 
		except Exception as e:
			# create error image
			self.create_image_file_error(out_file_path)
			result = HaikooResult(text=text, image=os.path.abspath(out_file_path), keywords=keywords) 
			result.error_message = str(e)
		finally:
			# cleanup downloaded file
			if is_url and os.path.exists(file_path):
				 os.remove(file_path)

		return result

	def create_thumbnail(self, image_path, out_file_path, x, y):
		"""
		Creates a thumbnail of the specified image.

		:return: The full path of the thumbnail image generated.
		"""

		img = Image.open(image_path)
		img.thumbnail((x, y))
		img.save(out_file_path)

		return os.path.abspath(out_file_path)





