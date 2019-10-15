import json

class HaikooResult:

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