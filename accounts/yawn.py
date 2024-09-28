import dlib
import cv2
import numpy as np
import base64

# Load face detector and landmark predictor
try:
    face_detector = dlib.get_frontal_face_detector()
    landmark_predictor = dlib.shape_predictor("C:\\Users\\mafin\\OneDrive\\Documents\\Djang\\login\\accounts\\shape_predictor_68_face_landmarks.dat")
except Exception as e:
    print(f"Error loading dlib model: {e}")

def detect_yawn(frame, threshold=40):

    try:
        # Flip the frame horizontally
        frame = cv2.flip(frame, 1) 

        # Convert the frame to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame
        faces = face_detector(gray)
        status = False  # Initial status is no yawn detected

        # Loop through detected faces
        for face in faces:
            # Get face rectangle coordinates
            x, y, w, h = (face.left(), face.top(), face.width(), face.height())
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Draw rectangle around the face

            # Get facial landmarks
            landmarks = landmark_predictor(gray, face)

            # Loop through all 68 landmark points and draw them
            for n in range(68):
                x_landmark = landmarks.part(n).x
                y_landmark = landmarks.part(n).y
                cv2.circle(frame, (x_landmark, y_landmark), 2, (255, 0, 0), -1)  # Draw blue circles for landmarks

            # Get the coordinates of the upper lip and lower lip
            upper_lip_top = (landmarks.part(51).x, landmarks.part(51).y)  # Landmark 51 (center of upper lip)
            lower_lip_bottom = (landmarks.part(57).x, landmarks.part(57).y)  # Landmark 57 (center of lower lip)

            # Calculate the Euclidean distance between upper lip and lower lip
            distance = np.linalg.norm(np.array(upper_lip_top) - np.array(lower_lip_bottom))

            # Check if the distance exceeds the threshold for yawning
            if distance > threshold:
                status = True  # Yawn detected
                cv2.putText(frame, "Menguap", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        if status:
            return frame, 'Menguap'
        else:
            return frame, 'Normal'

    except Exception as e:
        print(f"Error during yawn detection: {e}")
        return None, False
