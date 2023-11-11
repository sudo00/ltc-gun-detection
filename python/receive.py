import pika, sys, os
from inference_video import YOLOModel
from phpserialize import *
import torch

print(torch.cuda.is_available())
exit()


model = YOLOModel(
    weights_path='weights/yolol-cctv-1500-1cls.pt',
    confidence = 0.7,
    device=0 #"cpu"
)

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='create')

    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")
        videoId = str(unserialize(body)[b'id'])
        
        print(videoId)

        input_file =  "../www/yii-project/web/uploads/videos/" + videoId + '.mp4'
        output_frames_folder = "../www/yii-project/web/uploads/images/"
        output_txt_folder = "detected/detected_txt"

        model.inference_video(input_file, output_frames_folder, output_txt_folder, videoId)

    channel.basic_consume(queue='create', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
