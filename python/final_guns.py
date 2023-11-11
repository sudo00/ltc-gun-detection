from collections import defaultdict
import os
import cv2
import numpy as np
from ultralytics import YOLO
import sys


# Load the YOLOv8 model
model = YOLO('./weights/yolol-cctv-1500-1cls.pt')


id = str(sys.argv[1])
video_path = '../files/videos/' + id + '.mp4'
# Open the video file
cap = cv2.VideoCapture(video_path)
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
frame_fps = int(cap.get(5))
frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
# Store the track history
track_history = defaultdict(lambda: [])
frame_count = 0 # To count total frames.

OUT_DIR = 'outputs'
os.makedirs(OUT_DIR, exist_ok=True)
name_for_video = "results.mp4"
out = cv2.VideoWriter(
    '../files/videos/' + id + "_result.mp4",
    cv2.VideoWriter_fourcc(*'mp4v'), frame_fps, 
    (frame_width, frame_height)
)
# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Run YOLOv8 tracking on the frame, persisting tracks between frames
        results = model.track(frame, persist=True, conf=0.7, device=0, augment=True, imgsz = 1088)
        frame_count+=1
        try:
            # Get the boxes and track IDs
            boxes = results[0].boxes.xywh.cpu()
            track_ids = results[0].boxes.id.int().cpu().tolist()

            # Visualize the results on the frame
            annotated_frame = results[0].plot()

            # Plot the tracks
            for box, track_id in zip(boxes, track_ids):
                x, y, w, h = box
                track = track_history[track_id]
                track.append((float(x), float(y)))  # x, y center point
                if len(track) > 30:  # retain 90 tracks for 90 frames
                    track.pop(0)

                # Draw the tracking lines
                points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
                cv2.polylines(annotated_frame, [points], isClosed=False, color=(230, 230, 230), thickness=10)

            # Display the annotated frame
            #cv2.imshow("YOLOv8 Tracking", annotated_frame)
            out.write(annotated_frame)
            img_file = id + f'_{frame_count}.jpg'
            output_frames_path = f'../files/images/{img_file}' # тут слэш для линукса
            cv2.imwrite(output_frames_path, annotated_frame)
            # Break the loop if 'q' is pressed
            #if cv2.waitKey(1) & 0xFF == ord("q"):
            #    break
        except AttributeError:
            # Display the annotated frame
            #cv2.imshow("YOLOv8 Tracking", frame)
            out.write(frame)
            # Break the loop if 'q' is pressed
            #if cv2.waitKey(1) & 0xFF == ord("q"):
            #    break
    else:
        # Break the loop if the end of the video is reached
        break

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()
