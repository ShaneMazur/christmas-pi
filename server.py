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
    #continue getting new frames regardless of any clients
    while True:
        frame = stream.read()
        frame = imutils.resize(frame, width=800)
        with lock:
            curr_frame = frame.copy()


def serve_feed():
    global curr_frame, lock
    # infite loop serving a stream
    while True:
        with lock:
            # if a frame is ready, go ahead
            if curr_frame is None:
                continue
            # jpg encoding
            (flag, encodedImage) = cv2.imencode(".jpg", curr_frame)
            # if successful encoding yeild the frame
            if not flag:
                continue
        # requires byte format
        yield b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + encodedImage.tobytes() + b"\r\n"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    return Response(serve_feed(), mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    # starting thread capturing frames
    t = threading.Thread(target=update_frame)
    t.daemon = True
    t.start()
    # start the flask app
    app.run(host="0.0.0.0", port="8000", debug=True, threaded=True, use_reloader=False)