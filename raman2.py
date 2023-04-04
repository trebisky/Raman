#! /usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from random import randint

import tkinter as tk
from tkinter import filedialog

# raman2.py
# Tom Trebisky  9-11-2021 10-15-2021
# The idea now is to combine tkinter and matplotlib

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

# Given a path with an RRUF project filename,
# extract the name of the mineral and the laser wavelength
# /home/tom/RamanLib/Actinolite__R040063__Raman__532__0__unoriented__Raman_Data_Processed__15158.txt
def rruf_extract ( path ) :
    species = "junk"
    laser = "555"
    w = path.split ( '__' )
    species = w[0].split ('/')[-1]
    laser = w[3]
    return species, laser

def plot_file ( path ) :
    print ( "Plotting data from file:", path )

    f = open ( path, 'r')
    data = np.genfromtxt(f, delimiter=',')
    f.close()

    species, laser = rruf_extract ( path )
    title = species + " " + laser + " nm"

    #print ( "Plotting", len(data), " points" )

    #plt.plot ( data[:,0], data[:,1], 'o' )
    plt.plot ( data[:,0], data[:,1] )
    plt.title ( title )
    plt.show()


# Files in the reference library have names like this:
# Adamite__R040130__Raman__514__0__unoriented__Raman_Data_Processed__9553.txt
# Notice the ending ".txt" even though these are in CSV format
# Some lines have CR/LF endings, but numpy genfromtxt doesn't seem to care
# The files also have a header, which have ## at the start and
# genfromtxt also skips those as comments.
# The files end in ##END=, followed by some number of blank lines.
# Happily genfromtxt also skips this as a comment and apparently
#  also ignores blank lines
#
# The inventory is as follows:
# Num of 514 = 480
# Num of 532 = 2462
# Num of 780 = 993
# Num of 785 = 1194
#
# Num of unk = 4
# RamanSearchFileFast.rsf
# RamanSearchFileSlow.rsf
# RamanSearchNameList.rsf
# RamanSearchNameInfo.rsf

# The "slow" file seems to be a concatenation of all the files,
#  but with data interpolated to even X values, incrementing by 1.0
# The "fast" file seems to be a concatenation of all the files
#  but with data interpolated to even X values, incrementing by 2.0
#
# The list file is what the python os.listdir() function gives us (5129 lines)
# The info file combines what we could extract from the filenames (5129*5 = 25645 lines)
# and the header.  We have 5 lines per file:
#  R number
#  mineral name
#  location
#  chemistry
#  Raman laser wavelength
# Data in the actual files are at non integral X values and roughly incremented by 0.5
#  so the "slow" file is big, but about half the size of all the files together.
#  the fast file is half the size of that, so about 1/4 the size of all the data files.

def file_inventory () :
    print ( "Spectra library in", spectra_lib_dir )

    #for name in os.listdir(spectra_lib_dir) :
    #    print ( name )

    # listdir seems to skip . and .., but the isfile check will avoid
    # including explicit subdirectories.
    #files = [name for name in os.listdir(spectra_lib_dir)]
    #files = [name for name in os.listdir(spectra_lib_dir) if os.path.isfile(name)]
    files = [name for name in os.listdir(spectra_lib_dir) if os.path.isfile(os.path.join(spectra_lib_dir, name))]
    #print ( files )

    #num_spec = len([name for name in os.listdir(spectra_lib_dir) if os.path.isfile(name)])
    num_spec = len ( files )
    print ( num_spec, "files in library" )
    # 5133 files

    #index = randint ( 0, num_spec-1 )
    #print ( "file", index, " is", files[index] )

    print ( "File inventory" )
    n_514 = 0
    n_532 = 0
    n_780 = 0
    n_785 = 0
    n_x = 0
    for name in os.listdir(spectra_lib_dir) :
        if "514" in name :
            n_514 += 1
        elif "532" in name :
            n_532 += 1
        elif "780" in name :
            n_780 += 1
        elif "785" in name :
            n_785 += 1
        else :
            print ( name )
            n_x += 1

    print ( "Num of 514 =", n_514 )
    print ( "Num of 532 =", n_532 )
    print ( "Num of 780 =", n_780 )
    print ( "Num of 785 =", n_785 )
    print ( "Num of unk =", n_x )

def plot_calcite () :

    #plot_file ( datafile )

    calcite_file = "Calcite__R040070__Raman__532__0__unoriented__Raman_Data_Processed__15330.txt"

    # on linux, file 1882 is Calcite with 2406 data points
    # on windows, file 1882 fetches Galkhaite
    #index = 1882
    #calcite = os.path.join ( spectra_lib_dir, files[index] )
    calcite = os.path.join ( spectra_lib_dir, calcite_file )
    plot_file ( calcite )

#file_inventory ()
#plot_calcite ()

root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename ( initialdir = spectra_lib_dir )
# print ( file_path )

# This works.  The above file dialog vanishes and the matplotlib plot appears
# with its menubar.  Not too shabby.
plot_file ( file_path )

# THE END
