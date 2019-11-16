import json

class HaikooResult:
    """
    The result of a haiku generation.
    It contains the generated text, keywords identified and used, and the resulting image.
    If any errors occurred during process, error_text will be set with the error message(s).
    """

    def __init__(self, text, keywords, image):
        self.text = text
        self.keywords = keywords
        self.image = image
        self.error_message = None

    def __str__(self):
        return json.dumps(self.__dict__, indent=4, sort_keys=True)

    @property
    def success(self):
        return self.error_message is None