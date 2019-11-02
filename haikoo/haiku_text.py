from markovify import Text
from .haiku_chain import HaikuChain
import json

class HaikuText(Text):
	"""
	A haiku text generator using Markov chains.
	"""

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
