from setuptools import setup, find_packages

setup(
	name = 'prodpy',
	version = '0.0.4',
	packages = find_packages(),
	install_requires = [
		'numpy>=1.26.4',
		'openpyxl>=3.1.2',
		'pandas>=2.2.2',
		'scipy>=1.13.0',
		],
	)