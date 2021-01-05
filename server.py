import argparse
import datetime
import threading
import time

import cv2
import imutils
from flask import Flask, Response, render_template
from imutils.video import VideoStream

app = Flask(__name__)

lock = threading.Lock()
curr_frame = None

stream = VideoStream(usePiCamera=1).start()
time.sleep(2.0)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


def update_frame():
    while True:
        frame = stream.read()
        frame = imutils.resize(frame, width=400)
        with lock:
            curr_frame = frame.copy()


def serve_feed():
    # grab global references to the output frame and lock variables
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if outputFrame is None:
                continue
            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            # ensure the frame was successfully encoded
            if not flag:
                continue
        # yield the output frame in the byte format
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + bytearray(encodedImage) + b"\r\n"
        )


if __name__ == "__main__":
    # start a thread that will perform motion detection
    t = threading.Thread(target=update_frame)
    t.daemon = True
    t.start()
    # start the flask app
    app.run(host="0.0.0.0", port="8000", debug=True, threaded=True, use_reloader=False)
