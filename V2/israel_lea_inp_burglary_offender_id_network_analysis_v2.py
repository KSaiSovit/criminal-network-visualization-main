"""
=================================== LICENSE ==================================
Copyright (c) 2021, Consortium Board ROXANNE
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

Neither the name of the ROXANNE nor the
names of its contributors may be used to endorse or promote products
derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY CONSORTIUM BOARD ROXANNE ``AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL CONSORTIUM BOARD TENCOMPETENCE BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
==============================================================================
"""

import os
import sys
import getopt
import time
import pickle
import json
import operator
import random
import pandas as pd
import networkx as nx
import networkx.algorithms.link_prediction as lp_methods

from networkx.readwrite import json_graph
from copy import deepcopy
from joblib import Parallel, delayed

tokens = os.path.abspath(__file__).split('/')
path2root = '/'.join(tokens[:-3])
if path2root not in sys.path:
    sys.path.append(path2root)

from analyzer import link_prediction
'''importing libraries'''

LIST_TOP_K = [10, 20, 50, 100, 200]

def load_graph_from_json_file(graph_file_path):
    with open(graph_file_path) as json_file:
        data = json.load(json_file)
    G = json_graph.node_link_graph(data)
    return G
'''

This function loads a graph from a JSON file into a specific graph format.

Steps:
- Opens the JSON file.
- Loads JSON data
- Creates graph object
- Returns the graph
'''

def dump_centrality_scores(graph, dump_path):
    scores = nx.betweenness_centrality(graph, weight='weight')
    with open(dump_path, 'wb') as fp:
        pickle.dump(scores, fp)
    print('Dumped file succesful: ' +  dump_path)
'''
This function calculates and saves betweenness centrality scores for a weighted graph.

Steps:
- Input
- Calculating scores
- Saving scores
'''

def get_top_k_central_nodes(scores, top_k=100):
    cd = sorted(scores.items(),key=operator.itemgetter(1),reverse=True)
    list_tuple_score_node = cd[:top_k]
    return list_tuple_score_node
'''

This function takes a dictionary of centrality scores for nodes in a graph and returns a list of the top K nodes with the highest scores. 

Input:
- scores
- top_k

Steps
- Sort the dictionary
- Select top K nodes
- Return the results

Output: A list of tuples, where each tuple contains a node and its corresponding centrality score.
'''

def select_top_k(candidates, top_k=3):
    candidates.sort(key=operator.itemgetter(1), reverse=True)
    return [u[0] for u in candidates[:top_k]]
'''

This function select_top_k selects the top k elements from a list of candidates based on their second element.

Input:
- candidates
- top_k (optional)/(default is 3)

Steps:
- Sort the candidates
- Select top k elements
- Return the results

This function assumes that the candidates list contains tuples with at least two elements.
The sorting and selection are based on the second element of each tuple.
top_k value can be adjusted to retrieve a different number of top elements.
'''

def generate_link_predictions(scores, sources, top_k=3):
    preds = dict()
    for u in sources:
        preds[u] = []

    for u, v, p in scores:
        preds[u].append((v, p))
    
    for u in preds:
        preds[u] = select_top_k(preds[u], top_k)

    return preds
'''
This function takes a dictionary of link prediction scores and a list of source nodes as input and returns a dictionary of predicted links for each source node.

Input:
- scores (A dictionary where keys are triples (u, v, p), representing edges between nodes u and v with predicted score p.)
- sources (A list of nodes for which you want to generate link predictions.)
- top_k (optional)/(default is 3)

Steps:
- Initialize predictions dictionary
- Iterate over sources
- Iterate over scores
- Select top K predictions
- Return the results

Output:
The function returns a dictionary preds where keys are source nodes and values are lists of tuples (v, p), representing the top top_k predicted links with their corresponding scores.
'''

def get_top_k_predicted_links(nx_undirected_graph, source_nodes, top_k=3):
    undirected_graph = nx_undirected_graph
    candidate_links = link_prediction._get_candidates(undirected_graph, source_nodes)
    print('length of candidate_links:', len(candidate_links))
    lp_scores = lp_methods.jaccard_coefficient(undirected_graph, candidate_links)
    predictions = generate_link_predictions(lp_scores, sources=source_nodes, top_k=top_k)

    return predictions
