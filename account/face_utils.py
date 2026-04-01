import os
import numpy as np
import cv2
import base64

def save_face_photo(image_data, filename):
    from django.conf import settings
    
    faces_dir = os.path.join(settings.MEDIA_ROOT, 'faces')
    os.makedirs(faces_dir, exist_ok=True)
    
    if ',' in image_data:
        image_data = image_data.split(',')[1]
    
    image_bytes = base64.b64decode(image_data)
    file_path = os.path.join(faces_dir, filename)
    
    with open(file_path, 'wb') as f:
        f.write(image_bytes)
    
    return f'faces/{filename}'


def verify_face(captured_image_data, stored_image_path):
    from django.conf import settings

    try:
        if ',' in captured_image_data:
            captured_image_data = captured_image_data.split(',')[1]
        
        image_bytes = base64.b64decode(captured_image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        captured_img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

        stored_path = os.path.join(settings.MEDIA_ROOT, stored_image_path)
        stored_img = cv2.imread(stored_path, cv2.IMREAD_GRAYSCALE)

        if captured_img is None or stored_img is None:
            return False

        captured_img = cv2.resize(captured_img, (200, 200))
        stored_img = cv2.resize(stored_img, (200, 200))

        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        faces1 = face_cascade.detectMultiScale(captured_img, 1.1, 4)
        faces2 = face_cascade.detectMultiScale(stored_img, 1.1, 4)

        if len(faces1) == 0 or len(faces2) == 0:
            return True

        hist1 = cv2.calcHist([captured_img], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([stored_img], [0], None, [256], [0, 256])
        
        cv2.normalize(hist1, hist1)
        cv2.normalize(hist2, hist2)
        
        similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

        return similarity > 0.5

    except Exception as e:
        print(f"Face verification error: {e}")
        return False