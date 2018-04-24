import os
import datetime
import logging
import sys
import time
import pymysql as pymy
import configparser
from sqlalchemy import create_engine
from warnings import filterwarnings
import pandas as pd
filterwarnings('ignore', category = pymy.Warning)

class DB:
	def __init__(self):
		self.config = configparser.ConfigParser()
		config = self.config
		self.config.read("".join([os.path.dirname(__file__),'/../','config']))
		self.instrument=config.get('trading','instrument')
		self.engine = create_engine('mysql+pymysql://'+config.get('database','user')+":"+config.get('database','password')+"@"+config.get('database','server')+":"+config.get('database','port')+"/"+config.get('database','database'))
		self.log = logging.getLogger(__name__)
		self.fh = logging.FileHandler('log/DB.log')
		self.fh.setLevel(logging.DEBUG)
		self.sh = logging.StreamHandler(sys.stderr)
		self.sh.setLevel(logging.DEBUG)
		self.log.addHandler(self.sh)
		self.log.addHandler(self.fh)
		logging.basicConfig(level=logging.DEBUG, handlers=[self.fh, self.sh])

	def getData(self, limit=100):
		df = pd.read_sql_query("(select * from bowhead_ohlc_tick ORDER BY timeid DESC LIMIT "+str(limit)+") ORDER BY id", self.engine)
		return df

	def savePosition(self, id, strategy, direction, status='active'):
		self.engine.execute("insert into trades (trade_id, strategy, direction, status) VALUES ('"+str(id)+"','"+strategy+"','"+direction+"','"+status+"');")

	def setPositionState(self, id, state):
		self.engine.execute("UPDATE trades SET status='"+state+"' where trade_id='"+id+"';")

	def closePosition(self, trade_id, profit=0):
		self.engine.execute("UPDATE trades SET status='closed', profit='"+profit+"'where trade_id='"+trade_id+"';")

	def getAllPositions(self):
		result = pd.read_sql_query("select * from trades;", self.engine)
		return result


	def getPositions(self, strategy, direction='long', status='active'):
		result = pd.read_sql_query("select * from trades where strategy='"+strategy+"' AND status='"+status+"' AND direction='"+direction+"';", self.engine)
		return result

if __name__ == '__main__':
	db = DB()
	db.getData()
