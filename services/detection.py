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


from deep_sort_realtime.deepsort_tracker import DeepSort

tracker = DeepSort(max_age=30)  # Adjust parameters

def detect_and_track(frame, bbox_coords):
    h, w = frame.shape[:2]
    x1 = int(bbox_coords["x1"] * w)
    y1 = int(bbox_coords["y1"] * h)
    x2 = int(bbox_coords["x2"] * w)
    y2 = int(bbox_coords["y2"] * h)
    cropped = frame[y1:y2, x1:x2]

    # YOLO Detection
    results = model(cropped)
    detections = []
    for result in results:
        for box in result.boxes:
            if box.cls == 0:  # Person class
                conf = box.conf.item()
                xyxy = box.xyxy[0].tolist()
                detections.append((xyxy, conf, 'person'))

    # DeepSORT Tracking
    tracks = tracker.update_tracks(detections, frame=cropped)
    return tracks