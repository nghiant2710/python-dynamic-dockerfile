import sys
import re
import shutil
import os

from distutils.version import LooseVersion
from string import Template

# Mandatory keys
IS_ARCH_BASED_IMAGE = 'isArchBasedImage'
IS_LANGUAGE_SPECIFIC_IMAGE = 'isLanguageSpecificImage'
SUPPORTED_DEVICE = 'supportedDevice'
SUPPORTED_DISTRO = 'supportedDistro'
DISTRO_ARCH = 'arch'
DISTRO_VARIANT = 'variant'
DISTRO_VARIANT_TEMPLATE = 'template'
DISTRO_VARIANT_FILE = 'requiredFile'
BINARY_VERSION = 'binaryVersion'
PATCH = 'patch'

def check_required_key(build_info, key=None, predecessor_key=None, successor_key=None):

	if key:
		if key not in build_info:
			raise Exception('"{0}" key is required in build information file!'.format(key))

	if predecessor_key and successor_key:
		for obj in build_info[predecessor_key]:
			if successor_key not in build_info[predecessor_key][obj]:
				raise Exception('Missing "{0}" key under {1}/{2} in build information file!'.format(successor_key, predecessor_key, obj))


def validate_image_buildinfo(build_info):
	check_required_key(build_info, key=IS_ARCH_BASED_IMAGE)
	check_required_key(build_info, key=IS_LANGUAGE_SPECIFIC_IMAGE)
	check_required_key(build_info, key=SUPPORTED_DISTRO)

	# if it's not arch-based image then supported device list must be there.
	if not build_info[IS_ARCH_BASED_IMAGE]:
		check_required_key(build_info, key=SUPPORTED_DEVICE)

	# check supported architectures for every distro.
	# check_required_key(build_info, predecessor_key=SUPPORTED_DISTRO, successor_key=DISTRO_ARCH)
	# check variant for every distro.
	check_required_key(build_info, predecessor_key=SUPPORTED_DISTRO, successor_key=DISTRO_VARIANT)
	# check template file for every variant
	for distro in build_info[SUPPORTED_DISTRO]:
		check_required_key(build_info[SUPPORTED_DISTRO][distro], predecessor_key=DISTRO_VARIANT, successor_key=DISTRO_VARIANT_TEMPLATE)
	# if it's language specific image then binary version should be there.
	if build_info[IS_LANGUAGE_SPECIFIC_IMAGE]:
		check_required_key(build_info, key=BINARY_VERSION)
	
	if PATCH in build_info:
		for tmp_patch in build_info[PATCH].keys():
			check_required_key(build_info[PATCH][tmp_patch], predecessor_key=DISTRO_VARIANT, successor_key=DISTRO_VARIANT_TEMPLATE)

def get_node_binary_info(version, distro, arch, dict_data):
	resin_url = "http://resin-packages.s3.amazonaws.com/node/v{version}/node-v{version}-linux-{arch}.tar.gz"
	node_url = "http://nodejs.org/dist/v{version}/node-v{version}-linux-{arch}.tar.gz"

	d = {'binary_hash': dict_data['node'][version]['hash'][arch]}

	if version != 'default':
		d['binary_base_version'] = re.search(r'(\d+\.\d+)', version).group()
	else:
		d['binary_base_version'] = 'default'

	d['binary_version'] = dict_data['node'][version]['version']
	d['binary_name'] = 'node-v{version}-linux-{arch}.tar.gz'.format(version=d['binary_version'],arch=arch)

	if 'arm' in arch:
		if (arch == 'armv6hf' or arch == 'armv7hf') and (LooseVersion(d['binary_version']) > LooseVersion('4')):
			url = node_url
			if arch == 'armv6hf':
				arch = 'armv6l'
			else:
				arch = 'armv7l'
		else:
			url = resin_url
	else:
		url = node_url
	d['binary_url'] = url.format(version=d['binary_version'],arch=arch)

	return d

def generate_language_dockerfile(build_info, dict_data, config):
	# TODO: return dockerfile for language specific
	for device in build_info[SUPPORTED_DEVICE]:
		device_info = dict_data['device'][device]
		for distro in build_info[SUPPORTED_DISTRO]:
			for binary_version in build_info[BINARY_VERSION]:
				bin_info = get_node_binary_info(binary_version, distro, device_info[DISTRO_ARCH][distro], dict_data)
				for variant in build_info[SUPPORTED_DISTRO][distro][DISTRO_VARIANT]:
					if variant == 'origin':
						dir_path = os.path.join(config['output_path'],device,distro,bin_info['binary_base_version'])
					else:
						dir_path = os.path.join(config['output_path'],device,distro,bin_info['binary_base_version'],variant)

					if not os.path.isdir(dir_path):
						os.makedirs(dir_path)
					template = open(os.path.join(config['template_path'], build_info[SUPPORTED_DISTRO][distro][DISTRO_VARIANT][variant][DISTRO_VARIANT_TEMPLATE])).read()
					content = Template(template).safe_substitute(bin_info, device=device)
					with open(os.path.join(dir_path,'Dockerfile'), 'wb') as fo:
						fo.write(content)

					if 'requiredFile' in build_info[SUPPORTED_DISTRO][distro][DISTRO_VARIANT][variant]:
						for f in build_info[SUPPORTED_DISTRO][distro][DISTRO_VARIANT][variant]['requiredFile']:
							shutil.copy(os.path.join(config['template_path'],f),dir_path)


	return None

def generate_non_language_dockerfile(build_info, dict_data, config):
	# TODO: return dockerfile for non language specific
	return None

def generate_dockerfile(build_info, dict_data, config):
	# TODO: generate dockerfiles.
	# NOTE: special cases handled here
	if build_info[IS_LANGUAGE_SPECIFIC_IMAGE]:
		generate_language_dockerfile(build_info, dict_data, config)
	else:
		generate_non_language_dockerfile(build_info, dict_data, config)
	return None
