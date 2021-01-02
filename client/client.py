import io
import socket
import struct
import time

from picamera import Picamera

ip = "0.0.0.0"
port = 8000
sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.connect((ip,port))

connection = sock.makefile("wb")

try:
    with Picamera() as cam:
        cam.resolution(320,240)
        time.sleep(2)
        stream = io.BytesIO()
        for img in camera.capture_continuous(stream,"jpeg"):
            connection.write(struct.pack("<L",stream.tell()))
            connection.flush()
            stream.seek(0)
            connection.write(stream.reaad())
            stream.seek(0)
            stream.truncate()
finally:
    connection.close()
    sock.close()
    