"""Validate one NEXUS output offline, or regenerate operator CLI schemas."""

import argparse
from functools import cache
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError
from pydantic.json_schema import GenerateJsonSchema
from referencing import Registry
from referencing.jsonschema import DRAFT202012

from nexus.models.episode import GenerationMetadata
from nexus.solver import SolveResult

SCHEMAS = Path(__file__).resolve().parents[1] / "schemas"
MODELS = {"generation-metadata-v1": GenerationMetadata, "solver-result-v1": SolveResult}


class EmittedFields(GenerateJsonSchema):
    def field_is_required(self, field, total):
        # model_dump includes defaults, even on actions nested inside a plan.
        if self.mode == "serialization" and field["type"] == "model-field":
            return field.get("serialization_exclude_if") is None
        return super().field_is_required(field, total)


def output_schema(name, model):
    filename = f"{name}.schema.json"
    schema = model.model_json_schema(
        mode="serialization", by_alias=True, schema_generator=EmittedFields
    )
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"https://raw.githubusercontent.com/petmal/NEXUS/main/schemas/{filename}",
        **schema,
    }


@cache
def contracts():
    """Resolve sibling schemas from this checkout, including older files without an ID."""
    docs = {
        p.name: json.loads(p.read_text(encoding="utf-8")) for p in SCHEMAS.glob("*.schema.json")
    }
    base = docs["terminal-performance-v1.schema.json"]["$id"].rsplit("/", 1)[0]
    registry = Registry().with_resources(
        (f"{base}/{name}", DRAFT202012.create_resource(doc)) for name, doc in docs.items()
    )
    return {
        name.removesuffix(".schema.json"): Draft202012Validator(doc, registry=registry)
        for name, doc in docs.items()
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="Check a JSON object; use - for stdin")
    validate.add_argument(
        "schema",
        choices=sorted(p.name.removesuffix(".schema.json") for p in SCHEMAS.glob("*.schema.json")),
    )
    validate.add_argument("file", help="JSON file or - for stdin")
    commands.add_parser("export", help="Regenerate generation metadata and solver schemas")
    args = parser.parse_args()
    if args.command == "validate":
        try:
            if args.file == "-":
                record = json.load(sys.stdin)
            else:
                with Path(args.file).open(encoding="utf-8") as stream:
                    record = json.load(stream)
            contracts()[args.schema].validate(record)
        except (OSError, ValueError, ValidationError) as exc:
            # Avoid printing a possibly large/private record as part of the error.
            message = (
                f"at {exc.json_path} (rule: {exc.validator})"
                if isinstance(exc, ValidationError)
                else str(exc)
            )
            parser.exit(1, f"Invalid {args.schema}: {message}\n")
        print(f"Valid {args.schema}")
        return
    for name, model in MODELS.items():
        (SCHEMAS / f"{name}.schema.json").write_text(
            json.dumps(output_schema(name, model), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
