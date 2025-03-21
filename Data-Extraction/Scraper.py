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

#Step 1: In this file given a link to a categroy of GitHub Marketplace, the code extracts  the All action pages in the category
# and get metadata + save scraped action pages

#given a action page url on the GHM get the link to repo +save the scraped page
def get_repo_links_from_action_page(action_name, url, category_name,save_scraped_path):
    try:
      repo_url = ""
      try:
        response = requests.get(url)
      except: print("problem with response")
      try:
        soup = BeautifulSoup(response.text, 'html.parser')
      except: print("problem with soup")
      try:
        save_path = save_scraped_path+"/" + category_name
        if not os.path.exists(save_path):
            os.makedirs(save_path)
          # save the scraped action page from GHM
        file_name = re.sub('[^\w_.)( -]', '', action_name)
        save_file_path = str(save_path +"/" + file_name + ".html")
        # print("file name created: " + str(save_file_path))
      except: print("problem with setting file name")
      try:
        with open(save_file_path, "w", encoding = 'utf-8') as file:
          # prettify the soup object and convert it into a string
            file.write(str(soup.prettify()))
        # print("scraped file saved: " + save_file_path)
      except: print("problem with save scraped file")
      try:
        link_soup = soup.findAll('a', class_='d-block mb-2')
        base_url = "https://github.com"
        # print("find tag for the repo links")
      except: print("problem with link soup")
      try:
        link = link_soup[0]
        # for link in link_soup:
        # print("got first link in action page: " + str(link))
      except: print("check list:" + link_soup)
      try:
        if(link.has_attr('href')):
              if (base_url in link["href"]):
                  repo_url = link["href"]
              else:
                repo_url = base_url+link["href"]
        # print("got the repo link: " + str(repo_url))
      except: print("problem with get repo link")
      try:
        return repo_url
      except: print("cannot return repo link")
    except:
        print("there is a problem with this page (most likely 404): " + str(url))


# given a link to page on GHM returns the dict_list of links of every action page on that page
# dict object:Name, short description, Link, verified creator(boolean), publisher, star to action page on GHM
def get_action_list_from_page(url, category_name, save_action_path, save_scraped_path):
    res = []
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser') # get html
    # action_obj_list = soup.findAll('div', class_="px-3") # each div represents an action on page
    action_obj_list = soup.findAll("a", class_="col-md-6 mb-4 d-flex no-underline")
    base_url = "https://github.com"
    for action_obj in action_obj_list:
        name = action_obj.find("h3", class_="h4")
        if name != None:
            dict_obj = {}
            name = name.text
            dict_obj["Name"] = name
            short_des = action_obj.find("p", class_="color-fg-muted lh-condensed wb-break-word mb-0").text
            dict_obj["short description"] = str(short_des)
            publisher = action_obj.find("span", class_="color-fg-muted").text
            dict_obj["publisher"] = publisher
            star_str = action_obj.find("span", class_="text-small color-fg-muted text-bold")
            star = 0
            if star_str != None:
                star = star_str.text
                # star = [int(i) for i in star_str.split() if i.isdigit()]
                # star = star[0]
            dict_obj["star"] = star
            verified_check = action_obj.find("svg", class_="octicon octicon-verified color-fg-accent")
            verified = False
            if verified_check != None: verified = True
            dict_obj["verified creator"] = verified
            link =str(base_url + action_obj['href'])
            dict_obj["Link"] =link
            dict_obj["repo_link"] = get_repo_links_from_action_page(name, link, cat_name,save_scraped_path) # getting a link to Action repository
            res.append(dict_obj)
    return res

#recursive function to gather link of all pages to a given category
# github has limitation of maximum 50 pages per category
def find_next_page(soup, page_list):
    next_page = soup.find('a', class_="next_page")
    flag = False
    try:
        flag = next_page.has_attr('href')
    except:
        flag = False
    if(flag):
        base_url = "https://github.com/"
        next_page_link = base_url + next_page["href"]
        page_list.append(next_page_link)
        response = requests.get(next_page_link)
        soup = BeautifulSoup(response.text, 'html.parser')
        find_next_page( soup, page_list)
    else:
      return



# Given a link to Action category page on GHM returns a list containing link to pages of the category
def get_all_pages_for_category(category_link, category_name):
  page_list = [category_link] # number of pages
  response = requests.get(category_link)
  soup = BeautifulSoup(response.text, 'html.parser')
  find_next_page(soup, page_list)
  return page_list
     


