import time
from tabulate import tabulate  # For table formatting
import openvino_genai
import fire  # For argument parsing
import ollama  # Import Ollama's Python client
import subprocess  # For running shell commands
from utils import ensure_chat_template, get_device_name  # Importing functions from utils.py

# Color variables
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
    def __init__(self, model_dir, model_name, prompt, system_prompt, device="GPU", output_file="answer.txt", use_ollama=False):
        self.model_dir = model_dir
        self.model_name = model_name  # Model name to be used if Ollama is true
        self.prompt = prompt
        self.system_prompt = system_prompt  # New system prompt parameter
        self.device = device
        self.output_file = output_file  # Output file for the generated answer
        self.use_ollama = use_ollama  # Flag to choose Ollama or OpenVINO

    def initialize_ollama(self):
        """Initialize Ollama server and download the model if not already available."""
        try:
            print("Initializing Ollama server...")
            subprocess.Popen("./ollama serve > ollama.log 2>&1 &", shell=True)
            time.sleep(5)  # Wait for the server to initialize

            # Check server readiness
            for i in range(10):  # Retry for up to 10 seconds
                result = subprocess.run("curl -s http://localhost:11434/status", shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    print("Ollama server is ready!")
                    break
                time.sleep(1)
            else:
                print("Ollama server failed to start within the expected time.")
                raise RuntimeError("Ollama server not ready")

            # Check if the model is already available
            result = subprocess.run("./ollama list", shell=True, capture_output=True, text=True)
            if self.model_name in result.stdout:
                print("Model is already available. Skipping download.")
            else:
                print("Downloading the model...")
                pull_result = subprocess.run(f"./ollama pull {self.model_name}", shell=True, check=True, capture_output=True, text=True)
                print("Model downloaded successfully!")
                print(f"Pull Output: {pull_result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to initialize Ollama or download the model. Error: {e}")
            print(f"Command Output: {e.output}")
            raise

    def run(self):
        """Run the benchmarking tool."""
        global token_count, generated_answer
        token_count = 0  # Initialize token counter
        generated_answer = ""  # Reset generated answer

        # Load the prompt
        with open(self.prompt, "r") as file:
            prompt_content = file.read().strip()

        # Prepend the system prompt to the user's prompt
        full_prompt = self.system_prompt + "\nUser: " + prompt_content

        framework = "Ollama" if self.use_ollama else "OpenVINO-GenAI"

        if self.use_ollama:
            self.initialize_ollama()
            start_time = time.time()
            try:
                # Use the Ollama Python client for chat
                response = ollama.chat(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt_content}
                    ]
                )
                print("Received response from Ollama.")
                end_time = time.time()
                generated_answer = response["content"]  # Extract generated content
                inferencing_time = end_time - start_time
            except ollama.ResponseError as e:
                print(f"Ollama API error: {e}")
                return
        else:
            # Initialize OpenVINO pipeline
            pipe = openvino_genai.LLMPipeline(self.model_dir, self.device)

            # Benchmarking with OpenVINO
            pipe.start_chat()
            start_time = time.time()
            try:
                pipe.generate(full_prompt, streamer=streamer)  # Use the full prompt with system instruction
            finally:
                end_time = time.time()
                pipe.finish_chat()

            generated_answer = generated_answer  # Capture answer from OpenVINO
            inferencing_time = end_time - start_time

        # Calculate metrics
        tokens_per_second = token_count / inferencing_time if inferencing_time > 0 else 0

        # Get device name
        device_name = get_device_name(self.device)

        # Tabular Output
        results = [
            ["Model Directory", self.model_dir],
            ["Model Name", f"{GREEN}{self.model_name}{RESET}"],  # Green colored model name
            ["Framework", f"{GREEN}{framework}{RESET}"],  # Green colored framework
            ["Device", self.device],  # General device classification (CPU, GPU)
            ["Device Name", device_name],  # Detailed device name
            ["Inference Time (s)", f"{inferencing_time:.2f}"],
            ["Tokens/s", f"{GREEN}{tokens_per_second:.2f}{RESET}"]  # Green colored tokens/s
        ]

        print()  # Empty line
        print("Benchmark Results:")  # "Benchmark Results:" in plain text
        print(tabulate(results, tablefmt="grid"))

        # Save the generated answer to a text file
        with open(self.output_file, "w") as output_file:
            output_file.write(generated_answer)

        print(f"\nGenerated answer saved to: {self.output_file}")
        print()  # Empty line
        print()  # Another empty line


def main(
    model_dir: str,
    model_name: str,
    prompt: str,
    system_prompt: str = "You are a helpful assistant.",  # Default system prompt
    device: str = "GPU",
    output_file: str = "answer.txt",  # Default output file name
    use_ollama: bool = False,  # Flag to enable Ollama support
):
    """Benchmarking the model with OpenVINO or Ollama."""
    tool = BenchmarkingTool(
        model_dir=model_dir,
        model_name=model_name,
        prompt=prompt,
        system_prompt=system_prompt,
        device=device,
        output_file=output_file,
        use_ollama=use_ollama
    )
    tool.run()


if __name__ == "__main__":
    fire.Fire(main)
