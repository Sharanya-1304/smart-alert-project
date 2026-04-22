import cv2
import numpy as np
import os
import time
import math
from ultralytics import YOLO
from alert import trigger_alert
from utils import save_evidence, log_event

PERSON_CONFIDENCE = 0.5
DISTANCE_THRESHOLD = 150
ALERT_COOLDOWN = 5

try:
    person_model = YOLO("models/yolov8n.pt")
    print("✓ YOLO person model loaded")
except:
    print("❌ YOLO model not loaded")
    person_model = None


def start_fire_detection(video_path, guardian_email=None):

    print("\n🔥 FIRE DETECTION FROM VIDEO\n")

    if not os.path.exists(video_path):
        print("❌ Video file not found:", video_path)
        return

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("❌ Cannot open video")
        return

    last_alert_time = 0
    previous_distance = None
    banner_active = False

    while True:

        ret, frame = cap.read()

        if not ret:
            print("✓ Video finished")
            break

        person_boxes = []
        fire_boxes = []
        min_distance = None

        # PERSON DETECTION
        if person_model is not None:

            results = person_model(frame)[0]

            for box in results.boxes:

                cls = int(box.cls[0])
                conf = float(box.conf[0])

                if cls == 0 and conf > PERSON_CONFIDENCE:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    person_boxes.append((x1, y1, x2, y2))

        # FIRE DETECTION
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # More specific fire colors: bright saturated reds and oranges (avoid skin tones)
        lower_fire = np.array([0, 150, 150])  # Higher saturation and brightness
        upper_fire = np.array([25, 255, 255])  # Narrower hue range

        mask = cv2.inRange(hsv, lower_fire, upper_fire)
        mask = cv2.GaussianBlur(mask,(5,5),0)

        kernel = np.ones((5,5),np.uint8)
        mask = cv2.dilate(mask,kernel,iterations=2)

        contours,_ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        for contour in contours:

            area = cv2.contourArea(contour)

            if area > 300:
                x,y,w,h = cv2.boundingRect(contour)
                fire_boxes.append((x,y,x+w,y+h))

        # DISTANCE CALCULATION
        for p in person_boxes:

            px = (p[0]+p[2])//2
            py = (p[1]+p[3])//2

            for f in fire_boxes:

                fx = (f[0]+f[2])//2
                fy = (f[1]+f[3])//2

                distance = math.sqrt((px-fx)**2 + (py-fy)**2)

                if min_distance is None or distance < min_distance:
                    min_distance = distance

        # ALERT CONDITION (PERSON COMING NEAR FIRE)

        if min_distance is not None:

            if previous_distance is not None:

                if (min_distance < previous_distance) and (min_distance < DISTANCE_THRESHOLD):

                    banner_active = True

                    if time.time() - last_alert_time > ALERT_COOLDOWN:

                        print(f"🚨 PERSON MOVING TOWARDS FIRE! Distance: {min_distance:.0f}px")

                        trigger_alert("proximity", guardian_email)
                        save_evidence(frame,"PROXIMITY")

                        log_event(
                            f"Person approaching fire distance: {min_distance:.0f}px",
                            "CRITICAL"
                        )

                        last_alert_time = time.time()

            previous_distance = min_distance

        # ALERT BANNER
        if banner_active:

            frame_height, frame_width = frame.shape[:2]

            cv2.rectangle(frame,(0,0),(frame_width,70),(0,0,255),-1)

            cv2.putText(
                frame,
                "⚠ ALERT: PERSON APPROACHING FIRE",
                (30,45),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255,255,255),
                3
            )

        cv2.imshow("Smart Fire Detection",frame)

        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()