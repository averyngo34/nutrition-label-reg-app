import io
import os
from flask import Flask, request, jsonify
from lib.form_reg import FormRecognizer
from PIL import Image


MODEL_ID = "29e649f9-4539-42dc-a79c-004a9effba76"
FORM_RECOG = FormRecognizer(MODEL_ID)

# Path to temporary write images.
TMP_IMAGE_PATH = "/tmp"

# "jpeg" extension doesn't seem to work.
EXTENSION_MAP = {
    "JPEG": "jpg",
}

app = Flask(__name__)


@app.route('/api', methods=['POST'])
def accept_image():
    file = request.files['file']
    print(
        f"Request from user '{request.remote_addr}' for file '{file.filename}'")
    image_path = process_image(file)
    analyze_image(image_path)
    return jsonify({'msg': 'success'})


def process_image(file) -> str:
    img = Image.open(file.stream)
    buf = io.BytesIO()
    img.save(buf, format=img.format)
    image_path = os.path.join(TMP_IMAGE_PATH, file.filename)
    print(f"Persisting image to '{image_path}'")
    with open(image_path, "wb") as f:
        f.write(buf.getvalue())
    return image_path


def analyze_image(image_path):
    print(f"Sending '{image_path}' to Azure for analysis")
    resp_url = FORM_RECOG.send_for_analysis(image_path)
    res = FORM_RECOG.get_result(image_path, resp_url)
    print("Operation complete:", res)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
