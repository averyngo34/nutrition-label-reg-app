# Nutrition Label Recognizer

## Installation

Setup your environment and install the requirements.

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Deactivate your environment when you're done.

```
source .venv/bin/activate
```

## Local Testing

Run the Flask Service

```
flask run
```

Send a client request.

```
curl -X POST -F file=@test_image/nl1.jpg http://localhost:5000/api
```

## Azure Deployment

Run the command and give it some time to run. HTTP code 202 is not a bad sign.
```
az webapp up --sku S1 --name sicc-ajm-project4 --location=eastus
```

Send a client request.

```
curl -X POST -F file=@test_image/nl1.jpg https://sicc-ajm-project4.azurewebsites.net/api
```

## Known Issues

* !!! If you add new dependencies, make sure to update the requirements.txt, because this is required to deploy it to Azure. 
* Do not allow `pkg_resources==0.0.0` in requirements.txt.
* cURL POST to Azure must be `https://` and not `http://`.

## License
[MIT](https://choosealicense.com/licenses/mit/)
