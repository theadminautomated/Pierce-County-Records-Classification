#!/usr/bin/env python
"""Launch a local Hugging Face text-generation server."""
from __future__ import annotations

import argparse
from pathlib import Path

import torch
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import uvicorn


class GenerateRequest(BaseModel):
    prompt: str


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Return CLI arguments."""
    parser = argparse.ArgumentParser(description="Run a local LLM server")
    parser.add_argument(
        "--model",
        default="piercecounty/records-classifier-phi2",
        help="Model id or path",
    )
    parser.add_argument(
        "--quant",
        type=int,
        choices=[4, 8],
        help="Optional quantization bits",
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to serve the API on"
    )
    return parser.parse_args(argv)


def _load_model(model_name: str, quant: int | None):
    """Load tokenizer and model to the appropriate device."""
    cache_dir = Path("models") / model_name.replace("/", "_")
    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
    model_kwargs: dict = {"cache_dir": cache_dir}
    if quant:
        from transformers import BitsAndBytesConfig

        model_kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=quant == 4, load_in_8bit=quant == 8
        )
    model = AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    return tokenizer, model, device


def create_app(model_name: str, quant: int | None) -> FastAPI:
    """Return a FastAPI app serving the model."""
    tokenizer, model, device = _load_model(model_name, quant)
    app = FastAPI()

    @app.post("/generate")
    def generate(req: GenerateRequest) -> dict[str, str]:
        tokens = tokenizer(req.prompt, return_tensors="pt").to(device)
        output = model.generate(**tokens, max_new_tokens=128)
        text = tokenizer.decode(output[0], skip_special_tokens=True)
        return {"text": text}

    return app


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    app = create_app(args.model, args.quant)
    uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    main()
