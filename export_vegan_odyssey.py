import os
import subprocess
import sys
import threading

from shutil import copyfile
from time import sleep

from cfg import template_builds


PROJECT_DIR = "/home/pspz/Vegan Game/"
SRC_DIR = os.path.join(PROJECT_DIR, "src/")
GODOT_DIR = os.path.join(PROJECT_DIR, "VO_godot/")
ANDROID_ENV = {
	"ANDROID_HOME": "/home/pspz/Android/Sdk",
	"ANDROID_NDK_ROOT": "/home/pspz/Android/Sdk/ndk-bundle",
	**os.environ
}
PRODUCTION_MODE = True


def read_lines(_path):
	# with is like your try .. finally block in this case
	with open(_path, 'r') as file:
	    # read a list of lines into data
	    return file.readlines()


def write_lines(_path, data):
	# and write everything back
	with open(_path, 'w') as file:
	    file.writelines(data)


def get_new_line(l, r, v):
	k, old_v = l.split("=")
	return "=".join([k, v]) + "\n"


def get_version_code(cfg, version):
	return cfg["code"].replace("XXXX", version)


def fix_project_code(cfg):
	print("Fixing project code...")
	_resizer_path = os.path.join(SRC_DIR, "scripts/resizer.gd")

	#var _f = 1.00
	data = read_lines(_resizer_path)

	# for every line
	for i, l in enumerate(data):
		if "var _f" in l:
				data[i] = get_new_line(l, "var _f ", " " + cfg["godot"]["f"])

	write_lines(_resizer_path, data)

	ad_test_id = '"ca-app-pub-3940256099942544/5224354917"'
	ad_real_id = '"ca-app-pub-1160358939410189/4394674925"'
	used_id = ad_real_id if PRODUCTION_MODE else ad_test_id

	_admob_path = os.path.join(SRC_DIR, "scripts/autoload/admob.gd")

	# var adRewardedId = "ca-app-pub-3940256099942544/1712485313"
	data = read_lines(_admob_path)

	# for every line
	for i, l in enumerate(data):
		if "var adRewardedId" in l:
				data[i] = get_new_line(l, "var adRewardedId ", " " + used_id)

	write_lines(_admob_path, data)


def fix_project_settings(cfg):
	print("Fixing project settings...")
	_project_settings_path = os.path.join(SRC_DIR, "project.godot")

	data = read_lines(_project_settings_path)

	rendering_pos = -1
	driver_name_found = False
	audio_driver_found = False

	# for every line
	for i, l in enumerate(data):
		if "window/handheld/orientation" in l:
			new_v = cfg["godot"]["orientation"]
			data[i] = get_new_line(l, "window/handheld/orientation", new_v)
		elif "[rendering]" in l:
			rendering_pos = i
		elif "quality/driver/driver_name" in l:
			driver_name_found = True
		elif 'driver="Android"' in l:
			audio_driver_found = True

	if not driver_name_found:
		data[rendering_pos] = '[rendering]\n\nquality/driver/driver_name="GLES2"'

	if not audio_driver_found:
		data[len(data) - 1] += '\n[audio]\n\ndriver="Android"\n'

	write_lines(_project_settings_path, data)


def fix_export_presets(cfg, version):
	print("Fixing export presets...")
	_export_presets_path = os.path.join(SRC_DIR, "export_presets.cfg")

	data = read_lines(_export_presets_path)

	# for every line
	for i, l in enumerate(data):
		if "version/code=" in l:
				new_v = get_version_code(cfg, version)
				data[i] = get_new_line(l, "version/code", new_v)

		elif "version/name=" in l:
			new_v = '"' + ".".join([version[0], version[1], version[2:]]) + '"'
			data[i] = get_new_line(l, "version/name", new_v)

		else:
			for replacement in cfg["export"].keys():
				if replacement + "=" in l:
					new_v = cfg["export"][replacement]
					data[i] = get_new_line(l, replacement, new_v)
					print("Replaced {} by {}".format(l, data[i]))

					break

	write_lines(_export_presets_path, data)


