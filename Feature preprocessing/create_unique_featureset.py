import pandas as pd
import ast
import os
import string
import re
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Initialize resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
stop_words = stopwords.words('english')
lemmatizer = WordNetLemmatizer()
model = SentenceTransformer('bert-base-nli-mean-tokens')
THRESHOLD = 90

# File paths
path = "./CI file paths.csv"
feature_path = "./unique_features.csv"

# Load data
df = pd.read_csv(path)
df_features = pd.read_csv(feature_path)
unique_feature = list(df_features["Feature"])

# Extract and process features
all_features = []
for i in range(len(df.index)):
    features = ast.literal_eval(df["features_cleaned"][i])
    all_features.extend(features)

# Initialize feature list
feature_list = []
for i in range(len(df.index)):
    features = list(set(ast.literal_eval(df["features_cleaned"][i])))
    print(f"Processing record {i + 1}/{len(df.index)} with {len(features)} features...")
    
    if not unique_feature:
        for feature in features:
            embedding = model.encode(feature)
            new_row = {"Feature": feature, "embedding": embedding}
            df_features = pd.concat([df_features, pd.DataFrame([new_row])], ignore_index=True)
            df_features.to_csv(feature_path, index=False)
        unique_feature = list(df_features["Feature"])
    else:
        for feature_candidate in features:
            if feature_candidate not in unique_feature:
                feature_candidate_embedding = model.encode(feature_candidate).reshape(1, -1)
                is_unique = True
                
                for j in range(len(df_features.index)):
                    feature_embedding_str = df_features["embedding"][j]
                    
                    # Convert embedding string to array
                    try:
                        feature_embedding = np.array(ast.literal_eval(feature_embedding_str))
                    except ValueError:
                        continue
                    
                    similarity = cosine_similarity(feature_candidate_embedding, feature_embedding.reshape(1, -1))[0][0] * 100
                    if similarity >= THRESHOLD:
                        is_unique = False
                        break
                
                if is_unique:
                    new_row = {"Feature": feature_candidate, "embedding": feature_candidate_embedding}
                    df_features = pd.concat([df_features, pd.DataFrame([new_row])], ignore_index=True)
                    df_features.to_csv(feature_path, index=False)
                    unique_feature = list(df_features["Feature"])

# Print summary
print(f"Total unique features processed: {len(set(all_features))}")
print(f"Combined unique features added: {len(feature_list)}")
