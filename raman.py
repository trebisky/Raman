#! /usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# raman.py
# Tom Trebisky  9-11-2021

# Symbolic links don't work on Windows.
#datafile = "data.rruff"
datafile = "BM_APT3-2_780_Hi.rruff"

# on Windows 10, os.name returns "nt".
#   on Linux it returns "posix"
# on Windows 10, sys.platform returns "xx".
#   on Linux it returns "linux"
print ( os.name )
print ( sys.platform )

f = open ( datafile, 'r')
data = np.genfromtxt(f, delimiter=',')
f.close()

#delete(data,0,0) # Erases the first row (i.e. the header)
#plt.plot ( data[:,0], data[:,1], 'o' )
plt.plot ( data[:,0], data[:,1] )

#N = 50
#x = np.random.rand(N)
#y = np.random.rand(N)
#plt.scatter(x, y)

plt.show()
