import requests

class ImageDescriber:

	def __init__(self, cv_key, cv_location="eastus"):
		# public attributes
		self.cv_location = cv_location
		self.api_url = "https://{}.api.cognitive.microsoft.com/vision/v2.0/describe".format(cv_location)

		# private attributes (keys and such)
		self._cv_key = cv_key

	def _process_request(self, image_url, image_data):
		# set HTTP headers
		headers = dict()
		headers["Ocp-Apim-Subscription-Key"] = self._cv_key;
		headers["Content-Type"] = "application/octet-stream";

		# use image URL in JSON body if provided
		json = None

		if image_url is not None:
			json = { "url": image_url }
			headers["Content-Type"] = "application/json";

		# add params
		params = { "maxCandidates": 1, "language": "en" }

		# send the request
		retries = 0
		maxRetries = 1
		result = None

		while retries < maxRetries:
			response = requests.request("post", self.api_url, headers = headers, json = json, data = image_data, params = params)

			if response.status_code == 200:
				# successful response
				print("success", response)

				if int(response.headers["content-length"]) > 0:
					result = response.json()

				break
			elif response.status_code == 500 or response.status_code == 400:
				# server or error; print message and end
				error = response.json()
				print(error["code"] + ": " + error["message"])
				break
			else:
				# unknown error; try again
				error = response.json()
				print(error)
				retries += 1

		return result


	def describe_file(self, image_file):
		with open(image_file, "rb") as f:
			data = f.read()

		response = self._process_request(None, data)
		return response["description"]["tags"]




