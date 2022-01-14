# Nutrition Label Recognizer

This Azure web application allows users to keep track of their daily nutrition intake by posting nutrition label photos of their foods.

This application was developed using 4 Azure services :
    1. Web App to interact with users
    2. Form Recognizer with custom trained model to scan the labels
    3. Cosmos DB to record the nutrition intake
    4. Functions to calculate and notify users of their daily nutrition intake

![alt text](http://github.gatech.edu/dngo34/nutrition-label-cloud-app/service_interaction.png)

When a nutrition label photo is sent to the web app, the web app reads and extracts nutrition facts through a Form Recognizer custom trained model. It then records this data to Azure Cosmos DB endpoint and update the user daily intake. The daily nutriton intake is then relayed back to users through the web app.


## Assumptions

1. Each submitted photo (JPEG, PNG, BMP, TIFF only)contains only one clear and readable nutrition label.
2. Photo must be in JPEF, PNG and TIFF format and less than 50 MB


## Prerequisites

Setup the environment by installing the requirements.

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Deactivate the environment when done.

```
deactivate
```

## Deployment and Testing

### Local

1. Start the web server.

```
flask run
```

2. Send the request each image to process. The extracted data is written to the Cosmos database.

```
curl -X POST -F file=@test_image/nl1.jpg http://localhost:5000/api/image
```

3. Use `LOCAL_SERVER` in `functions/__init__.py:37`.

4. Run the Azure function app to generate the summary.


```
func start
```

5. Verify in browser at http://localhost:5000/summary


### Azure

1. Run the command and give it some time to run. HTTP code 202 is not a bad sign. If the application is already running, this will re-deploy it.
```
az webapp up --sku S1 --name sicc-ajm-project4 --location=eastus
```

2. Send a POST request for each image to process. The extracted data will be written to the Cosmos database.

```
curl -X POST -F file=@test_image/nl1.jpg https://sicc-ajm-project4.azurewebsites.net/api/image
```

3. Set `AZURE_SERVER` in `functions/__init__.py:37`.

4. Run the Azure function app to generate the summary.

```
func azure functionapp publish sicc-ajm-project4-func
```

5. Verify in browser at https://sicc-ajm-project4.azurewebsites.net/summary


## Notes

* If you add new dependencies, make sure to update the requirements.txt, because this is required to deploy it to Azure. 
* Do not allow `pkg_resources==0.0.0` in requirements.txt.
* cURL POST to Azure must be `https://` and not `http://`.

## License
[MIT](https://choosealicense.com/licenses/mit/)
