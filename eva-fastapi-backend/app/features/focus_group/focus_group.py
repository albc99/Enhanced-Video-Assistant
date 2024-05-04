from openai import AzureOpenAI
from transformers import pipeline
import json
import textwrap
import json
import datetime

"""
File: focus_group.py
Description: This file contains the FocusGroup class.
Functionality: This class is used to analyze the sentiment, tone, engagement, and clarity of a video transcript.
"""
with open('/features/credentials.json', 'r') as file:
    data = json.load(file)

# Assign values from the JSON file to variables
AZURE_OPENAI_KEY = data['AZURE_OPENAI_KEY']

class FocusGroup():
    """
    """
    def __init__(self):
        """
        """    
        self.pipe = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
        with open('/features/credentials.json', 'r') as file:
            self.data = json.load(file)


    def run(self,transcript):
        """
        Get feedback 
        """
        engagement_clarity_feedback = json.loads(self.__get_feedback_eng_clarity(transcript=transcript))
        sentiment_feedback,clip_tones = self.__get_feedback_sentiments(transcript=transcript)
        tone_feedback = self.__get_feedback_tone(transcript=transcript)
        
        #merge both the feedbacks
        sentiment_feedback.update(engagement_clarity_feedback)
        print(transcript)
        return sentiment_feedback,clip_tones, tone_feedback
    
    def run_no_audio(self,labels):
        """
        Get feedback 
        """
        def strip_start_end_times(data):
            for item in data:
                if "instances" in item:
                    for instance in item["instances"]:
                        if "adjustedStart" in instance:
                            del instance["adjustedStart"]
                        if "adjustedEnd" in instance:
                            del instance["adjustedEnd"]
                        if "confidence" in instance:
                            del instance['confidence']
                if "language" in item:
                    del item['language']

        strip_start_end_times(labels)
        # Multiply the timestamps by 2
        for clip in labels:
            if "instances" in clip:
                for instance in clip["instances"]:
                    if "start" in instance:
                        instance["start"] *= 2
                    if "end" in instance:
                        instance["end"] *= 2

        self.labels_jstr = json.dumps(labels)

        engagement_clarity_feedback = json.loads(self.__get_feedback_eng_clarity_no_audio(labels=self.labels_jstr))
        sentiment_feedback,clip_tones = ({}, [])

        tone_feedback = json.loads(self.__get_tone_no_audio(labels=self.labels_jstr))
        #merge both the feedbacks
        sentiment_feedback.update(engagement_clarity_feedback)

        return sentiment_feedback,clip_tones, tone_feedback
    
    def __get_feedback_sentiments(self,transcript):
        """
        Get feedback on sentiments
        """

        text_values = [segment['text'] for segment in transcript['segments']]
        clip_tones = []
        #get sentiment scores for each clip
        sentiment_scores = self.pipe(text_values)
        for i,segment in enumerate(transcript["segments"]):
            segment["sentiment_label"] = sentiment_scores[i]["label"]
            segment["sentiment_score"] = sentiment_scores[i]["score"]
            clip_tones.append({"start":segment["start"],"end":segment["end"],"sentiment_label":segment["sentiment_label"],"sentiment_score":segment["sentiment_score"]})
        sentiment_output = self.__analyze_sentiments(sentiments_dict=transcript)
        return sentiment_output,clip_tones
    
    def __analyze_sentiments(self,sentiments_dict):
        """
        Analyze the sentiment output from cardiffnlp model
        """
        sentiments_count = {"positive":0,"negative":0,"neutral":0}
        cummulative_sentiment_scores = {"positive":0,"negative":0,"neutral":0}

        #get count of sentiment_labels for clips
        for clip in sentiments_dict["segments"]:
            sentiments_count[clip["sentiment_label"]]+=1
            cummulative_sentiment_scores[clip["sentiment_label"]]+=clip["sentiment_score"]

        #dominanst sentimetn is the one with most clips
        dominant_sentiment = max(sentiments_count, key=sentiments_count.get)

        #calculate percentage for sentimenet_labels frequency
        tone_percentages = {}
        num_of_clips = len(sentiments_dict["segments"])
        for tone,freq in sentiments_count.items():
            tone_percentages[tone]= round((freq/num_of_clips)*100,2)

        #calculate net sentiment score for each label based off model's sentiment_score output 
        total_sentiment = cummulative_sentiment_scores["negative"]+cummulative_sentiment_scores["positive"]+cummulative_sentiment_scores["neutral"]
        # Convert to a scale of 10 and round to 2 decimal places
        sentiment_scores = {"positive": round((cummulative_sentiment_scores["positive"] / total_sentiment) * 10, 2),
                            "negative": round((cummulative_sentiment_scores["negative"] / total_sentiment) * 10, 2),
                            "neutral": round((cummulative_sentiment_scores["neutral"] / total_sentiment) * 10, 2)}

        output = {"sentiment_percentages":tone_percentages,"sentiment_score":sentiment_scores,"dominant_sentiment":dominant_sentiment}

        return output
    
    def __get_feedback_tone(self, transcript):
        """
        Get feedback tone
        """
        client = AzureOpenAI(
            api_version=self.data["AZURE_OPENAI_API_VERSION"],
            api_key=self.data["AZURE_OPENAI_API_KEY"],
            azure_endpoint=self.data["AZURE_OPENAI_API_ENDPOINT"],
            )
        
        outputFormat = """{"Tone Score": "x / 10", "Tone Feedback": "<DETAILED FEEDBACK ON TONE, WITH CITED EXAMPLES AND TIMESTAMPS>"}"""
        rubric = """      
                    Tone: Assess the overall positivity, formality, enthusiasm, appropriateness of the video's transcript. Include examples of positive, formal, enthusiastic, and appropriate language use (i.e. in 00:01:12 ~ 00:01:30, the speaker's enthusiastic tone effectively engages the audience)
                    """
        prompt = f"""
                Analyze the provided video transcript data (a list of dictionaries with 'start', 'end', 'text') focusing on Tone based on the following rubric {rubric}. Rate the tone on a scale of 10 and provide feedback that always includes detailed advice with specific, cited examples from the transcript. Ensure your feedback explicitly mentions examples from the transcript, citing the 'start' and 'end' times in HH:mm:ss format, to illustrate points about the thone of the transcript. Format your response as follows: {outputFormat}
                """
      
        # Check if the transcript is too long
        temp = ""
        for i in transcript['segments']:
            start_time = datetime.timedelta(seconds=round(i['start'], 2))
            end_time = datetime.timedelta(seconds=round(i['end'], 2))
            start_time_str = str(start_time).rstrip('0').rstrip('.')
            end_time_str = str(end_time).rstrip('0').rstrip('.')
            temp += f" (start: {start_time_str}, end: {end_time_str}) "
            temp += ' '.join(i['text'].split())

        if len(temp) > 4096:
            print("LONGLONGLONGLONGLONGLONGLONG")
            # Split the transcript into chunks
            transcript_chunks = [temp[i:i+4096] for i in range(0, len(temp), 4096)]

            responses = []
            count = 0
            for chunk in transcript_chunks:
                print(f"iteration: {count}")
                count += 1
                messages = [
                    {"role": "user", "content": chunk},
                    {"role": "user", "content": prompt}
                ]
                response = client.chat.completions.create(
                    model="GPT-35-TURBO",
                    messages=messages,
                    max_tokens=1000
                )
                responses.append(response.choices[0].message.content)

            responses_str = " ".join(responses)
            
            final_prompt = """
                            Given the responses obtained from the GPT model, assign an overall score for each aspect of the tone (out of 10) based on the responses. Provide concise and specific feedback for each category, reflecting the extent to which the transcript meets the evaluation criteria provided to you in previous shells. Include one of the examples used in responses in your feedback. Output (dictionary) must follow the format: {"Tone Score": "x / 10", "Tone Tip": "<FEEDBACK ON Tone>"}
                            """

            final_response = client.chat.completions.create(
                model="GPT-35-TURBO",
                messages=[
                {"role":"user", "content": responses_str},
                {"role": "user", "content": final_prompt}
                ],
                temperature=0.9,
                max_tokens=1000,
                top_p=0.9,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None
            )
            response_str = final_response.choices[0].message.content
        else:
            # Send the transcript to the GPT model
            print("SHORTSHORTSHORTSHORTSHORT")
            response = client.chat.completions.create(
                model="GPT-35-TURBO",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": temp}
                ],
                temperature=0.9,
                max_tokens=1000,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None
                )
            response_str = response.choices[0].message.content
        response_str = response_str.replace('transcript', 'video')    
        result = json.loads(response_str)

        return result

    def __get_feedback_eng_clarity(self, transcript):
        """
        Get feedback on engagement and clarity
        """
        client = AzureOpenAI(
            api_version=self.data["AZURE_OPENAI_API_VERSION"],
            api_key=self.data["AZURE_OPENAI_API_KEY"],
            azure_endpoint=self.data["AZURE_OPENAI_API_ENDPOINT"],
            )
        prompt = "Analyze a video transcript provided as a list of dictionaries, each containing 'start', 'end', 'text', for clarity and engagement. Apply the following criteria: \n\n- **Clarity**: Evaluate the organization, language, and ease of understanding of the transcript.\n- **Engagement**: Assess the storytelling, interactivity, and emotional or intellectual appeal of the content.\n\nRate both clarity and engagement on a scale of 1 to 10. Provide feedback that always includes detailed advice with specific, cited examples from the transcript. Ensure your feedback explicitly mentions examples from the transcript, citing the 'start' and 'end' times in HH:mm:ss format, to illustrate points about clarity and engagement. Format your response as follows:\n\n```json\n{\n  \"Clarity Score\": \"x/10\",\n  \"Clarity Tip\": \"<FEEDBACK ON CLARITY WITH SPECIFIC EXAMPLES AND TIMESTAMPS>\",\n  \"Engagement Score\": \"x/10\",\n  \"Engagement Tip\": \"<FEEDBACK ON ENGAGEMENT WITH SPECIFIC EXAMPLES AND TIMESTAMPS>\"\n}\n```"
        
       # Pre-process transcript into a stripped string and timestamps converted to HH:mm:ss format
        temp = ""
        for i in transcript['segments']:
            start_time = datetime.timedelta(seconds=round(i['start'], 2))
            end_time = datetime.timedelta(seconds=round(i['end'], 2))
            start_time_str = str(start_time).rstrip('0').rstrip('.')
            end_time_str = str(end_time).rstrip('0').rstrip('.')
            temp += f" (start: {start_time_str}, end: {end_time_str}) "
            temp += ' '.join(i['text'].split())

         # Check if the transcript is too long
        if len(temp) > 4096:
            print("LONGLONGLONGLONGLONGLONGLONG")

            # Split the transcript into chunks
            transcript_chunks = [temp[i:i+4096] for i in range(0, len(temp), 4096)]
            responses = []

            for chunk in transcript_chunks:
                messages = [
                    {"role": "user", "content": chunk},
                    {"role": "user", "content": prompt}
                ]
                response = client.chat.completions.create(
                    model="GPT-35-TURBO",
                    messages=messages,
                    max_tokens=1000
                )
                responses.append(response.choices[0].message.content)

            responses_str = " ".join(responses)
        
            final_prompt = """
                Given the responses obtained from the GPT model, assign an overall score for clarity and engagement (out of 10) based on the responses. Provide concise and specific feedback for each category, reflecting the extent to which the transcript meets the evaluation criteria provided to you in previous shells. Include one of the examples used in responses in your feedback. Output (dictionary) must follow the format: {"Clarity Score": "x / 10", "Clarity Tip": "<FEEDBACK ON CLARITY>", "Engagement Score": "x / 10", "Engagement Tip": "<FEEDBACK ON ENGAGEMENT>"}
                """

            final_response = client.chat.completions.create(
                model="GPT-35-TURBO",
                messages=[
                {"role": "system", "content": responses_str},
                {"role": "user", "content": final_prompt}
                ],
                temperature=0.9,
                max_tokens=1000,
                top_p=0.9,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None
            )
            response_str = final_response.choices[0].message.content
        else:
            # Send the transcript to the GPT model
            print("SHORTSHORTSHORTSHORTSHORT")
            # segment = str(transcript['segments'])
            # with open('/code/app/uploads/segment.txt', 'w') as file:
            #     file.write(segment)
          
            response = client.chat.completions.create(
                model="GPT-35-TURBO",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": temp}
                ],
                temperature=0.9,
                max_tokens=1000,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None
                )
            response_str = response.choices[0].message.content
        response_str = response_str.replace('transcript', 'video')    

        return response_str
    
    def __get_feedback_eng_clarity_no_audio(self, labels):
        # Initialize Azure OpenAI client
        client = AzureOpenAI(
            api_version=self.data["AZURE_OPENAI_API_VERSION"],
            api_key=self.data["AZURE_OPENAI_API_KEY"],
            azure_endpoint=self.data["AZURE_OPENAI_API_ENDPOINT"],
            )
        outputFormat = """ {"Clarity Score": "x / 10", "Clarity Tip": "","Engagement Score": "x / 10", "Engagement Tip": ,}"""

        rubric = """      
                    Clarity: Assess clarity by the clearness of the video's contents assumed through proivded labels. Include examples of well-explained concepts or areas needing improvement (i.e. in 00:01:12 ~ 00:01:30, golf equipments are clearly shown).
                    Engagement: Engagement is based on number of labels. More labels means more engaging (Yet, the score never exceed 6). Always suggest to add audio to the video for more engagement.
                """
        prompt = """
                    Given labels obtained from an audio-less video, assume the contents of the video according to the label’s time stamps and its contents. 
                    Then, given the following evaluation criteria, analyze the video  and assumed story with provided labels. Assign a score out of 10 for clarity, and engagement, reflecting the extent to which the transcript meets these criteria. 
                    Use the provided output format to structure your response. 
                """
    
        fullPrompt = prompt + rubric + "Return a dictionary with your scores and example-based tips according to the transcript analysis similar to:\n" + outputFormat

        # Define the maximum token length for a single request
        MAX_TOKENS = 4096

        # Split the labels into chunks that are small enough for the GPT model
        labels_chunks = textwrap.wrap(self.labels_jstr, MAX_TOKENS)

        # Initialize an empty list to store the responses
        responses = []

        # Loop over each chunk
        for chunk in labels_chunks:
            # Create a message with the chunk
            messages = [
                {"role": "user", "content": chunk},
                {"role": "user", "content": fullPrompt}
            ]

            # Send the message to the GPT model
            response = client.chat.completions.create(
                model="GPT-3-Turbo",
                messages=messages,
                max_tokens=300
            )

            # Store the response
            responses.append(response.choices[0].message.content)

        responses_str = " ".join(str(e) for e in responses)  

        final_prompt = "Using these responses, assign an overall score for clarity and engagement (out of 10), and provide overall feedbacks (Not exceeding 3 sentences) for each category based on the responses, reflecting the extent to which the transcript meets these criteria." + rubric + "Use the provided output format to structure your response. " + outputFormat

        messages = [
                {"role":"user", "content": responses_str},
                {"role": "user", "content": final_prompt}
            ]
        response = client.chat.completions.create(
                model="GPT-3-Turbo",
                messages=messages,
                max_tokens=300
            )

        return response.choices[0].message.content
    
    def __get_tone_no_audio(self, labels):
        # Initialize Azure OpenAI client
        client = AzureOpenAI(
            api_version=self.data["AZURE_OPENAI_API_VERSION"],
            api_key=self.data["AZURE_OPENAI_API_KEY"],
            azure_endpoint=self.data["AZURE_OPENAI_API_ENDPOINT"],
            )
        outputFormat = """{"Tone Score": "x / 10", "Tone Feedback": "<DETAILED FEEDBACK ON TONE, WITH CITED EXAMPLES AND TIMESTAMPS>"}"""

        rubric = """      
                    Tone: Assess the overall positivity, formality, enthusiasm, appropriateness of the video's contents assumed through provided labels. Include examples of positive, formal, enthusiastic, and appropriate language use (i.e. in 00:01:12 ~ 00:01:30, the speaker's enthusiastic tone effectively engages the audience)
                """
        
        prompt = f"""
                    When given labels obtained from an audio-less video, assume the contents of the video according to the label’s time stamps and its contents. 
                    Then, given the following evaluation criteria, analyze the video  and assumed story with provided labels. Assign a score out of 10 for tone, reflecting the extent to which the transcript meets these criteria: {rubric}. 
                    Use the provided output format to structure your response. Output format: {outputFormat}.
                """

        # Define the maximum token length for a single request
        MAX_TOKENS = 4096

        # Split the labels into chunks that are small enough for the GPT model
        labels_chunks = textwrap.wrap(self.labels_jstr, MAX_TOKENS)

        # Initialize an empty list to store the responses
        responses = []

        # Loop over each chunk
        for chunk in labels_chunks:
            # Create a message with the chunk
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": chunk}
            ]

            # Send the message to the GPT model
            response = client.chat.completions.create(
                model="GPT-3-Turbo",
                messages=messages,
                max_tokens=300
            )

            # Store the response
            responses.append(response.choices[0].message.content)

        responses_str = " ".join(str(e) for e in responses)  

        final_prompt = "Using these responses, assign an overall score for Tone (out of 10), and provide overall feedbacks (3~5 sentences) based on the responses, reflecting the extent to which the video labels meets these criteria." + rubric + "Use the provided output format to structure your response. " + outputFormat

        messages = [
                {"role":"user", "content": responses_str},
                {"role": "user", "content": final_prompt}
            ]
        response = client.chat.completions.create(
                model="GPT-3-Turbo",
                messages=messages,
                max_tokens=300
            )

        return response.choices[0].message.content

    def is_related(query, summary):
        # Implement your logic here to check if the query is related to the summary
        # This could be a simple keyword check, or a more complex natural language processing task
        return True

    def focus_group_chat(self, query,project_data):
        """
        Get response for chatbox query
        """
        client = AzureOpenAI(
            api_version=self.data["AZURE_OPENAI_API_VERSION"],
            api_key=self.data["AZURE_OPENAI_API_KEY"],
            azure_endpoint=self.data["AZURE_OPENAI_API_ENDPOINT"],
            )
        prompt = f"""
                I will provide summary of a video transcript. Analyze and provide short,precise and meaningful response for the following query using that summary:

                User Query: {query}

                Video Transcript summary: {project_data['summary']}
                """
        
        messages = [
                {"role": "system", "content": "You are a Video Assistant. Your role is to provide feedback to elevate users' video editing experience."},
                {"role": "system", "content": "For un-realted queries, please respond with 'Sorry can't help with that :)'"},
                {"role": "user", "content": prompt}
            ]
        response = client.chat.completions.create(
                model="GPT-35-Turbo",
                messages=messages,
                max_tokens=300
            )

        return response.choices[0].message.content