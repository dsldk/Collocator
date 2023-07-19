# Collocator

Webservice to search in simple ngram collocations.

## Run in Docker

```bash
git clone https://github.com/dsldk/collocator/ collocator/
cd collocator
docker compose --env dev.env up
```

The webservice will now be accessible on localhost:9005

## Endpoints

See localhost:9005/docs

E.g.

```url
http://localhost:9005/models
http://localhost:9005/search/infomedia/hus
http://localhost:9005/search/infomedia/hus?threshold=0.4
http://localhost:9005/search/infomedia/hus?forms=hus,huset,huse,husene
```

## Usage from Python module

```python
import requests
from json import loads

URL = "http://localhost:9005"

# Available models:
response = requests.get(f"{URL}/models")
result = loads(response.text)

# Search
word = "hus"
model_name = "infomedia"
params = {"threshold": 0.3}

response = requests.get(f"{URL}/{model_name}/{word}", params=params)
result = loads(response.text)
```
