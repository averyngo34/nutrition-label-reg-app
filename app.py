from lib.form_reg import FormRecognizer
import lib.cosmos as cosmos
import pdb
import sys
from PIL import Image
from flask import Flask, request, jsonify
import os
import io
import json



MODEL_ID = "29e649f9-4539-42dc-a79c-004a9effba76"
FORM_RECOG = FormRecognizer(MODEL_ID)

# Path to temporary write images.
TMP_IMAGE_PATH = "/tmp"

# "jpeg" extension doesn't seem to work.
EXTENSION_MAP = {
    "JPEG": "jpg",
}

CONTAINER = cosmos.init(cosmos.ENDPOINT, cosmos.KEY, cosmos.DATABASE,
                        cosmos.DATABASE, cosmos.PARTITION_KEY)

app = Flask(__name__)


@app.route('/api/image', methods=['POST'])
def accept_image():
    file = request.files['file']
    print(
        f"Request from user '{request.remote_addr}' for file '{file.filename}'")
    image_path = process_image(file)
    nutrition_data = analyze_image(image_path)
    if nutrition_data is None:
        return jsonify({'msg': 'failed'})
    cosmos.add_nutrition(CONTAINER, nutrition_data)
    return jsonify({'msg': 'success'})


@app.route('/summary', methods=['POST', 'GET'])
def summary_update():
    if request.method == "POST":
        body = None
        if "request" in request.form.to_dict():
            data = json.loads(request.form.to_dict()["request"])
            body = aggregate_data(data)
        summary_update.summary = body
        print(f"Received: {summary_update.summary}")
        return jsonify({'msg': 'success'})

    if request.method == "GET":
        if summary_update.summary is None:
            return "No summary"
        if len(summary_update.summary) == 0:
            return "No summary"
        return summary_update.summary

summary_update.summary = None


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
    return res

def aggregate_data(data):
    results = {}
    for entry in data:
        entry = entry["recog_fields"]
        for k, vs in entry.items():
            if k not in results:
                results[k] = 0
            if isinstance(vs, dict):
                try:
                    results[k] += int(vs["val"])
                except:
                    print(f"couldn't handle key '{k}', '{vs}'")
            else:
                try:
                    results[k] += int(vs)
                except:
                    print(f"couldn't handle key '{k}', '{vs}'")
    return results



#if __name__ == "__main__":
#    app.run(host="0.0.0.0", port=5000)
