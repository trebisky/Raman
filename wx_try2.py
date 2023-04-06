#! /usr/bin/python

# Learn how to create a wxPython popup window

# ---------------------------------------

import wx
import os
import sys

class MyDialog ( wx.Dialog ) :
        def __init__ ( self ) :
            wx.Dialog.__init__ ( self, None, -1, "test dialog", size=(200,50) )
            b = wx.Button ( self, wx.ID_OK, "Done", pos=(20,20) )
            b.SetDefault ()

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

            # This gives useless raw key codes, with no way to know
            # if the shift key is down or not.
            #self.Bind ( wx.EVT_CHAR_HOOK, self.OnKey, t )
            # The following yields no events at all for me.
            #self.Bind ( wx.EVT_CHAR, self.OnKey, t )

            self.Bind ( wx.EVT_TEXT, self.OnText, t )

            self.mytext = ""

            self.list_size = 20
            lb = wx.ListBox ( panel )
            box.Add ( lb, -1, wx.EXPAND | wx.ALL, self.list_size )
            self.listbox = lb

            b1 = wx.Button ( panel, label="Done" )
            box.Add ( b1, 0 )
            self.Bind ( wx.EVT_BUTTON, self.OnDone, b1 )

            b2 = wx.Button ( panel, label="Load" )
            box.Add ( b2, 0 )
            self.Bind ( wx.EVT_BUTTON, self.OnLoad, b2 )

            b3 = wx.Button ( panel, label="Clear" )
            box.Add ( b3, 0 )
            self.Bind ( wx.EVT_BUTTON, self.OnClear, b3 )

            panel.SetSizer ( box )
            self.Centre ()

        def capture_info ( self ) :
            sel = self.listbox.GetSelection()
            print ( "Selection = ", sel )
            if sel != -1 :
                text = self.listbox.GetString(sel)
                print ( "Selection text = ", text )

        # For some crazy reason, this will go into a recursion loop
        # unless we destroy the window.
        def OnClose ( self, event ) :
            self.capture_info ()
            self.parent.OnSelectDone()
            self.Destroy ()

        def OnDone ( self, event ) :
            self.capture_info ()
            self.parent.OnSelectDone()
            self.Close ()

        # Set and Clear don't seem to be documented methods
        def OnClear ( self, event ) :
            self.listbox.Clear ()

        def OnText ( self, event ) :
            txt = self.text.GetValue ()
            print ( "Text = ", txt )
            if len(txt) < 2 :
                print ( "Not enough" )
                return

            txt = txt.capitalize()

            count = 0
            for name in lib :
                if name.startswith ( txt ) :
                    count += 1
            print ( count, " files match" )

            if count > self.list_size :
                print ( "Too many" )
                return

            info = []
            for name in lib :
                if name.startswith ( txt ) :
                    info.append ( name )
            self.listbox.Set ( info )

        # This is pretty ugly (i.e. very low level)
        # You get every key press as a bare code
        # letters come through as upper case ascii,
        # so you need to detect if shift is down (or up)
        def OnKey ( self, event ) :
            key = event.GetKeyCode()
            print ( "Key = ", key, hex(key) )
            self.mytext += chr(key)
            self.text.SetValue ( self.mytext )

        def OnLoad ( self, event ) :
            if self.want_a :
                self.listbox.Set ( self.choice_a )
                self.want_a = False
            else :
                self.listbox.Set ( self.choice_b )
                self.want_a = True

