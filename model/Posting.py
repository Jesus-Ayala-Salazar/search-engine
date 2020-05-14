from collections import defaultdict

class Posting:
	#(self, *args, **kwargs):
	#def __init__(self, doc_id):
	def __init__(self, *args, **kwargs):
		#if only one arg is given it is the doc_id
		if len(args) == 1:
			self.doc_id = args[0]
			self.tags = defaultdict(int)    # {tag: freq}
			self.tf_idf = 0
			self.weight = 0
		else: # if not one, then it must be 4, and in order it is doc_id,freq,tags,tf_idf
			self.doc_id = args[0]
			self.freq = args[1]
			self.tags = args[2]
			self.tf_idf = args[3]