'''
This function predicts potential links in an undirected graph for specific source nodes, returning the top K predictions for each source.

Input:
- nx_undirected_graph
- source_nodes (list of nodes)
- top_k (optional)/(default is 3)

Steps:
- Get candidate links
- Calculate link prediction scores
- Generate link predictions
- Return predictions

Output:
The function returns a dictionary where keys are source nodes and values are lists of tuples (v, p), representing the top top_k predicted links with their corresponding Jaccard coefficient scores.
'''

def has_two_hop_neighbors(nx_undirected_graph, node):
    neighbors = nx_undirected_graph.neighbors(node)
    second_hop_neighbors = set()

    for v in neighbors:
        second_hop_neighbors = second_hop_neighbors.union(set(nx_undirected_graph.neighbors(v)))
    second_hop_neighbors = second_hop_neighbors.difference(neighbors)

    if node in second_hop_neighbors:
        second_hop_neighbors.remove(node)
    
    if len(second_hop_neighbors) > 0:
        return True
    else:
        return False 
'''
This function determines whether a given node in an undirected graph has any second-hop neighbors, meaning nodes two connections away.

Input:
- nx_undirected graph
- node

Steps:
- Find direct neighbours
- Find second-hop neighbours
- Exclude for existence

Output:
This function returns a boolean value: True if the given node has at least one second-hop neighbor, False otherwise.

This function utilizes sets to handle node neighbors and avoid duplicates.
It considers both the structure of the graph and potential self-loops for an accurate answer.
'''

def run_link_predictions(nx_undirected_graph, removed_edge):
    result = dict()

    source, target = removed_edge
    temp_graph = deepcopy(nx_undirected_graph)
    temp_graph.remove_edge(source, target)

    pred_links = get_top_k_predicted_links(temp_graph, source_nodes=[source], top_k=5)
    # print(pred_links)

    result[removed_edge] = {
        'top_5': target in pred_links[source],
        'top_3': target in pred_links[source][:3],
        'top_1': target in pred_links[source][:1],
    }
    # print(result, pred_links)

    return result
'''
This function, run_link_predictions, analyzes how removing a specific edge from an undirected graph affects link prediction accuracy.

Input:
- nx_undirected_graph
- removed_edge

Steps:
- Initialize results dictionary
- Extract edge nodes
- Create temporary graph 
(Uses deepcopy to create a copy of the original graph (temp_graph).
 Removes the specified removed_edge from the temp_graph.)
- Run link prediction
- Analyze prediction accuracy
- Return results

Output:

This function, run_link_predictions, analyzes how removing a specific edge from an undirected graph affects link prediction accuracy. Here's a breakdown:

Input:

nx_undirected_graph: An undirected networkx graph object representing the network.
removed_edge: A tuple (source, target) specifying the edge to remove for analysis.
Steps:

Initialize results dictionary:

Creates an empty dictionary result to store the analysis outcome.
Extract edge nodes:

Unpacks the removed_edge tuple to get the source and target nodes.
Create temporary graph:

Uses deepcopy to create a copy of the original graph (temp_graph).
Removes the specified removed_edge from the temp_graph.
Run link prediction:

Calls get_top_k_predicted_links to predict potential links in the modified graph (temp_graph):
Uses the source node (source) as the starting point.
Predicts the top 5 potential links (top_k=5).
(The commented-out print statement could be used for debugging to view these predictions).
Analyze prediction accuracy:

Checks if the original target node (target) is present in the predicted links for the source node:
Records whether it's among the top 5 (top_5).
Records whether it's among the top 3 (top_3).
Records whether it's the top predicted link (top_1).
Adds these results to the result dictionary for the removed_edge.
Return results:

Returns the result dictionary, containing information about whether the removed edge affected the prediction of the original target node for different ranking positions.

Output:
The function returns a dictionary result with the removed edge as the key.

- top_5: True/False indicating if the original target node was among the top 5 predicted links after removing the edge.
- top_3: True/False indicating if the original target node was among the top 3 predicted links.
- top_1: True/False indicating if the original target node was the top predicted link.
'''

def run_link_predictions_with_multi_edges(nx_undirected_graph, list_removed_edge):
    result = dict()

    temp_graph = deepcopy(nx_undirected_graph)
    set_source_node = set()
    for removed_edge in list_removed_edge:
        source, target = removed_edge
        set_source_node.add(source)
        set_source_node.add(target)

        if removed_edge in temp_graph.edges():
            temp_graph.remove_edge(source, target)
    
    list_source_node = list(set_source_node)
    print(nx.info(temp_graph))
    # print('List of source node', list_source_node)

    pred_links = get_top_k_predicted_links(temp_graph, source_nodes=list_source_node, top_k=5)
    # print(pred_links)

    for removed_edge in list_removed_edge:
        source, target = removed_edge
        result[removed_edge] = {
            'top_5': target in pred_links[source] or source in pred_links[target],
            'top_3': target in pred_links[source][:3] or source in pred_links[target][:3],
            'top_1': target in pred_links[source][:1] or source in pred_links[target][:1]
        }
    # print(result, pred_links)

    return result
