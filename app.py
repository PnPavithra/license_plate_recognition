from flask import Flask, request, jsonify
import cv2
import numpy as np
import pytesseract
import os
from ultralytics import YOLO
import pandas as pd

app = Flask(__name__)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
model = YOLO('best.pt')

Upload = 'uploads'
if not os.path.exists(Upload):
    os.makedirs(Upload)

@app.route('/up_img', methods=['POST'])
def up_img():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file:
            filepath = os.path.join(Upload, file.filename)
            file.save(filepath)

            print(f"Image saved at {filepath}")
            image = cv2.imread(filepath)
            if image is None:
                return jsonify({'error': 'Failed to load image'}), 500

            print(f"Original image shape: {image.shape}")
            image = cv2.resize(image, (1020, 500))

            results = model.predict(image)
            a = results[0].boxes.data
            if a is None or len(a) == 0:
                return jsonify({'error': 'No bounding boxes detected'}), 500

            print(f"Bounding boxes: {a}")
            px = pd.DataFrame(a).astype('float')

            pro_num = set()
            text = ""

            for i, row in px.iterrows():
                x1, y1, x2, y2 = map(int, row[:4])
                print(f"Cropping area: x1={x1}, y1={y1}, x2={x2}, y2={y2}")

                if x2 <= x1 or y2 <= y1:
                    print("Invalid cropping coordinates")
                    continue

                crop = image[y1:y2, x1:x2]
                if crop.size == 0:
                    print("Empty crop area")
                    continue

                print(f"Cropped image shape: {crop.shape}")
                gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
                gray = cv2.bilateralFilter(gray, 10, 20, 20)

                txt = pytesseract.image_to_string(gray).strip()
                if txt:
                    print(f"OCR Result: {txt}")

                txt = txt.replace('(', '').replace(')', '').replace(',', '').replace(']', '')

                if txt and txt not in pro_num:
                    pro_num.add(txt)
                    text += txt + " "

            os.remove(filepath)
            print(f"Final OCR Text: {text.strip()}")
            return jsonify({'txt': text.strip()})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)