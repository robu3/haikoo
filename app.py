import sys, json

from argparse import ArgumentParser
from haikoo.haikoo import Haikoo
from haikoo.image_describer import ImageDescriber

# load configuration options from config file
try:
	with open("config.json") as f:
		config = json.loads(f.read())
except:
	print("Missing or invalid configuration file: config.json")

if "cv_key" not in config or "cv_region" not in config:
	print("Config file must contain 'cv_key' and 'cv_region' settings.")
	exit()

# generate haiku
describer = ImageDescriber(config["cv_key"], config["cv_region"])
parser = ArgumentParser(description="Generate haiku poems inspired by an image.")
parser.add_argument("image", type=str, help="Path to the image to use as inspiration.")
parser.add_argument("--model", type=str, default="fusion", help="Name of the Markov model to use. Valid options: classic, frost, shakespeare, fusion")
parser.add_argument("--text", type=str, default=None, help="Haiku text to overlay on the image (optional, will be generated if not provided)")
args = parser.parse_args()

haikoo = Haikoo(describer, args.model)
haiku = haikoo.create_image(file_path=args.image, out_file_path="haikoo.png", text=args.text)

print(haiku)
