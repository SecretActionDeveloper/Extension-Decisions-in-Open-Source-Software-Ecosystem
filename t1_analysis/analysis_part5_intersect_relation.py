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

def intersect(list1, list2):
    res = False
    for elm in list1: 
        if elm in list2: 
            res = True
            break
    return res

def get_overlap_percentage(list1, list2): ## percentage of feature overlap over all features
    res = 0
    all_feat = [] 
    all_feat.extend(list1)
    all_feat.extend(list2)
    all_feat_unique = list(set(all_feat))
    count_intersecting = 0
    for feat in all_feat_unique:
        if feat in list1 and feat in list2: count_intersecting += 1
    if len(all_feat_unique) != 0:
        res = count_intersecting/len(all_feat_unique)

    return res

path = ".\CI_t1_processed.csv"
df = pd.read_csv(path)

df["temp"] = ""
for i in range(len(df.index)):
    action = df["Action Name"][i]
    features = ast.literal_eval(df["Processed_Features"][i])
    df["temp"][i] =  features

df["intersect_count"] = 0; df["intersecting_actions"] = ""
count = 0
for i in range(len(df.index)):
    action = df["Action Name"][i]
    features = df["temp"][i]
    intersect_count = 0
    intersecting_actions=[]
    if len(features) != 0: 
        for j in range(len(df.index)):
            if i != j:
                other_features = df["temp"][j]
                other_action = df["Action Name"][j]
                if intersect(features, other_features) and not is_two_list_same(features, other_features) and not is_subset(features, other_features):
                    intersect_count += 1
                    overlap = get_overlap_percentage(features, other_features)
                    intersecting_actions.append((other_action, overlap))
        df["intersect_count"][i] =  intersect_count
        df["intersecting_actions"][i] = intersecting_actions
        if intersect_count > 0: count += 1

print("Number of actions that intersect with other actions: "  + str(count))
# # Number of actions that intersect with other actions: 5096
