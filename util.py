import configparser

def process_config(conf_file):
	"""
		read configuration from files and saved to a dict
	"""
	params = {}
	config = configparser.ConfigParser()
	config.read(conf_file)
	for section in config.sections():
		if section == 'database':
			for option in config.options(section):
				params[option] = eval(config.get(section, option))
		if section == 'app':
			for option in config.options(section):
				params[option] = eval(config.get(section, option))
	return params