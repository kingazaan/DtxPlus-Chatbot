import re
import markdown2
from .models import Patient
from .bot import get_langchain_response, extract_entities_from_conversation
from .knowledge_graph import KnowledgeGraph # , create_patient_node, add_entities_to_graph
from ml_models.topic_and_filter_based import filter_profane_query, filter_unrelated_query
from ml_models.classifier import classify_text
from dateutil import parser
from django.utils import timezone

# Medical patterns for matching queries
MEDICAL_PATTERNS = [
    r'\b(?:appointment|reschedule|change date|schedule)\b',
    r'\b(?:medications?|medicine|medication change|treatment|antibiotics|pills|pharmacy)\b',
    r'\b(?:prescription|doctor visit|clinic|check-up)\b',
    r'\b(?:symptoms?|diagnosis|condition|therapy)\b'
]

def extract_date_from_message(message):
    """Extract the date from the user message using dateutil."""
    try:
        parsed_date = parser.parse(message, fuzzy=True)
        if parsed_date and timezone.is_naive(parsed_date):
            parsed_date = timezone.make_aware(parsed_date, timezone.get_current_timezone())
        if parsed_date and parsed_date >= timezone.now():
            return parsed_date
    except (ValueError, OverflowError):
        return None

def check_for_medical_conditions(query):
    """Check if a query is related to medical conditions or appointments."""
    appointment_related = re.search(r'\b(?:appointment|reschedule|change date|schedule)\b', query, re.IGNORECASE)
    medical_related = re.search(r'\b(?:prescription|medication change)\b', query, re.IGNORECASE)
    return {
        'appointment_related': bool(appointment_related),
        'medical_related': bool(medical_related)
    }

def process_query(user_message, patient):
    """Process the user query and handle the different checks."""
    
    # Step 1: Run profanity check
    filter_result = filter_profane_query(user_message)
    if filter_result == "Rejected due to profanity":
        return filter_result
    
    # Step 2: Classify the query
    predicted_label = classify_text(user_message)
    if predicted_label == 1:
        return markdown2.markdown(get_langchain_response(user_message, str(patient.first_name + ' ' + patient.last_name)))
    
    # Step 3: Run the topic model as a backup if the classifier fails
    topic_probability = filter_unrelated_query(user_message)
    if topic_probability > 0.25:
        return markdown2.markdown(get_langchain_response(user_message, str(patient.first_name + ' ' + patient.last_name)))
    
    return "This seems unrelated to health matters. Please ask a health-related question."

def update_patient_entities(patient, user_message):
    """Extract entities from the user message and update patient data."""
    entities = extract_entities_from_conversation(user_message)

    # Insert the extracted information into the knowledge graph
    kg = KnowledgeGraph(uri="bolt://localhost:7687", user="neo4j", password="pleasehelpme1")
    kg.create_patient_node(str(patient.first_name + ' ' + patient.last_name))
    kg.add_entities_to_graph(str(patient.first_name +  ' ' + patient.last_name), entities)
    kg.close()

    return entities