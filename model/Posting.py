from collections import defaultdict

class Posting:
	#(self, *args, **kwargs):
	#def __init__(self, doc_id):
	def __init__(self, *args, **kwargs):
		#if only one arg is given it is the doc_id
		if len(args) == 1:
			self.doc_id = args[0]
			self.freq = 0
			self.tags = defaultdict(int)    # {tag: freq}
			self.tf_idf = 0
		else: # if not one, then it must be 4, and in order it is doc_id,freq,tags,tf_idf
			self.doc_id = args[0]
			self.freq = args[1]
			self.tags = args[2]
			self.tf_idf = args[3]
	
	def get_doc_id(self):
		return self.doc_id
	def get_freq(self):
		return self.freq
	def get_tags(self):
		return self.tags
	def get_tf_idf(self):
		return self.tf_idf
	# for debugging
	def __str__(self):
		return f'doc id: {self.doc_id} | freq: {self.freq} | tags: {self.tags} | tf_idf: {self.tf_idf}'
