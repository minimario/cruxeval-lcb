import os
import json
from itertools import product

from openai_prompt import (
    batch_prompt_direct_input,
    batch_prompt_cot_input,
    batch_prompt_direct_output,
    batch_prompt_cot_output,
)

from datasets import load_dataset

def run_openai(model, mode, cot, temperature):
    dataset = load_dataset("minimario/livecodebench-execute-v3")["test"]
    # dataset = [json.loads(l) for l in open("../data/cruxeval.jsonl", "r").readlines()]

    if mode == "input": prompts = [(data["code"], data["output"]) for data in dataset] 
    else: prompts = [(data["code"], data["input"]) for data in dataset] 
    
    if cot: 
        max_tokens = 1000
    else: 
        max_tokens = 100

    fn = {
        (True, "input"): batch_prompt_cot_input,
        (True, "output"): batch_prompt_cot_output,
        (False, "input"): batch_prompt_direct_input,
        (False, "output"): batch_prompt_direct_output,
    }[(cot, mode)]

    outputs = fn(
        prompts,
        temperature=temperature,
        n=10,
        model=model,
        max_tokens=max_tokens,
        stop=["[/ANSWER]"],
    )

    save_dir = get_save_dir(mode, model, cot, temperature)
    outputs_dict = {f"sample_{i}": [j[0] for j in o] for i, o in enumerate(outputs)}
    print(f"Saving to {save_dir}")
    json.dump(outputs_dict, open(save_dir, "w"))
    return outputs

def get_save_dir(mode, model, cot, temperature):
    if cot: 
        base_dir = f"../model_generations/{model}+cot_temp{temperature}_{mode}"
    else:
        base_dir = f"../model_generations/{model}_temp{temperature}_{mode}"
    try: os.makedirs(base_dir)
    except: pass
    return os.path.join(base_dir, "generations.json")
        
if __name__ == "__main__":
    models = ["gpt-4-1106-preview"]
    # models = ["gpt-3.5-turbo-0613"]
    modes = ["output"]
    cots = [False, True]
    temperatures = [0.2]
    for model, mode, cot, temperature in product(models, modes, cots, temperatures):
        run_openai(model, mode, cot, temperature)
        # break # comment out to run the whole thing $$