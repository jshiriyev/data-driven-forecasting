import numpy

from dataclasses import dataclass

@dataclass
class Operation:
	"""PRODUCTION-INJECTION-INFLUX PARAMETERS

	Np 		: Cumulative oil produced, STB
	Gp		: Cumulative gas produced, scf
	Wp		: Cumulative water produced, bbl
	
	Ginj	: Cumulative gas injected, scf
	Winj	: Cumulative water injected, STB

	GOR		: Instantaneous gas-oil ratio, scf/STB

	Calculated property:

	Rp		: Cumulative gas-oil ratio, scf/STB

	"""

	Np 		: float = 0.
	Gp 		: float = 0.
	Wp 		: float = 0.

	Ginj 	: float = 0.
	Winj 	: float = 0.

	GOR 	: float = None

	@property
	def Rp(self):
		return numpy.nan if self.Np==0 else self.Gp/self.Np

	@staticmethod
	def get(**kwargs):
		return {key: value for key, value in kwargs.items() if key in Operation().__dict__}
	

if __name__ == "__main__":

	print(Operation().__dict__)

	# opr = Operation(Np=500,Gp=200,Wp=50)

	# print(opr)

	# # print(dir(opr))

	# # print("S" in opr.__dict__)

	# setattr(opr,"Np",777)

	# print(opr)