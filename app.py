from flask import Flask, render_template, Response
import cv2
import torch
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# MySQL connection parameters
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''
MYSQL_DB = 'detections'

# Connect to MySQL
def get_mysql_connection():
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        return conn
    except Error as e:
        print("Error connecting to MySQL:", e)
        return None

# Save detection to MySQL database
def save_detection(label, action, conf, box):
    conn = get_mysql_connection()
    if conn is None:
        print("Failed to connect to MySQL database")
        return

    cursor = conn.cursor()
    query = '''
        INSERT INTO detections 
        (timestamp, object_label, action_label, confidence, bbox_xmin, bbox_ymin, bbox_xmax, bbox_ymax)
        VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s)
    '''
    data = (label, action, conf, box[0], box[1], box[2], box[3])

    try:
        cursor.execute(query, data)
        conn.commit()
    except Error as e:
        print("Failed to insert detection:", e)
    finally:
        cursor.close()
        conn.close()

# Dummy action recognition (customize as needed)
def dummy_action_recognition(object_name):
    if object_name in ['car', 'truck', 'bus']:
        return "moving"
    elif object_name == 'person':
        return "walking"
    else:
        return "static"

# Video frame generator with detection & saving to DB
def generate_frames():
    cap = cv2.VideoCapture(0)  # webcam

    while True:
        success, frame = cap.read()
        if not success:
            break

        results = model(frame)
        detections = results.xyxy[0]

        for *box, conf, cls in detections.cpu().numpy():
            xmin, ymin, xmax, ymax = map(int, box)
            confidence = float(conf)
            class_id = int(cls)
            label = model.names[class_id]
            action = dummy_action_recognition(label)

            # Save detection to MySQL
            save_detection(label, action, confidence, (xmin, ymin, xmax, ymax))

            # Draw bounding box and label
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
            text = f"{label} {action} {confidence:.2f}"
            cv2.putText(frame, text, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
