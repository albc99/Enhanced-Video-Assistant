from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
import re

"""
File: text_similarity.py
Description: This file contains the TextComparer class.
Functionality: This file is used to compare the similarity between two texts using the Sentence Transformers model or TF-IDF.
"""

class TextComparer():
    def __init__(self, language="english", method="model", model_name="sentence-transformers/all-mpnet-base-v2"):
        self.method = method
        if method == "model":
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
        elif method == "vectorizer" or method=="tfidf":
            self.vectorizer = TfidfVectorizer(stop_words="english")
            

    def set_superior_text(self, superior_text):
        """
        Set the text, either summary or full transcript, and handle chunking if too long
        """

        self.superior_text = superior_text

        if self.method == "model":
            tokenize_input = self.tokenizer.encode(superior_text, add_special_tokens=True)

            # Check if the tokenized input is empty or too short
            if not tokenize_input or len(tokenize_input) < 3:
                # Handle the case of empty or short sequences
                print("Error: Empty or short tokenized input.")
                return

            # Check if the tokenized input is too long
            max_input_length = 384  # current (all-mpnet-base-v2) model's maximum input length
            
            if len(tokenize_input) > max_input_length:
                self.superior_text_emb = self.__handle_embedding_for_longer_text(superior_text,max_input_length)

            else:
                # Convert inputs to PyTorch tensors
                input_tensor = torch.tensor([tokenize_input])
                with torch.no_grad():
                    outputs = self.model(input_tensor)
                    cls_emb = outputs.last_hidden_state[:, 0, :]

                self.superior_text_emb = cls_emb.detach().numpy()

        return

    def __handle_embedding_for_longer_text(self,superior_text,max_text_length=384):
        """
        Divide into text into list of sentences and find mean of all embeddings

        inspired from https://towardsdatascience.com/easily-get-high-quality-embeddings-with-sentencetransformers-c61c0169864b
        """
        sentences = list(set(re.findall('[^!?。.？！]+[!?。.？！]?', superior_text)))

        # Check if the tokenized input is empty or too short
        if not sentences or len(sentences) < 1:
            # Handle the case of empty or short sequences
            print("Error: Empty or short sentences.")
            return

        current_chunk = []
        chunks = []
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_text_length:
                current_chunk.append(sentence)
            else:
                chunks.append("".join(current_chunk))
                current_chunk = [sentence]

        if current_chunk:
            chunks.append("".join(current_chunk))

        # Convert inputs to PyTorch tensors
        # Process each chunk and collect embeddings
        sentence_embeddings = []
        with torch.no_grad():
            for sentence in chunks:
                print(len(sentence))
                input_ids = self.tokenizer.encode(sentence, add_special_tokens=True,max_length=512)
                print(len(input_ids))
                input_tensor = torch.tensor([input_ids]) 
                outputs = self.model(input_tensor)
                cls_emb = outputs.last_hidden_state[:, 0, :]
                sentence_embeddings.append(cls_emb.detach().numpy())

        # Aggregate embeddings by taking the mean
        return torch.mean(torch.stack([torch.tensor(embedding) for embedding in sentence_embeddings]), dim=0)

    
    def get_similarity_score(self, text1):
        """
        
        """
        
        if self.method == "model":
            return self.__get_similarity_model(text1)
        elif self.method == "vectorizer" or self.method=="tfidf":
            return self.__get_similarity_tfidf(text1)
        else:
            raise ValueError("Unsupported similarity method. Use 'model' or 'tfidf'.")

    def __get_similarity_model(self, text1):
        """
        
        """
        tokenize_input = self.tokenizer.encode(text1, add_special_tokens=True)
        # Check if the tokenized input is empty or too short
        if not tokenize_input or len(tokenize_input) < 3:
            # Handle the case of empty or short sequences
            print("Error: Empty or short tokenized input.")
            return 0

        # Check if the tokenized input is too long
        max_input_length = 384  # current (all-mpnet-base-v2) model's maximum input length
        
        if len(tokenize_input) > max_input_length:
            cls_emb = self.__handle_embedding_for_longer_text(text1)

        else:
            # Convert inputs to PyTorch tensors
            input_tensor = torch.tensor([tokenize_input])
            with torch.no_grad():
                outputs = self.model(input_tensor)
                cls_emb = outputs.last_hidden_state[:, 0, :]

        cls_emb = cls_emb.detach().numpy()
        similarity = self.__cosine_similarity([cls_emb, self.superior_text_emb])
        return similarity

    def __get_similarity_tfidf(self, text1):
        """
        
        """
        tfidf_matrix = self.vectorizer.fit_transform([self.superior_text, text1])
        similarity_matrix = cosine_similarity(tfidf_matrix)
        similarity = similarity_matrix[0, 1]
        return similarity

    def __cosine_similarity(self, text_encodings):
        # Flatten the arrays to make sure they have shape (768,)
        flat_encoding_0 = text_encodings[0].flatten()
        flat_encoding_1 = text_encodings[1].flatten()

        # Calculate the cosine similarity between the flattened embeddings
        similarity = np.dot(flat_encoding_0, flat_encoding_1) / (np.linalg.norm(flat_encoding_0) * np.linalg.norm(flat_encoding_1))
        return similarity

