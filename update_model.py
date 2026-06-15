import json
from datetime import datetime
from pathlib import Path

import requests

API_URL = "https://openrouter.ai/api/frontend/v1/catalog/models"
OUTPUT_FILE = "models.json"


def should_keep(model):
    slug = model.get("slug", "").lower()
    endpoint = model.get("endpoint")

    if endpoint is None:
        return False

    if slug.startswith("openrouter/"):
        return False

    if slug.endswith("-latest"):
        return False

    endpoint = model.get("endpoint") or {}

    if endpoint.get("is_free") is True:
        return False

    output_modalities = model.get("output_modalities") or []

    return output_modalities in (
        ["text"],
        ["embeddings"],
    )


def build_model(model):
    endpoint = model.get("endpoint") or {}

    supported_parameters = endpoint.get(
        "supported_parameters"
    ) or []

    pricing = endpoint.get("pricing") or {}

    reasoning_config = (
        model.get("reasoning_config")
        or {}
    )

    return {
        "hf_slug": model.get("hf_slug"),
        "name": model.get("short_name")
                or model.get("name"),
        "author": model.get("author"),
        "reasoning": model.get(
            "supports_reasoning"
        ),
        "tool_call": "tools" in supported_parameters,
        "release_date": None,
        "modalities": {
            "input": model.get(
                "input_modalities"
            ),
            "output": model.get(
                "output_modalities"
            ),
        },
        "limit": {
            "context": model.get(
                "context_length"
            ),
            "output": endpoint.get(
                "max_completion_tokens"
            ),
        },
        "pricing": {
            "input": pricing.get(
                "prompt"
            ),
            "output": pricing.get(
                "completion"
            ),
            "input_cache_read": pricing.get(
                "input_cache_read"
            ),
            "input_cache_write": pricing.get(
                "input_cache_write"
            ),
        },
        "supported_parameters":
            supported_parameters,
        "reasoning_config": {
            "start_token":
                reasoning_config.get(
                    "start_token"
                ),
            "end_token":
                reasoning_config.get(
                    "end_token"
                ),
            "is_mandatory_reasoning":
                reasoning_config.get(
                    "is_mandatory_reasoning"
                ),
            "supports_reasoning_effort":
                reasoning_config.get(
                    "supports_reasoning_effort"
                ),
            "supported_reasoning_efforts":
                reasoning_config.get(
                    "supported_reasoning_efforts"
                ),
            "default_reasoning_effort":
                reasoning_config.get(
                    "default_reasoning_effort"
                ),
            "reasoning_return_mechanism":
                reasoning_config.get(
                    "reasoning_return_mechanism"
                ),
        },
        "scrape_metadata": {
            "last_update_datetime":
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "openrouter",
            "source_url": API_URL,
        },
    }


def main():
    response = requests.get(
        API_URL,
        timeout=60,
    )
    response.raise_for_status()

    data = response.json().get(
        "data",
        []
    )

    result = {}

    for model in data:
        if not should_keep(model):
            continue

        slug = model["slug"].lower()

        result[slug] = build_model(
            model
        )

    Path(OUTPUT_FILE).write_text(
        json.dumps(
            result,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"Generated {len(result)} models"
    )
    print(
        f"Saved to {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()