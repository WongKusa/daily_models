import json
from collections import defaultdict
from pathlib import Path

INPUT_FILE = "models.json"
OUTPUT_FILE = "clean_models.json"


def normalize_key(model_id: str) -> str:
    key = model_id.lower()

    # remove provider prefix
    if "/" in key:
        key = key.split("/", 1)[1]

    # normalize separators
    key = key.replace("_", "-")

    # normalize instruct -> it
    if key.endswith("-instruct"):
        key = key[:-len("-instruct")] + "-it"

    return key


def simplify_model(model_id: str, model: dict) -> dict:
    cleaned = dict(model)

    cleaned.pop("reasoning_config", None)
    cleaned.pop("scrape_metadata", None)

    result = {
        "oid": model_id,
        **cleaned
    }

    return result

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        models = json.load(f)

    output = {}

    # normalized name -> original model ids
    normalized_map = defaultdict(list)

    for model_id in models:
        normalized = normalize_key(model_id)
        normalized_map[normalized].append(model_id)

    print("=" * 80)
    print("NORMALIZATION COLLISIONS")
    print("=" * 80)

    collision_count = 0

    for normalized, originals in sorted(normalized_map.items()):
        if len(originals) > 1:
            collision_count += 1

            print(f"\n{normalized}")

            for item in originals:
                print(f"  - {item}")

    if collision_count == 0:
        print("No collisions found.")

    print()
    print("=" * 80)

    # collect normalized keys first
    all_normalized_keys = {
        normalize_key(model_id)
        for model_id in models
    }

    skipped_preview = []

    for model_id, model_data in models.items():

        normalized_key = normalize_key(model_id)

        # preview handling
        if normalized_key.endswith("-preview"):

            base_model = normalized_key[:-8]

            if base_model in all_normalized_keys:
                skipped_preview.append(
                    (normalized_key, base_model)
                )
                continue

        output[normalized_key] = simplify_model(
            model_id,
            model_data
        )

    Path(OUTPUT_FILE).write_text(
        json.dumps(
            output,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print("\nPREVIEW MODELS SKIPPED")

    if not skipped_preview:
        print("None")
    else:
        for preview, base in skipped_preview:
            print(
                f"{preview} -> {base}"
            )

    print()
    print("=" * 80)
    print(f"Input Models  : {len(models)}")
    print(f"Output Models : {len(output)}")
    print(f"Saved         : {OUTPUT_FILE}")
    print("=" * 80)


if __name__ == "__main__":
    main()