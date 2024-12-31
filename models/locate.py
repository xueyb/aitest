import base64
import os
import ast
import torch
from config import Config
import logging
import requests
from io import BytesIO
from PIL import Image, ImageDraw
from mobile.client import Coordinate
from qwen_vl_utils import process_vision_info
from huggingface_hub import hf_hub_download, list_repo_files
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor

MODEL_REPO = "showlab/ShowUI-2B"
DESTINATION_FOLDER = "./showui-2b"
LOCATE_PROMPT = "Based on the screenshot of the page, I give a text description and you give its corresponding location. The coordinate represents a clickable location [x, y] for an element, which is a relative coordinate on the screenshot, scaled from 0 to 1."   

class RatioCoordinate:
    def __init__(self, x_ratio, y_ratio):
        self.x_ratio = x_ratio
        self.y_ratio = y_ratio

    def to_pixel(self, device_pixel_config) -> Coordinate:
        return Coordinate(x_pixel=device_pixel_config[0] * self.x_ratio, y_pixel=device_pixel_config[1] * self.y_ratio)

class Locate:
    def __init__(self, config: Config, run_path):
        self._device_pixel_config = (config.device_width, config.device_height)
        self._run_path = run_path
        logging.info(f"Project absolute path: {self._run_path}")
    
    def _locate_ratio(self, query) -> RatioCoordinate:
        pass
    
    def _draw_point(self, image_input, point=None, radius=5):
        if isinstance(image_input, str):
            image = Image.open(BytesIO(requests.get(image_input, timeout=10).content)) if image_input.startswith('http') else Image.open(image_input)
        else:
            image = image_input

        if point:
            x, y = point[0] * image.width, point[1] * image.height
            ImageDraw.Draw(image).ellipse((x - radius, y - radius, x + radius, y + radius), fill='red')
        return image
    
    def locate_pixel(self, query):
        ratio_coordinate = self._locate_ratio(query)
        coordinate = ratio_coordinate.to_pixel(self._device_pixel_config)
        logging.info(f"The location pixel is: {coordinate.x_pixel}, {coordinate.y_pixel}")
        return coordinate

class LocalLocate(Locate):
    def __init__(self, config: Config, run_path):
        super().__init__(config, run_path)
        logging.info("LocalLocate initialized completely. ")

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

    def _locate_ratio(self, query) -> RatioCoordinate:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": LOCATE_PROMPT},
                    {"type": "image", "image": os.path.join(self._run_path, "records/screencaps", f"{query}.png")},
                    {"type": "text", "text": query}
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
        )[0]

        click_xy = ast.literal_eval(output_text)
        # [0.73, 0.21]

        marked_image = self._draw_point(os.path.join(self._run_path, "records/screencaps", f"{query}.png"), click_xy)
        marked_image.save(os.path.join(self._run_path, "records/screencaps", f"{query}.png"))
        return RatioCoordinate(x_ratio=click_xy[0], y_ratio=click_xy[1])

class RemoteLocate(Locate):
    def __init__(self, config: Config, run_path):
        super().__init__(config, run_path)
        self.host = config.locate_model_host
        logging.info("RemoteLocate initialized completely. ")

    def _locate_ratio(self, query) -> RatioCoordinate:
        base64_image = None
        image_path = os.path.join(self._run_path, "records/screencaps", f"{query}.png")
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": LOCATE_PROMPT},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                    {"type": "text", "text": query}
                ]
            }
        ]

        response = requests.post(
            f"{self.host}/v1/chat/completions", 
            headers={"Content-Type": "application/json"},
            json={
                "model": "showlab/ShowUI-2B",
                "messages": messages
            }
        )

        click_xy = ast.literal_eval(response.json()["choices"][0]["message"]["content"])
        marked_image = self._draw_point(image_path, click_xy)
        marked_image.save(image_path)
        return RatioCoordinate(x_ratio=click_xy[0], y_ratio=click_xy[1])

    def _marked_image(self, query, image_path):
        target_path = os.path.join(self._run_path, "records/screencaps", f"{query}.png")

        try:
            os.rename(image_path, target_path)
            return target_path
        except Exception as e:
            raise Exception(f"move marked image failed: {str(e)}") from e