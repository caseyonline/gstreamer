import sys
import time
import threading
import gi,re
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0') 
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gst, GObject, Gtk, GLib

def on_period():
   print("----------------------------------- on_period -----------------------------------")
   threading.Timer(5, on_period).start()

def on_message(bus, message):

    if message.type == Gst.MessageType.ELEMENT:
        struct = message.get_structure()
        structname = struct.get_name()
        structstring = struct.to_string()
        gstobj = message.src
        objectname = gstobj.get_name()
        if "tsdemux" in structname:
            pts = "-"
            if struct.get_value('pts'):
               pts = str(struct.get_value('pts'))
            print("tsdemux stats >>> pid: %d, offset: %d, pts: %s" % (struct.get_value('pid'), struct.get_value('offset'), pts))
        else:
            print("pipeline element: name=" + structname + " string=" + structstring + " objectname=" + objectname)
    elif message.type == Gst.MessageType.STREAM_STATUS:
        msg = str(message.parse_stream_status())
        print("pipeline streamStatus="+msg)
    elif message.type == Gst.MessageType.ERROR:
        msg = str(message.parse_error())
        print("pipeline error="+msg)
    elif message.type == Gst.MessageType.WARNING:
        err, debug = message.parse_warning()
        details = message.parse_warning_details()
        if "continuity-mismatch" in details.get_value('warning-type'):
           print("Packet Drop >>> packet: %d, stream: %d, pid: %i" % (details.get_value('packet'), details.get_value('stream'), details.get_value('pid')))

    else:
        print("pipeline type="+str(int(message.type)))


def on_message_queue(bus, message):
    print("queue type="+str(int(message.type)))

def on_message_src(bus, message):
    print("src type="+str(int(message.type)))

def on_message_tsdemux(bus, message):
    print("tsdemux type="+str(int(message.type)))

def on_pad_added(src, new_pad):
    print("Received new pad '{0:s}' from '{1:s}'".format(new_pad.get_name(),src.get_name()))
    new_pad.link(fileout.get_static_pad("sink"))

Gst.init(None)

# pipeline = udpsrc uri='udp://192.168.1.192:2000' ! queue ! tsdemux ! filesink location='/home/caseymac/Videos/tests/test.out'

pipeline = Gst.Pipeline('the_pipeline')

udpsrc = Gst.ElementFactory.make('udpsrc','my_source')
queue1 = Gst.ElementFactory.make('queue','my_queue1')
tsdemux = Gst.ElementFactory.make('tsdemux','my_tsdemux')
fileout = Gst.ElementFactory.make('filesink','my_output')
capsfilter = Gst.ElementFactory.make('capsfilter','my_capsfilter')

udpsrc.set_property('uri','udp://192.168.1.192:2000')
fileout.set_property('location', '/home/caseymac/Videos/tests/test.out')
tsdemux.set_property('program-number',1)
tsdemux.set_property('emit-stats',True)
videocaps = Gst.caps_from_string('video/x-h264')
capsfilter.set_property('caps',videocaps)

pipeline.add(queue1)
pipeline.add(fileout)
pipeline.add(udpsrc)
pipeline.add(tsdemux)
pipeline.add(capsfilter)

udpsrc.link(queue1)
queue1.link(tsdemux)
tsdemux.connect('pad-added',on_pad_added)

bus = pipeline.get_bus()
bus.add_signal_watch()
bus.connect("message",on_message)

queuebus = queue1.get_bus()
queuebus.add_signal_watch()
queuebus.connect("message",on_message_queue)

srcbus = udpsrc.get_bus()
srcbus.add_signal_watch()
srcbus.connect("message",on_message_src)

tsdemuxbus = tsdemux.get_bus()
tsdemuxbus.add_signal_watch()
tsdemuxbus.connect("message",on_message_tsdemux)

on_period()

pipeline.set_state(Gst.State.PLAYING)
try:
  x = GLib.MainLoop()
  while True:
    x.run()
except Exception as e:
  if fatal_exceptions:
    raise
  print(str(e))