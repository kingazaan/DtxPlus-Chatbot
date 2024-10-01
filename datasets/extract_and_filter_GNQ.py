import json
import gzip
import pandas as pd

# Path to the gzipped file
input_file = 'GNQ_dev\\v1.0-simplified_nq-dev-all.jsonl.gz'  # Change to your actual file path
output_file = 'nq_sample.csv'  # Output CSV file to save the 25MB sample

# Initialize an empty list to store the data
sample_data = []

# Approximate size of each JSON line object
average_line_size = 2_000  # This is an estimate; actual size may vary

# Target size in bytes (25MB)
target_size = 100 * 1024 * 1024  # 50 MB in bytes
current_size = 0

# Open the gzipped file and process the data
with gzip.open(input_file, 'rt', encoding='utf-8') as f:
    for line in f:
        if current_size > target_size:
            break
        # Parse each line as JSON
        data = json.loads(line)
        # Add data to list
        sample_data.append({
            'question': data['question_text'],
            'long_answer': data['annotations'][0]['long_answer']['start_token'] if data['annotations'][0]['long_answer']['start_token'] != -1 else 'N/A',
            'short_answers': [ans['start_token'] for ans in data['annotations'][0]['short_answers']] if data['annotations'][0]['short_answers'] else 'N/A'
        })
        # Estimate the size of the current line and update the size counter
        current_size += average_line_size

# Convert the sample data to a pandas DataFrame
df = pd.DataFrame(sample_data)

# Save the sample to CSV
df.to_csv(output_file, index=False)

print(f"Sample saved to {output_file}")
