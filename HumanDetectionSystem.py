import time
from flask import Flask, render_template, Response, jsonify, request
import cv2
import numpy as np
from datetime import datetime

app = Flask(__name__)

# ------------------- YOLO SETUP -------------------

net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
with open("coco.names", "r") as f:
    classes = f.read().strip().split("\n")

# get person class id
try:
    person_class_id = classes.index("person")
except ValueError:
    person_class_id = None

layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# ------------------- CAMERA -------------------
camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)  
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
time.sleep(1.0)

# ------------------- STATE -------------------
stream_active = False     
detect_active = False    
human_detected = False
human_count = 0
last_detected_time = None
detection_counter = 0
NO_DETECTION_THRESHOLD = 5  # frames

# simple clamp helper
def clamp(v, low, high):
    return max(low, min(high, v))

# ------------------- FRAME GENERATOR -------------------
def gen_frame():
    global human_detected, human_count, last_detected_time, detection_counter
    placeholder_img = create_placeholder_frame(640, 480, text="Stream is off\nClick Start Stream")
    while True:
        if not stream_active:
            
            ret, buffer = cv2.imencode('.jpg', placeholder_img)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.1)
            continue

        
        ret, frame = camera.read()
        if not ret:
            
            ret, buffer = cv2.imencode('.jpg', placeholder_img)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            continue

        
        if detect_active and person_class_id is not None:
            height, width = frame.shape[:2]
            blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
            net.setInput(blob)
            outputs = net.forward(output_layers)

            boxes = []
            confidences = []
            for output in outputs:
                for detection in output:
                    scores = detection[5:]
                    class_id = int(np.argmax(scores))
                    confidence = float(scores[class_id])
                    if class_id == person_class_id and confidence > 0.5:
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)
                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))

            #draw boxes
            if len(boxes) > 0:
                indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
                num_humans = len(indexes)
            else:
                indexes = []
                num_humans = 0

            if num_humans > 0:
                for i in indexes.flatten():
                    x, y, w, h = boxes[i]
                    # safety bounds
                    x1 = clamp(x, 0, width - 1)
                    y1 = clamp(y, 0, height - 1)
                    x2 = clamp(x + w, 0, width - 1)
                    y2 = clamp(y + h, 0, height - 1)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(frame, "Human", (x1, max(15, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

            # smoothing
            if num_humans > 0:
                detection_counter = 0
                human_detected = True
                human_count = num_humans
                last_detected_time = datetime.now().strftime("%H:%M:%S")
            else:
                detection_counter += 1
                if detection_counter >= NO_DETECTION_THRESHOLD:
                    human_detected = False
                    human_count = 0

        else:
            
            human_detected = False
            human_count = 0

        # encode and stream 
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


def create_placeholder_frame(w, h, text="Stream is off"):
    img = np.ones((h, w, 3), dtype=np.uint8) * 220
    lines = text.split('\n')
    y0 = h // 2 - (len(lines) * 20) // 2
    for i, line in enumerate(lines):
        (tw, th), _ = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
        x = max(10, (w - tw) // 2)
        y = y0 + i * 30
        cv2.putText(img, line, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (80, 80, 80), 2, cv2.LINE_AA)
    return img

# ------------------- ROUTES -------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/camera')
def video_feed():
    return Response(gen_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_stream', methods=['POST'])
def start_stream():
    global stream_active
    stream_active = True
    return jsonify({"stream_active": stream_active})

@app.route('/stop_stream', methods=['POST'])
def stop_stream():
    global stream_active, detect_active
    stream_active = False
    detect_active = False
    return jsonify({"stream_active": stream_active, "detect_active": detect_active})

@app.route('/toggle_detect', methods=['POST'])
def toggle_detect():
    global detect_active
    detect_active = not detect_active
    return jsonify({"detect_active": detect_active})

@app.route('/status')
def status():
    return jsonify({
        "stream_active": bool(stream_active),
        "detect_active": bool(detect_active),
        "detected": bool(human_detected),
        "human_count": int(human_count),
        "last_detected_time": last_detected_time
    })

# ------------------- CLEANUP -------------------
import atexit
@atexit.register
def cleanup():
    try:
        camera.release()
    except:
        pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