# given a link to a page gather info
def collect_action_page_links(page_link, cat_name, save_action_path,save_scraped_path, save_action_page_links):
  #path to where the links to action pages for this category are saved
    save_action_page_links_path = save_action_page_links+"/" + cat_name
    if not os.path.exists(save_action_page_links_path): # make the path to where csv of the action pages to this category are saved
        os.makedirs(save_action_page_links_path)
    save_action_page_links_file = cat_name  + "_GHM_action_page_links.csv"
    if not os.path.exists(save_action_page_links_path+"/"+save_action_page_links_file): #if file does not exists--> create
        # create csv file and save
        df_action_page = pd.DataFrame(columns=['Action Name', 'category', 'short description', 'verified creator',
        'publisher', "star",'Link to action page on GHM', 'link to action repo'])
        df_action_page .to_csv(save_action_page_links_path +"/"+save_action_page_links_file, index = False)

    # make a list of existing action page links
    count = 0
    action_list = []
    action_list = get_action_list_from_page(page_link, cat_name, save_action_path, save_scraped_path)# list of dict
    
    for action in action_list: # create dataset
        action_name = action["Name"]
        df_action_page  = pd.read_csv(save_action_page_links_path +"/"+save_action_page_links_file)
        existing_action_page_links = df_action_page ['Action Name'].tolist()
        # if action_name not in existing_action_page_links: # if the action does not exists
        if action_name not in df_action_page['Action Name'].values:
            action_des = action["short description"]
            action_link = action["Link"]
            verified_creator = action["verified creator"]
            publisher = action["publisher"]
            num_star = action["star"]
            # get repo link + save scraped pages of the action
            repo_link = action["repo_link"]
            # make a row
            new_row = {'Action Name': action_name, 'category': cat_name, 'short description': action_des,
                        "verified creator":verified_creator, "publisher": publisher,'star': num_star,
                        'Link to action page on GHM': action_link,"link to action repo": repo_link}
            df_action_page.loc[len(df_action_page )] = new_row
            df_action_page.to_csv(save_action_page_links_path +"/"+save_action_page_links_file, index = False)
            existing_action_page_links.append(action_name)
            count = count + 1
    return count


    # print("total number of links to actions pages extracted: " + str(count))



##########EXAMPLE USAGE#######################
## scrape actions for each category
cat_name = "Code_quality"
save_action_path = "Scraped\Actions"
save_scraped_path = "Scraped\ScrappedActionPage"
save_action_page_links = "Scraped\datasets"

## the following is suggested for large categories to overcome the limit os 1000 actions in GitHub category
link_list = [] 
base_cat_link = "https://github.com/marketplace?category=code-quality&type=actions"  # no sorting algorithm
best_match_link = "https://github.com/marketplace?category=deployment&query=sort%3Amatch-desc&type=actions&verification="
recently_added_link = "https://github.com/marketplace?category=deployment&query=sort%3Acreated-desc&type=actions&verification="
most_installed = "https://github.com/marketplace?category=deployment&query=sort%3Apopularity-desc&type=actions&verification="
link_list.append(base_cat_link)
link_list.append(best_match_link)
link_list.append(recently_added_link); link_list.append(most_installed)

keyword_set = ["docker+image", "run+build", "cloud+deploy", "easy+build", "automatic+deployment"] # this is dependent on the category (check paper for details)
for keyword in keyword_set:
    link0 = base_cat_link+ "&verification=&query="+keyword # no algorithm
    link1 = "https://github.com/marketplace?category=deployment&type=actions&verification=&query=sort%3Amatch-desc+"+keyword # best match
    link2 = "https://github.com/marketplace?category=deployment&type=actions&verification=&query=sort%253Acreated-desc+"+keyword # recently added
    link3 = "https://github.com/marketplace?category=deployment&type=actions&verification=&query=sort%253Apopularity-desc+"+keyword # most install/star
    link_list.append(link0); link_list.append(link1); link_list.append(link2); link_list.append(link3)

alphabet_set = list(set(string.ascii_lowercase))# + list(set(string.digits)) #+ list(set(string.ascii_uppercase)) #letters and numbers 
for letter in alphabet_set:
  # print(letter + ":")
    link0 = base_cat_link+ "&verification=&query="+letter
    link1 = "https://github.com/marketplace?category=testing&type=actions&verification=&query=sort%253Amatch-desc+"+letter # best match
    link2 = "https://github.com/marketplace?category=testing&type=actions&verification=&query=sort%253Acreated-desc+"+letter # recently added
    link3 = "https://github.com/marketplace?category=testing&type=actions&verification=&query=sort%253Apopularity-desc+"+letter # most install/star
    link_list.append(link0)#; link_list.append(link1); link_list.append(link2); link_list.append(link3)

total = 0
for link in link_list:
    # print(str(link) + ":")
    cat_pages = get_all_pages_for_category(link, cat_name) # gather all possible Actions pages in a category
    print(str(len(cat_pages)) + " Pages are extracted for "+ cat_name)
    count = 0
    for page in cat_pages:
        # print(page)
        num = collect_action_page_links(page, cat_name, save_action_path,save_scraped_path, save_action_page_links) # for each Action page collect actions data
        count = count + num
    total = total + count
    print("total number of links to actions extracted for this page: " + str(count))
    # print("//////////////////")
print("total number of links to actions extracted: " + str(total))



