from transformers import AutoTokenizer,AutoModel,T5Tokenizer, T5ForConditionalGeneration,AutoModelForSpeechSeq2Seq
import os

# from https://fgiasson.com/blog/index.php/2023/08/23/how-to-deploy-hugging-face-models-in-a-docker-container/

def download_model(model_path, model_name):
    """Download a Hugging Face model and tokenizer to the specified directory"""
    # Check if the directory already exists
    if not os.path.exists(model_path):
        # Create the directory
        os.makedirs(model_path)

    if "t5" in model_name:
        model = T5ForConditionalGeneration.from_pretrained(model_name)
        tokenizer = T5Tokenizer.from_pretrained(model_name)

    elif "sentence-transformers" in model_name:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name)

    elif "cardiffnlp" in model_name:
        tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment-latest")
        model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment-latest")
    # for openai whisper models
    else:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSpeechSeq2Seq.from_pretrained(model_name)
    # Save the model and tokenizer to the specified directory
    model.save_pretrained(model_path)
    tokenizer.save_pretrained(model_path)

from transformers import AutoTokenizer, AutoModelForSequenceClassification

download_model("models/","cardiffnlp/twitter-roberta-base-sentiment-latest")
download_model('models/', 't5-base')
download_model('models/', 't5-small')
download_model('models', 'sentence-transformers/all-mpnet-base-v2')