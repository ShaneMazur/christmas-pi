import io
import socket

import cv2
import numpy
from PIL import Image

timeout = 30
ip = "0.0.0.0"
port = 8000

sock = socket.socket()
sock.bind((ip,port))
sock.listen(0)

connection = sock.accept()[0].makefile("rb")
try:
    print("Searching for stream...")
    while True:
        if not (image_len := struct.unpack("<L", connection.read(struct.calcsize("<L")))[0]):
            break
        stream = io.BytesIO()
        stream.write(connection.read(image_len))
        image = Image.open(stream)
        cv2.imshow("Video",cv2.cvtColor(numpy.array(image),cv2.COLOR_RGB2BGR))
finally:
    connection.close()
    sock.close()
    
