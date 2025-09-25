# 🧑‍🤖 Human Detection System

This project is a **real-time human detection system** built with **Python, OpenCV, Flask, and YOLOv3**.  
It captures live video from a camera, detects humans, and streams the processed frames to a web interface.

---

## 🚀 Features
- Real-time human detection using **YOLOv3**.
- Web interface powered by **Flask**.
- Displays bounding boxes and detection status.
- Provides JSON API endpoint for detection info.
- Lightweight and modular design.

---

## 🛠️ Tech Stack
- **Python 3.11**
- **Flask** (Web framework)
- **OpenCV (cv2.dnn)** (Deep learning & video capture)
- **NumPy** (Matrix operations)
- **YOLOv3** (Object detection model)

---


---

## ⚙️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Soumyajit-io/HumanDetectionSystem.git
   cd HumanDetectionSystem
2. Create a virtual environment :
3. ```bash
   python -m venv .venv
   source .venv/bin/activate   # For Linux/Mac
   .venv\Scripts\activate      # For Windows
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
5. Download YOLOv3 weights (not included in repo due to size limit):

   Official source: [YOLOv3 weights](https://pjreddie.com/media/files/yolov3.weights) (Darknet)

   Place the file in the project root directory.

---

---

## ▶️ Usage

1. Run the app:
   ```bash
   python HumanDetectionSystem.py

2. Open your browser at:
   ```bash
   http://127.0.0.1:5000/

---
