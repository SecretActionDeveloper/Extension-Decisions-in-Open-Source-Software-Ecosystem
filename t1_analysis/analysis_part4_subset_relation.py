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

def is_subset(list1, list2):
    answer = True
    for elm in list1:
        if elm not in list2: 
            answer = False
            break
    return answer

path = ".\CI_t1_processed_1.csv"
df = pd.read_csv(path)

df["temp"] = ""
for i in range(len(df.index)):
    action = df["Action Name"][i]
    features = ast.literal_eval(df["Processed_Features"][i])
    df["temp"][i] =  features

df["subset_count"] = False; df["super_set_actions"] = False
all_subsets = 0
for i in  range(len(df.index)):
    features = df["temp"][i]
    action = df["Action Name"][i]
    subset_count = 0; super_set_actions = []
    if len(features) != 0:
        for j in range(len(df.index)):
            if i != j:
                other_features = df["temp"][j]
                other_action = df["Action Name"][j]
                if is_subset(features, other_features) and not is_two_list_same(features, other_features):
                    subset_count += 1
                    percentage = round(len(features) / len(other_features), 2)
                    super_set_actions.append((other_action, percentage))
    df["subset_count"][i] = subset_count
    df["super_set_actions"][i] = super_set_actions
    if subset_count > 0: all_subsets += 1

print("Number of actions that are subset of other actions: "  +str(all_subsets))
# Number of actions that are subset of other actions: 301
