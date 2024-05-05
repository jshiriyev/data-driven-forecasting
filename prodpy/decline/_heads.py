from dataclasses import dataclass

@dataclass
class Heads:
	
	dates 	: str
	orate 	: str = "Oil Rate"
	grate 	: str = "Gas Rate"
	wrate 	: str = "Water Rate"

	lrate	: str = "Liquid Rate"
	wcut 	: str = "Water Cut"
	gor	 	: str = "Gas Oil Ratio"
	