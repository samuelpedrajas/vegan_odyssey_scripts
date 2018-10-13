from configurations.sdk19_armv7_normal import cfg as cfg_1911
from configurations.sdk19_armv7_large import cfg as cfg_1912
from configurations.sdk19_armv7_xlarge import cfg as cfg_1913

from configurations.sdk21_arm64v8_normal import cfg as cfg_2121
from configurations.sdk21_arm64v8_large import cfg as cfg_2122
from configurations.sdk21_arm64v8_xlarge import cfg as cfg_2123

from configurations.sdk19_x86_normal import cfg as cfg_1931
from configurations.sdk19_x86_large import cfg as cfg_1932
from configurations.sdk19_x86_xlarge import cfg as cfg_1933

from configurations.sdk19_x86_64_normal import cfg as cfg_1941
from configurations.sdk19_x86_64_large import cfg as cfg_1942
from configurations.sdk19_x86_64_xlarge import cfg as cfg_1943

template_builds = [
	{
		"sdk": "19",
		"arch": "armv7",
		"cfgs": [cfg_1911, cfg_1912, cfg_1913]
	}, 	{
		"sdk": "21",
		"arch": "arm64v8",
		"cfgs": [cfg_2121, cfg_2122, cfg_2123]
	}, 	{
		"sdk": "19",
		"arch": "x86",
		"bits": "32",
		"cfgs": [cfg_1931, cfg_1932, cfg_1933]
	}, 	{
		"sdk": "19",
		"arch": "x86",
		"bits": "64",
		"cfgs": [cfg_1941, cfg_1942, cfg_1943]
	}
]
