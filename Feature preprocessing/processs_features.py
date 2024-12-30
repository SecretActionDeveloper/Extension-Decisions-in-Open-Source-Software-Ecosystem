### process features to ensure highly similar ones are replaced by a common feature instead

import pandas as pd
import ast
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# File paths
file_name = "path to unprocessed data"
input_path = f"folder\\{file_name}"
output_path = f"output folder\\{file_name}"
feature_path = ".\\unique_features.csv"

# Load data
df = pd.read_csv(input_path)
df_features = pd.read_csv(feature_path)

# Initialize model
model = SentenceTransformer('bert-base-nli-mean-tokens')
THRESHOLD = 90

# Print dataset summary
print(f"Number of actions: {len(df['Action_Name'])}")
print(f"Unique actions: {len(df['Action_Name'].unique())}")
print(f"Unique features in dataset: {len(df_features['Feature'])}")

# Prepare processed columns
df["Processed_Features"] = ""
df["Feature_embedding"] = ""

# Function to parse embeddings from string
def parse_embedding(embedding_str):
    try:
        embedding_str = embedding_str.strip("[]")
        return np.fromstring(embedding_str, sep=" ")
    except:
        return np.array([])

# Process each row
ci_features = []
for idx, row in df.iterrows():
    print(f"Processing row {idx + 1}/{len(df)}")
    features_raw = ast.literal_eval(row["features_cleaned"])
    unique_features = list(set(features_raw))
    cleaned_features = []
    embeddings = []

    for feature in unique_features:
        feature_embed = model.encode(feature)
        vector1 = feature_embed.reshape(1, -1)
        matched = False

        # Compare with unique features
        for _, feature_row in df_features.iterrows():
            uniq_feature = feature_row["Feature"]
            uniq_embed = parse_embedding(feature_row["embedding"])
            if uniq_embed.size > 0:  # Only compare if embedding is valid
                vector2 = uniq_embed.reshape(1, -1)
                similarity = cosine_similarity(vector1, vector2)[0][0] * 100
                if similarity >= THRESHOLD:
                    matched = True
                    if uniq_feature not in cleaned_features:
                        cleaned_features.append(uniq_feature)
                        embeddings.append(uniq_embed)
                    break

        # If no match, add as new feature
        if not matched:
            print(f"New unique feature found: {feature}")
            cleaned_features.append(feature)
            embeddings.append(feature_embed)

    ci_features.extend(cleaned_features)
    df.at[idx, "Processed_Features"] = cleaned_features
    df.at[idx, "Feature_embedding"] = [embed.tolist() for embed in embeddings]

    # Save progress periodically
    if (idx + 1) % 10 == 0 or idx == len(df) - 1:
        df.to_csv(output_path, index=False)

# Summary
print(f"Total unique features: {len(df_features['Feature'].unique())}")
print(f"Unique features in CI category: {len(set(ci_features))}")
