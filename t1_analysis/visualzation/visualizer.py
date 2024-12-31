import pandas as pd
from ast import literal_eval
import networkx as nx
import pylab as plt
from pyvis import network as net
from networkx.algorithms import community
import pickle
import ast
import warnings
warnings.filterwarnings("ignore")

def FindMaxLength(lst):
    maxList = max(lst, key = lambda i: len(i))
    maxLength = len(maxList)
    return maxLength

def FindMinLength(lst):
    maxList = min(lst, key = lambda i: len(i))
    maxLength = len(maxList)
    return maxLength

def FindAverageLength(lst):
  total = len(lst)
  sum_len = 0
  for elm in lst:
    l = len(elm)
    sum_len += l
  try: avg = round(sum_len/total, 2)
  except: avg = 0
  return avg
  
def make_pairs(lst):
    pairs = []
    for i in range(len(lst)):
        for j in range(i + 1, len(lst)):
            pairs.append([lst[i], lst[j]])
    return pairs

def check_subset(list1, list2):
    set1 = set(list1)
    set2 = set(list2)
    return set1.issubset(set2)

def check_value_not_in_list_of_dicts(lst, key, value):
    for dictionary in lst:
        if key in dictionary and dictionary[key] == value:
            return False
    return True

def simplify_list(lst):
    simplified = []
    for sublist in lst:
        found = False
        for s in simplified:
            if any(item in s for item in sublist):
                s.extend(item for item in sublist if item not in s)
                found = True
                break
        if not found:
            simplified.append(sublist)
    return simplified

def extract_common_pairs(list_of_lists):
    common_pairs = []
    for i in range(len(list_of_lists)):
      sub_list1 = list_of_lists[i]
      pairs = make_pairs(sub_list1)
      pair_is_repeated = False
      for j in range(len(list_of_lists)):
          if i != j:
            sub_list2 = list_of_lists[j]
            pairs2 = make_pairs(sub_list2)
            for pair in pairs:
              if pair in pairs2:
                pair_is_repeated = True
                if pair not in common_pairs:
                  common_pairs.append(pair)
    return common_pairs


def get_res_test(path, save_vis, data_name, cat_name):
  file_path = save_vis+"/"+cat_name+"_report.txt"
  with open(file_path, "w") as f:
    f.write("Category: " + cat_name +"\n")
  df = pd.read_csv(path)
  df = df.dropna(subset=["Processed_Features"])
  df.reset_index(drop=True, inplace=True)
  for i in range(len(df.index)):
    try: df["Processed_Features"][i] = ast.literal_eval(df["Processed_Features"][i])
    except: print(df["Processed_Features"][i])
  print("There are " + str(len(df)) +" actions in " + str(data_name))
  max_num_feature = FindMaxLength(list(df["Processed_Features"]))
  min_num_feature = FindMinLength(list(df["Processed_Features"]))
  print("The max number of feature an action posses: " + str(max_num_feature))
  print("The min number of feature an action posses: " + str(min_num_feature))
  print("Average number of features per actions: " + str(FindAverageLength(list(df["Processed_Features"]))))
  print("##############################")
  with open(file_path, "a") as f:
    f.write("The max number of feature an action posses: " + str(max_num_feature) +"\n")
    f.write("The min number of feature an action posses: " + str(min_num_feature) +"\n")
    f.write("Average number of features per actions: " + str(FindAverageLength(list(df["Processed_Features"]))) +"\n")
#   ################################################################################
  G = nx.Graph()
  for i in range(len(df.index)):
      action = df["Action Name"][i]
      features = df["Processed_Features"][i]
      G.add_node(action, label = action, shape="diamond", color="green")
      publisher = df["publisher"][i]
      G.add_node(publisher, label = publisher, shape="dot", color="red")
      G.add_edge(action, publisher, color = "red")
      for feature in features:
          G.add_node(feature, label = feature, shape = "triangle" , color = "blue")
          G.add_edge(action, feature, color="green" )
  print("Created feature network")
  print("##############################")
  components = [G.subgraph(c).copy() for c in nx.connected_components(G)]
  print("There are " + str(len(components)) + " disjoint/ connected components in feature network")
  with open(file_path, "a") as f:
    f.write("There are " + str(len(components)) + " disjoint/ connected components in feature network-- objectives of the category"+"\n")
  print("##############################")
  ##################################################################################
  options = {
    "interaction": {
    "navigationButtons": True
    },
    "stabilization":{
        "enabled": True,
        "iterations": 800
      }
  }
  ##################################################################################
  print("Saving feature network + visualization")
  pickle.dump(G, open(save_vis + "/" +data_name+"_feature_net.pickle", 'wb'))
  G2 = net.Network(notebook=True)
  G2.options = options
  G2.from_nx(G)
  G2.show(save_vis + "/" +data_name+"_feature_net.html")
  print("Saved pvis visualization: feature_net")
  print("##############################")
  ###################################################################################
  print("10 most important features")
  with open(file_path, "a") as f:
    f.write("10 most important features: " + "\n")
  degree_centrality = nx.degree_centrality(G)
  count = 10
  for node in sorted(degree_centrality, key=degree_centrality.get, reverse=True):
    if count > 0:
      print(node, degree_centrality[node])
      with open(file_path, "a") as f:
        f.write(str(count) + ". "+ str(node) + "|" + str(degree_centrality[node]) +"\n")
      count = count -1
  print("##############################")
  print("distribution of degrees")
  degrees = [G.degree(n) for n in G.nodes()]
  print("##############################")