'''
Analyzes how removing multiple edges from an undirected graph affects link prediction accuracy.
Extends run_link_predictions to handle multiple edge removals and multiple source nodes.

Inputs:
- nx_undirected_graph
- list_removed_edge

Steps:
- Initiaslize
- Create temporary graph
- Handle multiple edge removals
    - Calls get_top_k_predicted_links to predict potential links in the modified graph:
        - Uses all nodes in list_source_node as starting points for prediction.
        - Predicts the top 5 potential links for each source node
- Analyze prediction accuracy for each removed edge
- Return results

Output:
Returns a dictionary result with removed edges as keys.
Values are dictionaries with keys top_5, top_3, and top_1, indicating if the original target node was predicted in those rankings after removing the edge.

Extends the analysis to handle multiple edge removals and multiple source nodes.
Considers bidirectional predictions (source to target and vice versa).
Assists in evaluating the robustness of link prediction algorithms under edge removal scenarios.
'''

def run_link_predictions_with_multi_edges_ground_truth(nx_undirected_graph, list_removed_edge):
    result = dict()

    temp_graph = deepcopy(nx_undirected_graph)
    set_source_node = set()
    for removed_edge in list_removed_edge:
        source, target = removed_edge
        set_source_node.add(source)
        set_source_node.add(target)

    list_source_node = list(set_source_node)
    print(nx.info(nx_undirected_graph))
    # print('List of source node', list_source_node)

    pred_links = get_top_k_predicted_links(temp_graph, source_nodes=list_source_node, top_k=5)
    print(pred_links)

    for removed_edge in list_removed_edge:
        source, target = removed_edge
        result[removed_edge] = {
            'top_5': target in pred_links[source] or source in pred_links[target],
            'top_3': target in pred_links[source][:3] or source in pred_links[target][:3],
            'top_1': target in pred_links[source][:1] or source in pred_links[target][:1]
        }

    # print(result, pred_links)

    return result
'''
This function, run_link_predictions_with_multi_edges_ground_truth, is similar to run_link_predictions_with_multi_edges with one key difference: the absence of ground truth information.

Analyzes how removing multiple edges from an undirected graph affects link prediction accuracy.
Similar to run_link_predictions_with_multi_edges, but without access to actual missing links as ground truth.

Inputs:
- nx_undirected_graph
- list_removed_edge

Steps:
- Initialize results dictionary and temporary graph
- Handle multiple edge removals
- Generate list of source nodes
- Run link prediction for multiple sources
- Analyze prediction accuracy (without ground truth)
- Return results

Key Difference:
- No explicit use of ground truth information about missing links.
- Analysis only shows presence in top predictions, not accuracy compared to actual missing links.
'''

def calculate_accuaracy(list_item):
    return (sum(list_item) / len(list_item)) * 100
'''
This function takes a list of items and returns the accuracy.
'''

def evaluate_results(dict_results):
    list_value_top_1 = []
    list_value_top_3 = []
    list_value_top_5 = []
    for _, value in dict_results.items():
        list_value_top_1.append(value['top_1'])
        list_value_top_3.append(value['top_3'])
        list_value_top_5.append(value['top_5'])
    
    acc_top_1 = round(calculate_accuaracy(list_value_top_1), 4)
    acc_top_3 = round(calculate_accuaracy(list_value_top_3), 4)
    acc_top_5 = round(calculate_accuaracy(list_value_top_5), 4)
    
    print('top_1:', round(calculate_accuaracy(list_value_top_1), 4))
    print('top_3:', round(calculate_accuaracy(list_value_top_3), 4))
    print('top_5:', round(calculate_accuaracy(list_value_top_5), 4))

    return (acc_top_1, acc_top_3, acc_top_5)
'''
This function calculates and prints the accuracy of link prediction results at different ranking positions (top 1, top 3, top 5).

Inputs:
- dict_results

Steps:
- Extract prediction values
- Calculate accuracy
- Print and return results
'''