def godot_export(output):
	print("Exporting with godot...")
	if os.path.isfile(output):
		print("Removing {}...".format(output))
		os.remove(output)

	process = subprocess.Popen(
		["./godot.x11.tools.64", "--export", "Android",
		output, "--path", SRC_DIR, "--audio-driver", "ALSA", "--editor"],
		stdout=subprocess.PIPE,
		cwd=os.path.join(GODOT_DIR, "bin/")
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


def _clean_godot():
	print("Cleaning android build...")

	for template in ["android_debug.apk", "android_release.apk"]:
		template_path = os.path.join(GODOT_DIR, "bin/", template)
		if os.path.isfile(template_path):
			print("Removing {}...".format(template_path))
			os.remove(template_path)

	process = subprocess.Popen(
		["scons", "p=android", "--clean"],
		stdout=subprocess.PIPE,
		cwd=GODOT_DIR,
		env=ANDROID_ENV
	)

	stdout, stderr = process.communicate()
	print("Clean finished:")
	print(stdout)


def _compile_godot(arch, sdk):
	cmd = ["scons", "optimize=custom", "platform=android", "android_arch={}".format(arch),
	"target=release", "android_neon=no", "deprecated=no", "xml=no", "disable_3d=yes",
	"android_stl=yes", "game_center=no", "store_kit=no", "icloud=no", "module_bmp_enabled=no",
	"module_bullet_enabled=no", "module_dds_enabled=no", "module_mobile_vr_enabled=no",
	"module_opus_enabled=no", "module_pvr_enabled=no", "module_svg_enabled=no",
	"module_tga_enabled=no", "module_theora_enabled=no", "module_visual_script_enabled=no",
	"module_webm_enabled=no", "verbose=no", "ndk_platform=android-{}".format(sdk), "-j4"]

	print("Compiling using:")
	print(" ".join(cmd))

	process = subprocess.Popen(
		cmd,
		stdout=subprocess.PIPE,
		cwd=GODOT_DIR,
		env=ANDROID_ENV
	)

	stdout, stderr = process.communicate()
	print("Finished compiling:")
	print(stdout)


def _gradlew_build(sdk):
	print("Starting gradle")
	process = subprocess.Popen(
		["./gradlew", "build", "-PMIN_SDK_VERSION={}".format(sdk)],
		stdout=subprocess.PIPE,
		cwd=os.path.join(GODOT_DIR, "platform/android/java"),
		env=ANDROID_ENV
	)

	stdout, stderr = process.communicate()
	print("Finished gradle:")
	print(stdout)


def prepare_templates(template_build):
	_clean_godot()

	copyfile(
		os.path.join(PROJECT_DIR, "distribution/android_manifests", template_build["manifest"]),
		os.path.join(GODOT_DIR, "platform/android/AndroidManifest.xml.template")
	)
	print("Manifest copied:", template_build["manifest"])

	arch, sdk = template_build["arch"], template_build["sdk"]

	_compile_godot(arch, sdk)
	_gradlew_build(sdk)


def export_cfg(cfg, version, out):
	#export
	print("Processing {}...".format(cfg["code"]))

	fix_project_code(cfg)
	fix_project_settings(cfg)
	fix_export_presets(cfg, version)
	version_code = get_version_code(cfg, version)
	godot_export(os.path.join(out, version_code + ".apk"))


def main(version):
	specific_release = len(version) > 4

	if specific_release:
		out = os.path.join(PROJECT_DIR, "distribution/")
		for template_build in template_builds:
			for cfg in template_build["cfgs"]:
				if version[:4] != cfg["code"][:4]:
					continue

				prepare_templates(template_build)
				export_cfg(cfg, version[4:], out)
				return
		print("NO SPECIFIC RELEASE FOUND: {}".format(version))
	else:
		out = os.path.join(PROJECT_DIR, "distribution/out/")
		# loop through all
		for template_build in template_builds:
			prepare_templates(template_build)

			for cfg in template_build["cfgs"]:
				export_cfg(cfg, version, out)


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Specify a version! (e.g: 1022)")
		sys.exit()
	elif len(sys.argv) > 2:
		PRODUCTION_MODE = False

	main(sys.argv[1])
