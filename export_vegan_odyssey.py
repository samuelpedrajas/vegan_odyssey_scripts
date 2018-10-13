import os
import subprocess
import sys
import threading

from cfg import template_builds
from shutil import copyfile
from time import sleep


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


def clean_godot():
	process = subprocess.Popen(
		["scons", "p=android", "--clean"],
		stdout=subprocess.PIPE,
		cwd="/home/pspz/Vegan Game/VO_godot/",
		env={
			**os.environ,
			"ANDROID_HOME": "/home/pspz/Android/Sdk",
			"ANDROID_NDK_ROOT": "/home/pspz/Android/Sdk/ndk-bundle"
		}
	)

	stdout, stderr = process.communicate()


def godot_export(apk_name):
	print("Exporting with godot...")
	output = os.path.join("/home/pspz/Vegan Game/distribution/out/", apk_name)

	if os.path.isfile(output):
		print("Removing {}...".format(output))
		os.remove(output)

	process = subprocess.Popen(
		["./godot.x11.tools.64", "--export", "Android",
		output, "--path", "/home/pspz/Vegan Game/src", "--audio-driver", "ALSA", "--editor"],
		stdout=subprocess.PIPE,
		cwd="/home/pspz/Vegan Game/VO_godot/bin/"
	)

	def _run_export(_process):
		stdout, stderr = _process.communicate()


	thread = threading.Thread(target=_run_export, args=(process, ))
	thread.start()

	while True:
		sleep(3)
		if os.path.isfile(output):
			print("APK CREATED!")
			sleep(3)
			process.terminate()
			thread.join()
			break
		else:
			print("APK STILL PENDING...")



def compile_godot(arch, sdk, bits=None):
	cmd = ["scons", "optimize=custom", "platform=android", "android_arch={}".format(arch),
	"target=release", "android_neon=no", "deprecated=no", "xml=no", "disable_3d=yes",
	"android_stl=yes", "game_center=no", "store_kit=no", "icloud=no", "module_bmp_enabled=no",
	"module_bullet_enabled=no", "module_dds_enabled=no", "module_mobile_vr_enabled=no",
	"module_opus_enabled=no", "module_pvr_enabled=no", "module_svg_enabled=no",
	"module_tga_enabled=no", "module_theora_enabled=no", "module_visual_script_enabled=no",
	"module_webm_enabled=no", "verbose=no", "ndk_platform=android-{}".format(sdk), "-j4"]

	if bits is not None:
		cmd = cmd + ["bits=" + bits]

	print("Compiling using:")
	print(" ".join(cmd))

	process = subprocess.Popen(
		cmd,
		stdout=subprocess.PIPE,
		cwd="/home/pspz/Vegan Game/VO_godot/",
		env={
			**os.environ,
			"ANDROID_HOME": "/home/pspz/Android/Sdk",
			"ANDROID_NDK_ROOT": "/home/pspz/Android/Sdk/ndk-bundle"
		}
	)

	stdout, stderr = process.communicate()
	print("Finished compiling:")
	print(stdout)


	print("Starting gradle")
	process = subprocess.Popen(
		["./gradlew", "build"],
		stdout=subprocess.PIPE,
		cwd="/home/pspz/Vegan Game/VO_godot/platform/android/java",
		env={
			**os.environ,
			"ANDROID_HOME": "/home/pspz/Android/Sdk",
			"ANDROID_NDK_ROOT": "/home/pspz/Android/Sdk/ndk-bundle"
		}
	)

	stdout, stderr = process.communicate()
	print("Finished gradle:")
	print(stdout)


# main loop
for template_build in template_builds:
	#clean_godot()
	copyfile(
		os.path.join("/home/pspz/Vegan Game/distribution/android_manifests",
			template_build["manifest"]),
		"/home/pspz/Vegan Game/VO_godot/platform/android/AndroidManifest.xml.template"
	)
	print("Manifest copied:", template_build["manifest"])
	bits = template_build.get("bits", None)
	compile_godot(template_build["arch"], template_build["sdk"], bits)

	for cfg in template_build["cfgs"]:
		#export
		print("Processing {}...".format(cfg["code"]))

		fix_project_code(cfg)
		fix_project_settings(cfg)
		fix_export_presets(cfg)
		version_code = get_version_code(cfg)
		godot_export(version_code + ".apk")
