# -*- coding:utf-8 -*-
import re
import pandas as pd
import os
import numpy as np
import time
from scipy import sparse

class CsvUtility(object):
	@staticmethod
	def read_norm_array_csv(file_name):
		result = []
		with open(file_name, 'r', encoding='utf-8') as f:
			for row in f.readlines():  # 将csv 文件中的数据保存到birth_data中
				result.append(row.strip())
		return result

	@staticmethod
	def reform_word_dict(file_name):
		raw_data = CsvUtility.read_norm_array_csv(file_name)
		reform_data = []
		for line in range(1, len(raw_data)):
			sp_line = raw_data[line].split(",")
			print(sp_line)
			reform_data.append([",".join(sp_line[:-1]), sp_line[-1]])
		return reform_data

	@staticmethod
	def write_word_dict(file_name, data):
		with open(file_name, 'w', encoding='utf-8') as f:
			for idata in data:
				f.write(idata + "\n")

	@staticmethod
	def write_relation(file_name, map_key_data, map_value_data):
		with open(file_name, 'w', encoding='utf-8') as f:
			for id, key in enumerate(map_key_data):
				for value in map_value_data[id]:
					f.write(key + '\t' + value + '\n')





