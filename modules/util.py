import sys
import os
import ConfigParser

DEFAULT_SECTION = 'Default'

def read_config(path, section=DEFAULT_SECTION):
	if not os.path.isfile(path):
		raise IOError("Configuration file {path} not found!".format(path=path))
	config_reader = ConfigParser.ConfigParser()
	config_reader.read(path)
	config_data = {}
	options = config_reader.options(section)
	for option in options:
		try:
			config_data[option] = config_reader.get(section, option)
		except:
			config_data[option] = None
	return config_data

def traverse_directory(path, ext=None):
	if not os.path.isdir(path):
		return None
	all_files = {}
	for root, dirs, files in os.walk(path):
		for tmpfile in files:
			full_path = os.path.join(root, tmpfile)
			if not ext:
				all_files[tmpfile] = full_path
			else:
				if tmpfile.endswith(ext):
					all_files[os.path.splitext(tmpfile)[0]] = full_path
	return all_files



				
