import re

class SyllableCounter:
    """
    A syllable counter.
    """
    VOWELS = ["a", "e", "i", "o", "u", "y"]

    def count(self, word):
        """
        This method counts the syllables in a word or phrase.
        """
        # remove silent e's at the end of a word
        # (generally silent, at least)
        if word[len(word) - 1] == "e":
            word = word[:-1]

        # count runs of consecutive vowels
        # could use a regular expression for this
        syllable_count = 0

        in_vowels = False

        for i in range(len(word)):
            is_vowel = word[i] in self.VOWELS

            if is_vowel:
                if not in_vowels:
                    syllable_count += 1
                in_vowels = True
            else:
                in_vowels = False

        # no word has zero syllables
        if syllable_count == 0:
            syllable_count = 1

        return syllable_count

    def split_syllables(self, word):
        """
        DEPRECATED. No longer in use, will be removed in the future.

        This method splits a word into its constituent syllables (as best it can).
        """
        start = 0
        end = 0
        is_start_vowel = False
        is_vowel = False
        is_prev_vowel = word[start] in self.VOWELS
        syllables = []

        # define a syllable as the transition from a consonant to a vowel(s) to a consonant
        # basically, a consonant sandwich with vowels in the middle
        # OR
        # a transition from a vowel to consonant(s) to a vowel
        # but exclude the ending vowel
        while end < len(word):
            is_start_vowel = word[start] in self.VOWELS
            is_vowel = word[end] in self.VOWELS

            #if start == 0:
                #is_prev_vowel = is_start_vowel

            # syllable starting with a consonant
            if not is_start_vowel:
                # C-V-C
                if is_prev_vowel and not is_vowel:
                    # add the syllable
                    # and start scanning for the next
                    syllables.append(word[start:end+1])
                    start = end + 1
                    end = start
            else:
                # syllable starting with a vowel
                # V-C-V
                if not is_prev_vowel and is_vowel:
                    # rollback one letter
                    # then add the syllable
                    end = end - 1
                    syllables.append(word[start:end+1])
                    start = end + 1
                    end = start

            # track previous letter
            is_prev_vowel = is_vowel
            end += 1

        # remainder letters
        if end == len(word) and start < end:
            if end - start > 1 or len(syllables) == 0:
                syllables.append(word[start:end+1])
            else:
                syllables[len(syllables) - 1] += word[start:end+1]

        return syllables

    def remove_punctuation(self, str):
        """
        Strips punctuation from the string.
        """
        return re.sub(r'[\.\?!,/]+', "", str)

    def split_sentence(self, sentence, syllable_count):
        """
        Splits the sentence into two at the specified number of syllables.
        This will also remove any punctuation.

        :return: Tuple of split halves.
        """
        sentence = self.remove_punctuation(sentence)
        words = sentence.split(" ")
        count = 0

        first = []

        while len(words) > 0:
            w = words.pop(0)

            first.append(w)
            count += self.count(w)

            if count >= syllable_count:
                break

        return (" ".join(first), " ".join(words))
        

