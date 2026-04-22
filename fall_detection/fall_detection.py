"""
Smart Fall Detection Module - AI-Powered Decision Making
Uses machine learning-inspired approach to detect falls by analyzing:
1. Body angle and orientation
2. Rate of change (angular velocity)
3. Trend analysis over time
4. Multiple confirmation criteria

Designed for real-world scenarios including wheelchair falls
"""

import cv2
import os
import time
import math
import numpy as np
from collections import deque
from ultralytics import YOLO
from alert import trigger_alert
from utils import save_evidence, log_event


class SmartFallDetector:
    """
    AI-inspired fall detection using multi-criteria analysis
    Makes autonomous decisions based on pattern recognition
    """

    def __init__(self):
        # Pose keypoint indices (COCO format)
        self.NOSE = 0
        self.LEFT_EYE = 1
        self.RIGHT_EYE = 2
        self.LEFT_EAR = 3
        self.RIGHT_EAR = 4
        self.LEFT_SHOULDER = 5
        self.RIGHT_SHOULDER = 6
        self.LEFT_ELBOW = 7
        self.RIGHT_ELBOW = 8
        self.LEFT_WRIST = 9
        self.RIGHT_WRIST = 10
        self.LEFT_HIP = 11
        self.RIGHT_HIP = 12
        self.LEFT_KNEE = 13
        self.RIGHT_KNEE = 14
        self.LEFT_ANKLE = 15
        self.RIGHT_ANKLE = 16

        # ========== HISTORY TRACKING FOR TREND ANALYSIS ==========
        self.spine_angle_history = deque(maxlen=60)     # Track angles over time
        self.torso_angle_history = deque(maxlen=60)
        self.ratio_history = deque(maxlen=60)           # W/H ratio history
        self.centroid_y_history = deque(maxlen=60)      # Vertical position
        self.head_y_history = deque(maxlen=60)          # Head position

        # Baseline values (first few frames establish "normal")
        self.baseline_spine_angle = None
        self.baseline_torso_angle = None
        self.baseline_ratio = None
        self.baseline_head_y = None
        self.baseline_frames_collected = 0
        self.baseline_established = False

        # ========== SMART THRESHOLDS (Relative to baseline) ==========
        # Instead of absolute thresholds, use relative changes
        self.ANGLE_CHANGE_WARNING = 8       # 8+ degree increase from baseline
        self.ANGLE_CHANGE_ALERT = 12        # 12+ degree increase = likely fall
        self.ANGLE_CHANGE_CRITICAL = 18     # 18+ degree increase = definite fall

        self.RATIO_CHANGE_WARNING = 0.15    # 15% increase in W/H ratio
        self.RATIO_CHANGE_ALERT = 0.25      # 25% increase
        self.RATIO_CHANGE_CRITICAL = 0.40   # 40% increase

        self.ANGULAR_VELOCITY_WARNING = 1.5  # Degrees per frame
        self.ANGULAR_VELOCITY_ALERT = 3.0
        self.ANGULAR_VELOCITY_CRITICAL = 5.0

        # Absolute thresholds (for already-fallen detection)
        self.ABSOLUTE_ANGLE_LYING = 45      # Person already horizontal
        self.ABSOLUTE_RATIO_LYING = 0.9     # Width >= 90% of height

        # ========== DETECTION STATE ==========
        self.fall_score = 0.0               # Cumulative fall probability
        self.fall_detected = False
        self.detection_reasons = []
        self.frames_analyzed = 0

    def get_keypoint(self, person, idx):
        """Safely get keypoint coordinates"""
        if len(person) > idx:
            x, y = float(person[idx][0]), float(person[idx][1])
            if x > 0 and y > 0:
                return (x, y)
        return None

    def calculate_angle_from_vertical(self, p1, p2):
        """Calculate angle from vertical axis (0 = upright, 90 = horizontal)"""
        if p1 is None or p2 is None:
            return None
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        if abs(dy) < 1:
            return 90  # Horizontal
        angle = abs(math.degrees(math.atan2(abs(dx), abs(dy))))
        return angle

    def get_body_metrics(self, person, frame_shape):
        """Extract all relevant body metrics from pose keypoints"""
        metrics = {
            'spine_angle': None,
            'torso_angle': None,
            'head_y': None,
            'hip_y': None,
            'width_height_ratio': None,
            'centroid_y': None,
            'valid': False
        }

        # Get keypoints
        nose = self.get_keypoint(person, self.NOSE)
        left_eye = self.get_keypoint(person, self.LEFT_EYE)
        right_eye = self.get_keypoint(person, self.RIGHT_EYE)
        left_shoulder = self.get_keypoint(person, self.LEFT_SHOULDER)
        right_shoulder = self.get_keypoint(person, self.RIGHT_SHOULDER)
        left_hip = self.get_keypoint(person, self.LEFT_HIP)
        right_hip = self.get_keypoint(person, self.RIGHT_HIP)

        # Calculate head position
        head = nose
        if head is None and left_eye and right_eye:
            head = ((left_eye[0] + right_eye[0]) / 2, (left_eye[1] + right_eye[1]) / 2)

        # Calculate shoulder midpoint
        shoulder_mid = None
        if left_shoulder and right_shoulder:
            shoulder_mid = ((left_shoulder[0] + right_shoulder[0]) / 2,
                           (left_shoulder[1] + right_shoulder[1]) / 2)
        elif left_shoulder:
            shoulder_mid = left_shoulder
        elif right_shoulder:
            shoulder_mid = right_shoulder

        # Calculate hip midpoint
        hip_mid = None
        if left_hip and right_hip:
            hip_mid = ((left_hip[0] + right_hip[0]) / 2,
                      (left_hip[1] + right_hip[1]) / 2)
        elif left_hip:
            hip_mid = left_hip
        elif right_hip:
            hip_mid = right_hip

        # Calculate spine angle (head to hip)
        if head and hip_mid:
            metrics['spine_angle'] = self.calculate_angle_from_vertical(hip_mid, head)
            metrics['head_y'] = head[1]
            metrics['hip_y'] = hip_mid[1]

        # Calculate torso angle (shoulder to hip)
        if shoulder_mid and hip_mid:
            metrics['torso_angle'] = self.calculate_angle_from_vertical(hip_mid, shoulder_mid)

        # Calculate width/height ratio
        y_coords = [float(person[i][1]) for i in range(len(person)) if float(person[i][1]) > 0]
        x_coords = [float(person[i][0]) for i in range(len(person)) if float(person[i][0]) > 0]

        if len(y_coords) >= 5 and len(x_coords) >= 5:
            height = max(y_coords) - min(y_coords)
            width = max(x_coords) - min(x_coords)
            if height > 15:
                metrics['width_height_ratio'] = width / height
                metrics['centroid_y'] = sum(y_coords) / len(y_coords)
                metrics['valid'] = True

        return metrics

    def establish_baseline(self, metrics):
        """Establish baseline from first few frames (person's normal posture)"""
        if self.baseline_established:
            return

        if not metrics['valid']:
            return

        self.baseline_frames_collected += 1

        # Accumulate baseline values
        if metrics['spine_angle'] is not None:
            if self.baseline_spine_angle is None:
                self.baseline_spine_angle = metrics['spine_angle']
            else:
                self.baseline_spine_angle = (self.baseline_spine_angle + metrics['spine_angle']) / 2

        if metrics['torso_angle'] is not None:
            if self.baseline_torso_angle is None:
                self.baseline_torso_angle = metrics['torso_angle']
            else:
                self.baseline_torso_angle = (self.baseline_torso_angle + metrics['torso_angle']) / 2

        if metrics['width_height_ratio'] is not None:
            if self.baseline_ratio is None:
                self.baseline_ratio = metrics['width_height_ratio']
            else:
                self.baseline_ratio = (self.baseline_ratio + metrics['width_height_ratio']) / 2

        if metrics['head_y'] is not None:
            if self.baseline_head_y is None:
                self.baseline_head_y = metrics['head_y']
            else:
                self.baseline_head_y = (self.baseline_head_y + metrics['head_y']) / 2

        # Establish baseline after 5 frames
        if self.baseline_frames_collected >= 5:
            self.baseline_established = True

    def calculate_trend(self, history, window=10):
        """Calculate trend (slope) of recent values"""
        if len(history) < window:
            return 0

        recent = list(history)[-window:]
        valid = [v for v in recent if v is not None]

        if len(valid) < 3:
            return 0

        # Simple linear regression
        n = len(valid)
        x = list(range(n))
        y = valid

        x_mean = sum(x) / n
        y_mean = sum(y) / n

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0

        slope = numerator / denominator
        return slope

    def calculate_angular_velocity(self, history):
        """Calculate rate of angle change"""
        if len(history) < 2:
            return 0

        valid = [(i, v) for i, v in enumerate(history) if v is not None]
        if len(valid) < 2:
            return 0

        # Use last two valid values
        _, v1 = valid[-2]
        _, v2 = valid[-1]

        return abs(v2 - v1)

    def detect_fall(self, person, frame_shape):
        """
        SMART FALL DETECTION - Makes autonomous decisions
        Uses multiple criteria and trend analysis
        """
        self.frames_analyzed += 1
        debug_info = {}
        self.detection_reasons = []

        # Get body metrics
        metrics = self.get_body_metrics(person, frame_shape)

        if not metrics['valid']:
            debug_info['error'] = 'Invalid metrics'
            return False, 0.0, debug_info

        # Establish baseline from first few frames
        if not self.baseline_established:
            self.establish_baseline(metrics)
            debug_info['status'] = 'Establishing baseline...'
            return False, 0.0, debug_info

        # Store in history
        self.spine_angle_history.append(metrics['spine_angle'])
        self.torso_angle_history.append(metrics['torso_angle'])
        self.ratio_history.append(metrics['width_height_ratio'])
        self.head_y_history.append(metrics['head_y'])
        self.centroid_y_history.append(metrics['centroid_y'])

        # ========== ANALYSIS ==========
        fall_score = 0.0

        # 1. ANGLE CHANGE FROM BASELINE
        spine_change = 0
        if metrics['spine_angle'] is not None and self.baseline_spine_angle is not None:
            spine_change = metrics['spine_angle'] - self.baseline_spine_angle
            debug_info['spine_angle'] = metrics['spine_angle']
            debug_info['spine_change'] = spine_change

            if spine_change >= self.ANGLE_CHANGE_CRITICAL:
                fall_score += 0.35
                self.detection_reasons.append(f'CRITICAL_ANGLE_CHANGE:{spine_change:.1f}')
            elif spine_change >= self.ANGLE_CHANGE_ALERT:
                fall_score += 0.25
                self.detection_reasons.append(f'ALERT_ANGLE_CHANGE:{spine_change:.1f}')
            elif spine_change >= self.ANGLE_CHANGE_WARNING:
                fall_score += 0.15
                self.detection_reasons.append(f'WARNING_ANGLE:{spine_change:.1f}')

        torso_change = 0
        if metrics['torso_angle'] is not None and self.baseline_torso_angle is not None:
            torso_change = metrics['torso_angle'] - self.baseline_torso_angle
            debug_info['torso_angle'] = metrics['torso_angle']
            debug_info['torso_change'] = torso_change

            if torso_change >= self.ANGLE_CHANGE_CRITICAL:
                fall_score += 0.30
            elif torso_change >= self.ANGLE_CHANGE_ALERT:
                fall_score += 0.20
            elif torso_change >= self.ANGLE_CHANGE_WARNING:
                fall_score += 0.10

        # 2. W/H RATIO CHANGE
        ratio_change = 0
        if metrics['width_height_ratio'] is not None and self.baseline_ratio is not None:
            ratio_change = metrics['width_height_ratio'] - self.baseline_ratio
            debug_info['ratio'] = metrics['width_height_ratio']
            debug_info['ratio_change'] = ratio_change

            if ratio_change >= self.RATIO_CHANGE_CRITICAL:
                fall_score += 0.30
                self.detection_reasons.append(f'CRITICAL_RATIO:{ratio_change:.2f}')
            elif ratio_change >= self.RATIO_CHANGE_ALERT:
                fall_score += 0.20
                self.detection_reasons.append(f'ALERT_RATIO:{ratio_change:.2f}')
            elif ratio_change >= self.RATIO_CHANGE_WARNING:
                fall_score += 0.10

        # 3. ANGULAR VELOCITY (Rate of tilt change)
        spine_velocity = self.calculate_angular_velocity(self.spine_angle_history)
        torso_velocity = self.calculate_angular_velocity(self.torso_angle_history)
        max_velocity = max(spine_velocity, torso_velocity)
        debug_info['angular_velocity'] = max_velocity

        if max_velocity >= self.ANGULAR_VELOCITY_CRITICAL:
            fall_score += 0.30
            self.detection_reasons.append(f'RAPID_TILT:{max_velocity:.1f}')
        elif max_velocity >= self.ANGULAR_VELOCITY_ALERT:
            fall_score += 0.20
            self.detection_reasons.append(f'FAST_TILT:{max_velocity:.1f}')
        elif max_velocity >= self.ANGULAR_VELOCITY_WARNING:
            fall_score += 0.10

        # 4. TREND ANALYSIS (Is angle consistently increasing?)
        spine_trend = self.calculate_trend(self.spine_angle_history, window=8)
        ratio_trend = self.calculate_trend(self.ratio_history, window=8)
        debug_info['spine_trend'] = spine_trend
        debug_info['ratio_trend'] = ratio_trend

        # Positive trend = angles/ratios increasing = falling
        if spine_trend > 0.8:
            fall_score += 0.25
            self.detection_reasons.append('FALLING_TREND')
        elif spine_trend > 0.5:
            fall_score += 0.15
        elif spine_trend > 0.3:
            fall_score += 0.08

        if ratio_trend > 0.03:
            fall_score += 0.15
        elif ratio_trend > 0.02:
            fall_score += 0.10

        # 5. ABSOLUTE POSITION CHECK (Already fallen)
        if metrics['spine_angle'] is not None and metrics['spine_angle'] >= self.ABSOLUTE_ANGLE_LYING:
            fall_score += 0.35
            self.detection_reasons.append(f'LYING_ANGLE:{metrics["spine_angle"]:.1f}')

        if metrics['width_height_ratio'] is not None and metrics['width_height_ratio'] >= self.ABSOLUTE_RATIO_LYING:
            fall_score += 0.30
            self.detection_reasons.append(f'LYING_RATIO:{metrics["width_height_ratio"]:.2f}')

        # 6. HEAD DROPPING CHECK
        if metrics['head_y'] is not None and self.baseline_head_y is not None:
            head_drop = metrics['head_y'] - self.baseline_head_y
            debug_info['head_drop'] = head_drop

            # Positive head_drop means head moved DOWN in frame (falling)
            if head_drop > 50:
                fall_score += 0.20
                self.detection_reasons.append(f'HEAD_DROP:{head_drop:.0f}px')
            elif head_drop > 30:
                fall_score += 0.10

        # 7. COMBINED CHANGE CHECK (Multiple indicators changing together)
        if (spine_change >= self.ANGLE_CHANGE_WARNING and
            ratio_change >= self.RATIO_CHANGE_WARNING):
            # Both angle and ratio changing = strong fall indicator
            fall_score += 0.15
            self.detection_reasons.append('COMBINED_CHANGE')

        # ========== DECISION ==========
        debug_info['fall_score'] = fall_score
        debug_info['reasons'] = self.detection_reasons.copy()

        # Accumulate score over frames
        self.fall_score = self.fall_score * 0.7 + fall_score * 0.3  # Weighted average
        debug_info['cumulative_score'] = self.fall_score

        # FALL DETECTION DECISION
        fall_detected = False

        # Immediate detection for high scores
        if fall_score >= 0.60:
            fall_detected = True
            debug_info['decision'] = 'HIGH_SCORE_IMMEDIATE'

        # Detection for medium score with good reasons
        elif fall_score >= 0.40 and len(self.detection_reasons) >= 2:
            fall_detected = True
            debug_info['decision'] = 'MEDIUM_SCORE_MULTI_REASON'

        # Detection for consistent falling pattern
        elif self.fall_score >= 0.35 and spine_trend > 0.3:
            fall_detected = True
            debug_info['decision'] = 'CONSISTENT_FALL_PATTERN'

        # Detection for absolute lying position
        elif (metrics['spine_angle'] and metrics['spine_angle'] >= 40 and
              metrics['width_height_ratio'] and metrics['width_height_ratio'] >= 0.8):
            fall_detected = True
            debug_info['decision'] = 'LYING_POSITION'

        # Detection for significant combined changes
        elif (spine_change >= 10 and ratio_change >= 0.20):
            fall_detected = True
            debug_info['decision'] = 'SIGNIFICANT_COMBINED_CHANGE'

        debug_info['fall_detected'] = fall_detected

        if fall_detected:
            self.fall_detected = True

        return fall_detected, fall_score, debug_info


