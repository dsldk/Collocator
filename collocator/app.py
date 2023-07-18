"""FastAPI service for wordres."""
from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse

from collocator import CONFIG, logger
from collocator.main import load_all_models, search_ngrams

title = CONFIG.get("general", "title")

app = FastAPI(
    title=CONFIG.get("general", "title"),
    description=CONFIG.get("general", "description"),
)


@app.get("/health", response_class=PlainTextResponse)
def healthcheck() -> str:
    """Healthcheck, for use in automatic ."""
    return "200"


@app.on_event("startup")
async def startup_event() -> None:
    global models
    models = await load_all_models()


@app.get("/search/{model}/{word}", response_class=JSONResponse)
async def search(
    word: str,
    model,
    threshold: float = 0.3,
    bundle_contexts: bool = True,
    forms: str = "",
    verbose_output: bool = True,
) -> JSONResponse:
    """Check wheter word might be a valid word in the given language."""
    lookup_forms = [word]
    if forms:
        lookup_forms += forms.split(",")
        lookup_forms = list(set(lookup_forms))
    result = {}
    for form in lookup_forms:
        result[form] = await search_ngrams(
            form, models.get(model, {}).get("connection", None), threshold=threshold
        )
    if bundle_contexts:
        result = bundle_context(result)
    message = {
        "word": word,
        "threshold": threshold,
        "ngrams": result,
        "included_forms": lookup_forms,
    }
    if verbose_output:
        message["model_info"] = {}
        # Copy keys from model to model_info
        for key in models.get(model, {}):
            if key not in ["connection", "ngrams"]:
                message["model_info"][key] = models[model][key]
    return JSONResponse(content=message)


@app.get("/models", response_class=JSONResponse)
async def available_models() -> JSONResponse:
    """Return a list of available models."""
    # model_info = {}
    # for model_name in models:
    #     model_info[model_name] = {}
    #     for key in models[model_name]:
    #         if key not in ["connection", "ngrams"]:
    #             model_info[model_name][key] = models[model_name][key]

    return JSONResponse(content=models)


def bundle_context(form_result: dict) -> dict:
    """Bundle the contexts together into."""
    result = {
        "left": [],
        "right": [],
        "in": [],
    }
    for _form, contexts in form_result.items():
        for context, ngrams in contexts.items():
            result[context].extend(ngrams)
    for context, ngrams in result.items():
        # Sort by score
        result[context] = sorted(ngrams, key=lambda x: x[1], reverse=True)
    return result
