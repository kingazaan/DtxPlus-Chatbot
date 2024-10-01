import pandas as pd

# Paths to the datasets
medquad_path = 'medquad_combined_qa.csv'
nq_sample_path = 'nq_sample.csv'
output_path = 'qa_dataset.csv'

# Load Dataset 1 (MedQuAD)
df_medquad = pd.read_csv(medquad_path)

# Load Dataset 2 (Natural Questions sample)
df_nq = pd.read_csv(nq_sample_path)

# Step 1: Add label to Dataset 1 (MedQuAD: label = 1)
df_medquad['label'] = 1

# Step 2: Add label to Dataset 2 (Natural Questions: label = 0)
df_nq['label'] = 0

# Step 3: Combine question and answer for Dataset 1 (MedQuAD) for better context
df_medquad['combined_text'] = df_medquad['question'] + " " + df_medquad['answer']

# Step 4: For Dataset 2 (Natural Questions), keep only the question (no answer concatenation)
df_nq['combined_text'] = df_nq['question']  # No answer concatenation for Dataset 2

# Step 5: Ensure both datasets have the same columns before combining
df_medquad = df_medquad[['combined_text', 'label']]
df_nq = df_nq[['combined_text', 'label']]

# Step 6: Combine both datasets (stack them together) and randomize order of rows
df_combined = pd.concat([df_medquad, df_nq], ignore_index=True)
df_combined = df_combined.sample(frac=1).reset_index(drop=True)

# Step 7: Save the combined dataset to CSV
df_combined.to_csv(output_path, index=False)

print(f"Combined dataset saved to: {output_path}")
print(f"Total rows in combined dataset: {df_combined.shape[0]}")
