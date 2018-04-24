from lib.Commander import Commander
from lib.Commander import Command
from lib import Helper
from threading import Thread
import time
from lib.Trader import Trader
import logging
import sys

class CommandHandler(Command):
	def __init__(self, trader):
		self.trader=trader
		Command.__init__(self)
		self.log = logging.getLogger(__name__)
		self.fh = logging.FileHandler('log/MAIN.log')
		self.fh.setLevel(logging.DEBUG)
		self.sh = logging.StreamHandler(sys.stderr)
		self.sh.setLevel(logging.DEBUG)
		self.log.addHandler(self.sh)
		self.log.addHandler(self.fh)
		logging.basicConfig(level=logging.DEBUG, handlers=[self.fh, self.sh])

	def do_echo(self, *args):
		return ' '.join(args)

	def do_raise(self, *args):
		raise Exception('Some Error')

	def do_trader(self, *args):
		'''Available commands for Trader:
- trader enable/disable <strategyname>: enables and disables strategies'''
		if len(args)<1:
			raise ValueError('At least one parameter expected - enable')
		elif args[0]!='enable' and args[0]!='disable':
			trader.print_fn("Wrong command - available 'enable/disable <strategyname>' ","error")
		elif len(args)<2:
			trader.print_fn("Missing arguement - expected 'enable/disable <strategyname>'","error")
		else:
			for strat in args[1:]:
				success = getattr(trader,args[0]+'_strategy')(strat)
				if success:
					trader.print_fn(args[0]+"d strategy: "+strat,"green")
				else:
					trader.print_fn("Can not find "+strat+": Note that we are case sensitive.","error")

	def do_stream(self, *args):
		'''Available commands for Streamer:
- stream start/stop: starts/stops streaming 1 minute OHLC data from Kraken'''
		if len(args)<1:
			raise ValueError('At least one parameter expected - start/stop/last')
		elif len(args)>=1:
			if args[0]=="start":
				trader.streamer.start()
				trader.print_fn("Streamer started","green")
			elif args[0]=="stop":
				trader.streamer.stop()
				trader.print_fn("Streamer stopped","green")
				trader.runAsyncTasks = False
			elif args[0]=="last":
				trader.print_fn(trader.streamer.getLast(),"blue")
			else:
				raise ValueError("Unknown parameter - start/stop/last")

if __name__=='__main__':

	#CALLBACK FOR TRADER AND STREAMER
	#PASSED TO STRAMER VIA TRADER TO NOTIFY ABOUT NEW DATA
	def handleData(self, data):
		process(self, data)

	trader = Trader(handleData)
	commander = Commander("BTC Trader", cmd_cb=CommandHandler(trader))
	trader.print_fn=commander.output
	trader.runAsyncTasks=True

	signals = Helper.getAvailableSignals()
	indicators = Helper.getAvailableIndicators()
	strategies = Helper.getAvailableStrategies()

	trader.print_fn("\nREGISTERED SIGNALS: "+str(signals)+"\n","blue")
	trader.print_fn("REGISTERED INDICATORS: "+str(indicators)+"\n","blue")
	trader.print_fn("REGISTERED STRATEGIES: "+str(strategies)+"\n","blue")

	welcome = '''Welcome to the Trading Bot!
1. Start streaming market data from Kraken by calling "stream start"
2. Wait for the streamer to sync historical data
3. Wait another minute for the latest OHLC to arrive. Be patient.
   Your Indicators, Signals and Strategies should light up now.
4. Enable trading strategies by calling "trader enable <strategyname>"

For further assistence call "help" or "help commandname" '''
	trader.print_fn(welcome+"\n","normal")

	#NEW DATA ARRIVED PROCESS DATA
	def process(self, data):
		commander.updateOHLCText(str(data))

		for signal in signals:
			value = getattr(trader.sig, 'sig_'+signal)()
			commander.updateTraderWidget('signal', signal, value)

		for indicator in indicators:
			value = getattr(trader.ind, 'ind_'+indicator)(single_value=True)
			commander.updateTraderWidget('indicator', indicator, value)

		for strategy in strategies:
			value = getattr(trader.strat, 'strat_'+strategy)()
			commander.updateTraderWidget('strategy', strategy, value)
		#EVAL ENABLED STRATEGIES AND POST ORDERS
		trader.evalStrategies()

	def run():
		#DO SOMETHING ASYNCHRONE
		while(trader.runAsyncTasks):
			time.sleep(10)

	#launch Asyncron Process
	t=Thread(target=run)
	t.daemon=True
	t.start()

	#start Commander GUI
	commander.loop()
