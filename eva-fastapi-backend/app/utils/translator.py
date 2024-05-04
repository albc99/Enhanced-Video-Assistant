import requests, uuid, json

# Add your key and endpoint
key = "75d58019efaf47718093ea354bbe288c"
endpoint = "https://api.cognitive.microsofttranslator.com"

# location, also known as region.
# required if you're using a multi-service or regional (not global) resource. It can be found in the Azure portal on the Keys and Endpoint page.
location = "centralus"

path = '/translate'
constructed_url = endpoint + path

def translate_text(from_language, to_language, transcript_segments_data):
    """
    Translates the text in the transcript segments from one language to another.

    Args:
        from_language (str): The language code of the original text.
        to_language (str): The language code to translate the text into.
        transcript_segments_data (dict): The dictionary containing the transcript segments data.

    Returns:
        dict: The updated transcript segments data with translated text.
    """
    params = {
        'api-version': '3.0',
        'from': str(from_language),
        'to': [str(to_language)]
    }

    headers = {
        'Ocp-Apim-Subscription-Key': key,
        # location required if you're using a multi-service or regional (not global) resource.
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # You can pass more than one object in body.
    body = [{"text": segment["text"]} for segment in transcript_segments_data["segments"]]

    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    response = request.json()

    # Rewrite the segment["text"] back to the translated text
    for i in range(len(transcript_segments_data["segments"])):
        transcript_segments_data["segments"][i]['text'] = response[i]['translations'][0]['text']

    return transcript_segments_data
    


