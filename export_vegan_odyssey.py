VERSION = 1022

_path = "/home/pspz/Vegan Game/src/export_presets.cfg"

# with is like your try .. finally block in this case
with open(_path, 'r') as file:
    # read a list of lines into data
    data = file.readlines()

for i, l in enumerate(data):
	if "version/code" in l:
		k, v = l.split("=")
		data[i] = "=".join([k, str(VERSION)]) + "\n"

# and write everything back
with open(_path, 'w') as file:
    file.writelines(data)
