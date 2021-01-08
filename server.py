import argparse
import datetime
import threading
import time

import cv2
import imutils
from flask import Flask, Response, render_template
from imutils.video import VideoStream

from overlays.motion_detect import SingleMotionDetector

app = Flask(__name__)

lock = threading.Lock()
frames = {
    "default": None,
    "motion": None,
}

stream = VideoStream(usePiCamera=1).start()
time.sleep(2.0)


def update_frame():
    global frames, lock, stream
    # continue getting new frames regardless of any clients
    while True:
        frame = stream.read()
        frame = imutils.resize(frame, width=800)
        with lock:
            frames["default"] = frame.copy()


def motion_detect():
    global frames, lock
    md = SingleMotionDetector(accumWeight=0.1)
    total = 0
    while True:
        if frames["default"] is not None:
            frame = frames["default"]
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (7, 7), 0)

            if total > 30:
                # detect motion in the image
                motion = md.detect(gray)
                if motion is not None:
                    # draw the "motion area" on the output frame
                    (thresh, (minX, minY, maxX, maxY)) = motion
                    cv2.rectangle(frame, (minX, minY), (maxX, maxY), (0, 0, 255), 2)

            # update the background model and increment the total number
            # of frames read thus far
            md.update(gray)
            total += 1
            # acquire the lock, set the output frame, and release the
            # lock
            with lock:
                frames["motion"] = frame.copy()


def serve_feed(frame_type="default"):
    global frames, lock
    # infite loop serving a stream
    while True:
        with lock:
            # if a frame is ready, go ahead
            if frames[frame_type] is None:
                continue
            # jpg encoding
            (flag, encodedImage) = cv2.imencode(".jpg", frames[frame_type])
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


@app.route("/motion")
def motion():
    return render_template("index.html")


@app.route("/detected_feed")
def detected_feed():
    return Response(
        serve_feed("motion"), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


if __name__ == "__main__":
    # starting thread capturing frames
    t = threading.Thread(target=update_frame)
    t.daemon = True
    t.start()
    # starting thread cdetecting motion
    t = threading.Thread(target=motion_detect)
    t.daemon = True
    t.start()
    # start the flask app
    app.run(host="0.0.0.0", port="8000", debug=True, threaded=True, use_reloader=False)
