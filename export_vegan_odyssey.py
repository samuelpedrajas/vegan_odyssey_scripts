from cfg import cfgs
from os import listdir
from os.path import isfile, join


version = input("Introduce version: ")


def read_lines(_path):
	# with is like your try .. finally block in this case
	with open(_path, 'r') as file:
	    # read a list of lines into data
	    return file.readlines()


def write_lines(_path, data):
	# and write everything back
	with open(_path, 'w') as file:
	    file.writelines(data)


def get_new_line(l, r, v, cfg):
	k, old_v = l.split("=")
	return "=".join([k, v]) + "\n"


def fix_export_presets(cfg):
	print("Fixing export presets...")
	_export_presets_path = "/home/pspz/Vegan Game/src/export_presets.cfg"

	data = read_lines(_export_presets_path)

	replacements = [
		"architectures/armeabi-v7a",
		"architectures/arm64-v8a",
		"architectures/x86",
		"architectures/x86_64",

		"screen/support_small",
		"screen/support_normal",
		"screen/support_large",
		"screen/support_xlarge"
	]

	# for every line
	for i, l in enumerate(data):
		if "version/code" in l:
				new_v = cfg["code"].replace("XXXX", version)
				data[i] = get_new_line(l, replacement, new_v, cfg)

		elif "version/name" in l:
			new_v = '"' + ".".join([version[0], version[1], version[2:]]) + '"'
			data[i] = get_new_line(l, replacement, new_v, cfg)

		else:
			for replacement in replacements:
				if replacement in l:
					new_v = cfg["export"][replacement]
					data[i] = get_new_line(l, replacement, new_v, cfg)
					print("Replaced {} by {}".format(l, data[i]))

					break

	write_lines(_export_presets_path, data)


# main loop
for cfg in cfgs:
	print("Processing {}...".format(cfg["code"]))

	# export
	fix_export_presets(cfg)
