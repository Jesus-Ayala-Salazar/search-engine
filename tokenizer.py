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
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from string import punctuation
import re
import math


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
		return f'doc id: {self.doc_id} | freq: {self.freq} | tags: {self.tags} | tf_idf: {self.tf_idf}'
	

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
	path = sys.argv[1]

	# {token: [] of Postings}
	postings_dict = defaultdict(list)

	# {doc_id: number of terms in document}
	num_tokens_dict = {}

	tokenize_each_file(path, postings_dict, num_tokens_dict)

	# calculate tf-idf
	num_documents = len(num_tokens_dict)
	for t in postings_dict:
		for p in postings_dict[t]:
			tf = p.freq / num_tokens_dict[p.doc_id]
			idf = math.log(num_documents / len(postings_dict[t]), 10)
			p.tf_idf = tf*idf

	# write postings to file
	with open('postings.txt', 'w', encoding='utf8') as file:
		for t in sorted(postings_dict):
			file.write(f'{t}:\n')
			for p in postings_dict[t]:
				file.write(f'{str(p)}\n')
			file.write('\n')
