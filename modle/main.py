"""main.py
Simple script to load LLaVA-Med-7B from Hugging Face and run a single image-text prompt.

Usage (in conda env `llava-med`):
    python main.py \
        --model microsoft/llava-med-v1.5-mistral-7b \
        --image path/to/xray.png \
        --prompt "请描述这张X光片中的异常情况"

If --image is omitted the model will answer text-only questions.

NOTE: Make sure you have installed the correct versions of transformers (>=4.41),
      accelerate, bitsandbytes, and that a CUDA GPU is available.
"""

import argparse
from pathlib import Path

import torch
from PIL import Image
from transformers import (
    LlavaForConditionalGeneration,
    AutoProcessor,
    BitsAndBytesConfig,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run LLaVA-Med-7B prompt")
    parser.add_argument(
        "--model",
        type=str,
        default="microsoft/llava-med-v1.5-mistral-7b",
        help="Hugging Face model ID or local directory",
    )
    parser.add_argument("--image", type=str, default=None, help="Path to image file")
    parser.add_argument(
        "--prompt",
        type=str,
        default="这是什么？",
        help="User question / instruction (Chinese or English)",
    )
    parser.add_argument(
        "--load-8bit", action="store_true", help="Load model with 8-bit quantisation"
    )
    return parser.parse_args()


def load_model(model_id: str, load_8bit: bool = False):
    """Load LLaVA-Med-7B model + processor."""
    print(f"[INFO] Loading model: {model_id} (8-bit={load_8bit})")

    # In 8-bit mode we let 🤗 Accelerate place the quantised weights automatically.
    if load_8bit:
        bnb_cfg = BitsAndBytesConfig(load_in_8bit=True, llm_int8_enable_fp32_cpu_offload=True)
        model = LlavaForConditionalGeneration.from_pretrained(
            model_id,
            device_map="auto",              # place layers on GPU(s) automatically
            low_cpu_mem_usage=True,
            quantization_config=bnb_cfg,
        )
    else:
        model = LlavaForConditionalGeneration.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            device_map="auto",
            low_cpu_mem_usage=True,
        ).to("cuda")

    model.eval()
    processor = AutoProcessor.from_pretrained(model_id)
    return model, processor


def main() -> None:
    args = parse_args()

    model, processor = load_model(args.model, args.load_8bit)

    image = None
    if args.image:
        image_path = Path(args.image)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        image = Image.open(image_path).convert("RGB")

    # Prepare inputs for LLaVA
    prompt = args.prompt
    inputs = processor(prompt, images=image, return_tensors="pt").to("cuda")

    with torch.inference_mode():
        output_ids = model.generate(**inputs, max_new_tokens=512)
    answer = processor.batch_decode(output_ids, skip_special_tokens=True)[0].strip()

    print("\n===== Model Answer =====\n")
    print(answer)


if __name__ == "__main__":
    main()
