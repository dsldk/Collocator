# Collocator

Webservice to search in simple ngram collocations.

## Run in Docker

```bash
git clone git clone https://github.com/dsldk/collocator/ collocator/
cd collocator
docker compose up
```

The webservice will now be accessible on localhost:9003

## Endpoints

See localhost:9003/docs

E.g.

```url
http://localhost:9003/models
http://localhost:9003/infomedia/hus
http://localhost:9003/infomedia/hus?forms=hus,huset,huse,husene
```

## Usage from Python module

```python
import requests
from json import loads

URL = "http://localhost:9003"

# Available models:
response = requests.get(f"{URL}/models")
result = loads(response.text)

# Search
word = "hus"
model_name = "infomedia"
params = {}

response = requests.get(f"{URL}/{model_name}/{word}", params=params)
result = loads(response.text)
```