def get_run_version():
    # Remove 1st argument from the
    # list of command line arguments
    argumentList = sys.argv[1:]
    
    # Options
    options = "hmr:"
    
    # Long options
    long_options = ["Help", "My_file", "Run"]
    
    try:
        # Parsing argument
        arguments, values = getopt.getopt(argumentList, options, long_options)
        
        # checking each argument
        for currentArgument, currentValue in arguments:
    
            if currentArgument in ("-h", "--Help"):
                print ("Displaying Help")
                
            elif currentArgument in ("-m", "--My_file"):
                print ("Displaying file_name:", sys.argv[0])
                
            elif currentArgument in ("-r", "--Run"):
                print (("Execute the run (% s)") % (currentValue))
                return currentValue
             
    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))
'''
This function handles command-line arguments and extract a specific value related to a run version. 

Parses command-line arguments passed to the program.
Extracts the value associated with the -r or --Run option, which is assumed to represent the run version.

Steps:
- Remove first argument
- Define options and long options
- Parese arguments
- Process each argument
- Handle errors

Output:
- Prints help messages or file name for specific options.
- Returns the extracted run version value if the -r or --Run option is used.
'''

def run_experiment_top_k_central_node(graph_file_path, nx_undirected_graph, scores_centrality):
    undirected_graph = nx_undirected_graph

    pd_data = []
    for top_k in LIST_TOP_K:
        print('Number of Central Nodes:', top_k, 'Running Version:', run_version)

        central_nodes = get_top_k_central_nodes(scores_centrality, top_k=top_k)

        source_nodes = []
        for node, value in central_nodes:
            source_nodes.append(node)
        print(source_nodes)

        removed_edges = set()
        for source_node in source_nodes:
            for u, v in undirected_graph.edges(source_node):
                if u != source_node:
                    removed_edges.add((source_node, u))
                
                if v != source_node:
                    removed_edges.add((source_node, v))
        print('Number of removed links:', len(removed_edges))
        
        results = Parallel(n_jobs=10, backend='multiprocessing')(
            delayed(run_link_predictions)
            (undirected_graph, removed_edge) for removed_edge in removed_edges
        )

        dict_results = dict()
        for result in results:
            for edge, value in result.items():
                if edge not in dict_results.keys():
                    dict_results[edge] = value
                else:
                    print('Duplicated value:', dict_results, edge, value)
        print(dict_results)

        acc_top_1, acc_top_3, acc_top_5 = evaluate_results(dict_results)

        row = (top_k, len(removed_edges), acc_top_1, acc_top_3, acc_top_5)
        pd_data.append(row)

    df = pd.DataFrame(pd_data, columns=['#_central_nodes', '#_removed_edges',
                                        'acc_top_1(%)', 'acc_top_3(%)', 'acc_top_5(%)'])
    df_file_path = 'analysis_results/burglary_dateset_analysis/' + 'df_' + graph_file_path.split('.')[0].split('/')[2] + \
                    '_undirected_betweenness_centrality_scores' + '_v' + run_version + '.csv'
    df.to_csv(df_file_path)
    print('Dumped:', df_file_path)
'''
Conducts experiments to evaluate link prediction accuracy under different scenarios of removing edges connected to top-k central nodes in an undirected graph.
Uses multiprocessing for parallel execution of link prediction tasks.
Saves results in a CSV file for analysis.

Inputs:
- graph_file_path
- nx_undirected_graph
- scores_centrality

Steps:
- Iterate through different top-k values
- Identify central nodes and edge to remove
- Run link prediction in parallel
- Evalute and store results
- Create and save DataFrame

Employs multiprocessing for potentially faster execution.
Saves results in a structured format for analysis.
'''

def run_experiment_on_removing_random_edges(graph_file_path, nx_undirected_graph, percent_removed_edges=0.01):
    undirected_graph = nx_undirected_graph

    removed_edges = random.sample(undirected_graph.edges(), int(round(percent_removed_edges * len(undirected_graph.edges()), 0)))
    print('Number of removed links:', len(removed_edges))

    results = run_link_predictions_with_multi_edges(undirected_graph, removed_edges)
    print(results)


    acc_top_1, acc_top_3, acc_top_5 = evaluate_results(results)

    pd_data = []
    row = (len(removed_edges), acc_top_1, acc_top_3, acc_top_5)
    pd_data.append(row)

    df = pd.DataFrame(pd_data, columns=['#_removed_edges', 'acc_top_1(%)', 'acc_top_3(%)', 'acc_top_5(%)'])
    df_file_path = 'analysis_results/burglary_dateset_analysis/' + 'df_' + graph_file_path.split('.')[0].split('/')[2] + \
                    '_removed_edges_' + str(int(percent_removed_edges*100)) + '%_v' + run_version + '.csv'
    df.to_csv(df_file_path)
    print('Dumped:', df_file_path)
