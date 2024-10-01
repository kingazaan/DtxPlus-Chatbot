# patient-chat-app
An app for patients to chat about medical issues with a bot that can help them for the future. DTxPlus take-home assignment

# TODO
I currently need to
- Refactor Views.py and topic_and_filter_based.py based on redundant code -- FIXED!
- Make sure the issue of the old chats in the database being shown is gone, and done with (requests session chat history stuff) -- FIXED! 
- Find out the fix for why the topic model/classifier keeps thinking some heatlh queries are not health queries (aka broken arm and stuff) -- FIXED!
- Implement the knowledge graph with neo4J, being done with extracting entities with a model good enough to do this

## Django and PostgresSQL notes
SO I made a project (patients chat app) and also an app (chatbot). The chatbot will have all the database information, and the patient chat app will have all the LLM stuff
TODO: I need to add webhooks so that the chat is automatic, roght now it needs to be refreshed. I can do this later
- I replaced the SQLite database with PostgreSQL, and changed these settings in settings.py -> databases
        'NAME': 'patient_chat_db',
        'USER': 'postgres',
        'PASSWORD': '211959'
- If I want to delete everything in my database without actually deleting the database, do: TRUNCATE patient_chat_db

## Notes for LLM and Entity Extraction (Langchain)
Using google gemini, API key: AIzaSyDCvTAzzXaZ9eGKJzdrIJL-ULMTMKOD9lU
Website: https://aistudio.google.com/app/apikey
Sample use case:
"""
    curl \
        -H 'Content-Type: application/json' \
        -d '{"contents":[{"parts":[{"text":"Hello, I have a cold and I need help with what over the counter medicines I can take. Can you help me?"}]}]}' \
        -X POST 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=AIzaSyDCvTAzzXaZ9eGKJzdrIJL-ULMTMKOD9lU'
        """
- Sample prompt:
    Hello, I have a cold and I need help with what over the counter medicines I can take. Can you help me?

### Making classifier for filtering chat information
9-23-2024 -- I want to make a ML classifier in order to only allow certain data to be passed into or responded to by Google Gemini. I need to first gather data, then preorocess and select the best model, then finally trian it.
- First I need to get a dataset of both healthc and non-health queries. Aka question/query -- text -- health or non health (binary).
- So I ended up using these 2 datasets:
Non-Health: https://ai.google.com/research/NaturalQuestions
Health: https://github.com/abachaa/MedQuAD
I did some feature modification and eventually combined these 2 datasets, with just a query and then lable of 0 (non-health) or 1 (health) questions.

## Making the knowledge graph
So I ended up using a mix of regex and entity extraction from emilyalsentzer/Bio_ClinicalBERT in order to extract certain entities to make a knowledge graph
I then used neo4j with credentials below:
    

## Personal notes for myself
- To start venv, do source venv/Scripts/activate
- Need to apply django migrations when I complete somethign using these, it si pretty easy just python manage.py migrate
- It is good to know, kinda like git commit
Every time you make changes, do this:
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver
- kinda long process to enable the Google Gemini API, but bascially neede dto download a key and then enable epi on https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/metrics?project=eminent-clock-302907
- If I had more time, I would first try and establish summaries for chats because that is very easy to implement and I was almost there, I just felt I had no time
- Also, I feel that the Neo4j database worked very well and there was redundant information in te PostgreSQL database and Neo4j database. I did not set up any updates for the PostgreSQL data but I would if I had/have more time
