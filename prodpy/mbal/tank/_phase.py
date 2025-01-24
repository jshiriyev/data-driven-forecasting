from dataclasses import dataclass

@dataclass
class Phase:
	"""
	RESERVOIR ROCK & FLUID PROPERTIES

	Bo		: Oil formation volume factor, bbl/STB
	Bw 		: Water formation volume factor, bbl/STB
	Bg		: Gas formation volume factor, bbl/scf

	cw		: Water compressibility, psi−1
	cf		: Formation (rock) compressibility, psi−1

	Rs		: Gas solubility, scf/STB

	"""

	Bo 		: float = 1.
	Bw 		: float = 1.
	Bg		: float = None

	cw 		: float = 1e-6
	cf 		: float = 1e-6

	Rs 		: float = None

	@staticmethod
	def get(**kwargs):
		return {key: value for key, value in kwargs.items() if key in Phase().__dict__}
