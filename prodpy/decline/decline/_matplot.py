from matplotlib import pyplot

class Matplot():

	def __init__(self,dates,nrows=6):

		self.dates = dates
		self.nrows = nrows

	def boot(self,height=15):

		self.figure,self.axes = pyplot.subplots(nrows=self.nrows)

		self.figure.set_figheight(height)

		xlim = self.xlim

		for index in range(self.nrows):
			self.axes[index].set_xlim(xlim)

	def plot(self,index,curve,model=None):

		self.axes[index].scatter(curve.dates,curve.rates,s=1)

		if model is not None:
			self.axes[index].plot(model.dates,model.rates)

		self.axes[index].set_ylabel(f"{curve.head}, {curve.unit}")

	@property
	def xlim(self):
		return min(self.dates),max(self.dates)
	