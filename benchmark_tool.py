#!/usr/bin/env python3
# Benchmarking tool for Hugging Face models with OpenVINO
import time
from tabulate import tabulate  # For table formatting
import openvino_genai
import fire  # For argument parsing
from utils import ensure_chat_template, get_device_name  # Importing functions from utils.py

# Color variables
RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"

# Global variable to count tokens
token_count = 0
generated_answer = ""  # Variable to store the generated answer

def streamer(subword):
    global token_count, generated_answer
    token_count += len(subword.split())
    generated_answer += subword  # Capture the generated subword/response
    return False  # Continue generation


class BenchmarkingTool:
    def __init__(self, model_dir, prompt, device="GPU"):
        self.model_dir = model_dir
        self.prompt = prompt
        self.device = device

    def run(self):
        """Run the benchmarking tool."""
        global token_count, generated_answer
        token_count = 0  # Initialize token counter
        generated_answer = ""  # Reset generated answer

        # Ensure chat_template exists
        ensure_chat_template(self.model_dir)

        # Load the prompt
        with open(self.prompt, "r") as file:
            prompt_content = file.read().strip()

        # Initialize pipeline
        pipe = openvino_genai.LLMPipeline(self.model_dir, self.device)
        config = openvino_genai.GenerationConfig()
        #config.max_new_tokens = 1000

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

        # Get device name
        device_name = get_device_name(self.device)

        # Tabular Output
        results = [
            ["Model", self.model_dir],
            ["Device", self.device],  # General device classification (CPU, GPU)
            ["Device Name", device_name],  # Detailed device name
            ["Inference Time (s)", f"{inferencing_time:.2f}"],
            ["Tokens/s", f"{GREEN}{tokens_per_second:.2f}{RESET}"]  # Green colored tokens/s
        ]

        # Print an empty line and the results with "Benchmark Results:" in red
        print()  # Empty line
        print(f"{RED}Benchmark Results:{RESET}")  # "Benchmark Results:" in red
        print(tabulate(results, tablefmt="grid"))

        # Print the generated answer
        print(f"\n{RED}Generated Answer:{RESET}\n{generated_answer}\n")

        # Print two empty lines after the table
        print()  # Empty line
        print()  # Another empty line


def main(
    model_dir: str,
    prompt: str,
    device: str = "GPU",
):
    """Benchmarking the Hugging Face model with OpenVINO."""
    tool = BenchmarkingTool(model_dir=model_dir, prompt=prompt, device=device)
    tool.run()


if __name__ == "__main__":
    fire.Fire(main)
