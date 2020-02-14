import sys
import os
import sys
from bs4 import BeautifulSoup
import lxml
import json
import nltk
from nltk.probability import FreqDist
from collections import defaultdict
import pymongo

from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from string import punctuation
import re


#IDF(t) = log_e(Total number of documents / Number of documents with term t in it).

#client = pymongo.MongoClient("mongodb+srv://admin:admincs121@cluster0-zsift.mongodb.net/test?retryWrites=true&w=majority") #connects to mongodb
#db = client['test-database'] #creates db
#col = db['test-collection'] #creates Collection


class Posting:
	def __init__(self, doc_id):
		self.doc_id = doc_id
		self.freq = 0
		self.tags = defaultdict(int)    # {tag: freq}
		self.tf_idf = 0

	# for debugging
	def __str__(self):
		return f'doc id: {self.doc_id} | freq: {self.freq} | tags: {self.tags}'
	

def tokenize_each_file(filename: str, postings_dict: {str: [Posting]}):
	"""Given a directory open each file within the given corpus and tokenize"""

	# extract html identifiers from json file
	with open(filename, 'r', encoding='utf8') as json_file:
		data = json.load(json_file)

	# get web pages directory
	dirname = os.path.dirname(filename)

	# iterate over each html file
	for identifier in data:
		html_filename = os.path.join(dirname, identifier)     # use '13/16' for html with title and body

		# need to get frequency in doc, doc_id, tags the token appears in
		with open(html_filename, 'rb') as html_file:
			soup = BeautifulSoup(html_file, 'lxml')
			lemmatizer = WordNetLemmatizer()
			token_list = []
			# {token: single Posting}
			inner_dict = defaultdict(lambda: Posting(identifier))
			important_tags = {'title','h1','h2','h3','h4','h5','h6','strong'}

			# for string in document
			for s in soup.strings:
				# for token in string
				for t in nltk.word_tokenize(s):
					# filtering
					if t.isalnum() and len(t) > 1:
						# add lemmatized token to list, increment frequency
						token = lemmatizer.lemmatize(t.lower())
						token_list.append(token)
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


if __name__ == "__main__":
	path = sys.argv[1]
	# {token: [] of Postings}
	postings_dict = defaultdict(list)
	tokenize_each_file(path, postings_dict)
	with open('postings.txt', 'w', encoding='utf8') as file:
		for t in postings_dict:
			file.write(f'{t}:\n')
			for p in postings_dict[t]:
				file.write(f'{str(p)}\n')