#   ###################################################################################
  all_nodes = [(node, degree) for node, degree in dict(G.degree()).items() if degree >= 0]
  df_features = pd.DataFrame(all_nodes, columns=['Features', 'Degree'])
  is_unique = len(set(list(df_features["Features"]))) ==len(list(df_features["Features"]))
  print("All nodes are unique: " + str(is_unique))
  with open(file_path, "a") as f:
    f.write("All nodes are unique: " + str(is_unique) + "\n")
#   ###################################################################################
  action_names = list(df["Action Name"])
  node_with_degree_one = [(node, degree) for node, degree in dict(G.degree()).items() if degree < 2]
  degree_1_nodes = pd.DataFrame(node_with_degree_one, columns=['nodes', 'Degree'])
  nodes = list(degree_1_nodes["nodes"])
  actions_with_degree1 = []; feature_with_degree_1=[]
  for n in nodes:
    if n in action_names:
      actions_with_degree1.append(n)
    else:
      feature_with_degree_1.append(n)
  if len(actions_with_degree1) != 0:
    print("number of actions with degree 1 or higher:  " + str(len(actions_with_degree1)))
    with open(file_path, "a") as f:
      f.write("number of actions with degree 1 or higher (actions with only one feature):  " + str(len(actions_with_degree1))+"\n")
    print("number of features with degree 1 or higher:  " + str(len(feature_with_degree_1)))
    with open(file_path, "a") as f:
      f.write("number of features with degree 1 or higher(features that belong to only one action):  " + str(len(feature_with_degree_1))+"\n")
