
from lib import DB
import numpy as np
import pandas as pd
import talib

class Indicator:

	def __init__(self, db=None):

		if db is None:
			self.db = DB.DB()
		else:
			self.db = db

	def ind_BBW(self, data=None, limit=20, single_value=False):
		if data is None:
			data = self.db.getData(limit*2-1)
		upper, middle, lower = talib.BBANDS(data.close.values, timeperiod=limit)
		bbw = (upper[-1]-lower[-1])/middle[-1]
		return bbw

	def ind_BBAND(self, data=None, limit=20, single_value=False):
		if data is None:
			data = self.db.getData(limit*2-1)
		upper, middle, lower = talib.BBANDS(data.close.values, timeperiod=limit, nbdevup=2, nbdevdn=2, matype=0)

		if single_value==True:
			return str(upper[-1])+"/"+str(middle[-1])+"/"+str(lower[-1])
		else:
			return upper[-1], middle[-1], lower[-1]


	def ind_MACD(self, data=None, single_value=False):
		if data is None:
			data = self.db.getData(60)
		macd, macdsignal, macdhist = talib.MACD(data.close.values, fastperiod=12, slowperiod=26, signalperiod=9)
		if single_value==True:
			return str(macd[-1])+"/"+str(macdsignal[-1])
		else:
			return macd[-1], macdsignal[-1]

	def ind_RSI(self, data=None, limit=14, single_value=True):
		if data is None:
			data = self.db.getData(limit*2-1)
		if single_value == True:
			return talib.RSI(data.close.values, timeperiod=limit)[-1]
		else:
			return talib.RSI(data.close.values, timeperiod=limit)


	def ind_CCI(self, data=None, limit=20, single_value=True):
		if data is None:
			data=self.db.getData(limit)
		if single_value==True:
			return talib.CCI(data.high.values, data.low.values, data.close.values, timeperiod=limit)[-1]
		else:
			return talib.CCI(data.high.values, data.low.values, data.close.values, timeperiod=limit)

	def ind_SMA(self, data=None, limit=20, single_value=True):
		if data is None:
			data=self.db.getData(limit)
		if single_value==True:
			return talib.SMA(data.close.values, timeperiod=limit)[-1]
		else:
			return talib.SMA(data.close.values, timeperiod=limit)


	def ind_EWMA(self, data=None, limit=20, single_value=True):
		if data is None:
			data=self.db.getData(limit)
		DATA = (data['close'])
		EMA = pd.Series(DATA.ewm(span=limit,ignore_na=True,min_periods=limit-1,adjust=True).mean())
		return EMA.iloc[-1]

	#TREND OVER LAST 3 CANDLES
	#RETURNS 1 / 0 / -1
	def ind_trend3(self, data=None, single_value=True):
		if data is None:
			data=self.db.getData(3)
		value = data['close']
		if value.iloc[-1]>=value.iloc[-2]>=value.iloc[-3]:
			return 1
		elif value.iloc[-1]<=value.iloc[-2]<=value.iloc[-3]:
			return -1
		else:
			return 0

	#TREND SAMPLING LONGTERM
	def ind_trendLong(self, data=None, single_value=True):
		if data is None:
			data=self.db.getData(30)
		value = data['close']
		if value.iloc[-1]<=value.iloc[-6]<=value.iloc[-11]<=value.iloc[-16]:
			return 1
		if value.iloc[-1]>=value.iloc[-6]>=value.iloc[-11]>=value.iloc[-16]:
			return -1
		else:
			return 0
