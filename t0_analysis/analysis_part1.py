import os
import ast
import pandas as pd

directory = "path to the processed file"

all_features = []
for root, dirs, files in os.walk(directory):
    for file_name in files:
        file_path = os.path.join(directory, file_name)
        df = pd.read_csv(file_path)
        for i in range(len(df.index)):
            features_raw = df["Processed_Features"][i]
            features = ast.literal_eval(features_raw)
            all_features.extend(features)

print("Number of features: "  +str(len(all_features)))
print("Number of unique features " + str(len(list(set(all_features)))))

# Number of features: 27,434
# Number of unique features 13,994
