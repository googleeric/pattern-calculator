import talib
import numpy as numpy
from numpy import genfromtxt


my_data = genfromtxt('2022_15minutes.csv', delimiter=',')

print(my_data)

close = my_data[:,4]

print(close)

# simple_moving_average = talib.SMA(close, timeperiod=10)

rsi = talib.RSI(close)

print(rsi)