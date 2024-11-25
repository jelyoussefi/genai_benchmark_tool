#!/usr/bin/env python3
# Benchmarking tool for Hugging Face models with OpenVINO
import argparse
import json
import os
import time
from pathlib import Path
import openvino_genai


def streamer(subword):
    global token_count
    token_count += len(subword.split())
    print(subword, end='', flush=True)
    return False  # Continue generation


def check_and_fix_chat_template(model_dir):
    """Check if chat_template exists in tokenizer_config.json and add it as a string if missing."""
    tokenizer_config_path = Path(model_dir) / "tokenizer_config.json"
    if not tokenizer_config_path.exists():
        raise FileNotFoundError(f"Tokenizer configuration file not found at {tokenizer_config_path}")

    # Read the tokenizer configuration
    with open(tokenizer_config_path, "r") as file:
        config = json.load(file)

    # Check for chat_template
    if "chat_template" not in config:
        print("Adding default chat_template to tokenizer_config.json...")
        # Add chat_template as a properly stringified JSON
        config["chat_template"] = json.dumps({
            "system": "You are a helpful assistant.",
            "user": "User: {input}",
            "assistant": "Assistant: {response}"
        })
        # Save the updated configuration
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

    # Check and fix chat_template in tokenizer configuration
    check_and_fix_chat_template(args.model_dir)

    # Load the prompt
    try:
        with open(args.prompt, "r") as file:
            prompt_content = file.read().strip()
    except FileNotFoundError:
        print(f"Error: Prompt file '{args.prompt}' not found.")
        return
    except Exception as e:
        print(f"Error reading the prompt file '{args.prompt}': {e}")
        return

    # Initialize the OpenVINO pipeline
    pipe = openvino_genai.LLMPipeline(args.model_dir, args.device)
    config = openvino_genai.GenerationConfig()
    config.max_new_tokens = 100

    # Benchmarking
    print(f"Benchmarking the model {args.model_dir} with {args.prompt}...")
    pipe.start_chat()
    try:
        start_time = time.time()
        pipe.generate(prompt_content, config, streamer)
        end_time = time.time()

        # Calculate metrics
        inferencing_time = end_time - start_time
        tokens_per_second = token_count / inferencing_time if inferencing_time > 0 else 0

        print(f"\n----------")
        print(f"Inferencing time: {inferencing_time:.4f} seconds")
        print(f"Tokens generated: {token_count}")
        print(f"Tokens per second: {tokens_per_second:.2f}")
    finally:
        pipe.finish_chat()


if __name__ == "__main__":
    main()
