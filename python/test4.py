import sys
import time
import gi,re
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0') 
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gst, GObject, Gtk, GLib

def on_message(bus, message):

    if message.type == Gst.MessageType.ELEMENT:
        struct = message.get_structure()
        structname = struct.get_name()
        structstring = struct.to_string()
        gstobj = message.src
        objectname = gstobj.get_name()
        print("pipeline element: name=" + structname + " string=" + structstring + " objectname=" + objectname)
    else:
        print("pipeline type="+str(int(message.type)))


def on_message_queue(bus, message):
    print("queue type="+str(int(message.type)))

def on_message_src(bus, message):
    print("src type="+str(int(message.type)))

def on_message_tsdemux(bus, message):
    print("tsdemux type="+str(int(message.type)))

Gst.init(None)

# pipeline = udpsrc uri='udp://192.168.1.192:2000' ! queue ! tsdemux program-number=1 ! queue ! h264parse ! 'video/x-h264' ! queue ! mpegtsmux ! queue ! filesink location='/home/caseymac/Videos/tests/test.ts'

pipeline = Gst.Pipeline('the_pipeline')

udpsrc = Gst.ElementFactory.make('udpsrc','my_source')
queue1 = Gst.ElementFactory.make('queue','my_queue1')
queue2 = Gst.ElementFactory.make('queue','my_queue2')
queue3 = Gst.ElementFactory.make('queue','my_queue3')
queue4 = Gst.ElementFactory.make('queue','my_queue4')
tsdemux = Gst.ElementFactory.make('tsdemux','my_tsdemux')
h264parse = Gst.ElementFactory.make('h264parse','my_h264parse')
mpegtsmux = Gst.ElementFactory.make('mpegtsmux','my_mpegtsmux')
fileout = Gst.ElementFactory.make('filesink','my_output')
videocaps = Gst.caps_from_string('video/x-h264')
capsfilter = Gst.ElementFactory.make('capsfilter','m_capsfilter')

udpsrc.set_property('uri','udp://192.168.1.192:2000')
fileout.set_property('location', '/home/caseymac/Videos/tests/test.ts')
tsdemux.set_property('program-number',1)
tsdemux.set_property('emit-stats',True)
capsfilter.set_property('caps',videocaps)

pipeline.add(queue1)
pipeline.add(queue2)
pipeline.add(queue3)
pipeline.add(queue4)
pipeline.add(fileout)
pipeline.add(udpsrc)
pipeline.add(tsdemux)
pipeline.add(h264parse)
pipeline.add(mpegtsmux)
pipeline.add(capsfilter)

udpsrc.link(queue1)
queue1.link(tsdemux)
tsdemux.link(queue2)
queue2.link(h264parse)
h264parse.link(capsfilter)
capsfilter.link(queue3)
queue3.link(mpegtsmux)
mpegtsmux.link(queue4)
queue4.link(fileout)


bus = pipeline.get_bus()
bus.add_signal_watch()
bus.connect("message",on_message)

# queuebus = queue.get_bus()
# queuebus.add_signal_watch()
# queuebus.connect("message",on_message_queue)

srcbus = udpsrc.get_bus()
srcbus.add_signal_watch()
srcbus.connect("message",on_message_src)

tsdemuxbus = tsdemux.get_bus()
tsdemuxbus.add_signal_watch()
tsdemuxbus.connect("message",on_message_tsdemux)


pipeline.set_state(Gst.State.PLAYING)
try:
  x = GLib.MainLoop()
  while True:
    x.run()
except Exception as e:
  if fatal_exceptions:
    raise
  print(str(e))