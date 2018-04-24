from lib import DB
from lib import Indicator
import pandas as pd

class Signal:

	def __init__(self, db=DB.DB()):
		self.db = db
		self.ind = Indicator.Indicator(db)


	def sig_BBANDSQZ(self, data=None):
		bbw = self.ind.ind_BBW(data)
		if bbw < 0.03:
			return 1
		else:
			return 0

	def sig_MACD(self, data=None):
		macd, macdsignal = self.ind.ind_MACD(data)
		if macd - macdsignal > 0:
			return 1
		if macd - macdsignal < 0:
			return -1
		else:
			return 0

	def sig_RSICROSS(self, data=None, single_value=False):
		rsivalues = self.ind.ind_RSI(data, single_value=False)
		if rsivalues[-1]<70 and rsivalues[-2]>70:
			#CROSSING FROM ABOVE: SHORT
			return -1
		elif rsivalues[-1]>=30 and rsivalues[-2]<30:
			#CROSSING FROM BELOW 30
			return 1
		else:
			return 0

	def sig_RSI(self, data=None):
		rsi = self.ind.ind_RSI(data)
		if rsi>70:
			return 1
		elif rsi<30:
			return -1
		else:
			return 0


	def sig_CCI(self, data=None):
		cci = self.ind.ind_CCI(data)
		if cci>=20:
			return 1
		elif cci<-20:
			return -1
		else:
			return 0





	def sig_trends(self, data=None):
		trend3 = self.ind.ind_trend3(data)
		trend = self.ind.ind_trendLong(data)
		if trend3>0 and trend>0:
			return 1
		elif trend3<0 and trend<0:
			return -1
		else:
			return 0

if __name__ == '__main__':
	sig = Signal()
	print(sig.trend3())

