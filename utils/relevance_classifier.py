from transformers import pipeline

classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

def is_relevant(text, threshold=0.9):
    try:
        result = classifier(text[:512])[0]
        return result["label"] == "POSITIVE" and result["score"] > threshold
    except:
        return False
