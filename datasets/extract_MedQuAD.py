import os
import xml.etree.ElementTree as ET
import pandas as pd

# Set the base directory where your folders are located
base_dir = 'MedQuAD'

# Initialize a list to store the QA pairs
qa_pairs = []
folder_error_count = dict()

# Function to extract question-answer pairs from an XML file
def extract_qa_from_xml(file_path, counter):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Find all QAPairs in the document
        for qa_pair in root.findall(".//QAPair"):
            question = qa_pair.find("Question").text.strip() if qa_pair.find("Question") is not None else ""
            answer = qa_pair.find("Answer").text.strip() if qa_pair.find("Answer") is not None else ""
            if question and answer:
                qa_pairs.append({'question': question, 'answer': answer})
    except Exception as e:
        counter += 1
        print(f"Error parsing {file_path}: {e}")
    
    return counter  # Return the updated counter

# Iterate over the folders 1 to 12
for folder_num in range(1, 13):
    print(f"Currently parsing folder #{folder_num}")
    folder_name = f"{folder_num}_QA"
    folder_path = os.path.join(base_dir, folder_name)
    counter = 0
    
    # Ensure the folder exists
    if os.path.exists(folder_path):
        print(f"Parsing folder {folder_name}...")
        # Iterate over all XML files in the folder
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".xml"):  # Only process XML files
                file_path = os.path.join(folder_path, file_name)
                counter = extract_qa_from_xml(file_path, counter)  # Update counter each time an error occurs
        
        # Store the error count for this folder
        folder_error_count[folder_num] = counter

# Convert the list of QA pairs to a DataFrame
df_qa = pd.DataFrame(qa_pairs)

# Save the combined QA pairs to a CSV file
output_csv = os.path.join('', 'medquad_combined_qa.csv')
df_qa.to_csv(output_csv, index=False)

# Preview the first few rows of the DataFrame
print(df_qa.head())

print('error count extracting from these folders:', folder_error_count)
print(f"Combined QA pairs saved to: {output_csv}")
