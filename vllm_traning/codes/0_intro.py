import vllm
print(vllm.__version__)

from vllm import LLM, SamplingParams

llm = LLM(model="mistralai/Mistral-7B-Instruct-v0.2")

sampling_params = SamplingParams(
    temperature=0.7,
    max_tokens=100
)

prompt = "Explain black holes in simple words."

outputs = llm.generate(prompt, sampling_params)

for output in outputs:
    print(output.outputs[0].text)