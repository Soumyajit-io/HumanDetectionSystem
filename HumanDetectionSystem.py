import cv2
import numpy as np
from flask import Flask, render_template, Response, jsonify
from datetime import datetime

app = Flask(__name__)

# ------------------- YOLO SETUP -------------------
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
with open("coco.names", "r") as f:
    classes = f.read().strip().split("\n")

person_class_id = classes.index("person")
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# ------------------- CAMERA -------------------
camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# ------------------- DETECTION STATE -------------------
human_detected = False
human_count = 0
detection_counter = 0
NO_DETECTION_THRESHOLD = 5  # frames
last_detected_time = None

# ------------------- FRAME GENERATOR -------------------
def gen_frame():
    global human_detected, human_count, detection_counter, last_detected_time
    while True:
        ret, frame = camera.read()
        if not ret:
            continue

        height, width = frame.shape[:2]

        # YOLO forward pass
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
        net.setInput(blob)
        outputs = net.forward(output_layers)

        boxes, confidences = [], []
        detected = False

        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if class_id == person_class_id and confidence > 0.5:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    detected = True

        # Non-Max Suppression
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        num_humans = len(indexes)

        if num_humans > 0:
            for i in indexes.flatten():
                x, y, w, h = boxes[i]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame, "Human Detected", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        # ------------------- SMOOTHING -------------------
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

        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# ------------------- ROUTES -------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/camera')
def video():
    return Response(gen_frame(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    return jsonify({
        "detected": human_detected,
        "last_detected_time": last_detected_time,
        "human_count": human_count
    })

if __name__ == "__main__":
    app.run(debug=True, threaded=True)