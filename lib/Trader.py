import sys
import logging
from lib import Streamer
from lib import Indicator
from lib import Signal
from lib import Strategy
from lib import DB
from lib import Helper
from lib import PyWhale

from threading import Thread
import time

class Trader():

       strategies = {key: False for key in Helper.getAvailableStrategies()}

       def __init__(self, callback, db=DB.DB()):
                self.streamer = Streamer.Streamer(callback)
                self.db = db
                self.ind = Indicator.Indicator(self.db)
                self.sig = Signal.Signal(self.db)
                self.strat = Strategy.Strategy(self.db)
                self.runAsyncTasks = True
                self.pw = PyWhale.PyWhale()
                self.pw.verbose = False
                for strategy in Helper.getAvailableStrategies():
                    self.strategies[strategy]=False
                self.log = logging.getLogger(__name__)
                self.fh = logging.FileHandler('log/trader.log')
                self.fh.setLevel(logging.DEBUG)
                self.sh = logging.StreamHandler(sys.stderr)
                self.sh.setLevel(logging.DEBUG)
                self.log.addHandler(self.sh)
                self.log.addHandler(self.fh)
                logging.basicConfig(level=logging.DEBUG, handlers=[self.fh, self.sh])

       def print_fn(self, msg, color):
                print(msg)

       def post_order(self, direction='long',leverage=20, size=20000000):
                price_data = self.pw.getPrice('BTC-USD')['BTC-USD']

                bid_price = float(price_data['bid'])
                ask_price = float(price_data['ask'])

                if direction=='long':
                    price = ask_price
                else:
                    price = bid_price
                tp = round((price * (20/leverage))/100,5)
                sl = round((price * (10/leverage))/100,5)
                if direction=='long':
                    takeprofit = float(price)+tp
                    stoploss = float(price)-sl
                else:
                    takeprofit = float(price)-tp
                    stoploss = float(price)+sl

                result = self.pw.newPosition(direction,'BTC-USD', leverage, size ,price,stop_loss=stoploss,take_profit=takeprofit)['id']

                return result

       def close_position(self, id, status):
                if status=='pending':
                        self.pw.cancelPosition(position_id=id)
                else:
                        self.pw.closePosition(position_id=id)

                self.db.setPositionState(id,'closed')

       def syncPositions(self):
                #SYNCS POSITION STATES OF DB AND PYWHALE
                PYPositions = self.pw.listPositions()+self.pw.listPositions(position_state='pending')
                closed_positions = self.pw.listPositions(position_state='closed')
                #DBPositions = list(self.db.getAllPositions()['trade_id'])
                #UPDATE POSITION STATE FROM PYWHALE TO DB
                if len(PYPositions)!=0:
                        for PYPosition in PYPositions:
                                self.db.setPositionState(PYPosition.get('id'),PYPosition.get('state'))
                if len(closed_positions)!=0:
                        for clpos in closed_positions:
                                self.db.closePosition(clpos.get('id'),str(clpos.get('profit')))

       def enable_strategy(self, strategy=''):
                if strategy in list(self.strategies.keys()):
                        self.strategies[strategy]=True
                        return True
                else:
                        return False

       def disable_strategy(self, strategy=''):
                if strategy in list(self.strategies.keys()):
                        self.strategies[strategy]=False
                        return True
                else:
                        return False

       def evalStrategies(self):
                self.syncPositions()
                for strategy, enabled in self.strategies.items():
                    if enabled==True:
                        active_long = list(self.db.getPositions(strategy,'long','active')['trade_id'])
                        pending_long = list(self.db.getPositions(strategy,'long','pending')['trade_id'])
                        active_short = list(self.db.getPositions(strategy,'short','active')['trade_id'])
                        pending_short = list(self.db.getPositions(strategy,'short','pending')['trade_id'])

                        result = (getattr(self.strat,'strat_'+strategy))()

                        if result==1:
                               #STRATEGY SUGGESTS LONG
                               if len(active_short+pending_short)!=0:
                                   self.print_fn("Strategy "+strategy+" flipped. Canceling SHORT ORDERS","green")
                                   #WE HAVE A SHORT, CANCEL ALL SHORTS
                                   for order in active_short:
                                       self.close_position(order, 'active')
                                   for order in pending_short:
                                       self.close_position(order, 'pending')
                               if len(active_long+pending_long)!=0:
                                   #WE ALREADY HAVE A LONG ORDER, KEEP IT
                                   continue
                               #WE NEED TO CREATE A NEW LONG
                               id = self.post_order(direction='long')
                               self.db.savePosition(id, strategy, 'long','pending')
                               self.print_fn("Posting LONG order (id:"+str(id)+") for Strategy "+strategy.upper(),"green")

                        elif result==-1:
                               #STRATEGY SUGGESTS SHORT
                               if len(active_long+pending_long)!=0:
                                   #WE HAVE A LONG BUT NEED A SHORT, CANCEL ALL LONG
                                   self.print_fn("Strategy "+strategy+" flipped. CANCELLING LONG Orders","green")
                                   for order in active_long:
                                       self.close_position(order, 'active')
                                   for order in pending_long:
                                       self.close_position(order, 'pending')
                               if len(active_short+pending_short)!=0:
                                   #WE ALREADY HAVE A SHORT, KEEP IT RUNNING
                                   continue
                               #WE NEED TO CREATE A NEW SHORT
                               id = self.post_order(direction='short')
                               self.db.savePosition(id, strategy, 'short', 'pending')
                               self.print_fn("Posted SHORT order (id:"+str(id)+") for Strategy "+strategy.upper(),"green")

                        elif result==0:
                               #STRATEGY IS INDIFFERENT, DO NOTHING
                               continue

                        else:
                               #CANT HAPPEN
                               continue
