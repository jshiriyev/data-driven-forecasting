from dataclasses import dataclass

from datetime import date

from ._survey import Depth

@dataclass
class Target:
	"""It is a Target dictionary for a well."""
	x 		: float = None
	y 		: float = None

	depth   : dict = None

	def __post_init__(self):

		if self.depth is not None:
			self.depth = Depth(**self.depth)

@dataclass
class Drilling:
	"""It is a drilling dictionary for a well."""
	start	: date = None
	end		: date = None

	depth 	: dict = None
	target  : dict = None

	def __post_init__(self):

		if self.depth is not None:
			self.depth = Depth(**self.depth)

		if self.target is not None:
			self.target = Target(**self.target)

if __name__ == "__main__":

	drill = Drilling(
		date(1990,2,2),
		date(1990,4,3),
		depth={}
		)

	print(drill.end)

	print(drill.start)

	print(drill.depth)