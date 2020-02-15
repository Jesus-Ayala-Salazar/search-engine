import sys
import os
from bs4 import BeautifulSoup
import lxml
import json
import nltk
from nltk.probability import FreqDist
from collections import defaultdict
import pymongo
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from string import punctuation
import re
import math
from model.Posting import Posting


#IDF(t) = log_e(Total number of documents / Number of documents with term t in it).

#client = pymongo.MongoClient("mongodb+srv://admin:admincs121@cluster0-zsift.mongodb.net/test?retryWrites=true&w=majority") #connects to mongodb
#db = client['test-database'] #creates db
###this for testing
#col = db['test-collection'] #creates Collection

#### this should be ran when everything works.
#sedb = client["se-database"]
#collec = sedb["inv-collection"]

### MUST ENCODE POSTING TO BE ABLE TO INPUT IT INTO THE DATABASE"
def encode_Posting(post: Posting):
	return {"_type": "Posting", "doc_id": post.get_doc_id(), "freq": post.get_freq(), "tags": post.get_tags(), "tf_idf": post.get_tf_idf()}

### MUST DECODE FROM DOCUMENT
def decode_Posting(document):
	assert document["_type"] == "Posting"
	return Posting(document["doc_id"], document["freq"], document["tags"], document["tf_idf"])

def sort_tfID(post: Posting):
	return post.get_tf_idf()
#mydict = {"ics": {"doc_10": 10}}
#mydict1 = {"yes": Posting("0/10")}

#col.insert_one(mydict)
#ol.insert_one(mydict1)

def tokenize_each_file(filename: str,
					   postings_dict: {str: [Posting]},
					   num_tokens_dict: {str: int}):
	"""Given a directory open each file within the given corpus and tokenize"""

	# extract html identifiers from json file
	with open(filename, 'r', encoding='utf8') as json_file:
		data = json.load(json_file)

	# get web pages directory
	dirname = os.path.dirname(filename)

	# iterate over each html file
	for doc_id in data:
		html_filename = os.path.join(dirname, doc_id)     # use '13/16' for html with title and body

		# need to get frequency in doc, doc_id, tags the token appears in
		with open(html_filename, 'rb') as html_file:
			soup = BeautifulSoup(html_file, 'lxml')
			lemmatizer = WordNetLemmatizer()
			num_tokens = 0
			# token_list = []
			# {token: single Posting}
			inner_dict = defaultdict(lambda: Posting(doc_id))
			important_tags = {'title','h1','h2','h3','h4','h5','h6','strong'}

			# for string in document
			for s in soup.strings:
				# for token in string
				for t in nltk.word_tokenize(s):
					# filtering
					if t.isalnum() and len(t) > 1 and t not in set(stopwords.words('english')):
						# add lemmatized token to list, increment frequency
						token = lemmatizer.lemmatize(t.lower())
						num_tokens += 1
						# token_list.append(token)
						inner_dict[token].freq += 1

						# if token in important tags, add it
						if s.parent.name in important_tags:
							inner_dict[token].tags[s.parent.name] += 1

			# prints all Postings in current document
			# for t in inner_dict:
			# 	print(f'{t}: {inner_dict[t]}\n')

			# add each Posting from current document to global dictionary
			for token in inner_dict:
				postings_dict[token].append(inner_dict[token])

			# add total number of tokens to doc_id dictionary
			num_tokens_dict[doc_id] = num_tokens

			# progress file to see number of current documents indexed
			with open('progress.txt', 'a', encoding='utf8') as file:
				file.write(f'doc id: {doc_id} | num words: {num_tokens}\n')


if __name__ == "__main__":
	####testing
	#p1 = Posting("0/8", 10, {"h1": 3, "title": 2}, 0.01)
	#p2 = Posting("1/8", 22, {"h1": 1, "title": 1}, 0.05)
	#p3 = Posting("2/8", 20, {"h1": 4, "title": 5}, 0.06)
	#mydict = {"ics": [encode_Posting(p1), encode_Posting(p2), encode_Posting(p3)], "informatics": [encode_Posting(p1), encode_Posting(p2), encode_Posting(p3)], "data": [encode_Posting(p1), encode_Posting(p2), encode_Posting(p3)]}
	#col.insert_one(mydict)
	#invi = col.find_one()
	#print(invi)
	###END OF TESTING

	path = sys.argv[1]

	# # {token: [] of Postings}
	postings_dict = defaultdict(list)

	# # {doc_id: number of terms in document}
	num_tokens_dict = {}

	tokenize_each_file(path, postings_dict, num_tokens_dict)

	#  # calculate tf-idf
	num_documents = len(num_tokens_dict)
	for t in postings_dict:
	 	for p in postings_dict[t]:
	 		tf = p.freq / num_tokens_dict[p.doc_id]
	 		idf = math.log(num_documents / len(postings_dict[t]), 10)
	 		p.tf_idf = tf*idf

	#  # sort by tf-idf
	#for t in postings_dict:
	#	postings_dict[t].sort(key = sort_tfID, reverse = True)

	## encode postings into a dict to add to mongodb

	# this dict will be added to db
	encoded_posting = defaultdict(list)

	#Copies posting_dict and encodes
	for t in postings_dict:
		for p in postings_dict:
			encode_Posting[t].append(encode_Posting(p))

	#  # insert into data base ran when we are done.
	#collec.insert_one(encoded_posting)
	 # write postings to file
	
	with open('postings.txt', 'w', encoding='utf8') as file:
		for t in sorted(postings_dict):
	 		file.write(f'{t}:\n')
	 		for p in postings_dict[t]:
	 			file.write(f'{str(p)}\n')
	 		file.write('\n')

