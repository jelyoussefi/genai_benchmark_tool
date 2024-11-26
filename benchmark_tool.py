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
    def __init__(self, model_dir, prompt, system_prompt, device="GPU", output_file="answer.txt"):
        self.model_dir = model_dir
        self.prompt = prompt
        self.system_prompt = system_prompt  # New system prompt parameter
        self.device = device
        self.output_file = output_file  # Output file for the generated answer

    def run(self):
        """Run the benchmarking tool."""
        global token_count, generated_answer
        token_count = 0  # Initialize token counter
        generated_answer = ""  # Reset generated answer

        # Ensure chat_template exists
        # ensure_chat_template(self.model_dir)

        # Load the prompt
        with open(self.prompt, "r") as file:
            prompt_content = file.read().strip()

        # Prepend the system prompt to the user's prompt
        full_prompt = self.system_prompt + "\nUser: " + prompt_content

        # Initialize pipeline
        pipe = openvino_genai.LLMPipeline(self.model_dir, self.device)
        config = openvino_genai.GenerationConfig()
        config.max_new_tokens = 1000

        # Benchmarking
        pipe.start_chat()
        start_time = time.time()
        try:
            pipe.generate(full_prompt, config, streamer)  # Use the full prompt with system instruction
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

        # Save the generated answer to a text file
        with open(self.output_file, "w") as output_file:
            output_file.write(generated_answer)

        # Print where the answer is saved
        print(f"\n{RED}Generated answer saved to:{RESET} {self.output_file}")

        # Optionally, print two empty lines after the table
        print()  # Empty line
        print()  # Another empty line

def main(
    model_dir: str,
    prompt: str,
    system_prompt: str = "You are a helpful assistant.",  # Default system prompt
    device: str = "GPU",
    output_file: str = "answer.txt",  # Default output file name
):
    """Benchmarking the Hugging Face model with OpenVINO."""
    tool = BenchmarkingTool(model_dir=model_dir, prompt=prompt, system_prompt=system_prompt, device=device, output_file=output_file)
    tool.run()

if __name__ == "__main__":
    fire.Fire(main)
