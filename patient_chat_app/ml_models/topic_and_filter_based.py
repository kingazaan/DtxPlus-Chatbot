from bertopic import BERTopic
from profanity_check import predict as profanity_predict
from sentence_transformers import SentenceTransformer

# Load the embedding model (this one is a general-purpose model)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load the BERTopic model and specify the embedding model
topic_model = BERTopic.load("etanios/short-pubmed-bertopic", embedding_model=embedding_model)

def filter_profane_query(query):
    # Step 1: Check for profanity using profanity-check
    profanity_score = profanity_predict([query])
    if profanity_score[0] == 1:  # 1 indicates likely profanity
        return "Rejected due to profanity"
    else:
        return "Accepted"

def filter_unrelated_query(query):
    # Step 1: Run the query through the topic model
    topics, probs = topic_model.transform([query])

    # Get the predicted topic as a string
    predicted_topic = topic_model.get_topic_info().loc[topics[0], "Name"]
    print(predicted_topic, probs)

    # If it passes the checks, return accepted along with the probability
    return probs[0]

# Example Usage
# query = "I need to take my inhaler fo rmy cough and flu because my sickness is getting worse. Can you reccomend me any allergy medications?"
# query = "Is running good for my heart health?"
# query = "How fast is a cheetah versus an elephant?"
# query = "My nephew is making me angry can I hit him?"
# result = filter_unrelated_query(query)
# print(result)
