"""
    First the transformers library needs to be installed using the below command:
        ```!pip install -q transformers```
"""
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
#

def load_stress_detector_model_tokenizer():
    tokenizer = AutoTokenizer.from_pretrained("/app/models/XLM-RoBERTa-FineTuned-With-Dreaddit" , local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained("/app/models/XLM-RoBERTa-FineTuned-With-Dreaddit" , local_files_only=True )
    return tokenizer, model


def check_for_stress_in_text(input_text, stress_model_detc, stress_tokenizer_detc):
    print("hereeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee test : ", input_text)
    inputs = stress_tokenizer_detc(input_text, return_tensors="pt")
    with torch.no_grad():
        logits = stress_model_detc(**inputs).logits
    prob_logits = torch.nn.functional.softmax(logits, dim=-1)
    return {"Not Stressed": prob_logits[0][0].item(), "Stressed": prob_logits[0][1].item()}
