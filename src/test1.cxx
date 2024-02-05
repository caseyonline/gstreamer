
#include <gst/gst.h>
#include <stdio.h>
#include <iostream>

#include "test.hxx"

using namespace std;

void test1(int ac, char* av[]) {

  GstElement *pipeline;
  GstBus *bus;
  GstMessage *msg;

  gst_init(&ac, &av);

  pipeline = gst_parse_launch("playbin uri=https://gstreamer.freedesktop.org/data/media/sintel_trailer-480p.webm",NULL);

  gst_element_set_state(pipeline, GST_STATE_PLAYING);

  bus = gst_element_get_bus(pipeline);

  // block until one of these bus conditions are met
  msg = gst_bus_timed_pop_filtered (bus, GST_CLOCK_TIME_NONE, (GstMessageType)(GST_MESSAGE_ERROR | GST_MESSAGE_EOS) );

  cout << "Bus msg: " << GST_MESSAGE_TYPE(msg) << endl;
  cout << GST_MESSAGE_ERROR << endl;

  gst_message_unref (msg);
  gst_object_unref (bus);
  gst_element_set_state (pipeline, GST_STATE_NULL);
  gst_object_unref (pipeline);

}
