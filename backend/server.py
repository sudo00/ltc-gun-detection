import os
import db
import json
from pathlib import Path

import cv2
from ultralytics import YOLO
from collections import defaultdict
import numpy as np

from flask import Flask, flash, request, Response, send_file
from flask_cors import CORS, cross_origin



UPLOAD_VIDEO_FOLDER = "../files/videos"
UPLOAD_IMAGE_FOLDER = "../files/images"
YOLA = "final_guns.py"
ALLOWED_EXTENSIONS = {"mp4"}

app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"
app.config["UPLOAD_VIDEO_FOLDER"] = UPLOAD_VIDEO_FOLDER
app.config["UPLOAD_IMAGE_FOLDER"] = UPLOAD_IMAGE_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 500 * 1000 * 1000  # 500 Mb
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


# Проверка расширения файла
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Загрузка файла на сервер
@app.route("/detection-source/file", methods=["POST"])
@cross_origin()
def upload_file():
    if "UploadForm[video]" not in request.files:
        return "No file part"

    file = request.files["UploadForm[video]"]
    if file and allowed_file(file.filename):
        id = db.create()
        file.save(os.path.join(app.config["UPLOAD_VIDEO_FOLDER"], id + ".mp4"))
        responseData = {"id": id}
        response = app.response_class(
            response=json.dumps(responseData), status=200, mimetype="application/json"
        )
        return response


# Отправка картинок по id видео
@app.route("/detection-source/get", methods=["GET"])
@cross_origin()
def download_file():
    responseData = []
    id = request.args.get("id")
    for path in Path(app.config["UPLOAD_IMAGE_FOLDER"]).glob(str(id) + "_*.jpg"):
        frame = str(path).split("_")[1].split(".jpg")[0]
        responseData.append({"url": str(path)[2:], "frame": int(frame)})
    responseData = sorted(responseData, key=lambda x: x["frame"], reverse=True)

    uuid = 1
    for data in responseData:
        data["id"] = uuid
        uuid += 1

    response = app.response_class(
        response=json.dumps(responseData), status=200, mimetype="application/json"
    )
    return response


# Вывод изображения по имени
@app.route("/files/images/<filename>")
@cross_origin()
def get_image(filename):
    return send_file(
        app.config["UPLOAD_IMAGE_FOLDER"] + "/" + filename, mimetype="image/jpg"
    )


# Работа нейросети, отправка потока кадров
@app.route("/video_feed")
@cross_origin()
def video_feed():
    id = request.args.get("id")
    return Response(
        gen_frames(str(id)), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# Нейроночка
def gen_frames(id):
    # Load the YOLOv8 model
    model = YOLO("./weights/yolol-cctv-1500-1cls.pt")

    # Open the video file
    video_path = "../files/videos/" + id + ".mp4"
    cap = cv2.VideoCapture(video_path)
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    frame_fps = int(cap.get(5))
    # Store the track history
    track_history = defaultdict(lambda: [])
    frame_count = 0  # To count total frames.

    OUT_DIR = "outputs"
    os.makedirs(OUT_DIR, exist_ok=True)
    out = cv2.VideoWriter(
        "../files/videos/" + id + "_result.mp4",
        cv2.VideoWriter_fourcc(*"mp4v"),
        frame_fps,
        (frame_width, frame_height),
    )
    # Loop through the video frames
    while cap.isOpened():
        # Read a frame from the video
        success, frame = cap.read()

        if success:
            # Run YOLOv8 tracking on the frame, persisting tracks between frames
            results = model.track(
                frame, persist=True, conf=0.7, device=0, augment=True, imgsz=1088
            )

            frame_count += 1
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
                    cv2.polylines(
                        annotated_frame,
                        [points],
                        isClosed=False,
                        color=(230, 230, 230),
                        thickness=10,
                    )

                # Display the annotated frame
                out.write(annotated_frame)
                img_file = id + f"_{frame_count}.jpg"
                output_frames_path = (
                    f"../files/images/{img_file}"
                )
                cv2.imwrite(output_frames_path, annotated_frame)
                ret, buffer = cv2.imencode(".jpg", annotated_frame)
                frame = buffer.tobytes()
                yield (
                    b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                )
            except AttributeError:
                # Display the annotated frame
                out.write(frame)
                ret, buffer = cv2.imencode(".jpg", frame)
                frame = buffer.tobytes()
                yield (
                    b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                )
        else:
            # Break the loop if the end of the video is reached
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    app.run("ltc-gun-detection.ru", "3000")
