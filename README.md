# CryptoTradingBot-Boilerplate
A Configurable WhaleclubTrading Bot for Crypto currencies WIP

lib/Indicator.py:
Technical Indicators are calculated here

lib/Signals.py:
Multiple Technical Indicators are combined into Signals

lib/Strategy.py:
Multiple Signals are combined into Strategies

lib/Streamer.py:
Streams and parses OHLC Data from kraken and stores data in MySQL database

lib/Trader.py
Places orders on Whaleclub according to Strategy results

DB.sql:
Mysql Tables for OHCL and traderesult data
