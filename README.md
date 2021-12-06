# Nutrition Label Recognizer

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


## Known Issues

* !!! If you add new dependencies, make sure to update the requirements.txt, because this is required to deploy it to Azure. 
* Do not allow `pkg_resources==0.0.0` in requirements.txt.
* cURL POST to Azure must be `https://` and not `http://`.

## License
[MIT](https://choosealicense.com/licenses/mit/)
