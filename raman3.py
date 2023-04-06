#! /usr/bin/python

# Proof of concept code for new Raman software
# Tom Trebisky  4-3-2023
# Use wxPython for basic file operations

# .........................
"""
Todo --

* wx.FileDropTarget allows files to be dropped onto some thing

* check on univeral X axis scale
* X axis scale flipping
* Unknown data trend and background removal
* Searching

"""

# ---------------------------------------

import wx
import os
import sys
import numpy as np

# Global variables point to major objects
graph = None    # graph object (left side)
library = None

display_list = []

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
    raman_lib_dir = os.path.expanduser ( "~/RamanLib" )
else :
    raman_lib_dir = "\CrystalSleuth\SearchRecords\RamanLib"

if not os.path.isdir ( raman_lib_dir ) :
    print ( "Cannot find Raman library:", raman_lib_dir )
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
        def __init__ ( self, path, is_unknown ) :
            self.path = path
            self.is_good = False
            self.is_unknown = is_unknown

            if not self.validate () :
                return

            with open ( path, 'r') as file:
                self.read_file_data (file)

            self.is_good = True

            # XXX
            # each data item should get a unique color
            if is_unknown :
                self.color = wx.BLACK
            else :
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

            self.scale_data ();


        def validate ( self ) :

            # ensure we can open the file
            # also read the first line
            try:
                with open ( self.path, 'r') as file:
                    first = file.readline()
            except IOError:
                print ( "Cannot open file '%s'." % self.path )
                return False

            # Library files start with this.
            if first.startswith ( "##" ) :
                return True

            # weak validation, we ensure the first line
            # has exactly one comma in it.
            ccount = first.count ( ',' )
            if ccount == 1 :
                return True

            print ( "Not a CSV file: %s" % self.path )
            return False

        def scale_data ( self ) :

            self.xy = []

            # We can adjust this to center data, etc.
            yrang = self.yrange

            #print ( "Scaling ", len(self.xx), " points" )

            for i in range(len(self.xx)) :
                xf = (self.xx[i] - self.xmin) / self.xrange
                #yf = (self.yy[i] - self.ymin) / self.yrange
                yf = (self.yy[i] - self.ybot) / yrang

                ix = graph.xoff + np.int_ ( graph.xsize * xf )
                iy = graph.yoff + np.int_ ( graph.ysize * (1.0-yf) )
                self.xy.append ( (ix,iy) )

            #print ( "Data has been scaled" )

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

            #self.SetBackgroundColour ( wx.RED )
            self.SetBackgroundColour ( "light grey" )

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
            #print ( "resize!" )

            self.setViewport ( event.Size.width, event.Size.height )

            for d in display_list :
                d.scale_data ()

            self.update ();

        def PaintData ( self ) :
            #print ( "PaintData 1" )
            # loop through data objects
            for d in display_list :
                dc = wx.PaintDC ( self )
                dc.SetPen ( wx.Pen( d.color, 2) )
                #print ( "PaintData 2", d.color, len(d.xy) )

                lastxy = None
                for xy in d.xy :
                    if xy and lastxy :
                        dc.DrawLine ( lastxy[0], lastxy[1], xy[0], xy[1] )
                    lastxy = xy

        # We get lots of paint events, for reasons I don't understand,
        # and not simply related to cursor motion.
        def OnPaint ( self, event ) :
            #print ( "Paint!" )

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

            #self.old_layout ()

        def old_layout ( self ) :
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

            # ??
            #self.update ( True )

        # probably nothing to do unless new data requires
        # an repaint of information on the screen
        def update ( self, is_new ) :
            # trigger a repaint
            self.Refresh ()

        # Tkinter was always a pain in the ass wanting you
        # to call a destroy method and spewing out weird messages
        # whatever you did. wxPython just works nicely if you do this.
        # Not only that, you can just type Control-C without irritation.
        def onExit ( self, event ) :
            sys.exit ()

        def onSelect ( self, event ) :
            #print ( "Let's select a file." )
            pass

        # Handler for file open button (now gone)
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

                self.data = Raman_Data ( pathname, True )
                if not self.data.is_good :
                    printf ( "No good data" )
                    return;

                #graph.PostData ( self.data )
                display_list.append ( self.data )
                graph.update ()

        def onUpdate ( self, event ) :
            print ( "Useless update button was pushed" )
            self.update ( True )
            graph.update ()

