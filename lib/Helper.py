from lib import Indicator
from lib import Signal
from lib import Strategy

def getAvailableIndicators():
	indicator_names = ([name for name in dir(Indicator.Indicator) if name.startswith('ind_')])
	indicator_names_clean = []
	for indicator in indicator_names:
		indicator_names_clean.append(indicator.split("_")[1])
	return indicator_names_clean

def getAvailableSignals():
	signal_names = ([name for name in dir(Signal.Signal) if name.startswith('sig_')])
	signal_names_clean = []
	for signal in signal_names:
		signal_names_clean.append(signal.split("_")[1])
	return signal_names_clean

def getAvailableStrategies():
	strategy_names = ([name for name in dir(Strategy.Strategy) if name.startswith('strat_')])
	strategy_names_clean = []
	for strategy in strategy_names:
		strategy_names_clean.append(strategy.split("_")[1])
	return strategy_names_clean
