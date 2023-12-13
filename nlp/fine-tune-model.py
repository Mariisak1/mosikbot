from transformers import AutoTokenizer, AutoModelForSequenceClassification, DataCollatorWithPadding
from datasets import load_dataset
from transformers import TrainingArguments, Trainer
import numpy as np
import evaluate

model_name = "distilbert-base-uncased"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=6)

raw_datasets = load_dataset("dair-ai/emotion")

train_dataset = raw_datasets["train"]

# tokenizes a batch of text and returns the tokenized batch
def tokenize(batch):
    """
    Tokenizes a batch of text and returns the tokenized batch

    Parameters
    ----------
    batch : str
        Batch of text to be tokenized
    
    Returns
    -------
    dict
        Tokenized batch
    """
    return tokenizer(batch["text"], truncation=True)

# tokenizes the datasets (train, validation and test)
tokenized_datasets = raw_datasets.map(tokenize, batched=True, batch_size=None)

# creates a data collator that will be used to pad the dataset
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

training_args = TrainingArguments(output_dir="sentilbert", evaluation_strategy="epoch")

accuracy_metric = evaluate.load("accuracy")
f1_metric = evaluate.load("f1")

# computes the metrics of the model to evaluate 
def compute_metrics(eval_pred):
    """
    Computes and returns the metrics of the model to evaluate, in this case accuracy and f1

    Parameters
    ----------
    eval_pred : str
        Evaluation prediction

    Returns
    -------
    dict
        Metrics of the model
    """
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return {
        "accuracy": accuracy_metric.compute(predictions=predictions, references=labels),
        "f1": f1_metric.compute(predictions=predictions, references=labels, average="weighted")
    }

# defined a trainer that will be used to train the model with our dataset
trainer = Trainer(
    model,
    training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["validation"],
    data_collator=data_collator,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics
)

# trains the model with our datasets according to the training arguments
trainer.train()
