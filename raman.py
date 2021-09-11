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
# on Windows 10, sys.platform returns "win32".
#   on Linux it returns "linux"
#print ( os.name )
#print ( sys.platform )

if ( sys.platform == "linux" ) :
    spectra_lib_dir = os.path.expanduser ( "~/RamanLib" )
else :
    spectra_lib_dir = "\CrystalSleuth\SearchRecords\RamanLib"

if not os.path.isdir ( spectra_lib_dir ) :
    print ( "Cannot find spectra library:", spectra_lib_dir )
    exit ()

print ( "Spectra library in", spectra_lib_dir )

for name in os.listdir(spectra_lib_dir) :
    print ( name )

#files = [name for name in os.listdir(spectra_lib_dir)]
#files = [name for name in os.listdir(spectra_lib_dir) if os.path.isfile(name)]
files = [name for name in os.listdir(spectra_lib_dir) if os.path.isfile(os.path.join(spectra_lib_dir, name))]
print ( files )

#num_spec = len([name for name in os.listdir(spectra_lib_dir) if os.path.isfile(name)])
num_spec = len ( files )
print ( num_spec, "files in library" )

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
