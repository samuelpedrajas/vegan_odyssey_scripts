from configurations.sdk19_armv7_normal import cfg as cfg_1911
from configurations.sdk19_armv7_large import cfg as cfg_1912


template_builds = [
	{
		"sdk": "19",
		"arch": "armv7",
		"cfgs": [cfg_1911, cfg_1912]
	},
]
