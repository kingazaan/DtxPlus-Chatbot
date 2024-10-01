import os
import re
from dateutil import parser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain import PromptTemplate
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForTokenClassification
from .knowledge_graph import KnowledgeGraph

# Declare json as api to use gemini
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/azaan/OneDrive/Documents/GitHub/dtxplus-chat-app/patient_chat_app/gemini_api_key.json'

# Initialize NER model for medical entity extraction
tokenizer = AutoTokenizer.from_pretrained("emilyalsentzer/Bio_ClinicalBERT")
model = AutoModelForTokenClassification.from_pretrained("emilyalsentzer/Bio_ClinicalBERT")
nlp = pipeline("ner", model=model, tokenizer=tokenizer)

# Helper function to extract medication and frequency using regex
def extract_medication_info(text):
    medication_pattern = r"(?:taking|on)\s+([a-zA-Z]+)"
    frequency_pattern = r"(once|twice|one|two|three|four|five|six|seven)\s+(?:a|per)\s+(day|week|month)"

    medication = re.search(medication_pattern, text)
    frequency = re.search(frequency_pattern, text)

    result = {}
    if medication:
        result['medication'] = medication.group(1)
    if frequency:
        result['frequency'] = f"{frequency.group(1)} {frequency.group(2)}"

    return result

# Helper function to extract appointment time using dateutil and regex
def extract_appointment_time(text):
    try:
        # Attempt to extract a date/time using dateutil
        appointment_time = parser.parse(text, fuzzy=True)
        return {'appointment_time': appointment_time.strftime("%Y-%m-%d %H:%M:%S")}
    except (ValueError, OverflowError):
        # Fallback to regex-based relative time extraction
        relative_time_pattern = r"(tomorrow|next week|next month|next (?:Monday|Tuesday|...))"
        relative_time = re.search(relative_time_pattern, text)
        if relative_time:
            return {'appointment_time': relative_time.group(1)}
    return None

# Helper function to extract diet-related info using regex
def extract_diet_info(text):
    diet_pattern = r"(?:on|following|eating)\s+(a\s+)?(keto|vegetarian|vegan|paleo|low-carb|gluten-free)\s+diet"
    general_food_pattern = r"(eating|consuming)\s+([a-zA-Z\s]+)"

    diet_match = re.search(diet_pattern, text)
    general_food_match = re.search(general_food_pattern, text)

    result = {}
    if diet_match:
        result['diet'] = diet_match.group(2)
    if general_food_match:
        result['food'] = general_food_match.group(2)

    return result

# Helper function to extract symptoms/conditions
def extract_symptoms_conditions(text):
    # Basic symptoms/conditions regex
    symptoms_pattern = r"(fever|cough|pain|headache|dizziness|nausea)"
    condition_pattern = r"(diabetes|hypertension|asthma|arthritis|cancer|depression)"

    symptoms = re.findall(symptoms_pattern, text)
    condition = re.search(condition_pattern, text)

    result = {}
    if symptoms:
        result['symptoms'] = symptoms
    if condition:
        result['condition'] = condition.group(1)

    return result

# Helper function to extract allergies using regex
def extract_allergy_info(text):
    allergy_pattern = r"(allergic to|have an allergy to)\s+([a-zA-Z\s]+)"

    allergy = re.search(allergy_pattern, text)

    result = {}
    if allergy:
        result['allergy'] = allergy.group(2)

    return result

# Helper function to extract lifestyle habits (e.g., smoking, drinking)
def extract_lifestyle_habits(text):
    smoking_pattern = r"(smoke|smoking)\s+(\d+\s*(packs?|cigarettes?)\s+(a day|a week))"
    drinking_pattern = r"(drink|drinking)\s+(\d+\s*(glasses?|bottles?)\s+(a day|a week))"

    smoking = re.search(smoking_pattern, text)
    drinking = re.search(drinking_pattern, text)

    result = {}
    if smoking:
        result['smoking'] = smoking.group(2)
    if drinking:
        result['drinking'] = drinking.group(2)

    return result

# Helper function to extract exercise info using regex
def extract_exercise_info(text):
    exercise_pattern = r"(exercise|run|walk|work out)\s*(\d+ times? a (day|week))"

    exercise = re.search(exercise_pattern, text)

    result = {}
    if exercise:
        result['exercise'] = exercise.group(2)

    return result

# Main function to extract entities from the conversation
def extract_entities_from_conversation(text):
    # Step 1: Run the text through the NER model for medication info
    entities = nlp(text)
    medication_info = extract_medication_info(text)

    # Step 2: Extract appointment time
    appointment_info = extract_appointment_time(text)

    # Step 3: Extract diet-related info
    diet_info = extract_diet_info(text)

    # Step 4: Extract symptoms and conditions
    symptoms_info = extract_symptoms_conditions(text)

    # Step 5: Extract allergy info
    allergy_info = extract_allergy_info(text)

    # Step 6: Extract lifestyle habits (smoking/drinking)
    lifestyle_info = extract_lifestyle_habits(text)

    # Step 7: Extract exercise info
    exercise_info = extract_exercise_info(text)

    # Combine all extracted entities
    extracted_info = {}
    if medication_info:
        extracted_info.update(medication_info)
    if appointment_info:
        extracted_info.update(appointment_info)
    if diet_info:
        extracted_info.update(diet_info)
    if symptoms_info:
        extracted_info.update(symptoms_info)
    if allergy_info:
        extracted_info.update(allergy_info)
    if lifestyle_info:
        extracted_info.update(lifestyle_info)
    if exercise_info:
        extracted_info.update(exercise_info)

    return extracted_info

# Add new helper function to query missing information
def query_missing_info(patient_name, extracted_info):
    # Initialize the Neo4j knowledge graph
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "pleasehelpme1"
    kg = KnowledgeGraph(uri, user, password)

    # Query the patient data
    graph_data = kg.query_patient_data(patient_name)

    # Close the Neo4j connection
    kg.close()

    # Fill missing info from the graph
    for relationship in graph_data:
        for key, value in relationship.items():
            if key.lower() not in extracted_info:
                extracted_info[key.lower()] = value

    return extracted_info

def get_langchain_response(user_message, patient_name):
    # Extract the entities from the user message
    extracted_info = extract_entities_from_conversation(user_message)

    # Query missing info from the graph
    enriched_info = query_missing_info(patient_name, extracted_info)

    # Initialize the Gemini LLM from Langchain
    llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7, top_p=0.85)
    prompt_template = PromptTemplate(input_variables=["query", "chat_history"], template="{query}")
    chain = LLMChain(llm=llm, prompt=prompt_template)
    full_message = f"Additional information for this patient is here, please feel free to use it if it can help you generate an answer to the prompt: {enriched_info}"

    # Run the chain to get the response
    bot_response = chain.invoke(str(user_message + ' ' + full_message))

    return bot_response['text']


# Example Usage in your main function
if __name__ == "__main__":
    patient_name = "John Doe"
    user_message = "I have a headache and I'm feeling dizzy."
    result = get_langchain_response(user_message, patient_name)
    print(result)

# # Example usage
# text = """
# I am taking lisinopril twice a day and I have an appointment next Monday at 3 pm. 
# I am also on a keto diet and I smoke 2 packs a day. 
# I am allergic to peanuts and I run 3 times a week. I have diabetes and I've had a headache and fever for the past few days.
# """
# result = extract_entities_from_conversation(text)
# print(result)