class MyDialog2 ( wx.Frame ) :
        def __init__ ( self, parent ) :
            wx.Frame.__init__ ( self, None, -1, "choices", size=(200,500) )

            # This is to catch when user clicks the window manager
            # control to close this subwindow.
            self.Bind ( wx.EVT_CLOSE, self.OnClose, self )

            self.parent = parent

            self.choice_a = [ "good", "bad", "ugly" ]
            self.want_a = True
            self.choice_b = [ "curly", "moe", "larry" ]

            panel = wx.Panel ( self )
            box = wx.BoxSizer ( wx.VERTICAL )

            t = wx.TextCtrl ( panel, -1, "your ad here", size = (-1,-1) )
            t.SetInsertionPoint ( 0 )
            self.text = t
            box.Add ( t, 0 )

            self.Bind ( wx.EVT_TEXT, self.OnText, t )

            self.mytext = ""

            self.lbox_size = 20
            lb = wx.ListBox ( panel )
            box.Add ( lb, -1, wx.EXPAND | wx.ALL, self.lbox_size )
            self.listbox = lb

            b1 = wx.Button ( panel, label="Done" )
            box.Add ( b1, 0 )
            self.Bind ( wx.EVT_BUTTON, self.OnDone, b1 )

            #b2 = wx.Button ( panel, label="Load" )
            #box.Add ( b2, 0 )
            #self.Bind ( wx.EVT_BUTTON, self.OnLoad, b2 )

            #b3 = wx.Button ( panel, label="Clear" )
            #box.Add ( b3, 0 )
            #self.Bind ( wx.EVT_BUTTON, self.OnClear, b3 )

            panel.SetSizer ( box )
            self.Centre ()

        # However we terminate the dialog, we end up here.
        def capture_info ( self ) :
            sel = self.listbox.GetSelection()
            if sel == -1 :
                return

            print ( "Selection = ", sel )
            text = self.listbox.GetString(sel)
            print ( "Selection text = ", text )

            lib_data = self.list[sel]
            print ( "Open: ", lib_data.fpath )
            data = Raman_Data ( lib_data.fpath, False )
            if not data.is_good :
                printf ( "Library data file in wrong format" )
                return;

            display_list.append ( data )
            # Zoro

        # Called when the window manager kills the window
        # For some crazy reason, this will go into a recursion loop
        # unless we destroy the window.
        def OnClose ( self, event ) :
            self.capture_info ()
            self.Destroy ()

        # This is nicer (called from the Done button)
        def OnDone ( self, event ) :
            self.capture_info ()
            self.Close ()

        # Set and Clear don't seem to be documented methods
        #def OnClear ( self, event ) :
        #    self.listbox.Clear ()

        def OnText ( self, event ) :
            txt = self.text.GetValue ()
            print ( "Text = ", txt )
            if len(txt) < 2 :
                print ( "Not enough" )
                return

            txt = txt.capitalize()

            count = 0
            for f in library.files :
                if f.species.startswith ( txt ) :
                    count += 1
            print ( count, " files match" )

            if count > self.lbox_size :
                print ( "Too many" )
                return

            # When selection is done, the first item is 0
            # "info" is what is displayed in the listbox
            # "self.list" has the same order, but has file paths
            info = []
            self.list = []
            for f in library.files :
                if f.species.startswith ( txt ) :
                    info.append ( f.species )
                    self.list.append ( f )
            self.listbox.Set ( info )

