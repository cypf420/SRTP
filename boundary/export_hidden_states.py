from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export the last-token hidden states for a prompt list.")
    parser.add_argument("--model-id", required=True, help="Local or remote Hugging Face model identifier.")
    parser.add_argument("--input-jsonl", required=True, help="JSONL file with a `text` field per row.")
    parser.add_argument("--output-npy", required=True, help="Output .npy path.")
    parser.add_argument("--max-length", type=int, default=1024, help="Tokenizer truncation length.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tokenizer = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
    )
    model.eval()

    vectors = []
    with Path(args.input_jsonl).open("r", encoding="utf-8") as handle:
        for line in handle:
            text = json.loads(line)["text"]
            encoded = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=args.max_length,
            )
            encoded = {key: value.to(model.device) for key, value in encoded.items()}
            with torch.no_grad():
                outputs = model(**encoded, output_hidden_states=True)
            last_hidden = outputs.hidden_states[-1][0, -1, :].detach().float().cpu().numpy()
            vectors.append(last_hidden)

    stacked = np.stack(vectors, axis=0)
    target = Path(args.output_npy)
    target.parent.mkdir(parents=True, exist_ok=True)
    np.save(target, stacked)
    print(f"Saved hidden states with shape {stacked.shape} to {target}")


if __name__ == "__main__":
    main()
