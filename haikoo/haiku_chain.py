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

	def __init__(self, corpus, state_size, model = None, keywords = None):
		self.syllable_counter = SyllableCounter()
		self.keywords = keywords
		self.num_syllables = 0
		self.syllable_count = 0
		self.num_words = 0

		# call parent class's constructor
		super().__init__(corpus, state_size, model)

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
				# item: (word, [count, syllables])
				syllable_item = (item[0], item[1][0], item[1][1])
				all_choices.append(syllable_item)

				if syllable_item[2] > 0 and syllable_item[2] <= (self.syllable_count - self.num_syllables):
					syllable_choices.append(syllable_item)

			# if no choices are under the syllable limit, oh well?
			if len(syllable_choices) == 0:
				syllable_choices = all_choices

			choices, weights, syllables = zip(*syllable_choices)
			cumdist = list(accumulate(weights))

		r = random.random() * cumdist[-1]
		pos = bisect.bisect(cumdist, r)
		selection = choices[pos]

		if syllables is not None:
			self.num_syllables += syllables[pos]
		else:
			self.num_syllables += self.syllable_counter.count(selection)

		self.num_words += 1

		return selection

	def build(self, corpus, state_size):
		"""
		Build a Python representation of the Markov model. Returns a dict
		of dicts where the keys of the outer dict represent all possible states,
		and point to the inner dicts. The inner dicts represent all possibilities
		for the "next" item in the chain, along with the count of times it
		appears.
		"""

		# Using a DefaultDict here would be a lot more convenient, however the memory
		# usage is far higher.
		model = {}

		for run in corpus:
			items = ([ BEGIN ] * state_size) + run + [ END ]
			for i in range(len(run) + 1):
				state = tuple(items[i:i+state_size])
				follow = items[i+state_size]
				if state not in model:
					model[state] = {}

				if follow not in model[state]:
					# track both count/frequency and number of syllables in the word
					model[state][follow] = [
						0,
						0 if (follow == BEGIN or follow == END) else self.syllable_counter.count(follow)
						]

				model[state][follow][0] += 1
		return model

	def precompute_begin_state(self):
		"""
		Caches the summation calculation and available choices for BEGIN * state_size.
		Significantly speeds up chain generation on large corpuses. Thanks, @schollz!
		"""
		begin_state = tuple([ BEGIN ] * self.state_size)
		choices, data = zip(*self.model[begin_state].items())
		weights, _ = zip(*data)

		cumdist = list(accumulate(weights))
		self.begin_cumdist = cumdist
		self.begin_choices = choices

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