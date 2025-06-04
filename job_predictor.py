from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

<<<<<<< HEAD

# Load model directly

tokenizer = AutoTokenizer.from_pretrained("Tobi3172/finetuned_BERT_for_JobPrediction")
model = AutoModelForSequenceClassification.from_pretrained("Tobi3172/finetuned_BERT_for_JobPrediction")

=======
# Load your fine-tuned BERT model (placeholder paths)
#MODEL_PATH = "fine_tuned_model"
#TOKENIZER_PATH = "fine_tuned_model"

# Load the model
#model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

# Load the tokenizer
#tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH)

tokenizer = AutoTokenizer.from_pretrained("Tobi3172/bert_based_job_predictor")
model = AutoModelForSequenceClassification.from_pretrained("Tobi3172/bert_based_job_predictor")

>>>>>>> 36b3fe0bd1a68ef566ba5076a29c1a2d5c7f4988

def predict_job_title(text):
    try:
        # Create input text
        input_text = text
        
        # Tokenize input
        inputs = tokenizer(
            input_text,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
        
        # Make prediction
        outputs = model(**inputs)
        predicted_class = torch.argmax(outputs.logits, dim=1).item()
        probabilities = torch.softmax(outputs.logits, dim=1)
        confidence = torch.max(probabilities).item()  # Get highest probability
        
        # Map class index to job title
        job_titles = {
            0: "Web Developer",
            1: "Software Developer",
            2: "Security Analyst",
            3: "Database Administrator",
            4: "Systems Administrator",
            5: "Project manager",
            6: "Network Administrator",
            7: "Java Developer",
            8: "Python Developer",
            9: "Front End Developer"
            # Add your actual job titles
        }
        
        return {
            "title": job_titles.get(predicted_class, "General Professional"),
            "confidence": round(confidence * 100, 1)  # Convert to percentage
        }
    
    except Exception as e:
        raise RuntimeError(f"Prediction failed: {str(e)}")
