import requests
from bs4 import BeautifulSoup
import os
import pandas as pd
import sys
import zipfile, io
import csv
import re
import numpy as np
import string
from github import Github
import os
from pprint import pprint
import yaml

# step3

#citation: https://stackoverflow.com/questions/9807634/find-all-occurrences-of-a-key-in-nested-dictionaries-and-lists
# given a dictionary and a key this function return all values to all the instances of the key
def findkeys(node, kv):
    if isinstance(node, list):
        for i in node:
            for x in findkeys(i, kv):
               yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in findkeys(j, kv):
                yield x

def get_dict_from_file(path):
  with open(path, encoding='utf8') as f:
      file =  yaml.safe_load(f) # a dictionary
  return file

# given a path to action, this function return content of all files and number of files in the repo
def get_content(path, content, count, action_yml_list):
    try:
        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            if os.path.isfile(file_path):
                if(file != "action.yml" and file != "action.yaml"):
                    # f = open(file_path, 'r',  encoding="utf8", errors='ignore')
                    # content = content + str(file)
                    # content = content + f.read()
                    count = count + 1
                    content.append(file)
                    # f.close()
                else: #get content of the action.yaml file
                    action_yml_file_dict =  get_dict_from_file(file_path)
                    action_yml_list.append(action_yml_file_dict)
            else:
                lis = []
                lis, count, action_yml_list = get_content(file_path, lis, count, action_yml_list)
                content.append(lis)
        return content, count, action_yml_list
    except:
        print("PROBLEM WITH GETTING FILES")
        return content, count, action_yml_list

path = "Scraped\datasets\Deployment\Deployment_GHM_action_page_links.csv"
path_to_file = "Scraped\Actions\Deployment"

df = pd.read_csv(path)
df["Num_of_files"] = ""; df["file_structure"] = ""
df["action_file_descriptions"] = ""; df["action_yml_list"]=""
# Get number of files
for i in range(len(df)):
    action_name = df["Action Name"][i]
    action_name = re.sub('[^\w_.)( -]', '', action_name)
    action_dir = os.path.join(path_to_file, action_name)
    if not os.path.exists(action_dir):
        print(i)
        print(f"The path '{action_dir}' does not exists.")
    else:
        file_name_list = []; num_file = 0; action_yml_list=[]

        file_name_list, num_file, action_yml_list = get_content(action_dir, file_name_list, num_file, action_yml_list)
        df["Num_of_files"][i] = num_file
        try:
            df["file_structure"][i] = file_name_list[0]
        except:
            df["file_structure"][i] = []
        df["action_yml_list"][i] = action_yml_list
        description_list = []
        for action_yml_dict in action_yml_list: #extract all `description` fields from the action.yamls
            descriptions = list(findkeys(action_yml_dict, "description")) 
            description_list.extend(descriptions)
        df["action_file_descriptions"][i] = description_list
        df.to_csv(path, index = False)
        print(i)
    df.to_csv(path, index = False)
print(len(df))
