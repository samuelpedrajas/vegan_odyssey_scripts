from configurations.sdk19_armv7_normal import cfg as cfg_1911
from configurations.sdk19_armv7_large import cfg as cfg_1912
from configurations.sdk19_armv7_xlarge import cfg as cfg_1913

from configurations.sdk21_arm64v8_normal import cfg as cfg_2121
from configurations.sdk21_arm64v8_large import cfg as cfg_2122
from configurations.sdk21_arm64v8_xlarge import cfg as cfg_2123


template_builds = [
	{
		"sdk": "19",
		"arch": "armv7",
		"cfgs": [cfg_1911, cfg_1912, cfg_1913]
	}, 	{
		"sdk": "21",
		"arch": "arm64v8",
		"cfgs": [cfg_2121, cfg_2122, cfg_2123]
	},
]
