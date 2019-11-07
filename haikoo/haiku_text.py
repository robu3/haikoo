from markovify import Text
from .haiku_chain import HaikuChain
import json, re

class HaikuText(Text):
	"""
	A haiku text generator using Markov chains.
	"""

	def __init__(self, input_text, state_size=2, chain=None, parsed_sentences=None, retain_original=True, well_formed=True, reject_reg=''):
		"""
		input_text: A string.
		state_size: An integer, indicating the number of words in the model's state.
		chain: A trained markovify.Chain instance for this text, if pre-processed.
		parsed_sentences: A list of lists, where each outer list is a "run"
			  of the process (e.g. a single sentence), and each inner list
			  contains the steps (e.g. words) in the run. If you want to simulate
			  an infinite process, you can come very close by passing just one, very
			  long run.
		retain_original: Indicates whether to keep the original corpus.
		well_formed: Indicates whether sentences should be well-formed, preventing
			  unmatched quotes, parenthesis by default, or a custom regular expression
			  can be provided.
		reject_reg: If well_formed is True, this can be provided to override the
			  standard rejection pattern.
		"""

		self.well_formed = well_formed
		if well_formed and reject_reg != '':
			self.reject_pat = re.compile(reject_reg)

		can_make_sentences = parsed_sentences is not None or input_text is not None
		self.retain_original = retain_original and can_make_sentences
		self.state_size = state_size

		if self.retain_original:
			self.parsed_sentences = parsed_sentences or list(self.generate_corpus(input_text))

			# Rejoined text lets us assess the novelty of generated sentences
			self.rejoined_text = self.sentence_join(map(self.word_join, self.parsed_sentences))
			self.chain = chain or HaikuChain(self.parsed_sentences, state_size)
		else:
			if not chain:
				parsed = parsed_sentences or self.generate_corpus(input_text)
			self.chain = chain or HaikuChain(parsed, state_size)

	@property
	def keywords(self):
		return self._keywords

	@keywords.setter
	def keywords(self, k):
		self._keywords = k
		self.chain.keywords = self._keywords

	@property
	def syllable_count(self):
		return self._syllable_count

	@syllable_count.setter
	def syllable_count(self, n):
		self._syllable_count = n
		self.chain.syllable_count = self._syllable_count

	@classmethod
	def from_dict(cls, obj, **kwargs):
		return cls(
			None,
			state_size = obj["state_size"],
			chain = HaikuChain.from_json(obj["chain"]),
			parsed_sentences = obj.get("parsed_sentences")
		)

	@classmethod
	def from_json(cls, json_str):
		return cls.from_dict(json.loads(json_str))

	@classmethod
	def from_chain(cls, chain_json, corpus=None, parsed_sentences=None):
		"""
		Init a Text class based on an existing chain JSON string or object
		If corpus is None, overlap checking won't work.
		"""
		chain = HaikuChain.from_json(chain_json, None)
		return cls(corpus or None, parsed_sentences=parsed_sentences, state_size=chain.state_size, chain=chain)

	def make_sentence(self, init_state = None, **kwargs):
		self.chain.reset()
		return super().make_sentence(init_state, **kwargs)
