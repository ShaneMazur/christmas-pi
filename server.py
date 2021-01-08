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


def update_frame():
    global curr_frame, lock
    while True:
        frame = stream.read()
        frame = imutils.resize(frame, width=800)
        with lock:
            curr_frame = frame.copy()


def serve_feed():
    global curr_frame, lock
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if curr_frame is None:
                continue
            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", curr_frame)
            # ensure the frame was successfully encoded
            if not flag:
                continue
        # yield the output frame in the byte format
        yield b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + encodedImage.tobytes() + b"\r\n"



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/video_feed")
def video_feed():
    return Response(serve_feed(), mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    # start a thread that will perform motion detection
    t = threading.Thread(target=update_frame)
    t.daemon = True
    t.start()
    # start the flask app
    app.run(host="0.0.0.0", port="8000", debug=True, threaded=True, use_reloader=False)


stream.stop()
