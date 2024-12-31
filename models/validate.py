import base64
from config import Config
from transformers import AutoProcessor
from huggingface_hub import hf_hub_download, list_repo_files
from qwen_vl_utils import process_vision_info
from transformers import Qwen2VLForConditionalGeneration
import os
import logging  
import torch
import requests

MODEL_REPO = "Qwen/Qwen2-VL-2B-Instruct"
DESTINATION_FOLDER = "./qwen2-vl"
VALIDATE_PROMPT = "please check the screenshot and tell me whether you can find the following element or not. if you can find the element in the screenshot, please directly answer 'found'. if you can't find it, answer 'not found'."

class Validate:
    def __init__(self, config: Config, run_path):
        self._run_path = run_path
        self._config = config

    def validate(self, query, validation):
        pass
    
class LocalValidate(Validate):
    def __init__(self, config: Config, run_path):
        super().__init__(config, run_path)
        logging.info("LocalValidate initialized completely. ")

        os.makedirs(DESTINATION_FOLDER, exist_ok=True)
        files = list_repo_files(repo_id=MODEL_REPO)
        for file in files:
            file_path = hf_hub_download(repo_id=MODEL_REPO, filename=file, local_dir=DESTINATION_FOLDER)
            print(f"Downloaded {file} to {file_path}")

        # load pretrained model
        model = Qwen2VLForConditionalGeneration.from_pretrained(
            DESTINATION_FOLDER,
            torch_dtype=torch.float32,
            device_map="cpu",
            low_cpu_mem_usage=True,
        )

        # load tokenizer and processor
        processor = AutoProcessor.from_pretrained("Qwen/Qwen2-VL-2B-Instruct")
        self._model = model
        self._processor = processor

    def validate(self, query, validation) -> bool:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": VALIDATE_PROMPT},
                    {"type": "image", "image": os.path.join(self._run_path, "records/screencaps", f"{query}_validation.png")},
                    {"type": "text", "text": validation}
                ],
            }
        ]
        text = self._processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True,
        )
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = self._processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )
        inputs = inputs.to(self._model.device)
        generated_ids = self._model.generate(**inputs, max_new_tokens=128)
        generated_ids_trimmed = [
            out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]

        output_text = self._processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )[0].lower().strip()
        logging.info(f"The validation result is: {output_text}")
        return output_text == "found"
    
class RemoteValidate(Validate):
    def __init__(self, config: Config, run_path):
        super().__init__(config, run_path)
        self.host = config.validate_model_host
        logging.info("RemoteValidate initialized completely. ")

    def validate(self, query, validation) -> bool:
        base64_image = None
        image_path = os.path.join(self._run_path, "records/screencaps", f"{query}_validation.png")
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        messages = [
            {
                "role": "user", 
                "content": [
                    {"type": "text", "text": VALIDATE_PROMPT},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                    {"type": "text", "text": validation}
                ]
            }
        ]

        response = requests.post(
            f"{self.host}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json={
                "model": "Qwen/Qwen2-VL-2B-Instruct",
                "messages": messages
            }
        )

        output_text = response.json()["choices"][0]["message"]["content"].lower().strip()
        logging.info(f"The validation result is: {output_text}")
        return output_text == "found"
