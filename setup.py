from setuptools import setup, find_packages

setup(
	name = 'prodpy',
	version = '0.0.34',
	packages = find_packages(),
	install_requires = [
		'numpy>=1.26.4',
		'openpyxl>=3.1.2',
		'pandas>=2.2.2',
		'scipy>=1.13.0',
		],
	)

# Run the followings from the command line to test it locally:

# python setup.py sdist bdist_wheel

# pip install dist/prodpy-{version}-py3-none-any.whl

# Run the followings from the command line to upload to pypi:

# twine upload dist/*