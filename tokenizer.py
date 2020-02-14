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



# {token: {freq, [docIDs], tfIdf, [html tags]}}
#IDF(t) = log_e(Total number of documents / Number of documents with term t in it).


#client = pymongo.MongoClient("mongodb+srv://admin:admincs121@cluster0-zsift.mongodb.net/test?retryWrites=true&w=majority") #connects to mongodb
#db = client['test-database'] #creates db
#col = db['test-collection'] #creates Collection

# possible Posting structure
class Posting:
	def __init__(self, doc_id: str, f:int, tags: [str]):
		self.doc_id = doc_id
		self.freq = f
		self.tags = tags
		self.tf_idf = 0
	def get_doc_id(self):
		return self.doc_id
	def get_freq(self):
		return self.freq
	def get_tags(self):
		return self.tags
	def add_freq(self):
		self.freq +=1
	


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
			
			#html_file = "<html><title>This is a title</title> <h1>This is h1</h1><b>bold 1</b>  <b>bold 2</b> <p>this is a <h1>header1</h1>paragraph <b>bolded in paragraph</b></p></html>"
			soup = BeautifulSoup(html_file, 'lxml')
			
			importantTags = {'h1','h2','h3','h4','h5','h6', 'b','strong'}
			#pageTitle = soup.title.text
			pageH1 = list(word.text for word in soup.find_all('h1')) 	#list
			pageH2 = list(word.text for word in soup.find_all('h2'))	#list
			pageH3 = list(word.text for word in soup.find_all('h3')) 	#list
			pageH4 = list(word.text for word in soup.find_all('h4'))	#list
			pageH5 = list(word.text for word in soup.find_all('h5'))	#list
			pageH6 = list(word.text for word in soup.find_all('h6'))	#list
			pageBold = list(word.text for word in soup.find_all('b'))	#list
			pageStrong = list(word.text for word in soup.find_all('s'))	#list

			###This is me attempting to get all of the text in the document if the word isn't part of any of the ALREADY GOTTEN tags.###
			# wordList = soup.find_all(lambda tag: tag.name not in importantTags and tag.name not in ['title','html','head','body'])
			# wordList = list(word.text for word in wordList)
			# print(wordList)

			# tokenize
			token_list = nltk.word_tokenize(soup.get_text())
			token_list = [t.lower() for t in token_list if t.isalnum() and len(t) > 1]

			# lemmatize
			lemmatizer = WordNetLemmatizer()
			#token_list = [lemmatizer.lemmatize(token) for token in token_list]
			lemmatized_token_list = list()
			tokenFrequency = defaultdict(int)
			for token in token_list:
				changedToken = lemmatizer.lemmatize(token)
				tokenFrequency[changedToken] += 1
				lemmatized_token_list.append(changedToken)
			print(lemmatized_token_list)


		break


if __name__ == "__main__":
	path = sys.argv[1]
	tokenize_each_file(path)

	# "dictionary" file {token : [Posting]}
	dict_postings = {}
