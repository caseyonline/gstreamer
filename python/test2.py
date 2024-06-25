import sys
import time
import gi,re
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0') 
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gst, GLib

def on_message(bus, message):

    if message.type == Gst.MessageType.ELEMENT:
        struct = message.get_structure()
        structname = struct.get_name()
        structstring = struct.to_string()
        gstobj = message.src
        objectname = gstobj.get_name()
        print("pipeline element: name=" + structname + " string=" + structstring + " objectname=" + objectname)
    elif message.type == Gst.MessageType.ERROR:
        msg = str(message.parse_error())
        print("pipeline error="+msg)
    else:
        print("pipeline type="+str(int(message.type)))

def on_message_player(bus, message):
    print("player type="+str(int(message.type)))

def on_sync_message_player(bus, message):
    print("player sync type="+str(int(message.type)))

def on_message_queue(bus, message):
    print("queue type="+str(int(message.type)))



Gst.init(None)

# pipeline = videotestsrc ! queue ! autovideosink

pipeline = Gst.Pipeline('the_pipeline')

src = Gst.ElementFactory.make('videotestsrc','my_source')
queue = Gst.ElementFactory.make('queue','my_queue')
player = Gst.ElementFactory.make('autovideosink','my_player')

src.set_property('background-color',0xffff0000)

pipeline.add(queue)
pipeline.add(player)
pipeline.add(src)

src.link(queue)
queue.link(player)


bus = pipeline.get_bus()
bus.add_signal_watch()
bus.connect("message",on_message)

playerbus = player.get_bus()
playerbus.add_signal_watch()
playerbus.enable_sync_message_emission()
playerbus.connect("message",on_message_player)
playerbus.connect("sync-message::element",on_sync_message_player)

queuebus = queue.get_bus()
queuebus.add_signal_watch()
queuebus.connect("message",on_message_queue)




pipeline.set_state(Gst.State.PLAYING)
try:
  x = GLib.MainLoop()
  while True:
    x.run()
except Exception as e:
  print(str(e))
