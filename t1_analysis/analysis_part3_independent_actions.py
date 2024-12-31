import pandas as pd 
import ast
import warnings
warnings.filterwarnings('ignore')

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

indep_count = 0; single_count = 0
df["Independent"] = False; df["Single_featured"] = False
for i in  range(len(df.index)):
    features = df["temp"][i]
    if len(features) != 0:
        if len(features) == 1:
            df["Single_featured"][i] = True
            single_count += 1
        action_is_independent = True 
        for j in range(len(df.index)):
            if i != j:
                other_features = df["temp"][j]
                if intersect(features, other_features):
                    action_is_independent = False
                    break
        if action_is_independent:
            df["Independent"][i]  = True
            indep_count += 1

print("Number of independent actions: " + str(indep_count))
print("Number of single featured actions: " + str(single_count))
        
# Number of independent actions: 627
# Number of single featured actions: 466
