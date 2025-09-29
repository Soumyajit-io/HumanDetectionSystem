# 🛰️ Drone Controller Dashboard + Human Detection System

This project is a prototype web dashboard for controlling a drone  
and performing real-time human detection using YOLOv3 for SIH .  
It streams live video from your laptop’s webcam, detects humans,  
and displays the processed frames along with detection statistics.

## Features
- Start Stream / Stop Stream: Toggle the webcam feed.
- Detect Humans: Activate YOLOv3 detection on the live stream.
- Real-Time Status:
  • Number of humans detected  
  • Last detection time  
  • Detection on/off indicator
- Dashboard UI:
  • Drone-like interface with GPS, battery, and control buttons.  
  • Integrated alert box for detection results.

## Tech Stack
- Python 3.11  
- Flask – Web server & API  
- OpenCV (cv2.dnn) – Video capture & deep learning inference  
- NumPy – Matrix operations  
- YOLOv3 – Object detection model  
- HTML/CSS/JavaScript – Frontend dashboard

## Installation

1. Clone the repository  
   git clone: https://github.com/Soumyajit-io/Drone_Controller_Dashboard_with_Human_Detection
   

2. Create a virtual environment  
   python -m venv .venv  
   (Activate it)  
   • Linux/Mac:  source .venv/bin/activate  
   • Windows:    .venv\Scripts\activate

3. Install dependencies  
   pip install -r requirements.txt

4. Download YOLOv3 weights (not included in repo)  
   Official source: https://pjreddie.com/media/files/yolov3.weights  
   Place yolov3.weights in the project root directory.

## Usage

1. Run the Flask server  
   HumanDetectionSystem.py

2. Open your browser and navigate to  
   http://127.0.0.1:5000/
