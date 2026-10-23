"""
vLLM continuous batching benchmark.

Note: This script requires a CUDA GPU and was run on a Kaggle notebook
(2x Tesla T4, 16GB VRAM each), not locally - neither deelopment laptop
has a dedicated GPU. See benchmarks/results.csv for the output
"""

import time
from vllm import LLM, SamplingParams

llm = LLM(model="Qwen/Qwen2.5-1.5B-Instruct")

def benchmark(batch_size, max_tokens_limit=50):
    prompts = ["Explain what a satellite ground station does, in two sentences."] * batch_size
    sampling_params = SamplingParams(max_tokens=max_tokens_limit)

    start = time.time()
    outputs = llm.generate(prompts, sampling_params)
    elapsed = time.time() - start

    total_tokens = sum(len(o.outputs[0].token_ids) for o in outputs)
    tokens_per_sec = total_tokens / elapsed

    print(f"batch_size={batch_size:>3} | elapsed={elapsed:6.2f}s | tokens/sec={tokens_per_sec:8.2f}")
    return tokens_per_sec

if __name__ == "__main__":
    for batch_size in [1, 4, 16, 32]:
        benchmark(batch_size)