class Raman_Frame ( wx.Frame ):

        def __init__ ( self, parent, title ):
            # Here is a stupid python design concept
            global graph

            wsize = ( xsize, ysize )
            top = wx.Frame.__init__(self, None, wx.ID_ANY, title, size=wsize )
            #top = wx.Frame.__init__(self, None, wx.ID_ANY, title, pos=(a,b), size=wsize )

            self.menu_setup ()

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

        def menu_setup ( self ) :

            filemenu= wx.Menu()
            #openFileItem = fileMenu.Append(wx.ID_OPEN, '&Open\tCTRL+O', "Open File")
            o_menu = filemenu.Append ( wx.ID_OPEN, "Open", "Open")
            s_menu = filemenu.Append ( 101, "Select", "Select")
            #filemenu.Append(wx.ID_ABOUT, "About","About")
            e_menu = filemenu.Append ( wx.ID_EXIT, "Exit", "Exit")

            self.Bind ( wx.EVT_MENU, self.OpenFile, o_menu )
            self.Bind ( wx.EVT_MENU, self.SelectFile, s_menu )
            #self.Bind ( wx.EVT_MENU, self.Exit, e_menu )

            # I considered making it possible to just click on the "Exit"
            # in the menubar, but decided that two clicks to exit was fine.
            exitmenu= wx.Menu()
            ee_menu = exitmenu.Append ( wx.ID_EXIT, "Exit", "Exit")
            self.Bind ( wx.EVT_MENU, self.Exit, ee_menu )

            bar = wx.MenuBar()
            bar.Append ( filemenu, "File" )
            bar.Append ( exitmenu, "Exit" )
            self.SetMenuBar ( bar )

        # We just launch the dialog without worrying about making it
        # Modal.  Also we don't worry about getting results from it
        # in this class, it will inject any results itself
        def SelectFile ( self, event ) :
            d2 = MyDialog2 ( self )
            d2.Show ()
            #self.select_dialog = d2

        # I never made this work, delete it someday
        def OldSelectFile ( self, event ) :
            print ( "Select file" )
            init_list = [ 'good', 'bad', 'ugly' ]
            x = event.GetEventObject ()
            print ( "Object = ", x )
            pos = x.ClientToScreen ( (0,0) )
            print ( "Pos = ", pos )
            sz = x.GetSize ()
            print ( "Size = ", sz )
            s = Select_Dialog ( self, wx.BORDER_SIMPLE, init_list )
            s.Show ()
            s.Popup ( focus=self )

        # This opens the users unknow file
        def OpenFile ( self, event ) :
            print ( "Let's open a file (2)!" )

            #wildcard="XYZ files (*.xyz)|*.xyz",
            with wx.FileDialog(self, "Open Raman data file",
               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return     # the user changed their mind

                # Proceed loading the file chosen by the user
                pathname = fileDialog.GetPath()
                print ( "Selected file: %s" % pathname )

                data = Raman_Data ( pathname, True )
                if not data.is_good :
                    printf ( "Ain't got no good data" )
                    return;

                #print ( "Data has been scaled" )
                #graph.PostData ( data )
                display_list.append ( data )
                graph.update ()

        def Exit ( self, event ) :
            sys.exit ()

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

# XXX - never worked, delete this someday
class Select_Dialog ( wx.PopupTransientWindow ) :
        def __init__ ( self, parent, style, init_data ) :
            #super().__init__ ( self, parent, style )
            wx.PopupTransientWindow.__init__ ( self, parent, style )
            tsize = ( 150, 300 )
            self.SetSize ( tsize )
            panel = wx.Panel ( self, size=tsize )
            panel.SetBackgroundColour ( "dark grey" )
            self.Layout ()


# There are some weird foreign non-ascii characters in some of the files
# and python does not like them:
# Cobaltarthurite__R070224__Raman__532__0__unoriented__Raman_Data_Processed__25613.txt
# UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc3 in position 73: invalid continuation byte
# For this file, the trouble is in the LOCALITY data:
##LOCALITY=Dolores prospect, Pastrana, MazarrÃ³n-Ã?guilas, Murcia, Spain

class Raman_Lib_File () :
        def __init__ ( self, file, fpath, cheat ) :
            self.file = file
            self.fpath = fpath

            # This gets the species name from the filename, which gives
            # for example "BastnasiteCe"
            if cheat :
                self.species = file[:file.index("_")]
                return

            # We get something somewhat nicer from inside the file,
            # namely Bastnasite-(Ce), but the price for this niceness
            # is that we must open each file and read the first line.
            # On linux this is slow the first time, but then the file
            #  data cache is loaded and it is quite fast after that.
            #print ( file )
            with open ( fpath, 'r') as f:
                    first = f.readline().rstrip()
            self.species = first[first.index("=")+1:]

            #print ( self.species )

# A typical filename looks like this:
# Benitoite__R050332__Raman__514__0__unoriented__Raman_Data_Processed__10941.txt
# Thse are not simple CSV files, but have some header information as follows:
##NAMES=Benitoite
##LOCALITY=San Benito County, California, USA
##RRUFFID=R050320
##CHEMISTRY=BaTiSi_3_O_9_
#
# Each header line begins with a pair of "#" pound signs
# Not only that, but the data ends with "##END="
# which may be followed by several blank lines and possible
# other rubbish.
#
# My library (circa 1890) has 5133 files.
# No subdirectories, so the "isfile" check below is superfluous.
# 4 of these files are special things for Crystal Sleuth,
# namely:
# RamanSearchFileFast.rsf
# RamanSearchFileSlow.rsf
# RamanSearchNameList.rsf
# RamanSearchNameInfo.rsf

# Note that the NameList and NameInfo files (generated by Crystal Sleuth)
# have all the information for all of the files, so we could get what
# we want by only opening two files (why is it not all just in one?)
# Perhaps someday we will do that, or else generate our one file with
# a summary.

# We effectively black list this species because of the weird characters
# in the locality, maybe someday we will return and do something about this.
# If I was the only one using the program, I would edit the two files in
# the library and get rid of the nasty characters, but other people will
# hopefully use the program and it is unreasonable to expect them to do that.
bogus_species = "Cobaltarthurite"

class Raman_Library () :
        def __init__ ( self ) :
            self.files = []
            for file in os.listdir ( raman_lib_dir ):
                fpath = os.path.join ( raman_lib_dir, file )
                # use the filename for the species name, but this will just
                # bite us later (maybe) if/when we try to read the spectrum
                #if file == bogus_file :
                #    self.files.append ( Raman_Lib_File ( file, fpath, True ) )
                #    continue
                if file.startswith ( bogus_species ) :
                    continue
                #print ( "Lib: ", file, fpath )
                if os.path.isfile ( fpath ) and file.endswith ( "txt" ) :
                    self.files.append ( Raman_Lib_File ( file, fpath, False ) )

class Raman_GUI ( wx.App ):
        def __init__ ( self ) :
            wx.App.__init__(self)
            frame = Raman_Frame ( None, "Turbo Raman" )
            self.SetTopWindow ( frame )
            frame.Show ( True )

# XXX what would be better would be to launch the GUI,
# but use the status bar to indicate this.
# Better yet, speed this up by reading a single summary file,
# either the .rsf file from Crystal Sleuth or something we
# generate.
print ( "Initializing, please wait ..." )

library = Raman_Library ()
print ( 'Library has: ', len(library.files), " files")

print ( "Initialization done." )

app = Raman_GUI ()
app.MainLoop()

# THE END