def start_fall_detection(video_path, guardian_email=None):
    """
    Main fall detection function with smart AI-powered detection
    """
    print("\n" + "="*60)
    print("SMART FALL DETECTION SYSTEM")
    print("AI-Powered Autonomous Decision Making")
    print("="*60)

    if not os.path.exists(video_path):
        print("Video file not found:", video_path)
        return

    # Load pose model
    try:
        model_paths = [
            "models/yolov8n-pose.pt",
            "yolov8n-pose.pt",
            os.path.join(os.path.dirname(__file__), "..", "models", "yolov8n-pose.pt"),
            os.path.join(os.path.dirname(__file__), "..", "yolov8n-pose.pt")
        ]

        model = None
        for path in model_paths:
            if os.path.exists(path):
                model = YOLO(path)
                print(f"Pose model loaded from: {path}")
                break

        if model is None:
            model = YOLO("yolov8n-pose.pt")
            print("Pose model downloaded")

    except Exception as e:
        print("Could not load pose model:", e)
        return

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Cannot open video:", video_path)
        return

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0

    print(f"Video: {fps:.1f} FPS, {total_frames} frames, {duration:.1f} seconds")

    # Initialize smart detector
    detector = SmartFallDetector()

    # Alert state
    alert_triggered = False
    banner_frame_count = 0
    banner_duration = int(fps * 5) if fps > 0 else 150
    pause_start_time = None
    pause_duration = 3

    frame_number = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Video finished")
            break

        frame_number += 1
        fall_detected_this_frame = False
        debug_info = {}

        try:
            results = model(frame, verbose=False)

            for r in results:
                if r.keypoints is None:
                    continue

                persons = r.keypoints.xy

                for person in persons:
                    if len(person) < 12:
                        continue

                    # Run smart fall detection
                    is_fall, score, debug_info = detector.detect_fall(person, frame.shape)

                    if is_fall:
                        fall_detected_this_frame = True

                    # Draw debug info
                    y_offset = 30

                    # Baseline status
                    if not detector.baseline_established:
                        cv2.putText(frame, "Establishing baseline...", (10, y_offset),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                        y_offset += 25
                    else:
                        # Spine angle change
                        if 'spine_change' in debug_info:
                            change = debug_info['spine_change']
                            color = (0, 0, 255) if change >= 12 else (0, 255, 255) if change >= 8 else (0, 255, 0)
                            cv2.putText(frame, f"Angle Change: {change:.1f}deg", (10, y_offset),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                            y_offset += 25

                        # Ratio change
                        if 'ratio_change' in debug_info:
                            change = debug_info['ratio_change']
                            color = (0, 0, 255) if change >= 0.25 else (0, 255, 255) if change >= 0.15 else (0, 255, 0)
                            cv2.putText(frame, f"Ratio Change: {change:.2f}", (10, y_offset),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                            y_offset += 25

                        # Angular velocity
                        if 'angular_velocity' in debug_info:
                            vel = debug_info['angular_velocity']
                            color = (0, 0, 255) if vel >= 3 else (0, 255, 255) if vel >= 1.5 else (0, 255, 0)
                            cv2.putText(frame, f"Tilt Rate: {vel:.1f}deg/f", (10, y_offset),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                            y_offset += 25

                        # Trend
                        if 'spine_trend' in debug_info:
                            trend = debug_info['spine_trend']
                            trend_text = "FALLING" if trend > 0.5 else "TILTING" if trend > 0.3 else "STABLE"
                            color = (0, 0, 255) if trend > 0.5 else (0, 255, 255) if trend > 0.3 else (0, 255, 0)
                            cv2.putText(frame, f"Trend: {trend_text}", (10, y_offset),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                            y_offset += 25

                        # Fall score
                        if 'fall_score' in debug_info:
                            score = debug_info['fall_score']
                            color = (0, 0, 255) if score >= 0.4 else (0, 255, 255) if score >= 0.2 else (0, 255, 0)
                            cv2.putText(frame, f"Fall Score: {score:.0%}", (10, y_offset),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                            y_offset += 25

                        # Detection reasons
                        if 'reasons' in debug_info and debug_info['reasons']:
                            reasons_text = " | ".join(debug_info['reasons'][:3])
                            cv2.putText(frame, reasons_text, (10, y_offset),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 165, 0), 1)
                            y_offset += 20

                    # Draw skeleton
                    skeleton_connections = [
                        (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),
                        (5, 11), (6, 12), (11, 12),
                        (11, 13), (13, 15), (12, 14), (14, 16),
                        (0, 5), (0, 6)
                    ]

                    for p1_idx, p2_idx in skeleton_connections:
                        if p1_idx < len(person) and p2_idx < len(person):
                            p1 = person[p1_idx]
                            p2 = person[p2_idx]
                            if p1[0] > 0 and p1[1] > 0 and p2[0] > 0 and p2[1] > 0:
                                color = (0, 0, 255) if is_fall else (0, 255, 0)
                                cv2.line(frame,
                                        (int(p1[0]), int(p1[1])),
                                        (int(p2[0]), int(p2[1])),
                                        color, 2)

        except Exception as e:
            print(f"Processing error (frame {frame_number}): {e}")

        # TRIGGER ALERT
        if fall_detected_this_frame and not alert_triggered:
            print(f"\n{'='*50}")
            print("FALL DETECTED!")
            print(f"Frame: {frame_number} / {total_frames}")
            print(f"Score: {debug_info.get('fall_score', 0):.0%}")
            print(f"Decision: {debug_info.get('decision', 'Unknown')}")
            print(f"Reasons: {', '.join(debug_info.get('reasons', ['Unknown']))}")
            print(f"{'='*50}\n")

            trigger_alert("fall", guardian_email)
            save_evidence(frame, "FALL")
            log_event("Fall detected - Smart AI Detection", "CRITICAL")

            alert_triggered = True
            banner_frame_count = 0
            pause_start_time = time.time()

        # WARNING BANNER
        if alert_triggered and banner_frame_count < banner_duration:
            frame_height, frame_width = frame.shape[:2]

            cv2.rectangle(frame, (0, 0), (frame_width, 100), (0, 0, 255), -1)

            cv2.putText(frame,
                       "WARNING: FALL DETECTED!",
                       (30, 50),
                       cv2.FONT_HERSHEY_SIMPLEX,
                       1.2,
                       (255, 255, 255),
                       3)

            cv2.putText(frame,
                       "ALERT SENT TO CAREGIVER",
                       (30, 90),
                       cv2.FONT_HERSHEY_SIMPLEX,
                       0.8,
                       (255, 255, 255),
                       2)

            banner_frame_count += 1

        # Show frame number
        cv2.putText(frame,
                   f"Frame: {frame_number}/{total_frames}",
                   (frame.shape[1] - 180, 30),
                   cv2.FONT_HERSHEY_SIMPLEX,
                   0.5,
                   (255, 255, 255),
                   1)

        cv2.imshow("Smart Fall Detection", frame)

        # Pause video when fall detected
        if pause_start_time is not None:
            elapsed = time.time() - pause_start_time
            if elapsed < pause_duration:
                time.sleep(0.1)
                cv2.imshow("Smart Fall Detection", frame)
            else:
                pause_start_time = None

        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # Summary
    print("\n" + "="*60)
    print("DETECTION SUMMARY")
    print("="*60)
    print(f"Frames processed: {frame_number}")
    print(f"Fall detected: {'YES' if alert_triggered else 'NO'}")
    if detector.baseline_established:
        print(f"Baseline spine angle: {detector.baseline_spine_angle:.1f}deg")
        print(f"Baseline W/H ratio: {detector.baseline_ratio:.2f}")
    print("="*60)