'''

This function analyzes link prediction accuracy under random edge removal in an undirected graph.

Analyzes how removing a random percentage of edges affects link prediction accuracy in a graph.
Compares with run_experiment_top_k_central_node which removes edges connected to central nodes.

Inputs:
- graph_file_path
- nx_undirected_graph
- percent_removed_edges

Steps:
- Select random edges to remove
- Run link prediction for removed edges
- Evalute and store results
- Create and save DataFrame

This function provides a complementary analysis to run_experiment_top_k_central_node by evaluating the impact of random edge removal on predictions.
The chosen percentage of edges to remove can be adjusted for different experiments.
Similar assumptions apply as in the previous breakdown regarding external functions and run_version.
'''

def run_experiment_on_ground_truth_graph(graph_file_path, nx_undirected_graph, nx_undirected_graph_ground_truth):
    undirected_graph = nx_undirected_graph
    undirected_graph_ground_truth = nx_undirected_graph_ground_truth

    new_nodes = set(undirected_graph_ground_truth.nodes()).difference(set(undirected_graph.nodes()))

    new_edges = set()
    for edge in undirected_graph_ground_truth.edges():
        source, target = edge

        if (source, target) not in undirected_graph.edges() and (target, source) not in undirected_graph.edges():
            new_edges.add((source, target))

    # new_edges = set(undirected_graph_ground_truth.edges()).difference(set(undirected_graph.edges()))

    print('new nodes:', len(new_nodes))
    print('====================================================')
    print('new edges:', len(new_edges))

    # new_edges_in_new_nodes = set()
    # for new_edge in new_edges:
    #     source, target = new_edge
    #     if source in new_nodes or target in new_nodes:
    #         new_edges_in_new_nodes.add(new_edge)
    # print('====================================================')
    # print('new_edges_in_new_nodes:', len(new_edges_in_new_nodes))

    new_edges_in_existing_nodes = set()
    for new_edge in new_edges:
        source, target = new_edge
        if source not in new_nodes and target not in new_nodes:
            new_edges_in_existing_nodes.add((source, target))

    print('====================================================')
    print('new_edges_in_existing_nodes:', len(new_edges_in_existing_nodes))

    set_no_neighbor_nodes = set()
    set_edges_having_two_hop_neighbors = set()
    for new_edge in new_edges_in_existing_nodes:
        source, target = new_edge

        if len([n for n in undirected_graph.neighbors(source)]) == 0:
            set_no_neighbor_nodes.add(source)
            print(source)

        if len([n for n in undirected_graph.neighbors(target)]) == 0:
            set_no_neighbor_nodes.add(target)
            print(target)
        
        if has_two_hop_neighbors(undirected_graph, source) and has_two_hop_neighbors(undirected_graph, target):
            set_edges_having_two_hop_neighbors.add(new_edge)
    
    print('set_no_neighbor_nodes:', set_no_neighbor_nodes, len(set_no_neighbor_nodes))
    print('set_edges_having_two_hop_neighbors:', set_edges_having_two_hop_neighbors, len(set_edges_having_two_hop_neighbors))

    removed_edges = set_edges_having_two_hop_neighbors
    print('Number of removed links:', len(removed_edges))

    results = run_link_predictions_with_multi_edges_ground_truth(undirected_graph, removed_edges)
    # print(results)


    acc_top_1, acc_top_3, acc_top_5 = evaluate_results(results)

    pd_data = []
    row = (len(removed_edges), acc_top_1, acc_top_3, acc_top_5)
    pd_data.append(row)

    df = pd.DataFrame(pd_data, columns=['#_removed_edges', 'acc_top_1(%)', 'acc_top_3(%)', 'acc_top_5(%)'])
    df_file_path = 'analysis_results/burglary_dateset_analysis/' + 'df_' + graph_file_path.split('.')[0].split('/')[2] + \
                    '_and_ground_truth_graph_' + 'v' + run_version + '.csv'
    df.to_csv(df_file_path)
    print('Dumped:', df_file_path)
