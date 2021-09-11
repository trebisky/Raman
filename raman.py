#! /usr/bin/python

import numpy as np
import matplotlib.pyplot as plt

# raman.py
# Tom Trebisky  9-11-2021

datafile = "data.rruff"

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
