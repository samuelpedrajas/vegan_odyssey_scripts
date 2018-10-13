import os
import subprocess
import sys

from cfg import template_builds


if len(sys.argv) < 2:
	print("Specify a version! (e.g: 1022)")
	sys.exit()

version = sys.argv[1]


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


def get_version_code(cfg):
	return cfg["code"].replace("XXXX", version)


def fix_project_code(cfg):
	print("Fixing project code...")
	_resizer_path = "/home/pspz/Vegan Game/src/scripts/resizer.gd"

	#var _f = 1.00

	data = read_lines(_resizer_path)

	# for every line
	for i, l in enumerate(data):
		if "var _f" in l:
				new_v = " " + cfg["godot"]["f"]
				data[i] = get_new_line(l, "var _f ", new_v, cfg)

	write_lines(_resizer_path, data)


def fix_project_settings(cfg):
	print("Fixing project settings...")
	_project_settings_path = "/home/pspz/Vegan Game/src/project.godot"

	data = read_lines(_project_settings_path)

	# for every line
	for i, l in enumerate(data):
		if "window/handheld/orientation" in l:
				new_v = cfg["godot"]["orientation"]
				data[i] = get_new_line(l, "window/handheld/orientation", new_v, cfg)

	write_lines(_project_settings_path, data)


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
				new_v = get_version_code(cfg)
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


def godot_export(apk_name):
	output = os.path.join("/home/pspz/Vegan Game/distribution/out/", apk_name)
	process = subprocess.Popen(
		["/home/pspz/Vegan Game/VO_godot/bin/godot.x11.tools.64", "--export", "Android",
		output, "--path", "/home/pspz/Vegan Game/src", "--audio-driver", "ALSA", "--editor"],
		stdout=subprocess.PIPE
	)

	stdout, stderr = process.communicate()

	process.kill()


def compile_godot(arch, sdk):
	pass


# main loop
for template_build in template_builds:
	compile_godot(template_build["arch"], template_build["sdk"])
	for cfg in template_build["cfgs"]:
		print("Processing {}...".format(cfg["code"]))

		# export
		fix_project_code(cfg)
		fix_project_settings(cfg)
		fix_export_presets(cfg)
		version_code = get_version_code(cfg)
		#godot_export(version_code + ".apk")
