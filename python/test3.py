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
        struct = message.get_structure()
        structname = struct.get_name()
        structstring = struct.to_string()
        gstobj = message.src
        objectname = gstobj.get_name()
        print("pipeline >>>: name=" + structname + " string=" + structstring + " objectname=" + objectname)



def on_message_queue(bus, message):
    print("queue type="+str(int(message.type)))

def on_message_src(bus, message):
    print("src type="+str(int(message.type)))

Gst.init(None)

# pipeline = udpsrc uri='udp://192.168.1.192:2000' ! queue ! filesink location='/home/caseymac/Videos/tests/test.ts'

pipeline = Gst.Pipeline('the_pipeline')

udpsrc = Gst.ElementFactory.make('udpsrc','my_source')
queue = Gst.ElementFactory.make('queue','my_queue')
fileout = Gst.ElementFactory.make('filesink','my_output')

udpsrc.set_property('uri','udp://192.168.1.192:2000')
fileout.set_property('location', '/home/caseymac/Videos/tests/test.ts')

pipeline.add(queue)
pipeline.add(fileout)
pipeline.add(udpsrc)

udpsrc.link(queue)
queue.link(fileout)

bus = pipeline.get_bus()
bus.add_signal_watch()
bus.connect("message",on_message)

queuebus = queue.get_bus()
queuebus.add_signal_watch()
queuebus.connect("message",on_message_queue)

srcbus = udpsrc.get_bus()
srcbus.add_signal_watch()
srcbus.connect("message",on_message_src)


pipeline.set_state(Gst.State.PLAYING)
try:
  x = GLib.MainLoop()
  while True:
    x.run()
except Exception as e:
  if fatal_exceptions:
    raise
  print(str(e))