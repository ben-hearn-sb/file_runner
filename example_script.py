import json
from collections import OrderedDict
import os

def printFileNames(inputFile=''):
	print inputFile

def changeFileParams(inputFile=''):
	path, ext = os.path.splitext(inputFile)
	fileName = path.split('/')[-1]
	data = returnJsonAsDict(jsonPath=inputFile, ordered=True)
	data['name'] = 'example_file_testing'
	#data['name'] = 'example_file'
	data['uvSets'] = 0
	writeJsonFile(fileData=data, outFile=inputFile)

def returnJsonAsDict(jsonPath='', ordered=False):
	with open(jsonPath, 'r') as f:
		if ordered:
			# Retrieving the JSON data in the same order it went in
			data = json.load(f, object_pairs_hook=OrderedDict)
		else:
			data = json.load(f)
	return data

def byteify(input):
	""" Returns a JSON dict as str instead of unicode """
	if isinstance(input, dict):
		return {byteify(key): byteify(value) for key, value in input.iteritems()}
	elif isinstance(input, list):
		return [byteify(element) for element in input]
	elif isinstance(input, unicode):
		return input.encode('utf-8')
	else:
		return input

def writeJsonFile(fileData=None, outFile=''):
	with open(outFile , 'w') as jsonFile:
		json.dump(fileData, jsonFile, indent=4)