#!/usr/bin/env python3
"""Direct test of MLX model without server"""

from mlx_lm import load, generate

print("Loading Qwen3-8B MLX model directly...")
model, tokenizer = load("mlx_qwen3_converted")

print("Model loaded successfully!")

# Test generation
prompt = "Hello, my name is"
print(f"\nPrompt: {prompt}")
print("Generating response...")

response = generate(
    model, 
    tokenizer, 
    prompt=prompt,
    max_tokens=50
)

print(f"Response: {response}")
print("\nModel is working correctly!")