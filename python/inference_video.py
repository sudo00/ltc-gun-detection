from ultralytics import YOLO
import cv2
import os
import torch
import sys

# setting device on GPU if available, else CPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print('Using device:', device)
print()

#Additional Info when using cuda
if device.type == 'cuda':
    print(torch.cuda.get_device_name(0))
    print('Memory Usage:')
    print('Allocated:', round(torch.cuda.memory_allocated(0)/1024**3,1), 'GB')
    print('Cached:   ', round(torch.cuda.memory_reserved(0)/1024**3,1), 'GB')


class YOLOModel:
    def __init__(self, weights_path: str, confidence=0.5, device: str = 'cpu'):
        self.device = device
        self.model = YOLO(weights_path)
        self.confidence=confidence


    def inference_video(self, source, output_frames_folder, output_txt_folder, videoId):
        # Load video
        cap = cv2.VideoCapture(source)
        # Loop through the video frames
        while cap.isOpened():
            # Read a frame from the video
            success, frame = cap.read()
            if success:
                # Run YOLOv8 inference on the frames
                results = self.model.predict(source,
                              conf=self.confidence,
                              device=self.device,
                              stream=True,
                              augment=True,
                              verbose=True)

                # For count frames
                frame_num = 0

                # For each frame
                for res in results:
                    labels =  res.boxes.cls.cpu().numpy()
                    scores  =  res.boxes.conf.cpu().numpy()
                    boxes   =  res.boxes.xyxy.cpu().numpy()


                    # print(labels, scores, boxes)
                    annotated_frame = res.plot()

                    # Make paths
                    txt_file = f'{videoId}_{frame_num}.txt'
                    output_txt_path = os.path.join(output_txt_folder, txt_file)

                    img_file = f'{videoId}_{frame_num}.jpg'
                    output_frames_path = os.path.join(output_frames_folder, img_file)

                    # If object detected, make txt file with and save image with bboxes
                    if labels.size > 0:
                        formatted = []
                        for label, score, bbox in zip(labels, scores, boxes):
                            label = int(label)
                            score = round(float(score), 4)
                            xmin, ymin, xmax, ymax = map(int, bbox)

                            line = f"{label} {score} {xmin} {ymin} {xmax} {ymax}"
                            formatted.append(line)
                        with open(output_txt_path, 'w') as f:
                            for obj in formatted:
                                f.write(obj)

                        cv2.imwrite(output_frames_path, annotated_frame)

                    frame_num += 1 
                break

            else:
                # Break the loop if the end of the video is reached
                break
        pass


model = YOLOModel(
    weights_path='weights/yolol-cctv-1500-1cls.pt',
    confidence = 0.7,
    device=0 #"cpu"
)


def main():

    id = sys.argv[1]
    input_folder = '../files/videos/' + str(id) + '.mp4'
    output_frames_folder = "../files/images"
    output_txt_folder = "detected/detected_txt"

    model.inference_video(input_folder, output_frames_folder, output_txt_folder, sys.argv[1])




if __name__ == '__main__':
    main()
