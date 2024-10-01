from neo4j import GraphDatabase

class KnowledgeGraph:

    def __init__(self, uri, user, password):
        # Initialize the connection to Neo4j
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Close the connection
        self.driver.close()

    def create_patient_node(self, patient_name):
        with self.driver.session() as session:
            session.write_transaction(self._create_patient, patient_name)

    def add_entities_to_graph(self, patient_name, entities):
        with self.driver.session() as session:
            session.write_transaction(self._add_hierarchical_entities, patient_name, entities)

    def query_patient_data(self, patient_name):
        with self.driver.session() as session:
            return session.read_transaction(self._query_patient, patient_name)

    @staticmethod
    def _query_patient(tx, patient_name):
        query = """
        MATCH (p:Patient {name: $patient_name})-[r:HAS_CONDITION|HAS_SYMPTOM|HAS_MEDICATION|HAS_APPOINTMENT|HAS_ALLERGY|HAS_LIFESTYLE]->(info)
        RETURN type(r) as relationship, info.name as detail
        """
        result = tx.run(query, patient_name=patient_name)
        return [{record["relationship"]: record["detail"]} for record in result]

    @staticmethod
    def _create_patient(tx, patient_name):
        # Create a patient node if it doesn't exist
        query = (
            "MERGE (p:Patient {name: $patient_name}) "
            "RETURN p"
        )
        tx.run(query, patient_name=patient_name)

    @staticmethod
    def _add_hierarchical_entities(tx, patient_name, entities):
        # Add condition and its symptoms and medications
        if 'condition' in entities:
            condition = entities['condition']
            tx.run(
                "MATCH (p:Patient {name: $patient_name}) "
                "MERGE (c:Condition {name: $condition}) "
                "MERGE (p)-[:HAS_CONDITION]->(c)",
                patient_name=patient_name, condition=condition
            )

            # Add symptoms under the condition
            if 'symptoms' in entities:
                for symptom in entities['symptoms']:
                    tx.run(
                        "MATCH (c:Condition {name: $condition}) "
                        "MERGE (s:Symptom {name: $symptom}) "
                        "MERGE (c)-[:HAS_SYMPTOM]->(s)",
                        condition=condition, symptom=symptom
                    )

            # Add medications under the condition
            if 'medication' in entities:
                tx.run(
                    "MATCH (c:Condition {name: $condition}) "
                    "MERGE (m:Medication {name: $medication}) "
                    "MERGE (c)-[:HAS_MEDICATION]->(m)",
                    condition=condition, medication=entities['medication']
                )

                # Add frequency to the medication
                if 'frequency' in entities:
                    tx.run(
                        "MATCH (m:Medication {name: $medication}) "
                        "MERGE (f:Frequency {name: $frequency}) "
                        "MERGE (m)-[:HAS_FREQUENCY]->(f)",
                        medication=entities['medication'], frequency=entities['frequency']
                    )

        # Add lifestyle node and link diet, smoking, exercise
        lifestyle_present = any(key in entities for key in ['diet', 'exercise', 'smoking'])
        if lifestyle_present:
            tx.run(
                "MATCH (p:Patient {name: $patient_name}) "
                "MERGE (l:Lifestyle {name: 'Lifestyle'}) "
                "MERGE (p)-[:HAS_LIFESTYLE]->(l)",
                patient_name=patient_name
            )

            # Add diet
            if 'diet' in entities:
                tx.run(
                    "MATCH (l:Lifestyle {name: 'Lifestyle'}) "
                    "MERGE (d:Diet {name: $diet}) "
                    "MERGE (l)-[:HAS_DIET]->(d)",
                    diet=entities['diet']
                )

            # Add exercise
            if 'exercise' in entities:
                tx.run(
                    "MATCH (l:Lifestyle {name: 'Lifestyle'}) "
                    "MERGE (e:Exercise {name: $exercise}) "
                    "MERGE (l)-[:HAS_EXERCISE]->(e)",
                    exercise=entities['exercise']
                )

            # Add smoking
            if 'smoking' in entities:
                tx.run(
                    "MATCH (l:Lifestyle {name: 'Lifestyle'}) "
                    "MERGE (s:Smoking {name: $smoking}) "
                    "MERGE (l)-[:HAS_SMOKING]->(s)",
                    smoking=entities['smoking']
                )

        # Add allergy directly linked to the patient
        if 'allergy' in entities:
            tx.run(
                "MATCH (p:Patient {name: $patient_name}) "
                "MERGE (a:Allergy {name: $allergy}) "
                "MERGE (p)-[:HAS_ALLERGY]->(a)",
                patient_name=patient_name, allergy=entities['allergy']
            )

        # Add appointment time directly linked to the patient
        if 'appointment_time' in entities:
            tx.run(
                "MATCH (p:Patient {name: $patient_name}) "
                "MERGE (a:Appointment {time: $appointment_time}) "
                "MERGE (p)-[:HAS_APPOINTMENT]->(a)",
                patient_name=patient_name, appointment_time=entities['appointment_time']
            )

# # Usage example
# if __name__ == "__main__":
#     # Create a new connection to the Neo4j database
#     uri = "bolt://localhost:7687"  # Change this based on your Neo4j config
#     user = "neo4j"
#     password = "pleasehelpme1"

#     # Instantiate the KnowledgeGraph class
#     kg = KnowledgeGraph(uri, user, password)

#     # Example data
#     patient_name = "John Doe"
#     extracted_entities = {
#         'medication': 'lisinopril',
#         'frequency': 'twice a day',
#         'appointment_time': 'next Monday at 3 pm',
#         'diet': 'keto',
#         'smoking': '2 packs a day',
#         'allergy': 'peanuts',
#         'exercise': '3 times a week',
#         'condition': 'diabetes',
#         'symptoms': ['headache', 'fever']
#     }

#     # Add patient node to graph
#     kg.create_patient_node(patient_name)

#     # Add extracted entities to the graph
#     kg.add_entities_to_graph(patient_name, extracted_entities)

#     # Close the connection when done
#     kg.close()
