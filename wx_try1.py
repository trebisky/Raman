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
            wx.Frame.__init__ ( self, None, -1, "choices", size=(200,400) )

            self.parent = parent

            self.choice_a = [ "good", "bad", "ugly" ]
            self.want_a = True
            self.choice_b = [ "curly", "moe", "larry" ]

            panel = wx.Panel ( self )
            box = wx.BoxSizer ( wx.VERTICAL )

            lb = wx.ListBox ( panel )
            box.Add ( lb, -1, wx.EXPAND | wx.ALL, 20 )
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

        def OnDone ( self, event ) :
            sel = self.listbox.GetSelection()
            print ( "Selection = ", sel )
            if sel != -1 :
                text = self.listbox.GetString(sel)
                print ( "Selection text = ", text )
            self.parent.OnSelectDone()
            self.Close ()

        # Set and Clear don't seem to be documented methods
        def OnClear ( self, event ) :
            self.listbox.Clear ()

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
            sel = self.select_dialog.listbox.GetSelection()
            print ( "P-Selection = ", sel )
            if sel != -1 :
                text = self.select_dialog.listbox.GetString(sel)
                print ( "P-Selection text = ", text )

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

app = Pop_GUI ()

# It will never return from here.
app.MainLoop()

# THE END
