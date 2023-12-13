from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
from torch.nn.functional import softmax

model = AutoModelForSequenceClassification.from_pretrained("sentiment-trainer/checkpoint-6000")
model.eval()

tokenizer = AutoTokenizer.from_pretrained("sentiment-trainer/checkpoint-6000")

sentence = ["I love you", "I'm surprised", "I don't care", "I'm so sad", "I'm so happy", "I'm so angry"]

batch = tokenizer(sentence, padding=True, truncation=True, return_tensors="pt")

# the model predicts the mood of the sentences provided
with torch.no_grad():  
    outputs = model(**batch)
    print(outputs)
    predictions = torch.softmax(outputs.logits, dim=1)
    print(predictions)
    label_ids = torch.argmax(predictions, dim=1).tolist()
    print(label_ids)
    print(f"Predicted labels: {label_ids}")