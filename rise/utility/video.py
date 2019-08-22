import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject
import sys
import time

VIDEO_OUT_LAUNCH = """rtpbin name=rtpbin buffer-mode=1 v4l2src device=/dev/video0 !
image/jpeg, width=(int)1280, height=(int)480, pixel-aspect-ratio=(fraction)1/1, framerate=(fraction)30/1 !
rtpjpegpay ! rtpbin.send_rtp_sink_0 rtpbin.send_rtp_src_0 !
udpsink port=5000 host=127.0.0.1 name=vrtpsink_l rtpbin.send_rtcp_src_0 !
udpsink port=5001 host=$DEST sync=false async=false name=vrtcpsink_l udpsrc port=5005 name=vrtcpsrc_l ! rtpbin.recv_rtcp_sink_0"""

VIDEO_IN_LAUNCH = """rtpbin name=rtpbin latency=250 drop-on-latecy=true buffer-mode=1
udpsrc caps="application/x-rtp,media=(string)video,clock-rate=(int)90000,
encoding-name=(string)JPEG,payload=(int)26" port=5000 ! rtpbin.recv_rtp_sink_0 rtpbin. !
rtpjpegdepay ! jpegparse ! jpegdec ! videorate ! autovideosink sync=false udpsrc port=5001 !
rtpbin.recv_rtcp_sink_0 rtpbin.send_rtcp_src_0 ! udpsink port=5005 host=127.0.0.1 sync=false async=false"""


class Video:
    def __init__(self):
        Gst.init(sys.argv)
        self._pipe = None
        self._isConnected = False

    def start(self, l):
        if self._isConnected:
            return
        self._isConnected = True
        self._pipe = Gst.parse_launch(l)
        self._pipe.set_state(Gst.State.PLAYING)

    def stop(self):
        if not self._isConnected:
            return
        self._isConnected = False
        self._pipe.set_state(Gst.State.NULL)
