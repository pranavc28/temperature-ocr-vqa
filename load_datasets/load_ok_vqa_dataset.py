import os
from datasets import load_dataset
from typing import Union


class OKVQA:
    def __init__(self, dataset_name: str | None = "howard-hou/OCR-VQA", num_images: Union[int, str] | None = 1000):
        if num_images == "all":
            split = "validation"
        else:
            split = f"validation[:{num_images}]"
        self.dataset = load_dataset(dataset_name, split=split)
        print(f"Loaded {len(self.dataset)} images")

    def get_dataset(self):
        return self.dataset