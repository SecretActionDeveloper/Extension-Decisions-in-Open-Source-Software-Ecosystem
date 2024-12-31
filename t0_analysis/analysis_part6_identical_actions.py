import pandas as pd 
import ast
import math
import warnings
warnings.filterwarnings('ignore')

def is_two_list_same(list1, list2):
    all_features = []
    answer = False
    all_features.extend(list1)
    all_features.extend(list2)
    unique_all_feat = list(set(all_features))
    for feat in unique_all_feat:
        if feat in list1 and feat in list2:
            answer  = True
        else:
            answer = False
            break
    return answer

path = ".\CI_t0_processed.csv"
df = pd.read_csv(path)

df["temp"] = ""
for i in range(len(df.index)):
    action = df["Action_Name"][i]
    features = ast.literal_eval(df["Processed_Features"][i])
    df["temp"][i] =  features

df["same_feat_count"] = 0; df["actions_with_same_features"] = ""
count = 0
for i in range(len(df.index)):
    action = df["Action_Name"][i]
    features = df["temp"][i]
    same_feat_count = 0
    actions_with_same_features=[]
    if len(features) != 0: 
        for j in range(len(df.index)):
            if i != j:
                other_features = df["temp"][j]
                other_action = df["Action_Name"][j]
                if is_two_list_same(features, other_features):
                    same_feat_count += 1
                    actions_with_same_features.append(other_action)
        df["same_feat_count"][i] =  same_feat_count
        df["actions_with_same_features"][i] = actions_with_same_features
        if same_feat_count > 0: count += 1

print("Number of actions with same features as other actions: "  + str(count))
# # Number of actions with same features as other actions: 1741
