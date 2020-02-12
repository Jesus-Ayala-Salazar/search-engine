import sys
import os
import sys
from bs4 import BeautifulSoup
import lxml
import json
import nltk
from nltk.probability import FreqDist
from collections import defaultdict


# possible Posting structure
class Posting:
	def __init__(self):
		self.doc_id = None
		self.freq = 0
		self.tags = []


def tokenize_each_file(filename: str):
	"""Given a directory open each file within the given corpus and tokenize"""

	# extract html identifiers from json file
	with open(filename, 'r', encoding='utf8') as json_file:
		data = json.load(json_file)

	# get web pages directory
	dirname = os.path.dirname(filename)

	# iterate over each html file
	for identifier in data:
		html_filename = os.path.join(dirname, '0/18')

		# need to get frequency in doc, doc_id, tags the token appears in
		with open(html_filename, 'rb') as html_file:
			soup = BeautifulSoup(html_file, 'lxml')
			token_list = nltk.word_tokenize(soup.get_text())
			token_list = [t.lower() for t in token_list if t.isalnum() and len(t) > 1]
			print(token_list)
		break


if __name__ == "__main__":
	path = sys.argv[1]
	tokenize_each_file(path)

	# "dictionary" file {token : [Posting]}
	dict_postings = {}
