import os
import re
from typing import List
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import FormTrainingClient

import json
import time
from requests import get, post

"""
Reference:
https://github.com/Azure-Samples/cognitive-services-quickstart-code/blob/master/python/FormRecognizer/rest/python-labeled-data.md
https://docs.microsoft.com/en-us/azure/applied-ai-services/form-recognizer/how-to-guides/try-sdk-rest-api?pivots=programming-language-python

Assumption: 
 1. There is only one page per analysis as the input file is of image format
"""

class FormRecognizer:

    def __init__(self, modelID: str) -> None:

        self.train_client = None
        self.modelID = modelID
        self.end_point = "https://eastus.api.cognitive.microsoft.com/"
        self.fr_key = self._get_key("formrecog")
        self.post_url = self.end_point + f"/formrecognizer/v2.1/custom/models/{self.modelID}/analyze"
        self._create_client()

    def send_for_analysis(self, file_path: str) -> str:
        """
        Send the image to the Form Recognizer endpoint for analysis.

        Args:
            file_path: the file path of the image to be sent for analysis
        Returns:
            The operation url where the analysis results can be retrieved from the Form Recognizer endpoint
            In case or error, None is returned.
        """

        # Check if image format is supported
        _, extension = os.path.splitext(file_path)

        if extension not in [".jpg", ".png", ".tiff"]:
            print(f"Error! {file_path} image format is invalid or unsupported.\n"
                  "Supported image formats are JPEG, PNG, and TIFF")
            return None

        print(f"image/{extension[1:]}")

        # Request headers
        headers = {
            'Content-Type': f"image/{extension[1:]}",
            'Ocp-Apim-Subscription-Key': self.fr_key,
        }

        with open(file_path, "rb") as f:
            data_bytes = f.read()

        try:
            # Send POST request asynchronously
            resp = post(url=self.post_url, data=data_bytes, headers=headers)

            if resp.status_code != 202:
                print(f"Analysis has failed for {file_path}\n"
                      f"Server response: {json.dumps(resp.json())}")
                return None

            print(f"Analysis has succeeded for {file_path}")
            return resp.headers["operation-location"]

        except Exception as e:
            print(f"Cannot post {file_path} for analysis\n"
                  f"Error: {str(e)}")
            return None

    def get_result(self, resp_url: str) -> dict:
        """
        Retrieve the analysis results returned by the send_for_analysis() method.
        If the analysis is successful, the result is parsed and check for validity.

        Args:
            resp_url: The operation url where the analysis results can be retrieved from the Form Recognizer endpoint
        Returns:
            If the image is a valid nutrition label, a dictionary of analyzed results is returned containing:
                - Timestamp of the analysis
                - Nested dictionary of recognized fields along with their values and units

            In case of error or failed analysis or the image is foudn to be invalid, None is returned.
        """

        # Timeout parameters in seconds
        wait_time = 0
        max_wait_time = 30
        wait_interval = 2

        # Attempt to retrieve the analysis results every wait_interval until successful
        while wait_time < max_wait_time:
            try:
                resp = get(url=resp_url, headers={"Ocp-Apim-Subscription-Key": self.fr_key})
                resp_json = resp.json()

                if resp.status_code != 200:
                    print(f"Error! Server could not analyze result for:\n{resp_url}\n"
                          f"Server response:\n{json.dumps(resp_json)}")
                    return None

                if resp_json["status"] == "failed":
                    print(f"Error! Server failed to analyze result for:\n{resp_url}\n"
                          f"Server response:\n{json.dumps(resp_json)}")
                    return None

                elif resp_json["status"] == "succeeded":
                    print(f"Analysis has been successfully completed for:\n{resp_url}")
                    return self._parse_result(resp_json)  # Process result

                # Sleep and retry
                time.sleep(wait_interval)
                wait_time += wait_interval

            except Exception as e:
                print(f"Cannot send request to analyze result for:\n{resp_url}\n"
                      f"Error: {str(e)}")
                return None

        print(f"Timeout! Cannot retrieve analysis results within {max_wait_time}s for:\n{resp_url}")
        return None

    def _parse_result(self, resp_json: dict) -> dict:
        """
        Parse the analysis results, and check if the image is a nutrition label.
        The image is considered a nutrition label if the trained model recognizes at least 2 out of 4 criteria below:
         - Serving Size field
         - Calories field with numeric value
         - Total Fat field with numeric value and valid unit
         - Total Carb field with numeric value and valid unit

        Args:
            resp_json: The server analysis json result
        Returns:
            A dictionary of analyzed results is returned containing:
                - Timestamp of the analysis : str
                - Validity of the image : bool
                - Nested dictionary of recognized fields along with their values and units
                    (if the image is a valid nutrition label)
        """
        results = {"timestamp": resp_json["createdDateTime"]}
        is_nl = 0   # Number of criterion met
        recog_fields = {}

        for field, field_val_dict in resp_json["analyzeResult"]["documentResults"][0]["fields"].items():
            if "valueString" in field_val_dict.keys():

                # Handle servingSize and calorie differently since they do not have units
                if field == "servingSize":
                    recog_fields[field] = field_val_dict["valueString"]
                    is_nl += 1
                    continue

                elif field == "calories" and field_val_dict["valueString"].isnumeric():
                    recog_fields[field] = field_val_dict["valueString"]
                    is_nl += 1
                    continue

                is_valid, val = self._read_valueString(field_val_dict["valueString"])
                if is_valid:
                    recog_fields[field] = val
                    if field in ["totalCarb", "totalFat"]:
                        is_nl += 1

        if is_nl >= 2:
            results["is_nl"] = True
            results["recog_fields"] = recog_fields
        else:
            results["is_nl"] = False

        return results

    def _read_valueString(self, val_str: str) -> (bool, dict):
        """
        Check if the valueString returned by the analysis is valid:
            - The first set of letters are numeric value
            - The second sets of letters represent valid units (gram or milligrams or micrograms)

        Args:
            val_str: valueString returned by the analysis
        Returns:
            - Validity of valueString : bool
            - Dictionary of value and units (if the valueString is valid)
        """
        # Split numeric value from string units
        split_str = re.split('(\d+)', val_str)

        if len(split_str) != 3 or not split_str[1].isnumeric() or not split_str[2].isalnum():
            return False, None

        val = split_str[1]
        unit = split_str[2]

        if unit not in ["g", "mg", "mcg"]:
            return False, None

        return True, {"val": val, "unit": unit}

    def _create_client(self) -> None:
        """
        Create a form recognizer client
        """
        credential = AzureKeyCredential(self.fr_key)
        self.train_client = FormTrainingClient(self.end_point, credential)

    def _get_key(self, key: str) -> str:
        """
        Access key vault to get secret.

        Args:
            key: key name
        Returns:
            Secret of the provided key name
        """
        vault_url = "https://nlvault.vault.azure.net"
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=vault_url, credential=credential)
        return client.get_secret(key).value