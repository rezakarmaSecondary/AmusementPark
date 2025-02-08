from ultralytics import YOLO
import cv2

model = YOLO("../best.pt")  # Replace with your trained model

def detect_persons_in_frame(frame, bbox_coordinates: dict) -> int:
    # Convert normalized coordinates to pixels
    h, w = frame.shape[:2]
    x1 = int(bbox_coordinates["x1"] * w)
    y1 = int(bbox_coordinates["y1"] * h)
    x2 = int(bbox_coordinates["x2"] * w)
    y2 = int(bbox_coordinates["y2"] * h)

    # Crop and detect
    cropped = frame[y1:y2, x1:x2]
    results = model(cropped)
    return sum(1 for box in results[0].boxes if box.cls == 0)  # Class 0 = person

