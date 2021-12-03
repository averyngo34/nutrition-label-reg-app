# Nutrition Label Recognizer

## Installation
We assume you have installed python3 and pip on your system.

Run install.sh on your system:
```bash
bash setup.sh
```

This install script will do the following:
1. Install Azure Key Vault Secrets client library for Python - Version 4.3.0
2. Install Use Form Recognizer SDKs

## Local Testing

Run the Flask Service

```
flask run
```

Send a client request.

```
curl -X POST -F file=@test_image/nl1.jpg http://localhost:5000/api
```

## License
[MIT](https://choosealicense.com/licenses/mit/)