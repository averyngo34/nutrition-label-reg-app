import os
import time
from lib.form_reg import FormRecognizer


def main():
    # Trained model ID
    modelID = "29e649f9-4539-42dc-a79c-004a9effba76"

    form_recog = FormRecognizer(modelID)

    for image in os.listdir("test_image"):

        image_path = os.getcwd() + "/test_image/" + image

        resp_url = form_recog.send_for_analysis(image_path)
        if resp_url is not None:
            print(form_recog.get_result(resp_url))

        # At the current pricing tier, the server can only handle an image at a time.
        time.sleep(2)

if __name__ == "__main__":
    main()
