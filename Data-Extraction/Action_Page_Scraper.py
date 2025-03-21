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

# step 2

# remove actions without link to repo (usually these are 404 pages)
def clean_dataset(df_path):
    df = pd.read_csv(df_path)
    new_df = df.dropna()
    new_df.to_csv(df_path, index = False)

# extract the name used to call the action in yml files this is same name but different formating:Action Name  vs actionname
def get_action_name_used(df_path):
    # print("ok")
    df = pd.read_csv(df_path)
    df["action_name_used"] = ""

    for i in range(len(df.index)):
        link = df["Link to action page on GHM"][i]
        value = link.split('/')[-1]
        df["action_name_used"][i] = value
    df.to_csv(df_path, index = False)

# get the list of contributor from the scraped action pages
def get_contributors(df_path, path_to_scraped_pages):
    df = pd.read_csv(df_path)
    df["Contributors"] = ""
    for i in range(len(df.index)):
        action_name = df["Action Name"][i]
        contributor_list = []
        file_name = re.sub('[^\w_.)( -]', '', action_name)
        path_to_file = str(path_to_scraped_pages +"/" + file_name + ".html")
        try:
            HTMLFileToBeOpened = open(path_to_file, "r", encoding="utf8")
            contents = HTMLFileToBeOpened.read()
            soup = BeautifulSoup(contents, 'html.parser')
            Container = soup.find_all(lambda tag: tag.name == 'div' and tag.get('class') == ['pb-3'])
            try:
                cont_container = Container[0].find_all(class_='ml-n1 clearfix')
                cont_list = cont_container[0].find_all('a')
                for cont in cont_list:
                    cont_name = cont["href"]
                    cont_name = re.sub('/', '', cont_name)
                    contributor_list.append(cont_name)
                df["Contributors"][i] = contributor_list
                df.to_csv(df_path, index = False)
            except: print("cannot get contributors")
        except: print("File does not exists")

# get the long description
def get_long_description(df_path, path_to_scraped_pages):
    df = pd.read_csv(df_path)
    df["Long_des"] = ""
    for i in range(len(df.index)):
        action_name = df["Action Name"][i]
        file_name = re.sub('[^\w_.)( -]', '', action_name)
        path_to_file = str(path_to_scraped_pages +"/" + file_name + ".html")
        try:
            HTMLFileToBeOpened = open(path_to_file, "r", encoding="utf8")
            contents = HTMLFileToBeOpened.read()
            soup = BeautifulSoup(contents, 'html.parser')
            des_container = soup.findAll('div', class_ ="markdown-body")
            try: des = des_container[0].text
            except: 
                try: des = des_container.text
                except: des = ""
            des = des.strip()
            des = os.linesep.join([s for s in des.splitlines() if s])
            df["Long_des"][i] = des
            df.to_csv(df_path, index = False)
        except: print("File does not exists")

def get_open_issues(df_path, path_to_scraped_pages):
    df = pd.read_csv(df_path)
    df["open_issues"] = ""
    for i in range(len(df.index)):
        action_name = df["Action Name"][i]
        file_name = re.sub('[^\w_.)( -]', '', action_name)
        path_to_file = str(path_to_scraped_pages +"/" + file_name + ".html")
        try:
            HTMLFileToBeOpened = open(path_to_file, "r", encoding="utf8")
            contents = HTMLFileToBeOpened.read()
            soup = BeautifulSoup(contents, 'html.parser')
            all_a = soup.findAll('a', class_="d-block mb-2")
            try:
                issue_container = all_a[1].find('span', class_="Counter float-right") 
                try:issue_count = [int(i) for i in issue_container.text.split() if i.isdigit()][0]
                except: 
                    try: issue_count = issue_container.text
                    except:  issue_count = 0   
                df["open_issues"][i] = issue_count
                df.to_csv(df_path, index = False)
            except: print("Could not get issue count")
        except: print("File does not exists")

def get_num_releases(df_path):
    df = pd.read_csv(df_path)
    df["num_releases"] = ""
    for i in range(len(df.index)):
        repo_link = df["link to action repo"][i]
        if not pd.isna(repo_link):
            response = requests.get(repo_link)
            soup = BeautifulSoup(response.text, 'html.parser')
            release_list = soup.findAll('a', class_="Link--primary no-underline Link")
            try:
                release_count_container = release_list[0].find('span', class_="Counter")
                release_count = release_count_container.text
            except:
                release_count = 1
            df["num_releases"][i] = release_count
            df.to_csv(df_path, index = False)

# get link to download the repo
def get_download_link(df_path):
    df = pd.read_csv(df_path)
    df["downlod_link"] = ""
    for i in range(len(df.index)):
        repo_link = df["link to action repo"][i]
        try:
            response = requests.get(repo_link)
            soup = BeautifulSoup(response.text, 'html.parser')
            repo_soup = soup.findAll('a', class_='d-flex flex-items-center color-fg-default text-bold no-underline')
            link = None
            for r in repo_soup:
                if "Download ZIP" in r.text:
                    link = "https://github.com/" + r['href']
            df["downlod_link"][i] = link
            df.to_csv(df_path, index = False)
        except: print("cannot get download link")

# download the action repos
def download(df_path, download_path):
    df = pd.read_csv(df_path)
    for i in range(len(df.index)):
        action_name = df["Action Name"][i]
        file_name = re.sub('[^\w_.)( -]', '', action_name)
        path = download_path+"/"+file_name
        url = df["download_rep_link"][i]
        try:
            if not os.path.exists(path):
                r = requests.get(url)
                z = zipfile.ZipFile(io.BytesIO(r.content))
                os.makedirs(path)
                z.extractall(path)
        except: print(" could not download the repo")
        print(i)
##################################################################################
df_path = "Scraped\datasets\Deployment\Deployment_GHM_action_page_links.csv"
path_to_scraped_pages = "Scraped\ScrappedActionPage\Deployment"
download_path = "Scraped\Actions\Deployment"

clean_dataset(df_path)#remove action without repo link
get_action_name_used(df_path)# get the name of action used in workflow files
get_contributors(df_path, path_to_scraped_pages)
get_long_description(df_path, path_to_scraped_pages)#get long description
get_open_issues(df_path, path_to_scraped_pages)#get open issues

get_num_releases(df_path)#get release number
get_download_link(df_path) #get download links
download(df_path, download_path) # download repo    
# print(len(next(os.walk(download_path))[1]))

df = pd.read_csv(df_path)
print(len(df))
