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
    elif message.type == Gst.MessageType.STREAM_STATUS:
        msg = str(message.parse_stream_status())
        print("pipeline streamStatus="+msg)
    elif message.type == Gst.MessageType.ERROR:
        msg = str(message.parse_error())
        print("pipeline error="+msg)
    elif message.type == Gst.MessageType.WARNING:
        err, debug = message.parse_warning()
        details = message.parse_warning_details()
        print("pipeline WARNING="+details.to_string())
    else:
        print("pipeline type="+str(int(message.type)))

def on_probe_idle(pad, info, user_data):
    print("on_probe_idle--------------------------------------")

    # Clean up old pipeline
    tsdemux.unlink(h264parse1)
    h264parse1.unlink(capsfilter1A)
    capsfilter1A.unlink(queue2)

    pipeline.remove(h264parse1)
    pipeline.remove(capsfilter1A)

    h264parse1.set_state(Gst.State.NULL)
    capsfilter1A.set_state(Gst.State.NULL)

    h264parse1.unref()
    capsfilter1A.unref()

    # Create new pipeline
    mpeg2video  = Gst.ElementFactory.make('mpegvideoparse','my_mpeg2video')
    capsfilter1B= Gst.ElementFactory.make('capsfilter','my_capsfilter1B')
    capsfilter1B.set_property('caps',Gst.caps_from_string('video/mpeg, alignment=au'))

    mpeg2video.ref()
    capsfilter1B.ref()

    pipeline.add(mpeg2video)
    pipeline.add(capsfilter1B)

    mpeg2video.sync_state_with_parent()
    capsfilter1B.sync_state_with_parent()

    pad.link(mpeg2video.get_static_pad("sink"))
    mpeg2video.link(capsfilter1B)
    capsfilter1B.link(queue2)

    pipeline.set_state(Gst.State.PLAYING)    

    return Gst.PadProbeReturn.REMOVE

def on_pad_added(src, new_pad):
    print("Received new pad '{0:s}' from '{1:s}'".format(new_pad.get_name(),src.get_name()))
    if "my_tsdemux" in src.get_name():
       if "video" in new_pad.get_name():
            caps = new_pad.get_current_caps()
            print(">>>>"+caps.to_string())
            if "video/x-h264" in caps.to_string():
                print("video/h264------------------------------------------------------------------------------")
                new_pad.link(h264parse1.get_static_pad("sink"))
                capsfilter1A.set_property('caps',Gst.caps_from_string('video/x-h264, alignment=au'))
                h264parse1.link(capsfilter1A)
                capsfilter1A.link(queue2)

            elif "video/mpeg" in caps.to_string():
                print("video/mpeg------------------------------------------------------------------------------")
                # queue1SrcPad = queue1.get_static_pad("src")
                # global global_new_pad
                # global_new_pad = new_pad

                new_pad.add_probe(Gst.PadProbeType.IDLE, on_probe_idle, None)
                # tsdemux.unlink(h264parse1)
                # h264parse1.unlink(capsfilter1)
                # capsfilter1.unlink(queue2)
                # new_pad.link(mpeg2video.get_static_pad("sink"))
                # capsfilter1.set_property('caps',Gst.caps_from_string('video/mpeg, alignment=au'))
                # mpeg2video.link(capsfilter1)
                # capsfilter1.link(queue2)

Gst.init(None)

# pipeline = udpsrc uri='udp://192.168.1.192:2000' ! queue ! tsdemux program-number=1 ! h264parse ! 'video/x-h264, alignment=au' ! queue ! nvtranscode codec=h264 bitrate=500000 ! queue ! h264parse ! 'video/x-h264, alignment=au, stream-format=byte-stream' ! queue ! mpegtsmux ! queue ! filesink location=tests/test.ts

pipeline = Gst.Pipeline('the_pipeline')

# create elements
udpsrc      = Gst.ElementFactory.make('udpsrc','my_source')
queue1      = Gst.ElementFactory.make('queue','my_queue1')
queue2      = Gst.ElementFactory.make('queue','my_queue2')
queue3      = Gst.ElementFactory.make('queue','my_queue3')
queue4      = Gst.ElementFactory.make('queue','my_queue4')
queue5      = Gst.ElementFactory.make('queue','my_queue5')
tsdemux     = Gst.ElementFactory.make('tsdemux','my_tsdemux')
h264parse1  = Gst.ElementFactory.make('h264parse','my_h264parse1')
h264parse2  = Gst.ElementFactory.make('h264parse','my_h264parse2')
capsfilter1A= Gst.ElementFactory.make('capsfilter','my_capsfilter1A')
capsfilter2 = Gst.ElementFactory.make('capsfilter','my_capsfilter2')
nvtranscode = Gst.ElementFactory.make('nvtranscode','my_nvtranscode')
mpegtsmux   = Gst.ElementFactory.make('mpegtsmux', 'my_mpegtsmux')
fileout     = Gst.ElementFactory.make('filesink','my_output')

if not udpsrc or not queue1 or not queue2 or not queue3 or not queue4 or not queue5 or not tsdemux or not h264parse1 or not h264parse2 or not capsfilter1A or not capsfilter2 or not nvtranscode or not mpegtsmux or not fileout:
    print("Error creating elements")
    exit(0)

# set properties
udpsrc.set_property('uri','udp://192.168.1.192:2000')
fileout.set_property('location', '/home/caseymac/Videos/tests/test.ts')
tsdemux.set_property('program-number',1)
capsfilter1A.set_property('caps',Gst.caps_from_string('video/x-h264, alignment=au'))
capsfilter2.set_property('caps',Gst.caps_from_string('video/x-h264, alignment=au, stream-format=byte-stream'))
nvtranscode.set_property('codec','h264')
nvtranscode.set_property('bitrate', 500000)

# add to pipeline
pipeline.add(udpsrc)
pipeline.add(queue1)
pipeline.add(queue2)
pipeline.add(queue3)
pipeline.add(queue4)
pipeline.add(queue5)
pipeline.add(tsdemux)
pipeline.add(h264parse1)
pipeline.add(h264parse2)
pipeline.add(capsfilter1A)
pipeline.add(capsfilter2)
pipeline.add(nvtranscode)
pipeline.add(mpegtsmux)
pipeline.add(fileout)

# create pipeline links
udpsrc.link(queue1)
queue1.link(tsdemux)
tsdemux.connect('pad-added',on_pad_added)
queue2.link(nvtranscode)
nvtranscode.link(queue3)
queue3.link(h264parse2)
h264parse2.link(capsfilter2)
capsfilter2.link(queue4)
queue4.link(mpegtsmux)
mpegtsmux.link(queue5)
queue5.link(fileout)

# create bus call backs to receive events
bus = pipeline.get_bus()
bus.add_signal_watch()
bus.connect("message",on_message)


pipeline.set_state(Gst.State.PLAYING)
try:
  x = GLib.MainLoop()
  while True:
    x.run()
except Exception as e:
  print(str(e))