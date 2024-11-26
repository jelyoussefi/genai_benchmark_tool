import json
from pathlib import Path

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

def get_device_name(device):
    """Return the name of the device based on the specified input (CPU or GPU)."""
    if device == "CPU":
        return get_cpu_model()
    elif device == "GPU":
        return get_gpu_model()
    else:
        return "Unknown Device"

def get_cpu_model():
    """Return the CPU model."""
    import platform
    try:
        cpu_model = platform.uname().processor or platform.processor()
        if not cpu_model or cpu_model == "x86_64" and platform.system() == "Linux":
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        cpu_model = line.split(":")[1].strip()
                        break
        return cpu_model or "CPU model not available"
    except Exception as e:
        print(f"Error fetching CPU model: {e}")
        return "CPU model not available"

def get_gpu_model():
    """Return the GPU model."""
    import subprocess
    try:
        gpu_model = "GPU model not available"
        result = subprocess.run(["lspci"], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "VGA compatible controller" in line or "3D controller" in line:
                if "Intel" in line:
                    gpu_model = line.split(": ")[1]
                    break
        return gpu_model.replace("Intel Corporation", "").strip()
    except Exception as e:
        print(f"Error fetching GPU model: {e}")
        return "GPU model not available"