class MyTop ( wx.Frame ) :
        def __init__ ( self ) :
            #wx.Frame.__init__ ( self, None, wx.ID_ANY, "Pop", size=(100,100) )
            xsize = 100
            ysize = 200
            wsize = ( xsize, ysize )
            title = "Pop"
            wx.Frame.__init__ ( self, None, wx.ID_ANY, title, size=wsize )

            self.select_dialog = None

            panel = wx.Panel ( self )
            box = wx.BoxSizer ( wx.VERTICAL )

            b1 = wx.Button ( panel, label="pop" )
            box.Add ( b1, 0 )
            self.Bind ( wx.EVT_BUTTON, self.OnPop, b1 )

            b2 = wx.Button ( panel, label="show" )
            box.Add ( b2, 0 )
            self.Bind ( wx.EVT_BUTTON, self.OnShow, b2 )

            b3 = wx.Button ( panel, label="select" )
            box.Add ( b3, 0 )
            self.Bind ( wx.EVT_BUTTON, self.OnSelect, b3 )

            b4 = wx.Button ( panel, label="exit" )
            box.Add ( b4, 0 )
            self.Bind ( wx.EVT_BUTTON, self.OnExit, b4 )

            panel.SetSizer ( box )

        def popit ( self ) :
            d = MyDialog ()
            result = d.ShowModal ()
            print ( "result = ", result )
            d.Destroy ()

        def OnPop ( self, event ) :
            self.popit ()

        # It seems a little suspicious to be asking a closed
        # object for information, but it is closed and not
        # destroyed, so everything is OK.
        def OnSelectDone ( self ) :
            self.Enable ()
            sel = self.select_dialog.listbox.GetSelection()
            print ( "P-Selection = ", sel )
            if sel != -1 :
                text = self.select_dialog.listbox.GetString(sel)
                print ( "P-Selection text = ", text )
            txt = self.select_dialog.text.GetValue ()
            print ( "Text = ", txt )

        def OnSelect ( self, event ) :
            d2 = MyDialog2 ( self )
            d2.Show ()
            self.select_dialog = d2
            # the following always gives us -1 because
            # the above returns immediately
            #sel = x.listbox.GetSelection()
            #print ( "P-Selection = ", sel )
            # So, we do a dance with Disable here and have
            # the dailog call the method above when done.
            # NOTE: this may not be necessary in my actual
            # application, I can handle the selection entirely
            # within the dialog and not care that his code
            # returns immediately to the event loop or if it
            # is responsive while the dialog is active.
            self.Disable ()

        def OnShow ( self, event ) :
            pos = self.GetPosition ()
            print ( "Position = ", pos )
            size = self.GetSize ()
            print ( "Size = ", size )

        def OnExit ( self, event ) :
            wx.Exit ()

class Pop_GUI ( wx.App ):
        def __init__ ( self ) :
            wx.App.__init__(self)

            #frame = wx.Frame( None, wx.ID_ANY, title, size=wsize )
            frame = MyTop ()
            self.SetTopWindow ( frame )
            frame.Show ( True )

            # It would seem to me that I could call the popit method
            # in the MyTop class, but this does not work.
            #MyTop.popit ()
            # However this does
            # But I elect not to launch with the popup popped up
            #frame.popit ()

        # This hook seems entirely optional
        def OnInit ( self ) :
            #print ( "On init called" )
            return True

        def OnExit ( self ) :
            print ( "On exit called" )
            return True

# We effectively black list this species because of the weird characters
# in the locality, maybe someday we will return and do something about this.
# If I was the only one using the program, I would edit the two files in
# the library and get rid of the nasty characters, but other people will
# hopefully use the program and it is unreasonable to expect them to do that.
bogus_species = "Cobaltarthurite"

if ( sys.platform == "linux" ) :
    raman_lib_dir = os.path.expanduser ( "~/RamanLib" )
else :
    raman_lib_dir = "\CrystalSleuth\SearchRecords\RamanLib"

if not os.path.isdir ( raman_lib_dir ) :
    print ( "Cannot find Raman library:", raman_lib_dir )
    exit ()

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
                    species = file[:file.index("_")]
                    self.files.append ( species )

# I see 5127 files (excluding the 2 blacklisted)
lib = Raman_Library ().files
print ( len(lib), " files found" )

app = Pop_GUI ()

# It will never return from here.
app.MainLoop()

# THE END
