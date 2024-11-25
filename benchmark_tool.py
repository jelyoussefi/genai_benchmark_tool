#!/usr/bin/env python3
# Benchmarking tool for Hugging Face models with OpenVINO
import argparse
import json
import time
from pathlib import Path
from tabulate import tabulate  # For table formatting
import openvino_genai


def streamer(subword):
    global token_count
    token_count += len(subword.split())
    return False  # Continue generation


def ensure_chat_template(model_dir):
    """Ensure chat_template exists in tokenizer_config.json."""
    tokenizer_config_path = Path(model_dir) / "tokenizer_config.json"
    if not tokenizer_config_path.exists():
        raise FileNotFoundError(f"Tokenizer configuration file not found at {tokenizer_config_path}")

    # Load configuration
    with open(tokenizer_config_path, "r") as file:
        config = json.load(file)

    # Add chat_template if missing
    if "chat_template" not in config:
        config["chat_template"] = json.dumps({
            "system": "You are a helpful assistant.",
            "user": "User: {input}",
            "assistant": "Assistant: {response}"
        })
        with open(tokenizer_config_path, "w") as file:
            json.dump(config, file, indent=4)


def main():
    global token_count
    token_count = 0  # Initialize token counter

    parser = argparse.ArgumentParser(description="Benchmarking tool for Hugging Face models with OpenVINO")
    parser.add_argument("--model_dir", required=True, help="Path to the model directory")
    parser.add_argument("--prompt", required=True, help="Path to the file containing the test prompt")
    parser.add_argument("--device", default="CPU", help="Device to run the model on (default: CPU)")
    args = parser.parse_args()

    # Ensure chat_template exists
    ensure_chat_template(args.model_dir)

    # Load the prompt
    with open(args.prompt, "r") as file:
        prompt_content = file.read().strip()

    # Initialize pipeline
    pipe = openvino_genai.LLMPipeline(args.model_dir, args.device)
    config = openvino_genai.GenerationConfig()
    config.max_new_tokens = 100

    # Benchmarking
    pipe.start_chat()
    start_time = time.time()
    try:
        pipe.generate(prompt_content, config, streamer)
    finally:
        end_time = time.time()
        pipe.finish_chat()

    # Calculate metrics
    inferencing_time = end_time - start_time
    tokens_per_second = token_count / inferencing_time if inferencing_time > 0 else 0

    # Tabular Output
    results = [
        ["Model", args.model_dir],
        ["Device", args.device],
        ["Inference Time (s)", f"{inferencing_time:.2f}"],
        ["Tokens/s", f"{tokens_per_second:.2f}"]
    ]
    print("\nBenchmark Results:")
    print(tabulate(results, tablefmt="grid"))


if __name__ == "__main__":
    main()
