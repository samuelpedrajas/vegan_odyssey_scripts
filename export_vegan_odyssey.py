from cfg import cfgs
from os import listdir
from os.path import isfile, join


VERSION = 1022

# export key - json key
EXPORT_REPLACEMENTS = [
	# "version/code": "",
	"architectures/armeabi-v7a",
	"architectures/arm64-v8a",
	"architectures/x86",
	"architectures/x86_64",

	"screen/support_small",
	"screen/support_normal",
	"screen/support_large",
	"screen/support_xlarge"
]



def read_lines(_path):
	# with is like your try .. finally block in this case
	with open(_path, 'r') as file:
	    # read a list of lines into data
	    return file.readlines()


def replace_value(_key, _value, data):
	for i, l in enumerate(data):
		if _key in l:
			k, v = l.split("=")
			data[i] = "=".join([k, _value]) + "\n"


def write_lines(_path):
	# and write everything back
	with open(_path, 'w') as file:
	    file.writelines(data)


_export_presets_path = "/home/pspz/Vegan Game/src/export_presets.cfg"

data = read_lines(_export_presets_path)

# main loop
for cfg in cfgs:
	print("Processing {}...".format(cfg))
