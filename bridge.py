import os

def bridge():
	#basic_dir = os.getcwd() + r'/'
	#os.chdir(basic_dir + r"plugins")
	plugin_bridge = {}
	plugin_list = []
	plugin_lis = os.listdir("plugins/")
	for plugi in plugin_lis:
		if os.path.isdir("plugins/" + plugi):
			plugin_list.append(plugi)
	for plugin in plugin_list:
		with open("plugins/" + plugin + r"/__init__.py", encoding="utf-8") as f:
			plugin_bridge[f.readline().strip()[1:]] = plugin
	#os.chdir(basic_dir)
	return plugin_bridge

#print(bridge())