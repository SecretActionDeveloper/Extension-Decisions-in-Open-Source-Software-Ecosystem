import pandas as pd

df_t1 = pd.read_csv("\CI_t1_processed.csv")

df_t0 = pd.read_csv("\CI_t0_processed.csv")

df_t0["publisher"] = ""
for i in range(len(df_t0.index)):
    action_name_0 = df_t0["Action_Name"][i]
    publisher = ""
    for j in range(len(df_t1.index)):
        action_name_1 = df_t1["Action Name"][j]
        if action_name_0 == action_name_1:
            publisher =  df_t1["publisher"][j]
            break
    df_t0["publisher"][i] = publisher

path = "\CI_t0_processed_5.csv"
df_t0 = df_t0[df_t0["publisher"] != ""]

df_t0.to_csv(path, index = False)
