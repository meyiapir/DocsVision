import os
import torch
from transformers import BertTokenizer
import re

class InferenceModel:
    def __init__(self, model_path):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = torch.load(model_path, map_location=self.device)
        self.tokenizer = BertTokenizer.from_pretrained("DeepPavlov/rubert-base-cased")
        self.model.to(self.device)
        self.model.eval()

        self.DOC_TYPES_DICT: dict[str, str] = {
            "proxy": ["доверенность"],
            "contract": ["договор"],
            "act": ["акт"],
            "application": ["заявление"],
            "order": ["приказ"],
            "invoice": ["счёт"],
            "bill": ["приложение"],
            "arrangement": ["соглашение"],
            "contractoffer": ["договор оферты"],
            "statute": ["устав"],
            "determination": ["решение"]
        }


    @staticmethod
    def clean_text(text):
        cleaned_text = re.sub(r'[^а-яА-Яa-zA-Z0-9]', ' ', text)
        cleaned_text = cleaned_text.lower()
        return cleaned_text

    def predict(self, text):
        text = self.clean_text(text)
        inputs = self.tokenizer(text, padding="max_length", truncation=True, max_length=512, return_tensors="pt")
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
        with torch.no_grad():
            outputs = self.model(**inputs)
        logits = outputs.logits
        prediction = torch.argmax(logits, dim=1).cpu().numpy()[0]
        if prediction == 7:
            check_class = self.find_by_name_frequency(text)
            if check_class is not None:
                prediction = check_class
        return prediction

    def find_by_name_frequency(self, text):
        r = []
        for i, document_type in enumerate(self.DOC_TYPES_DICT):
            count = 0
            for word in self.DOC_TYPES_DICT[document_type]:
                count = text.lower().count(f'{word.lower()} ')
            count /= len(self.DOC_TYPES_DICT[document_type])

            r.append((tuple(self.DOC_TYPES_DICT.keys())[i], count))
        r.sort(reverse=True, key=lambda x: x[1])
        counts = list(map(lambda x: x[1], r))
        score = (counts[0] - counts[1])/(counts[0] or 1) if counts[0] else 0
        if score >= 0.5:
            return list(self.DOC_TYPES_DICT.keys()).index(r[0][0])
        else:
            return None
