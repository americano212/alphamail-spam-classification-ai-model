from transformers import BertTokenizer
from transformers import BertForSequenceClassification
import torch
import numpy as np
import time
import json

class inferenceModel:
    def __init__(self):
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        else:
            self.device = torch.device("cpu")
        
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased', cache_dir='/tmp')

        model_path = "/var/task/model_pt" # "./model_pt"
        self.model = BertForSequenceClassification.from_pretrained(model_path)
        
        self.model = self.model.to(self.device)
        self.model.eval()

    def preprocess(self, data):
        if type(data) is not str:
            raise ValueError("data must be of type str")
        s = "[CLS] " + str(data).lower() + " [SEP]"
        tokenized_text = self.tokenizer.tokenize(s)
        input_id = self.tokenizer.convert_tokens_to_ids(tokenized_text)
        input_id = input_id[:min(len(input_id), 512)]
        new_arr = [0] * 512  # 0으로 초기화된 크기 512의 리스트 생성
        new_arr[:len(input_id)] = input_id
        input_id = [new_arr]
        input_id_np = np.array(input_id)
        attention_mask = np.where(input_id_np > 0, 1, 0).tolist()
        attention_mask_np = np.array(attention_mask)
        input_id = torch.from_numpy(input_id_np)
        attention_mask = torch.from_numpy(attention_mask_np)
        return input_id, attention_mask

    def inference(self, input_id, attention_mask):
        self.model.eval()
        st = time.perf_counter()
        output = self.model(input_id, 
                        token_type_ids=None, 
                        attention_mask=attention_mask)
        logits = output[0]
        logits = logits.detach().cpu().numpy()
        logits_flat = np.argmax(logits, axis=1).flatten()
        et = time.perf_counter()
        print(f"time elapsed : {int(round((et - st) * 1000))}ms")

        return logits_flat

def handler(event, context):
    try:
        body = event.get("body-json", {})
        data = body.get("data", "")

        if not data:
            raise ValueError("No data provided")
        model = inferenceModel()
        _id, _mask = model.preprocess(data)
        result = model.inference(_id, _mask)[0]
        
        return {
            'statusCode': 200,
            'body': int(result)
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps(f"Error: {str(e)}")
        }