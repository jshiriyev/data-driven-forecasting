from setuptools import setup, find_packages

setup(
	name = 'prodpy',
	version = '0.0.30',
	packages = find_packages(),
	install_requires = [
		'numpy>=2.3.1',
		'openpyxl>=3.1.2',
		'pandas>=2.2.2',
		'scipy>=1.13.0',
        'plotly>=5.22.0',
        'lasio>=0.31',
        'matplotlib>=3.10.6'
		],
	)

# Run the followings from the command line to test it locally:

# python setup.py sdist bdist_wheel

# pip install dist/prodpy-{version}-py3-none-any.whl

# Run the followings from the command line to upload to pypi:

# twine upload dist/*