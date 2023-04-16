import cv2
import mediapipe as mp
from flask import Flask, Response, render_template
from pygame import mixer 

mixer.init() 
# mixer.music.load('./assets/Alert Siren Sound FX.mp3')

app = Flask(__name__)
mp_pose = mp.solutions.pose
cap = cv2.VideoCapture(0)

#colors here 
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

human_count = 0
human_detected = False
#main function li besh ngenerati beha el skeleton ta3 el personnel 
def generate():
    global human_count
    global human_detected
    active = True 
    while active:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)

        # Convert the frame to RGB for use with Mediapipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        with mp_pose.Pose(min_detection_confidence=0.3, min_tracking_confidence=0.3) as pose:
            results = pose.process(frame_rgb)
            if results.pose_landmarks is not None:
                
                # Draw lines between adjacent landmarks : joints and such , like hands , shoulders and pelvis area
                for connection in mp_pose.POSE_CONNECTIONS:
                    start_index = connection[0]
                    end_index = connection[1]
                    start_point = tuple([int(results.pose_landmarks.landmark[start_index].x * frame.shape[1]), int(results.pose_landmarks.landmark[start_index].y * frame.shape[0])])
                    end_point = tuple([int(results.pose_landmarks.landmark[end_index].x * frame.shape[1]), int(results.pose_landmarks.landmark[end_index].y * frame.shape[0])])
                    cv2.line(frame, start_point, end_point, GREEN, 2 )

                # Draw circles at each landmark ( joint )
                for landmark in results.pose_landmarks.landmark:
                    x = int(landmark.x * frame.shape[1])
                    y = int(landmark.y * frame.shape[0])
                    cv2.circle(frame, (x, y), 3, BLUE, -1)

                # Set human_detected to True and increment human_count by 1
                human_detected = True
                human_count += 1

            # If no human is detected, reset human_count and human_detected
            else:
                human_count = 0
                human_detected = False

        # displaying warning message on the camera and alerting nearby personnel plus activating warning siren
        # if human_detected:
            
        #     cv2.putText(frame, "ALERT : Human detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,  BLUE, 2)
        # else:
        #     cv2.putText(frame, "CLEAR : No personnel around", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, GREEN, 2)
            # mixer.music.play()
        # Convert the frame to JPEG format ( besh najmou nraw les images 3al navigateur ) step 1 
        frame_encoded = cv2.imencode('.jpg', frame)[1].tobytes()

        # Yield the frame in byte format setp 2 : ba3d el conversion 
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_encoded + b'\r\n')

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
#home page
@app.route('/')
def index():
  return render_template('index.html')
#safety camerea feed page
@app.route('/video_feed')
def video_feed():
  return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/add_module')
def addmodule():
  return render_template('new_module.html')

if __name__ == "__main__":
  app.run(debug=True)