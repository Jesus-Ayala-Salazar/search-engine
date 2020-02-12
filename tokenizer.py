import os
import sys
from bs4 import BeautifulSoup
import lxml
#tokenize --> use algorithms
#dbdicto
def tokenize_each_file(parent: str):
	"""Given a directory open each file within the given corpus and tokenize"""
	c = 0
	for folder in os.listdir(parent):
		if folder.endswith(".json") or folder.endswith(".tsv"):
			continue
		else:
			for file in os.listdir(parent+"\\"+folder):
				with open(parent+"\\"+ folder+"\\" +file, "rb") as f:
					html = f.read()
					print(html)
					soup = BeautifulSoup(f, "lxml")
					#print(folder, file)
					soup.prettify()
					break
				
		#break
	#print(str(soup.prettify()))
"""tokenize
INVIND[token] """
if __name__ == "__main__":
	path = sys.argv[1]
	tokenize_each_file(path)
