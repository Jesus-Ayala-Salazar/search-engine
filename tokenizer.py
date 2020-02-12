import sys
import os
import sys
from bs4 import BeautifulSoup
import lxml
import json


def tokenize_each_file(filename: str):
	"""Given a directory open each file within the given corpus and tokenize"""
	with open(filename, 'r', encoding='utf8') as json_file:
		data = json.load(json_file)

		for path in data:



if __name__ == "__main__":
	path = sys.argv[1]
	tokenize_each_file(path)
