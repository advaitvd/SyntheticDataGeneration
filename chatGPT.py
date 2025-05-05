import openai
import random
from openai import OpenAI
import sys
import os
import json
from secrets import KEY
from tqdm import tqdm

# Author : Advait Vinay Dhopeshwarkar (advait.dhopeshwarkar@tihiitb.org)
# Date   : 26-04-2025

save_dir = sys.argv[1]
language = sys.argv[2]
generation_model = "o4-mini"
formating_model = "gpt-4o"

client = OpenAI(api_key=KEY)

# start conversation
messages = [
	{"role": "system", "content": "You are a helpful assistant."}
]

topics = [
    'Agriculture And Farming',
	'Law And Government',
	'Finance And Banking',
	'Sports And Entertainment',
	'Military And Defence',
	'Politics',
	'Education And Research',
	'Science And Technology',
	'Rural Development',
	'Business And Economics',
	'Art History And Culture'
]

for topic in topics:
    topic = "Indian " + topic
    print(f"Generating for {topic}")
    m = messages[:]
    query = {"role": "user", "content": f'''
        Please generate a conversation between two speakers in English (strictly english for now).
        The topic of the conversation is {topic}. The generated conversation must be realistic. Make the
        conversation long with around 100 dialogues with rich meaningful sentences. The output must look like the following:
        S1: sentence1\nS2: sentence2\nS1: sentence3\n and so on...
        - Make the conversation rich with content belonging to the provided topic.
        - Ensure that there are exactly two speakers per conversation.
        - Do not add any explaination. Just output the required conversation.
        '''}
    m.append(query)
    response = client.chat.completions.create(model=generation_model, messages=m)
    assistant_reply = response.choices[0].message.content.strip()
    assistant_reply = '\n'.join([sent for sent in assistant_reply.split('\n') if len(sent.strip())!=0])
    print(f"Generation Response Length: {len(assistant_reply)}")
	
    def generate_translation_query(content, language):
        query = {"role": "user", "content": f'''
        Translate the sentence below into {language}. Follow the specified guidelines.
        - Ensure that the conversation is realistic.
        - Whenever {language} speakers speak, they tend to use certain english words, so these must me maintained.
        - Such english words must be enclosed within special tags like this example: <lang:Foreign>hello</lang:Foreign>.
        - Additionally, randomly, but sparsely insert tags like [babble], [bg-speech], [laugh], [music], [no-speech], [noise], [overlap], [silence] to indicate these effects in the conversation.
        - Wherever initials or abbreviations are used use tag like this example <initial>YMCA</initial>.
        - English words, and tags must not be over used. Use it only when really required. Take this into account while translating.
        - All English words HAVE to be enclosed with foreign tags as described.
        - Just output the required translation text content without explaination.
        Sentence: {content}
        Translation:
        '''}
        return query

    translated_content = []
    conversation_en = assistant_reply
    dialogue = assistant_reply.split('\n')
    for line in tqdm(dialogue, total=len(dialogue), desc="[PROGRESS]"):
        line = line.split(':')
        query = generate_translation_query(line[-1].strip(), language)
        m = messages[:]
        m.append(query)
        response = client.chat.completions.create(model=formating_model, messages=m)
        assistant_reply = response.choices[0].message.content.strip()
        line = assistant_reply if len(line) == 1 else f'{line[0]}: {assistant_reply}'
        translated_content.append(line)

    translated_content = '\n'.join(translated_content)
	
    print(f"Translation Response Length: {len(translated_content)}")
    translated_content = '\n'.join([line.strip() for line in translated_content.split('\n') if len(line.strip()) > 0])
    subdir = os.path.join(save_dir, topic.replace(' ', ''))
    os.makedirs(subdir, exist_ok=True)
    conversation_file_name = os.path.join(subdir, "conversation.text")
    with open(conversation_file_name, 'w') as f:
        f.write(translated_content + '\n')
    
    conversation_english_file_name = os.path.join(subdir, "conversation.en.text")
    with open(conversation_english_file_name, 'w') as f:
        f.write(conversation_en)

    m = messages[:]
	# Generate speaker details
    query = {"role": "user", "content": f'''
        Conversation:
        {translated_content}\n
        For the provided conversation, please generate speaker information. Generate it in the following format:
        {{"S1":{{"speakers":[{{"gender": "Male","speakerId": "S-61123","recorderId": "785","nativity": "be_IN","ageRange": "25-50"}}]}},"S2": {{"speakers":[{{"gender": "Female","speakerId": "S-83456","recorderId": "786","nativity": "be_IN","ageRange": "25-50"}}]}}}}
        Randomly generate values for "gender" field, "speakerId", "recorderId". "nativity" must be the language of the conversation and "ageRange"
        must also be randomly chosen. Please only give the string of the json object that has been requested without any explaination or any rendering
        wrapper. I only want the raw json object string '{{...}}' so that I can directly json serialize it.
        '''}
    m.append(query)
    response = client.chat.completions.create(model=formating_model, messages=m)
    assistant_reply = response.choices[0].message.content.strip()
    if assistant_reply[0] != '{':
        # Sometimes the output comes as markdown randered form like ```json ... ```
        assistant_reply = assistant_reply[8:-4]
    print(assistant_reply)
    speaker_det_file_name = os.path.join(subdir, "speaker_details.json")
    with open(speaker_det_file_name, 'w', encoding='utf-8') as f:
        json.dump(
            json.loads(assistant_reply),
            f, ensure_ascii=False,
            indent=2)

    m = messages[:]
	# Generate conversation details
    query = {"role": "user", "content": f'''
        Conversation:
        {translated_content}\n
        For the provided conversation, please generate conversation information. Generate it in the following
        format: {{"domain":"Sports","topic":"Indian cricket discussion","language":"bn_IN","conversation_name":"Bengali-CR"}}
        The "domain" must be the domain based on the conversation. The "topic" must also be based on the topic being discussed in the
        conversation. "language" must be the language that is being spoken predominantly in the conversation. "conversation_name" must be an
        identifier for the conversation. Please only give the string of the json object that has been requested without any explaination or 
        any rendering wrapper. I only want the raw json object string '{{...}}' so that I can directly json serialize it.
        '''}
    m.append(query)
    response = client.chat.completions.create(model=formating_model, messages=m)
    assistant_reply = response.choices[0].message.content.strip()
    if assistant_reply[0] != '{':
        # Sometimes the output comes as markdown randered form like ```json ... ```
        assistant_reply = assistant_reply[8:-4]
    print(assistant_reply)
    conversation_det_file_name = os.path.join(subdir, "conversation_details.json")
    with open(conversation_det_file_name, 'w', encoding='utf-8') as f:
        json.dump(
            json.loads(assistant_reply),
            f, ensure_ascii=False,
            indent=2)
