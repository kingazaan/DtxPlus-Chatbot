from transformers import BertTokenizer, BertForSequenceClassification
import torch

# Load tokenizer and model from the results folder
tokenizer = BertTokenizer.from_pretrained('ml_models/classifier_model')
model = BertForSequenceClassification.from_pretrained('ml_models/classifier_model')

# Define classification function
def classify_text(input_text):
    # Tokenize input
    inputs = tokenizer(input_text, return_tensors='pt', padding=True, truncation=True)
    
    # Perform classification
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Get the predicted label
    predicted_class = torch.argmax(outputs.logits, dim=1).item()
    
    return predicted_class

# if __name__ == "__main__":
#     test_text = "What are the symptoms of seasonal allergies?"
#     predicted_label = classify_text(test_text)
#     print(f"Predicted label: {predicted_label}")