#   ###################################################################################
  # Find atomic actions: if an actions has all feature that's in feature_with_degree_1 it means that is the only action with this feature
  # hence it is atomic action
  df_atomic_Actions = df.copy()
  for index, row in df_atomic_Actions.iterrows():
      features = row['Processed_Features']
      found_unique_feature = False
      for feature in features:
        if feature in feature_with_degree_1:
          found_unique_feature = True
        else:
          found_unique_feature = False
          break
      if not found_unique_feature:
        df_atomic_Actions = df_atomic_Actions.drop(index)
  df_atomic_Actions = df_atomic_Actions.reset_index(drop=True)
  print("There are " + str(len(df_atomic_Actions)) + " Atomic Actions.")
  with open(file_path, "a") as f:
    f.write("There are " + str(len(df_atomic_Actions)) + " Atomic Actions working on unique objectives." + "\n")
  print("##############################")
  #Add publisher to find atomic publishers
  print("adding publisher to atomic network")
  G_degree_1 = nx.Graph()
  for i in range(len(df_atomic_Actions.index)):
      action = df_atomic_Actions["Action Name"][i]
      features = df_atomic_Actions["Processed_Features"][i]
      publisher = df_atomic_Actions["publisher"][i]
      G_degree_1.add_node(action, label = action, shape="diamond", color="green")
      G_degree_1.add_node(publisher, label = publisher, shape="dot", color="red")
      G_degree_1.add_edge(action, publisher, color = "red")
      # add features that connected to at least another action
      for f in features:
          G_degree_1.add_node(f, label = f, shape = "triangle" , color = "blue")
          G_degree_1.add_edge(action, f, color = "green")
  print("Finished adding publishers")
  print("##############################")
  ###################################################################################
  print("creating pyvis")
  pickle.dump(G_degree_1, open(save_vis + "/" +data_name+"_atomic_publisher.pickle", 'wb'))
  G2 = net.Network(notebook=True)
  G2.options = options
  G2.from_nx(G_degree_1)
  G2.show(save_vis + "/" +data_name+"_atomic_publisher.html")
  print("Saved pvis visualization: atomic_publisher")
  print("##############################")
  ###################################################################################
  components = [G_degree_1.subgraph(c).copy() for c in nx.connected_components(G_degree_1)]
  print("There are " + str(len(components)) + " atomic publishers working on one or more atomic actions")
  with open(file_path, "a") as f:
    f.write("There are " + str(len(components)) + " atomic publishers working on one or more atomic actions" + "\n")
  print("##############################")
  ###################################################################################
  nodes_with_degree_2_or_more = [(node, degree) for node, degree in dict(G.degree()).items() if degree >= 2]
  df_degree2 = pd.DataFrame(nodes_with_degree_2_or_more, columns=['nodes', 'Degree'])
  print("There are " + str(len(list(df_degree2["nodes"]))) + "  nodes with degree 2 or more")
  with open(file_path, "a") as f:
    f.write("There are " + str(len(list(df_degree2["nodes"]))) + "  nodes with degree 2 or more" + "\n")
  # are all node features?
  nodes = list(df_degree2["nodes"])
  actions_with_degree2 = []; features_with_degree2 = []
  for n in nodes:
    if n in action_names:
      actions_with_degree2.append(n)
    else:
      features_with_degree2.append(n)
  if len(actions_with_degree2) != 0:
    print("not all nodes are features")
    print("number of actions with degree 2 or higher:  " + str(len(actions_with_degree2)))
    with open(file_path, "a") as f:
      f.write("number of actions with degree 2 or higher (actions with at least 2 features):  " + str(len(actions_with_degree2)) +"\n")
    print("number of features with degree 2 or higher:  " + str(len(features_with_degree2)))
    with open(file_path, "a") as f:
      f.write("number of features with degree 2 or higher (features common between at least 2 actions):  " + str(len(features_with_degree2))+"\n")
  ###################################################################################
  #Find composite Actions
  df_degree_2 = df.copy()
  for index, row in df_degree_2.iterrows():
      features = row['Processed_Features']
      keep = False
      for f in features_with_degree2:
        if f in features:
          keep  = True
          break
      if not keep:
          df_degree_2 = df_degree_2.drop(index)
  df_degree_2 = df_degree_2.reset_index(drop=True)
  print("There are " + str(len(df_degree_2)) + " actions with at least one feature of degree 2 or higher (Composite Actions)")
  with open(file_path, "a") as f:
      f.write("There are " + str(len(df_degree_2)) + " actions with at least one feature in common with at least another actions--composite actions (features of degree 2 or higher)" +"\n")
  print("##############################")
  print("Adding publishers to the network")
  G_degree_2 = nx.Graph()
  for i in range(len(df_degree_2.index)):
      action = df_degree_2["Action Name"][i]
      features = df_degree_2["Processed_Features"][i]
      publisher = df_degree_2["publisher"][i]
      G_degree_2.add_node(action, label = action, shape="diamond", color="green")
      G_degree_2.add_node(publisher, label = publisher, shape="dot", color="red")
      G_degree_2.add_edge(action, publisher, color = "red")
      # add features that connected to at least another action
      for f in features:
          G_degree_2.add_node(f, label = f, shape = "triangle" , color = "blue")
          G_degree_2.add_edge(action, f, color = "green")
  print("Finished adding publishers")
  print("##############################")
  components = [G_degree_2.subgraph(c).copy() for c in nx.connected_components(G_degree_2)]
  with open(file_path, "a") as f:
    f.write("There are " + str(len(components)) + " objectives targeted by composite publishers" + "\n")
  print("There are " + str(len(components)) + " objectives targeted by composite publishers")
  print("##############################")
  #Find number of composite publishers:
  publisher_list = list(df["publisher"]); action_list =  list(df["Action Name"])
  all = [(node, degree) for node, degree in dict(G_degree_2.degree()).items() if degree >= 0]
  temp_degree2 = pd.DataFrame(all, columns=['nodes', 'Degree'])
  nodes = list(temp_degree2["nodes"])
  publishers= [];
  for n in nodes:
    if n in publisher_list:
      publishers.append(n)
  with open(file_path, "a") as f:
    f.write("There are " + str(len(publishers)) + " composite publishers" + "\n")
  print("There are " + str(len(publishers)) + " composite publishers out of total " + str(len(set(publisher_list))))
  ###########################################################################################
  pickle.dump(G_degree_2, open(save_vis + "/" +data_name+"_objectives_composite_publisher.pickle", 'wb'))
  G2 = net.Network(notebook=True)
  G2.options = options
  G2.from_nx(G_degree_2)
  G2.show(save_vis + "/" +data_name+"_objectives_composite_publisher.html")
  print("Saved pvis visualization 2")
  print("##############################")
  ###########################################################################
  # Find features that happen together
  all = [(node, degree) for node, degree in dict(G_degree_2.degree()).items() if degree >= 0] # list of tuple of node, degree
  temp_degree2 = pd.DataFrame(all, columns=['nodes', 'Degree'])
  nodes = list(temp_degree2["nodes"]);
  publishers= []; action_list = []; feature_list = []
  publisher_list = list(df["publisher"]); action_list_df =  list(df["Action Name"])
  for n in nodes:
      if n in publisher_list:
        publishers.append(n)
      elif n in action_list_df: action_list.append(n)
      else: feature_list.append(n)

  disjoint_components = list(nx.connected_components(G_degree_2))
  features_that_come_together = []; base_features = []
  for component in disjoint_components:
    subgraph = G_degree_2.subgraph(component)
    edges = list(subgraph.edges())
    edges_action_feature = []
    for e in edges:
        if e[0] not in publishers and e[1] not in publishers:
          edges_action_feature.append(e)
    component_action_list = []; component_feature_list=[]
    for e in edges_action_feature:
      if e[0] in action_list and e[0] not in component_action_list: component_action_list.append(e[0])
      if e[1] in action_list and e[1] not in component_action_list: component_action_list.append(e[1])
      if e[0] not in action_list and e[0] not in component_feature_list: component_feature_list.append(e[0])
      if e[1] not in action_list and e[1] not in component_feature_list: component_feature_list.append(e[1])
    feature_count_action_list = []; action_added=[]
    for action in component_action_list:
      if action not in action_added:
        features = []
        for e in edges_action_feature:
          if e[0] == action and e[1] not in features:
            features.append(e[1])
          if e[1] == action and e[0] not in features:
            features.append(e[0])
        feature_count_action_list.append({"action": action, "features":features })
        action_added.append(action)
    # find features that come together
    list_list_feature = [] ; Find_base_feature_list_fature = []
    for elm in feature_count_action_list:
        feature = elm["features"]
        list_list_feature.append(feature)
        Find_base_feature_list_fature.extend(feature)

    # find the base features of the comoponent
    base_candicate_set_list =list(set(Find_base_feature_list_fature)); base_count_list=[]
    for feature in base_candicate_set_list:
      feature_count = Find_base_feature_list_fature.count(feature)
      base_count_list.append((feature, feature_count))

    num_actions = len(component_action_list);
    for tup in base_count_list:
      if tup[1] == num_actions and num_actions> 2 : base_features.append(tup[0])
    features_pair_come_together = extract_common_pairs(list_list_feature)

    # print(features_pair_come_together)
    # check if the pairs are repeated
    repeated_pairs = []
    for i in range(len(features_pair_come_together)):
      repeat_count = 0
      pair = features_pair_come_together[i]
      elm11 = pair[0]; elm12 = pair[1]
      for j in  range(len(features_pair_come_together)):
        if i!=j:
          pair2 = features_pair_come_together[j]
          elm21 = pair2[0]; elm22 = pair2[1]
          if elm11 == elm21 and elm12 == elm22: repeat_count +=1
          if elm11 == elm22 and elm12 == elm21: repeat_count +=1
      if repeat_count >= 2:
        for elm in repeated_pairs:
          if (elm11 != elm[0] or elm12 != elm[1]) or (elm11 != elm[1] or elm12 != elm[0]): repeated_pairs.append(pair)
    consolidate_list = simplify_list(repeated_pairs)
    features_that_come_together.extend(consolidate_list)

  print("Features that happen together in this network: "+str(features_that_come_together))
  with open(file_path, "a", encoding="utf-8") as f:
    f.write("#####################################\n")
    f.write("Features that happen together in this network: "+str(features_that_come_together) + "\n")
    f.write("#####################################\n")
  size_counts = {}

  for sublist in features_that_come_together:
      size = len(sublist)
      if size in size_counts:
          size_counts[size] += 1
      else:
          size_counts[size] = 1

  print("possible tuple sizes for features that happen together:", len(size_counts))
  with open(file_path, "a") as f:
    f.write("possible tuple sizes for features that happen together:" + str(len(size_counts)) + "\n")
  print("Different sizes and their counts:")
  with open(file_path, "a") as f:
    f.write("Different sizes and their counts:" + "\n")
  for size, count in size_counts.items():
      print("Size:", size, "- Count:", count, "| There are " + str(count) + ", " + str(size)+"-tuple feature set that happen together")
      with open(file_path, "a") as f:
        f.write("There are " + str(count) + ", " + str(size)+"-tuple feature set that happen together (these tuples appear more than once together)"+"\n")
  print("We found " +str( len(base_features) )+" Basal Features: ")
  print(base_features)
  with open(file_path, "a") as f:
        f.write("We found " + str(len(base_features)) +" Basal Features: "+"\n")
        f.write(str(base_features)+"\n")

  ##############################################################################################

### make sure the dataset has all necessary columns which are processed in previous steps. 
path = ".\CI_t1_processed.csv"
save_vis = "Visualization_t1"
data_name = "t_1"
get_res_test(path, save_vis, data_name, data_name)
