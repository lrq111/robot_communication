# Set your own model path

import sys
import os
import re
from pyltp import Segmentor, Postagger, Parser, NamedEntityRecognizer, SentenceSplitter
import jieba

class NLPUtility(object):
	def __init__(self, word_pattern_file="H:\\new_github_workspace\\Syptom_Knowledge_Graph_309\\test_result.csv"):
		self.word_pattern_file = word_pattern_file

	def load_jieba_model(self):
		print("正在加载jieba模型... ...")
		jieba.load_userdict(self.word_pattern_file)
		print("加载模型完毕。")

	def key_word_extract(self, sentence, data_dict):
		value_count = {}
		seg_list = jieba.cut(sentence)
		# print(seg_list)
		for word in seg_list:
			if word in data_dict:
				vals = data_dict[word]
				for val in vals:
					if val in value_count:
						value_count[val] += 1
					else:
						value_count[val] = 1
		return value_count

	def condition_extract(self, text, data_dict):
		sentences = re.split(r'(\.|\!|\?|。|！|？|\.{6})', text)
		# print(sentences)
		sub = []
		cond = []
		for sentence in sentences:
			seg_list = jieba.lcut(sentence)
			print(seg_list)
			for w_i, word in enumerate(seg_list):
				if word in data_dict and w_i < len(seg_list) - 1:
					sub.append(word)
					cond.append(seg_list[w_i+1])
		return sub, cond






