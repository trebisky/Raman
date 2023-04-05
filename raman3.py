#! /usr/bin/python

# Proof of concept code for new Raman software
# Tom Trebisky  4-3-2023
# Use wxPython for basic file operations

# ---------------------------------------

import wx
import os
import sys
import numpy as np

# Global variable point to graph object (left side)
graph = None

# Geometry for initial layout
xsize = 800
ysize = 600

# The right side needs about 250 pixels
right_size =250
split_pos = xsize - right_size

# Check every second for something or other
timer_delay = 1000    # milliseconds

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

# This is called to open and load data from what
# should be a CSV file with Raman data.
#
# A CSV file of the sort we read, simply looks like this:
#  8.803156e+001,0.000000e+000
#  8.851367e+001,4.551096e+002
# No header or any variety whatsoever.
#
# We will end up with several objects of this sort,
# one for each file this is visible and/or in use

class Raman_Data () :
        def __init__ ( self, path ) :
            self.path = path
            self.is_good = False

            # ensure we can open the file
            try:
                with open ( path, 'r') as file:
                    first = file.readline()
            except IOError:
                print ( "Cannot open file '%s'." % path )
                return

            # weak validation, we ensure the first line
            # has exactly one comma in it.
            ccount = first.count ( ',' )
            if ccount != 1 :
                print ( "Not a CSV file: %s" % path )
                return

            with open ( path, 'r') as file:
                self.read_file_data (file)

            # XXX
            # each data item should get a unique color
            self.color = wx.BLUE

            self.xx = self.data[:,0]
            self.yy = self.data[:,1]

            self.xmin = np.amin ( self.xx )
            self.xmax = np.amax ( self.xx )
            self.xrange = self.xmax - self.xmin

            self.ymin = np.amin ( self.yy )
            self.ymax = np.amax ( self.yy )
            self.yrange = self.ymax - self.ymin

            # Can adjust to give Y a margin
            self.ybot = self.ymin

            print ( "X range: ", self.xrange )
            print ( "Y range: ", self.yrange )

            self.scale_data ( graph );

            self.is_good = True

        def scale_data ( self, win ) :

            self.win = win
            self.xy = []

            # We can adjust this to center data, etc.
            yrang = self.yrange

            print ( "Scaling ", len(self.xx), " points" )

            for i in range(len(self.xx)) :
                xf = (self.xx[i] - self.xmin) / self.xrange
                #yf = (self.yy[i] - self.ymin) / self.yrange
                yf = (self.yy[i] - self.ybot) / yrang

                ix = win.xoff + np.int_ ( win.xsize * xf )
                iy = win.yoff + np.int_ ( win.ysize * (1.0-yf) )
                self.xy.append ( (ix,iy) )

        # This is called with the file open
        def read_file_dataC ( self, file ) :
            count = 0
            for line in file:
                count += 1
            print ( count, " lines in file" )

        def read_file_data ( self, file ) :
            # leverage numpy to read CSV
            self.data = np.genfromtxt ( file, delimiter=',' )
            nn = len(self.data)
            print ( "Read", nn, " points" )


# The left panel has the graph
class Left_Panel ( wx.Panel ) :
        def __init__ ( self, parent ) :
            wx.Panel.__init__ ( self, parent )

            # list of data objects being displayed
            self.data = []

            self.SetBackgroundColour ( wx.RED )

            # set up starting size
            self.setViewport ( xsize, ysize )

            # various events
            self.Bind ( wx.EVT_SIZE, self.OnResize )
            self.Bind ( wx.EVT_PAINT, self.OnPaint )

            #self.Bind ( wx.EVT_MOTION, self.OnMove )


        def setViewport ( self, w, h ) :

            self.width = w
            self.height = h

            # not yet
            self.lmargin = 40   # left only
            self.ymargin = 10   # top and bottom

            self.xoff = 0   # lmargin
            self.yoff = 0   # ymargin
            self.xsize = w
            self.ysize = h

        # We get 3 resize events just starting up.
        # we need this to refresh after resize
        # also to post width for Move checks
        def OnResize ( self, event ) :
            print ( "resize!" )

            self.setViewport ( event.Size.width, event.Size.height )

            self.update ();

        def PostData ( self, data ) :
            #self.data = data.xy
            self.data.append ( data )

        def PaintData ( self ) :
            print ( "PaintData 1" )
            # loop through data objects
            for d in self.data :
                dc = wx.PaintDC ( self )
                #dc.SetPen ( wx.Pen(wx.BLUE, 2) )
                dc.SetPen ( wx.Pen( d.color, 2) )
                print ( "PaintData 2", d.color, len(d.xy) )

                lastxy = None
                for xy in d.xy :
                    if xy and lastxy :
                        dc.DrawLine ( lastxy[0], lastxy[1], xy[0], xy[1] )
                    lastxy = xy

        # We get lots of paint events, for reasons I don't understand,
        # and not simply related to cursor motion.
        def OnPaint ( self, event ) :
            print ( "Paint!" )

            dc = wx.PaintDC ( self )
            dc.Clear ()

            #w, h = self.GetSize()

            self.PaintData ()

        def update ( self ) :
            # trigger a repaint
            self.Refresh ()

