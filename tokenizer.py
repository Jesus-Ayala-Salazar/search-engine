import os
from bs4 import BeautifulSoup
import lxml
#tokenize --> use algorithms
def tokenize_each_file(parent: str):
	"""Given a directory open each file within the given corpus and tokenize"""
	c = 0
	for folder in os.listdir(parent):
		if folder.endswith(".json") or folder.endswith(".tsv"):
			continue
		else:
			for file in os.listdir(parent+"\\"+folder):
				#print(str(folde
				with open(parent+"\\"+ folder+"\\" +file, "rb") as f:
					html= f.read()
					print(html)
					soup = BeautifulSoup(f, "lxml")
					#print(folder, file)
					print(soup.prettify())
					break
				
		break
	print(str(soup.prettify()))
	#soup.prettify()


if __name__ == "__main__":
	tokenize_each_file("C:\\Users\\eduar\\121\\Assign3\\WEBPAGES_CLEAN")


