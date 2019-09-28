import sys, markovify

# open the source file
source_file = sys.argv[1]

with open(source_file) as f:
	corpus = f.read() 

# build the text model
#text_model = markovify.NewlineText(corpus)
text_model = markovify.Text(corpus)

#for i in range(3):
#	print(text_model.make_sentence())

with open(source_file + ".json", "w") as f:
	f.write(text_model.to_json())

