#include <gst/gst.h>
#include <stdio.h>
#include <iostream>

#include "test.hxx"

using namespace std;

/* Structure to contain all our information, so we can pass it to callbacks */
typedef struct _CustomData {
  GstElement *pipeline;
  GstElement *source;
  GstElement *convert;
  GstElement *convertVideo;
  GstElement *resample;
  GstElement *sink;
  GstElement *sinkVideo;
} CustomData;

static void pad_added_handler (GstElement *src, GstPad *new_pad, CustomData *data);

void test3(int ac, char* av[]) {

  CustomData data;
  GstBus *bus;
  GstMessage *msg;
  GstStateChangeReturn ret;
  gboolean terminate = FALSE;

  gst_init(&ac, &av);

  /* Create the elements */
  data.source = gst_element_factory_make ("uridecodebin", "source");
  data.convert = gst_element_factory_make ("audioconvert", "convert");
  data.convertVideo = gst_element_factory_make ("videoconvert", "convertVideo");
  data.resample = gst_element_factory_make ("audioresample", "resample");
  data.sink = gst_element_factory_make ("autoaudiosink", "sink");
  data.sinkVideo = gst_element_factory_make ("autovideosink", "sinkVideo");

  data.pipeline = gst_pipeline_new ("test-pipeline");

  if (!data.pipeline || !data.source || !data.convert || !data.resample || !data.sink || !data.convertVideo || !data.sinkVideo) {
    g_printerr ("Not all elements could be created.\n");
    return;
  }

  // create the pipeline and include all 'elements', order is not important now.  We'll link them in order next
  gst_bin_add_many (GST_BIN (data.pipeline), data.source, data.convert, data.resample, data.sink, data.convertVideo, data.sinkVideo, NULL);

  // apply the links in order, one for video and one for audio
  if (!gst_element_link_many (data.convert, data.resample, data.sink, NULL)) {
    g_printerr ("Audio Elements could not be linked.\n");
    gst_object_unref (data.pipeline);
    return;
  }
  if (!gst_element_link_many (data.convertVideo, data.sinkVideo, NULL)) {
    g_printerr ("Video Elements could not be linked.\n");
    gst_object_unref (data.pipeline);
    return;
  }

  /* Set the URI to play */
  g_object_set (data.source, "uri", "https://gstreamer.freedesktop.org/data/media/sintel_trailer-480p.webm", NULL);

  /* Connect to the pad-added signal to the 'source' element and specify the callback for handling dynamic linking */
  g_signal_connect (data.source, "pad-added", G_CALLBACK (pad_added_handler), &data);

  /* Start playing */
  ret = gst_element_set_state (data.pipeline, GST_STATE_PLAYING);
  if (ret == GST_STATE_CHANGE_FAILURE) {
    g_printerr ("Unable to set the pipeline to the playing state.\n");
    gst_object_unref (data.pipeline);
    return;
  }

  /* Listen to the bus */
  bus = gst_element_get_bus (data.pipeline);
  do {
    msg = gst_bus_timed_pop_filtered (bus, GST_CLOCK_TIME_NONE,
      (GstMessageType)(GST_MESSAGE_STATE_CHANGED | GST_MESSAGE_ERROR | GST_MESSAGE_EOS));

      /* Parse message */
      if (msg != NULL) {
        GError *err;
        gchar *debug_info;

        switch (GST_MESSAGE_TYPE (msg)) {
          case GST_MESSAGE_ERROR:
            gst_message_parse_error (msg, &err, &debug_info);
            g_printerr ("Error received from element %s: %s\n", GST_OBJECT_NAME (msg->src), err->message);
            g_printerr ("Debugging information: %s\n", debug_info ? debug_info : "none");
            g_clear_error (&err);
            g_free (debug_info);
            terminate = TRUE;
            break;
          case GST_MESSAGE_EOS:
            g_print ("End-Of-Stream reached.\n");
            terminate = TRUE;
            break;
          case GST_MESSAGE_STATE_CHANGED:
            /* We are only interested in state-changed messages from the pipeline */
            if (GST_MESSAGE_SRC (msg) == GST_OBJECT (data.pipeline)) {
              GstState old_state, new_state, pending_state;
              gst_message_parse_state_changed (msg, &old_state, &new_state, &pending_state);
              g_print ("Pipeline state changed from %s to %s:\n",
                gst_element_state_get_name (old_state), gst_element_state_get_name (new_state));
              }
              break;
          default:
          /* We should not reach here */
          g_printerr ("Unexpected message received.\n");
          break;
          }
      gst_message_unref (msg);
      }
  } while (!terminate);

  /* Free resources */
  gst_object_unref (bus);
  gst_element_set_state (data.pipeline, GST_STATE_NULL);
  gst_object_unref (data.pipeline);
  return ;

}

/* This function will be called by the pad-added signal */
static void pad_added_handler (GstElement *src, GstPad *new_pad, CustomData *data) {
  // get the 'sink' 'pad' from both audio and video convert elements
  GstPad *sink_pad       = gst_element_get_static_pad (data->convert,      "sink");
  GstPad *sink_pad_video = gst_element_get_static_pad (data->convertVideo, "sink");
  GstPadLinkReturn ret;
  GstCaps *new_pad_caps = NULL;
  GstStructure *new_pad_struct = NULL;
  const gchar *new_pad_type = NULL;

  g_print ("Received new pad '%s' from '%s':\n", GST_PAD_NAME (new_pad), GST_ELEMENT_NAME (src));

  /* check to see if a pad is already linked from a previous call
  /*
  if (gst_pad_is_linked (sink_pad_video)) {
    g_print ("We are already linked. Ignoring video.\n");
    goto exit;
  }
  if (gst_pad_is_linked (sink_pad)) {
    g_print ("We are already linked. Ignoring audio.\n");
    goto exit;
  }
  */

  /* Check the new pad's type */
  new_pad_caps = gst_pad_get_current_caps (new_pad);
  new_pad_struct = gst_caps_get_structure (new_pad_caps, 0);
  new_pad_type = gst_structure_get_name (new_pad_struct);
  if (g_str_has_prefix (new_pad_type, "audio/x-raw")) {
    /* Attempt the link */
    ret = gst_pad_link (new_pad, sink_pad);
    if (GST_PAD_LINK_FAILED (ret)) {
      g_print ("Type is audio:'%s' but link failed.\n", new_pad_type);
    } else {
      g_print ("Link succeeded (type '%s').\n", new_pad_type);
    }
  }
  else if (g_str_has_prefix (new_pad_type, "video/x-raw")) {
    /* Attempt the link */
    ret = gst_pad_link (new_pad, sink_pad_video);
    if (GST_PAD_LINK_FAILED (ret)) {
      g_print ("Type is video:'%s' but link failed.\n", new_pad_type);
    } else {
      g_print ("Link succeeded (type '%s').\n", new_pad_type);
    }
  }
  else  {
    g_print ("It has type '%s' which is not raw audio nor video. Ignoring.\n", new_pad_type);
    goto exit;
  }



  exit:
    /* Unreference the new pad's caps, if we got them */
    if (new_pad_caps != NULL)
      gst_caps_unref (new_pad_caps);

    /* Unreference the sink pad */
    gst_object_unref (sink_pad);
    gst_object_unref (sink_pad_video);

}
