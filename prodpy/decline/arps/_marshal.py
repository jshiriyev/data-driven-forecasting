class Marshal:
	"""The class contains methods to get the correct pair of options."""

	@staticmethod
	def option(mode:str=None,exponent:float=None):
		"""Returns mode and exponent based on their values."""
		if mode is None and exponent is None:
			return 'Exponential',0

		if mode is None and exponent is not None:
			return Marshal.mode(float(exponent)),float(exponent)

		if mode is not None and exponent is None:
			return mode.capitalize(),Marshal.exponent(mode)

		return Marshal.option(mode=None,exponent=float(exponent))

	@staticmethod
	def mode(exponent:float):
		"""Returns mode based on the exponent value."""
		if exponent == 0.:
			return 'Exponential'

		if exponent > 0. and exponent < 1.:
			return 'Hyperbolic'

		if exponent == 1.:
			return 'Harmonic'

		raise Warning("Exponent value needs to be in the range of 0 and 1.")

	@staticmethod
	def exponent(mode:str):
		"""Returns exponent based on the mode."""
		if mode.capitalize() == 'Exponential':
			return 0.

		if mode.capitalize() == 'Hyperbolic':
			return 0.5

		if mode.capitalize() == 'Harmonic':
			return 1.

		raise Warning("Available modes are Exponential, Hyperbolic, and Harmonic.")

if __name__ == "__main__":

	print(Marshal.option("Hyperbolic",0.))