# The right panel has buttons and controls
class Right_Panel ( wx.Panel ) :
        def __init__ ( self, parent ) :
            wx.Panel.__init__ ( self, parent )

            rsz = wx.BoxSizer ( wx.VERTICAL )
            self.SetSizer ( rsz )

            bp1 = wx.Panel ( self, -1 )
            self.b_up = wx.Button ( bp1, wx.ID_ANY, "Update")
            self.b_up.Bind ( wx.EVT_BUTTON, self.onUpdate )

            self.b_ex = wx.Button ( bp1, wx.ID_ANY, "Exit")
            self.b_ex.Bind ( wx.EVT_BUTTON, self.onExit )

            self.b_op = wx.Button ( bp1, wx.ID_ANY, "Open")
            self.b_op.Bind ( wx.EVT_BUTTON, self.onOpen )

            b1 = wx.BoxSizer ( wx.HORIZONTAL )
            #b1.Add ( self.b_up, 1, wx.EXPAND )
            b1.Add ( self.b_up, proportion=0 )
            #b1.Add ( self.b_ex, 1, wx.EXPAND )
            b1.Add ( self.b_ex, proportion=0 )
            b1.Add ( self.b_op, proportion=0 )
            bp1.SetSizer ( b1 )

            bp2 = wx.Panel ( self, -1 )
            self.b_se = wx.Button ( bp2, wx.ID_ANY, "Select")
            self.b_se.Bind ( wx.EVT_BUTTON, self.onSelect )

            b2 = wx.BoxSizer ( wx.HORIZONTAL )
            b2.Add ( self.b_se, proportion=0 )
            bp2.SetSizer ( b2 )

            rsz.Add ( bp1, 1, wx.EXPAND )
            rsz.Add ( bp2, 1, wx.EXPAND )

            # XXX ??
            self.update ( True )

        # probably nothing to do unless new data requires
        # an repaint of information on the screen
        def update ( self, is_new ) :
            # trigger a repaint
            self.Refresh ()
            #pass

        # Tkinter was always a pain in the ass wanting you
        # to call a destroy method and spewing out weird messages
        # whatever you did. wxPython just works nicely if you do this.
        # Not only that, you can just type Control-C without irritation.
        def onExit ( self, event ) :
            sys.exit ()

        def onSelect ( self, event ) :
            print ( "Let's select a file." )
            pass

        # Handler for file open button
        def onOpen ( self, event ) :
            print ( "Let's open a file!" )

            #wildcard="XYZ files (*.xyz)|*.xyz",
            with wx.FileDialog(self, "Open Raman data file",
               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return     # the user changed their mind

                # Proceed loading the file chosen by the user
                pathname = fileDialog.GetPath()
                print ( "Selected file: %s" % pathname )

                self.data = Raman_Data ( pathname )
                if not self.data.is_good :
                    printf ( "No good data" )
                    return;

                print ( "Data has been scaled" )
                graph.PostData ( self.data )
                graph.update ()

        def onUpdate ( self, event ) :
            print ( "Useless update button was pushed" )
            self.update ( True )
            graph.update ()

class Temp_Frame ( wx.Frame ):

        def __init__ ( self, parent, title ):
            # Here is a stupid python design concept
            global graph

            wsize = ( xsize, ysize )
            wx.Frame.__init__(self, None, wx.ID_ANY, title, size=wsize )
            #top = wx.Frame.__init__(self, None, wx.ID_ANY, title, pos=(a,b), size=wsize )

            #splitter = wx.SplitterWindow ( self, -1 )
            splitter = wx.SplitterWindow(self, style = wx.SP_LIVE_UPDATE)

            self.lpanel = Left_Panel ( splitter )
            self.rpanel = Right_Panel ( splitter )

            graph = self.lpanel

            # only left side grows
            splitter.SetSashGravity ( 1.0 )

            splitter.SetMinimumPaneSize ( right_size )
            splitter.SplitVertically ( self.lpanel, self.rpanel )
            splitter.SetSashPosition ( split_pos, True )

            self.timer = wx.Timer ( self )
            self.Bind ( wx.EVT_TIMER, self.timer_update, self.timer )
            self.timer.Start ( timer_delay )

        # Called at 1 Hz
        # I doubt whether the Raman tool will need this
        def timer_update ( self, event ) :
            #print ( "Tick" )
            pass
            #if self.data.new_data () :
            #    #print ( "Data arrived" )
            #    #self.data.gather_data ( None )
            #    self.lpanel.update ()
            #    self.rpanel.update ( True )
            #else:
            #    self.rpanel.update ( False )


class Raman_GUI ( wx.App ):
        def __init__ ( self ) :
            wx.App.__init__(self)
            frame = Temp_Frame ( None, "Turbo Raman" )
            self.SetTopWindow ( frame )
            frame.Show ( True )

app = Raman_GUI ()
app.MainLoop()

# THE END
