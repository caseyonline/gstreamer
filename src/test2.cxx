#include <gst/gst.h>
#include <stdio.h>
#include <iostream>

#include "test.hxx"

using namespace std;

void test2(int ac, char* av[]) {

  GstElement *pipeline, *source, *sink;
  GstBus *bus;
  GstMessage *msg;
  GstStateChangeReturn ret;

  gst_init(&ac, &av);

  // create elements
  source = gst_element_factory_make("videotestsrc", "source");
  sink = gst_element_factory_make("autovideosink", "sink");

  // create an empty pipeline
  pipeline = gst_pipeline_new("test2-pipeline");

  if (!pipeline || !source || !sink) {
    g_printerr("Not all elements could be created\n");
    return;
  }

  // Build the pipeline
  gst_bin_add_many (GST_BIN(pipeline), source, sink, NULL);
  if (gst_element_link(source,sink) != TRUE) {
    g_printerr("Elements could not be linked\n");
    return;
  }

  // modify the sources's properties, 1=static, 4=red square, and so on
  g_object_set (source, "pattern", 0, NULL);

  // start playinig
  ret = gst_element_set_state(pipeline, GST_STATE_PLAYING);
  if (ret == GST_STATE_CHANGE_FAILURE) {
    g_printerr("Unable to set the pipeline to the playing state\n");
    gst_object_unref (pipeline);
    return;
  }

  bus = gst_element_get_bus(pipeline);
  msg = gst_bus_timed_pop_filtered(bus, GST_CLOCK_TIME_NONE, (GstMessageType)(GST_MESSAGE_ERROR | GST_MESSAGE_EOS));

  if (msg != NULL) {
    switch (GST_MESSAGE_TYPE(msg)) {
      case GST_MESSAGE_ERROR:
        break;

      case GST_MESSAGE_EOS:
        break;

      default:
        ;
    }

  }

  gst_object_unref(bus);
  gst_element_set_state(pipeline, GST_STATE_NULL);
  gst_object_unref(pipeline);

}
