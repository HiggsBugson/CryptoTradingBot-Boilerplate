from lib import DB
import pandas as pd
from lib import Signal
from lib import Indicator
import talib

class Strategy:

	def __init__(self, db=DB.DB()):
		self.db = db
		self.ind = Indicator.Indicator(self.db)
		self.sig = Signal.Signal(self.db)

	def strat_RSICCI(self, data=None, limit=60):
		if data is None:
			data = self.db.getData(60)
		rsi_sig = self.sig.sig_RSI(data)
		cci_sig = self.sig.sig_CCI(data)
		if rsi_sig > 0 and cci_sig > 0:
			return 1
		elif rsi_sig < 0 and cci_sig < 0:
			return -1
		else:
			return 0

	def strat_RSIBBSQZ(self, data=None, limit=60):
		if data is None:
			data = self.db.getData(60)
		rsi_sig = self.sig.sig_RSI(data)
		bbw_sig = self.sig.sig_BBANDSQZ(data)

		if rsi_sig>0 and bbw_sig>0:
			return 1

		if rsi_sig<0 and bbw_sig>0:
			return -1
		else:
			return 0

	def strat_RSIMACD(self, data=None, limit=60):
		if data is None:
			data = self.db.getData(60)
		macd = self.sig.sig_MACD(data)
		rsi_sig = self.sig.sig_RSI(data)
		if rsi_sig>0 and macd>0:
			return 1
		elif rsi_sig<0 and macd<0:
			return -1
		else:
			return 0

	def strat_RSIENGCDL(self, data=None, limit=60):
		if data is None:
			data = self.db.getData(60)

		rsi_sig = self.sig.sig_RSI(data)
		candle = talib.CDLENGULFING(data.open.values, data.high.values, data.high.values, data.close.values)[-1]
		if rsi_sig>0 and candle == 100:
			return 1
		elif rsi_sig<0 and candle == -100:
			return -1
		else:
			return 0

	#CCI over or under the value of +/-20
	def strat_SimpleCCI(self, data=None, limit=60):
		'''Strategy SimpleCCI:
		LONG for CCI over 20, Short for CCI below -20
		Very bad results on small intervals. Use only for testing in demo mode.
		'''
		if data is None:
			data=self.db.getData(60)
		return self.sig.sig_CCI(data)

	def strat_Trends(self, data=None, limit=60):
		'''Strategy Trends:
		Takes trend of 3 candles and trend over 30 candles into account.
		LONG if both trends are positive, SHORt if trends are negative.
		'''
		if data is None:
			data=self.db.getData(60)
		return self.sig.sig_trends(data)


	#MovingAverageMeanReversion
	def strat_MAMR(self, data=None, limit=60):
		'''Strategy MovingAverageMeanReversion
		Only triggers on very strong signals.

		SHORT
		If the mean of 10 candles falls below 95% of the mean of 30 candles
		and at the same time trend of 3 candles is falling.

		LONG
		If the mean of 10 candles rises above 105% of the mean of 30 candles
		and at the same time trend of 3 candles if rising
		and at the same time trend of 30 candles is rising too
		'''
		if data is None:
			data=self.db.getData(60)
		mean10 = self.ind.ind_SMA(data,10)
		mean30 = self.ind.ind_SMA(data,30)
		trend = self.ind.ind_trend3(data)
		longtrend = self.ind.ind_trendLong(data)
		if mean10 < mean30 * 0.95 and trend<0:
			return -1
		elif mean10>mean30*1.05 and trend>0:
			if longtrend < 0:
				pass
			else:
				return 1
		else:
			return 0


if __name__ == '__main__':
	strat = Strategy()
	print(strat.strat_MAMR())

