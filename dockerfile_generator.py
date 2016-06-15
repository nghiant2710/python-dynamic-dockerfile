#!/usr/bin/env python2

import sys
import os
import json

from modules import util
from modules import generator

CONFIG_PATH = 'conf/dd.conf'

def load_data(path, ext=None):
	if not os.path.isdir(path):
		raise IOError("Directory {path} not found!".format(path=path))
	dict_data = {}
	all_files = util.traverse_directory(path, ext)
	for key in all_files:
		dict_data[key] = json.loads(open(all_files[key]).read())
	return dict_data

def generate_dockerfile(image_data, dict_data, config):
	generator.validate_image_buildinfo(image_data)
	generator.generate_dockerfile(image_data, dict_data, config)


def main():

	image_list = None
	if len(sys.argv) > 1:
		# read image list to be built, otherwise build all
		image_list = sys.argv[1:]

	# read config
	config = util.read_config(CONFIG_PATH)
	dict_path = config['dictionary_path']
	image_path = config['image_path']
	template_path = config['template_path']
	output_path = config['output_path']

	# load dictionary
	dict_data = load_data(dict_path,'.json')
	image_data = load_data(image_path,'.json')

	if image_list:
		if not all(image in image_data for image in image_list):
			raise Exception('Image(s) build info do not exist {image}'.format(image=image_list))
	else:
		image_list = image_data.keys()
	
	for image in image_list:
		generate_dockerfile(image_data[image], dict_data, config)

if __name__ == "__main__":
	if not main():
		sys.exit(1)
	sys.exit(0)