'''
This function focuses on analyzing link prediction in a scenario where you have access to an additional "ground truth" graph with more edges than the original graph.

Analyzes how adding missing edges from a ground truth graph affects link prediction accuracy in the original graph.
Compares to previous experiments analyzing edge removal (random and based on centrality).

Inputs:
- graph_file_path
- nx_undirected_graph
- nx_undirected_graph_ground_truth

Steps:
- Identify new nodes and edges
- Analyze edges within existing nodes
    - Filters new_edges to keep only those connecting existing nodes in both graphs (new_edges_in_existing_nodes).
    - Identifies nodes with no neighbors in the original graph within new_edges_in_existing_nodes.
    - Identifies edges where both nodes have at least two-hop neighbors in the original graph (set_edges_having_two_hop_neighbors).
- Treat identified edges as missing information
    - Considers set_edges_having_two_hop_neighbors as the set of "missing edges" to analyze.
    - Uses run_link_predictions_with_multi_edges_ground_truth to analyze prediction accuracy for these missing edges, assuming no ground truth information about their existence.
- Evalute and store results

Utilizes the additional information from the ground truth graph to assess the potential impact of missing edges on prediction accuracy.
Considers edges where both nodes have two-hop neighbors as potentially predictable even without direct connections.
Assumes run_link_predictions_with_multi_edges_ground_truth is defined elsewhere and handles the lack of ground truth information for the analyzed edges.
'''

if __name__ == "__main__":
    start = time.time()
    run_version = get_run_version()
    if run_version is None:
        run_version = str(0)
    # Opening JSON file
    # graph_file_path = 'datasets/preprocessed/locard_dataset_viewers_broadcasters_network.json'
    graph_file_path = 'datasets/preprocessed/israel_lea_inp_burglary_offender_id_network.json'
    graph = load_graph_from_json_file(graph_file_path)
    undirected_graph = graph.to_undirected()
    print(nx.info(undirected_graph))

    # graph_by_date_file_path = 'datasets/preprocessed/israel_lea_inp_burglary_offender_id_network_from_2010-01-01_to_2019-12-31.json'
    graph_by_date_file_path = 'datasets/preprocessed/israel_lea_inp_burglary_offender_id_network_from_2010-01-01_to_2018-12-31.json'
    graph_by_date = load_graph_from_json_file(graph_by_date_file_path)
    undirected_graph_by_date = graph_by_date.to_undirected()
    print(nx.info(undirected_graph_by_date))


    # # nx.write_gpickle(G, 'datasets/nx_graphs/locard_dataset_viewers_broadcasters_network.gpickle')
    # G = nx.read_gpickle('datasets/nx_graphs/locard_dataset_viewers_broadcasters_network.gpickle')

    print(nx.info(graph))
    print(nx.info(undirected_graph))
    scores_centrality_file_path = 'analysis_results/burglary_dateset_analysis/' + graph_file_path.split('.')[0].split('/')[2] + \
                       '_undirected_betweenness_centrality_scores' + '.pickle'
    dump_centrality_scores(undirected_graph, scores_centrality_file_path)

    scores = nx.betweenness_centrality(G, weight='weight')
    with open('analysis_results/burglary_dateset_analysis/betweenness_centrality_scores_israel_lea_inp_burglary_offender_id_network.pickle', 'wb') as fp:
        pickle.dump(scores, fp)

    scores_centrality = pickle.load(open(scores_centrality_file_path, 'rb'))

    # run_experiment_top_k_central_node(graph_file_path, undirected_graph, scores_centrality)
    run_experiment_on_removing_random_edges(graph_file_path, undirected_graph, percent_removed_edges=0.01)
    # run_experiment_on_ground_truth_graph(graph_file_path=graph_by_date_file_path,
    #                                      nx_undirected_graph=undirected_graph_by_date,
    #                                      nx_undirected_graph_ground_truth=undirected_graph)

    end = time.time()
    print('{:.4f} s'.format(end-start))
'''

The provided code appears to be the main entry point for executing several link prediction experiments on a graph representing connections between burglary offenders.

Steps:
- Retrives run version
- Loads graphs
- Calculates and saves centrality scores
- Selects and runs expreiments
- Measures ecexution time

Overall flow:
- The script loads two graph representations of the offender network (full and date-limited).
- It calculates and saves betweenness centrality scores for the full network.
- It runs selected experiments:
    - Analyzing link prediction accuracy after removing top-k central nodes (commented out).
    - Analyzing link prediction accuracy after removing 1% of edges randomly.
    - Analyzing link prediction accuracy using a ground truth graph with more edges (commented out, requires more context).
- It measures and prints the total execution time.
'''