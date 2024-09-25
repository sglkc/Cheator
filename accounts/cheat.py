import cv2
import mediapipe as mp
import math
import time

# Inisialisasi MediaPipe Pose dan Face Mesh
mp_pose = mp.solutions.pose
mp_face_mesh = mp.solutions.face_mesh
pose = mp_pose.Pose()
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Landmark untuk bagian atas tubuh (termasuk kepala dan bahu)
upper_body_landmarks = [
    mp_pose.PoseLandmark.NOSE,
    mp_pose.PoseLandmark.LEFT_SHOULDER,
    mp_pose.PoseLandmark.RIGHT_SHOULDER,
    mp_pose.PoseLandmark.LEFT_EYE,
    mp_pose.PoseLandmark.RIGHT_EYE,
    mp_pose.PoseLandmark.LEFT_EAR,
    mp_pose.PoseLandmark.RIGHT_EAR,
    mp_pose.PoseLandmark.MOUTH_LEFT,
    mp_pose.PoseLandmark.MOUTH_RIGHT,
]

# Fungsi untuk menghitung sudut kemiringan bahu
def calculate_angle(shoulder_left, shoulder_right):
    x1, y1 = shoulder_left
    x2, y2 = shoulder_right
    delta_x = x2 - x1
    delta_y = y2 - y1
    angle = math.degrees(math.atan2(delta_y, delta_x))
    return angle

# Fungsi untuk menghitung jarak Euclidean antara dua titik
def calculate_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Fungsi untuk menghitung jarak horizontal antara batas kiri dan kanan
def calculate_horizontal_distance(min_x, max_x):
    return max_x - min_x

start_time = None
tengok_kiri_detected = False
cheating_duration = 0.75

# Fungsi utama untuk memproses frame dan mendeteksi cheating
def process_frame(frame):
    global start_time, tengok_kiri_detected

    frame = cv2.flip(frame, 1)

    # Konversi frame ke RGB
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Proses gambar untuk mendeteksi pose dan wajah
    pose_results = pose.process(image)
    face_results = face_mesh.process(image)

    # Konversi kembali ke BGR untuk tampilan
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Inisialisasi variabel untuk box
    min_x, min_y = image.shape[1], image.shape[0]
    max_x, max_y = 0, 0
    padding_top = 100  # Padding untuk bagian atas kotak
    box_color = (0, 0, 255)  # Default merah
    text = "Tengok Kanan"  # Default teks
    cheating = False

    # Gambar kotak di sekitar tubuh bagian atas
    if pose_results.pose_landmarks:
        shoulder_positions = {}

        for idx, landmark in enumerate(pose_results.pose_landmarks.landmark):
            if idx in [lmk.value for lmk in upper_body_landmarks]:
                cx, cy = int(landmark.x * image.shape[1]), int(landmark.y * image.shape[0])
                if idx == mp_pose.PoseLandmark.LEFT_SHOULDER.value:
                    shoulder_positions['left'] = (cx, cy)
                elif idx == mp_pose.PoseLandmark.RIGHT_SHOULDER.value:
                    shoulder_positions['right'] = (cx, cy)

                # Update koordinat kotak
                min_x, max_x = min(min_x, cx), max(max_x, cx)
                min_y, max_y = min(min_y, cy), max(max_y, cy)

        # Tambahkan padding hanya ke bagian atas bounding box
        min_y = max(0, min_y - padding_top)

        # Hitung sudut kemiringan bahu
        if 'left' in shoulder_positions and 'right' in shoulder_positions:
            angle = calculate_angle(shoulder_positions['left'], shoulder_positions['right'])

            # Tentukan warna kotak dan teks berdasarkan sudut
            if abs(angle) < 176:
                box_color = (0, 0, 255)  # Merah
                text = "Cheating"
            else:
                box_color = (255, 0, 0)  # Biru
                text = "Stand By"
                
    # Gambar skeleton pada bagian pose
    # if pose_results.pose_landmarks:
    #     mp_drawing.draw_landmarks(
    #         image, 
    #         pose_results.pose_landmarks, 
    #         mp_pose.POSE_CONNECTIONS,
    #         mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),  # Warna dan gaya landmark
    #         mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2, circle_radius=2)  # Warna dan gaya koneksi
    #     )

    # if face_results.multi_face_landmarks:
    #     for face_landmarks in face_results.multi_face_landmarks:
    #         # Gambar Face Mesh pada gambar
    #         mp_drawing.draw_landmarks(
    #             image=image,
    #             landmark_list=face_landmarks,
    #             connections=mp_face_mesh.FACEMESH_TESSELATION,  # Menggambar tessellation (mesh wajah)
    #             landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),  # Warna landmark
    #             connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1)  # Warna koneksi mesh
    #         )

    # Deteksi arah pandangan wajah
    if face_results.multi_face_landmarks:
        for face_landmarks in face_results.multi_face_landmarks:
            left_eye = face_landmarks.landmark[33] 
            right_eye = face_landmarks.landmark[263] 
            nose_tip = face_landmarks.landmark[1] 

            # Mengonversi koordinat normalisasi ke piksel
            h, w, _ = image.shape
            left_eye_x = int(left_eye.x * w)
            right_eye_x = int(right_eye.x * w)
            nose_x = int(nose_tip.x * w)
            nose_y = int(nose_tip.y * h)

            # Tentukan threshold jarak
            threshold = 20  # Jarak minimal dalam piksel
            threshold_vertical = 45

            # Mengecek apakah hidung sudah cukup jauh dari mata kiri
            if nose_x - left_eye_x < threshold:
                if start_time is None:
                    start_time = time.time()
                elif time.time() - start_time >= cheating_duration:
                    box_color = (0, 0, 255)  # Merah
                    text = "Cheating"
                else:
                    box_color = (0, 255, 255)  # Kuning
                    text = "Tengok Kiri"
                tengok_kiri_detected = True
            elif nose_x - right_eye_x + 30 > threshold:
                if start_time is None:
                    start_time = time.time()
                elif time.time() - start_time >= cheating_duration:
                    box_color = (0, 0, 255)  # Merah
                    text = "Cheating"
                else:
                    box_color = (0, 255, 255)  # Kuning
                    text = "Tengok Kanan"
            elif nose_y - (left_eye.y * h) > threshold_vertical:
                if start_time is None:
                    start_time = time.time()
                elif time.time() - start_time >= cheating_duration:
                    box_color = (0, 0, 255)  # Merah
                    text = "Cheating"
                else:
                    box_color = (0, 255, 255)  # Kuning
                    text = "Menunduk"
            else:
                start_time = None
                tengok_kiri_detected = False

    if text == "Cheating":
        cheating = True
    else:
        cheating = False

    # Gambar kotak di sekitar bagian atas tubuh dan tambahkan teks
    cv2.rectangle(image, (min_x, min_y), (max_x, max_y), box_color, 2)
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)[0]
    text_x = min_x + 10
    text_y = min_y + max_y - min_y - 10
    cv2.putText(image, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, box_color, 2)

    if cheating:
        return image, "cheating"
    else:
        return image, "no cheating"
