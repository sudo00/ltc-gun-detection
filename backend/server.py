import os
from flask import Flask, flash, request, redirect, url_for
from flask import send_from_directory
from werkzeug.utils import secure_filename
import db
import json
from pathlib import Path
from subprocess import Popen
from flask_cors import CORS, cross_origin
from flask import send_file

from flask import Flask, Response
import cv2
import sys

UPLOAD_VIDEO_FOLDER = '../files/videos'
UPLOAD_IMAGE_FOLDER = '/files/images'
YOLA='final_guns.py'
ALLOWED_EXTENSIONS = {'mp4'}

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['UPLOAD_VIDEO_FOLDER'] = UPLOAD_VIDEO_FOLDER
app.config['UPLOAD_IMAGE_FOLDER'] = UPLOAD_IMAGE_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1000 * 1000
# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/detection-source/file', methods=['POST'])
@cross_origin()
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'UploadForm[video]' not in request.files:
            flash('No file part')
            return 'No file part'

        file = request.files['UploadForm[video]']
        if file and allowed_file(file.filename):
            id = db.create()
            file.save(os.path.join(app.config['UPLOAD_VIDEO_FOLDER'], id + ".mp4"))
            responseData = {"id": id}
            response = app.response_class(
                response=json.dumps(responseData),
                status=200,
                mimetype='application/json'
            )
#            Popen(['python3', YOLA, id], cwd='../python/') # something long running
            return response

@app.route('/detection-source/get', methods=['GET'])
@cross_origin()
def download_file():
    responseData = []
    id = request.args.get('id')

    for path in Path('..' + app.config["UPLOAD_IMAGE_FOLDER"]).glob(str(id) + "_*.jpg"):        
        frame = str(path).split("_")[1].split('.jpg')[0] 
        responseData.append({'url': str(path)[2:], 'frame': int(frame)})

    responseData = sorted(responseData, key=lambda x: x['frame'], reverse=True)
    
    uuid = 1
    for data in responseData:        
        data['id'] = uuid
        uuid += 1

    response = app.response_class(
        response=json.dumps(responseData),
        status=200,
        mimetype='application/json'
    )
    return response
        

@app.route('/files/images/<filename>')
@cross_origin()
def get_image(filename):
    return send_file('..' + app.config["UPLOAD_IMAGE_FOLDER"] + "/" + filename, mimetype='image/jpg')



def gen_frames():
    cap = cv2.VideoCapture('../files/videos/1.mp4')
    while True:
        success, frame = cap.read()
        if not success:
            break
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
@cross_origin()
def video_feed():
    id = request.args.get('id')
    return Response(gen_frames_1(str(id)), mimetype='multipart/x-mixed-replace; boundary=frame')



from collections import defaultdict
import os
import cv2
import numpy as np

from ultralytics import YOLO

def gen_frames_1(id):
        # Load the YOLOv8 model
        model = YOLO('../python/weights/yolol-cctv-1500-1cls.pt')

        # Open the video file

        #id = '1'#str(sys.argv[1])
        video_path = '../files/videos/' + id + '.mp4'
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
                    ret, buffer = cv2.imencode('.jpg', annotated_frame)
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

                    # Break the loop if 'q' is pressed
                    #if cv2.waitKey(1) & 0xFF == ord("q"):
                    #    break
                except AttributeError:
                    # Display the annotated frame
                    #cv2.imshow("YOLOv8 Tracking", frame)
                    out.write(frame)
                    ret, buffer = cv2.imencode('.jpg', frame)
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

                    # Break the loop if 'q' is pressed
                    #if cv2.waitKey(1) & 0xFF == ord("q"):
                    #    break
            else:
                # Break the loop if the end of the video is reached
                break

        # Release the video capture object and close the display window
        cap.release()
        cv2.destroyAllWindows()






if __name__ == "__main__":
    app.run('92.53.64.152', '3000')
