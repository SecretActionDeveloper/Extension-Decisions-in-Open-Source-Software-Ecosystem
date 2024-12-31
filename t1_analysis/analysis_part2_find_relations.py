import pandas as pd 
import ast
import warnings

# Suppress specific warning
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


path = ".\CI_t1_processed.csv"
df = pd.read_csv(path)

df["temp"] = ""
for i in range(len(df.index)):
    action = df["Action Name"][i]
    features = ast.literal_eval(df["Processed_Features"][i])
    df["temp"][i] =  features

print("There are " + str(len(df)) + " actions in this category")
print("##############################")
all_features = []; single_featured = 0; single_features_shared = 0
for i in range(len(df.index)):
    features = df["temp"][i]
    if " " in features: print(features)
    all_features.extend(list(set(features)))

res = []        
for i in range(len(df.index)):
    features = df["temp"][i]
    if len(features) == 1: 
        single_featured += 1
        feat = features[0]
        feat_count = all_features.count(feat)
        if feat_count> 1: res.append((feat, feat_count))


print("count of unique features: " + str(len(list(set(all_features)))))
print("number of Actions with single feature: " + str(single_featured))
print("##############################")
res = []
for i in range(len(df.index)):
    action = df["Action Name"][i]
    features = df["temp"][i]
    df["temp"][i] =  features
    if len(features) != 0: 
        for j in range(len(df.index)):
            if i != j:
                other_features = df["temp"][j]
                other_action = df["Action Name"][j]
                if len(features) == len(other_features):
                    if is_two_list_same(features, other_features):
                        res.append((action, other_action))
print("number of pairs of actions that share exact same functionalities: " + str(len(res)))

print("##############################")
print("Find subsets")
res = []
for i in range(len(df.index)):
    action = df["Action Name"][i]
    features = df["temp"][i]
    if len(features) != 0: 
        for j in range(len(df.index)):
            if i != j:
                other_features = df["temp"][j]
                other_action = df["Action Name"][j]
                if is_subset(features, other_features) and not is_two_list_same(features, other_features):
                        unique_feat = [item for item in other_features if item not in features]
                        percentage = len(features) / len(other_features) *100
                        res.append((action, other_action, percentage))
print("number of actions that subset of another action: " + str(len((res))))                       

print("##############################")
print("Find Independent actions")
res = []; res1 = []
for i in range(len(df.index)):
    action = df["Action Name"][i]
    features = df["temp"][i]
    if len(features) != 0:
        action_is_independent = True 
        for j in range(len(df.index)):
            if i != j:
                other_features = df["temp"][j]
                other_action = df["Action Name"][j]
                if intersect(features, other_features):
                     action_is_independent = False
                     break
        if action_is_independent and action not in res: 
            res.append(action)
            if len(features) > 1:
                res1.append(action)
print("number of actions that are independent: " + str(len((res))))
print("number of actions that are independent and have single feature: " + str(len(res)-len(res1))) 
print("number of actions that are independent and more than one feature: " + str(len(res1)))      

print("##############################")
print("Find intersection actions")
res = []
for i in range(len(df.index)):
    action = df["Action Name"][i]
    features = df["temp"][i]
    if len(features) != 0: 
        for j in range(len(df.index)):
            if i != j:
                other_features = df["temp"][j]
                other_action = df["Action Name"][j]
                if intersect(features, other_features) and not is_two_list_same(features, other_features) and not is_subset(features, other_features):
                        res.append(action)
                        break

print("number of actions that intersect with another action: " + str(len((res))))   
print("number of unique actions that intersect with  another action: " + str(len(list(set(res))))) 

