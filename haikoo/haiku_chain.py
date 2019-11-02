from markovify import Chain
from markovify.chain import accumulate
from markovify.chain import BEGIN, END
import bisect
import random
import json
from .syllable_counter import SyllableCounter

# Python3 compatibility
try: # pragma: no cover
	basestring
except NameError: # pragma: no cover
	basestring = str

class HaikuChain(Chain):
	"""
	A modified Markov chain tweaked to produce better haiku.
	Takes the 5-7-5 syllable count and keywords into account.
	"""
	VOWELS = ["a", "e", "i", "o", "u", "y"]

	def __init__(self, corpus, state_size, model, keywords = None):
		# call parent class's constructor
		super().__init__(corpus, state_size, model)
		self.keywords = keywords
		self.num_syllables = 0
		self.syllable_count = 0
		self.syllable_counter = SyllableCounter()
		self.num_words = 0

	def reset(self):
		self.num_syllables = 0
		self.num_words = 0

	def walk(self, init_state = None):
		if init_state is not None:
			self.num_syllables = self.syllable_counter.count(init_state[0])
			self.num_syllables += self.syllable_counter.count(init_state[1])

		return list(self.gen(init_state))

	def move(self, state):
		"""
		Given a state, choose the next item.
		Weight heavily words in our keyword list.
		"""
		print(f"MOVE: {self.num_syllables} / {self.syllable_count}")
		print(state)
		#print(f"MOVE: {self.model[state].items()}")

		# reached syllable count
		if self.num_syllables >= self.syllable_count:
			return END

		if state == tuple([ BEGIN ] * self.state_size):
			choices = self.begin_choices
			cumdist = self.begin_cumdist
		else:
			# original code
			#choices, weights = zip(*self.model[state].items())
			#cumdist = list(accumulate(weights))
			items = self.model[state].items()

			# check syllable count
			syllable_choices = []
			all_choices = []

			for item in items:
				# remove choices that would put us over the syllable count
				# ignore the end tokens if possible
				if item[0] == END:
					cnt = 0
				else:
					cnt = self.syllable_counter.count(item[0])

				syllable_item = (item[0], item[1], cnt)
				all_choices.append(syllable_item)

				if cnt > 0 and cnt <= (self.syllable_count - self.num_syllables):
					syllable_choices.append(syllable_item)

			# if no choices are under the syllable limit, oh well?
			if len(syllable_choices) == 0:
				syllable_choices = all_choices

			choices, weights, syllables = zip(*syllable_choices)
			cumdist = list(accumulate(weights))
			print(syllable_choices)


		r = random.random() * cumdist[-1]
		pos = bisect.bisect(cumdist, r)
		selection = choices[pos]

		if syllables is not None:
			self.num_syllables += syllables[pos]
		else:
			self.num_syllables += self.syllable_counter.count(selection)

		self.num_words += 1

		return selection

	@classmethod
	def from_json(cls, json_thing, keywords = None):
		"""
		Given a JSON object or JSON string that was created by `self.to_json`,
		return the corresponding markovify.Chain.
		"""

		if isinstance(json_thing, basestring):
			obj = json.loads(json_thing)
		else:
			obj = json_thing

		if isinstance(obj, list):
			rehydrated = dict((tuple(item[0]), item[1]) for item in obj)
		elif isinstance(obj, dict):
			rehydrated = obj
		else:
			raise ValueError("Object should be dict or list")

		state_size = len(list(rehydrated.keys())[0])

		inst = cls(None, state_size, rehydrated, keywords)
		return inst