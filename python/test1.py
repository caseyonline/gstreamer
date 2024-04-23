import sys
import time
import gi,re
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0') 
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gst, GObject,Gtk


Gst.init(sys.argv)

# Gst.Pipeline
pipeline = Gst.parse_launch("videotestsrc num-buffers=100 ! autovideosink")

pipeline.set_state(Gst.State.PLAYING)

time.sleep(2)