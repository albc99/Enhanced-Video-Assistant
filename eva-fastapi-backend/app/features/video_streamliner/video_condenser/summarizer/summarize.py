from transformers import T5Tokenizer, T5ForConditionalGeneration, pipeline
import torch

"""
File: summarize.py
Description: This file contains the classes that are used to summarize the input transcript.
Functionality: This file contains the classes that are used to summarize the input transcript using the T5 and Pegasus models.
"""

class T5Summarizer:
    """
    T5 model summarizer class that can handle variable-length input using tokenization and chunking.
    """
    # refer to: https://huggingface.co/docs/transformers/model_doc/t5
    def __init__(self, model="t5-small") -> None:
        self.model = T5ForConditionalGeneration.from_pretrained(model)
        self.tokenizer = T5Tokenizer.from_pretrained(model)
        self.pipeline_summarizer = pipeline("summarization", model=model)

    def tokenize_and_truncate(self, text, max_length):
        # Tokenize input text 
        inputs = self.tokenizer(text, return_tensors="pt", max_length=max_length, truncation=True)
        return inputs

    def chunk_text(self, text, max_length):

        chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
        return chunks

    def summarize(self, transcript_text, max_length=200, min_length=10, length_penalty=2.0, num_beams=4, max_input_length=512):
        """
        Summarize the given transcript.

        Parameters:
        @transcript_text: The input transcript text to be summarized.
        @max_length : The maximum length of the generated summary.
        @min_length : The minimum length of the generated summary.
        @length_penalty : Length penalty to encourage or discourage longer summaries.
        @num_beams : Number of beams to use in beam search during generation.
        @max_input_length: Maximum length for input text chunks.

        Returns:
        - str: The generated summary of the input transcript.
        """
        # Chunk the input text
        text_chunks = self.chunk_text(transcript_text, max_input_length)
       
        # Summarize each chunk
        summaries = []
        for chunk in text_chunks:
            chunk = "summarize: "+chunk
            # Tokenize and truncate input chunk
            inputs = self.tokenize_and_truncate(chunk, max_input_length)

            # Generate summary for the chunk
            summary_ids = self.model.generate(**inputs, max_length=max_length, min_length=min_length, length_penalty=length_penalty, num_beams=num_beams)

            summary_text = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            summaries.append(summary_text)

        # merge all summaries
        final_summary = " ".join(summaries)
        return final_summary

    def summarize_with_pipeline(self, transcript_text, max_length=200, min_length=10, length_penalty=2.0, num_beams=4):
        """
        Summarize the given transcript using the pipeline approach. Have some issues with input length
        """
        # Generate a summary using the pipeline
        #for some reason this didn't work if input text len > 512 which is default max_len val,and wasn't able to set a new val either
        # so using above tokenizer approach now by tokenizing
        summary = self.pipeline_summarizer(transcript_text, max_length=max_length, min_length=min_length, length_penalty=length_penalty, num_beams=num_beams)

        return summary[0]['summary_text']

class PegasusSummarizer:
    
    """
    Use Pegasus model
    """
    def __init__(self, model_name="google/pegasus-xsum"):
        from transformers import PegasusForConditionalGeneration, PegasusTokenizer
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = PegasusTokenizer.from_pretrained(model_name)
        self.model = PegasusForConditionalGeneration.from_pretrained(model_name).to(self.device)

    def summarize(self, src_text, max_length=150, min_length=50, length_penalty=2.0, num_beams=4):

        #refer to model here: https://huggingface.co/docs/transformers/model_doc/pegasus
        # Tokenize and prepare input batch
        batch = self.tokenizer(src_text, truncation=True, padding="longest", return_tensors="pt").to(self.device)

        # Generate summary
        summarizer = self.model.generate(**batch, max_length=max_length, min_length=min_length, length_penalty=length_penalty, num_beams=num_beams)

        # Decode and return summary
        summary = self.tokenizer.batch_decode(summarizer, skip_special_tokens=True)[0]
        return summary

