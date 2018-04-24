import os
import datetime
import logging
import sys
import time
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
import configparser
import threading
import krakenex
import decimal

logging.getLogger("urllib3").setLevel(logging.CRITICAL)


class Streamer:

	def __init__(self, callback):
		self.callback = callback
		self.config = configparser.ConfigParser()
		config = self.config
		self.config.read("".join([os.path.dirname(__file__),'/../','config']))
		self.mysql = MySQLdb.connect(config.get('database','server'),config.get('database','user'),config.get('database','password'), db=config.get('database','database'))
		self.instrument=config.get('trading','instrument')
		self.db = self.mysql.cursor()
		self.stopPolling=False
		self.log = logging.getLogger(__name__)
		self.fh = logging.FileHandler('log/streamer.log')
		self.fh.setLevel(logging.ERROR)
		self.sh = logging.StreamHandler(sys.stdout)
		self.sh.setLevel(logging.ERROR)
		self.log.addHandler(self.sh)
		self.log.addHandler(self.fh)
		logging.basicConfig(level=logging.ERROR, handlers=[self.fh, self.sh])
		self.kraken = krakenex.API()
		self.currentCandle = ""
		self.lastCandle = ""

	def run_kraken(self):
		since = 1506816000
		k = self.kraken
		db = self.db
		mysql = self.mysql
		self.currentCandle = ""

		#getLast12Hours from API

		while True:
			try:
				ret = k.query_public('OHLC',data={'pair': 'XXBTZUSD','since':since})
				if len(ret['error']) == 0:
					since = ret['result']['last']-60
					break
				else:
					#connection failed or slow. wait a little
					time.sleep(5)
			except:
				time.sleep(10)
				continue

		#get last comitted(!) candle
		candles = (ret['result']['XXBTZUSD'])
		#remove last entry as its not committed
		candles.pop()

		for candle in candles:
			try:
				db.execute("INSERT INTO bowhead_ohlc_tick (instrument,timeid,open,close,high,low,volume) VALUES('XXBTZUSD',"+str(candle[0])+","+str(float(candle[1]))+","+str(float(candle[4]))+","+str(float(candle[2]))+","+str(float(candle[3]))+","+str(float(candle[6]))+");")
				mysql.commit()
				self.currentCandle = candle
				#self.callback(self, self.currentCandle)
			except:
				continue

		#start getting recent data
		since = decimal.Decimal(time.time())
		while(self.stopPolling==False):
			while True:
				try:
					ret = k.query_public('OHLC',data={'pair': 'XXBTZUSD','since':since})
					if len(ret['error']) == 0:
						since = ret['result']['last']-60
						break
					else:
						#connection failed or slow. wait a little
						time.sleep(10)
				except:
					time.sleep(10)
					continue

			#get last comitted(!) candle
			candles = (ret['result']['XXBTZUSD'])
			if len(candles) < 2:
				continue

			#is that a new candle?
			if (candles[-2])[0] != self.lastCandle:
				self.lastCandle = (candles[-2])[0]
				candle = candles[-2]
				try:
					db.execute("INSERT INTO bowhead_ohlc_tick (instrument,timeid,open,close,high,low,volume) VALUES('XXBTZUSD',"+str(candle[0])+","+str(candle[1])+","+str(candle[4])+","+str(candle[2])+","+str(candle[3])+","+str(float(candle[6]))+");")
					mysql.commit()
					self.currentCandle=candle
					self.callback(self, self.currentCandle)
				except:
					continue
			time.sleep(10)
		return

	def getLast(self):

		return(" ".join(str(x) for x in self.currentCandle))

	def start(self):
		t = threading.Thread(target=self.run_kraken)
		t.start()

	def stop(self):
		self.stopPolling=True

if __name__ == '__main__':
        s = Streamer()
        s.start()
