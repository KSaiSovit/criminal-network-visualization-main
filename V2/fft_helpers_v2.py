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
# helper functions for ROXANNE's first field test

import ast
import itertools
import networkx as nx
import numpy as np

import os
import sys

tokens = os.path.abspath(__file__).split('/')
path2root = '/'.join(tokens[:-2])
if path2root not in sys.path:
    sys.path.append(path2root)

print('fft_helpters: path2root = ', path2root)

if path2root not in sys.path:
    sys.path.append(path2root)
from storage.kit.VBx import diarization_lib
from storage.builtin_datasets import BuiltinDataset
'''
1. Setting up the path:
- It uses os.path.abspath(__file__) to get the absolute path of the current file.
- It splits the path into tokens using / as the delimiter.
- It constructs the path2root by joining all tokens except the last two with /.
- It checks if path2root is already in the sys.path system variable, which defines the search path for importing modules.
- If not, it adds path2root to sys.path.
- Finally, it prints the value of path2root for information.

2. Importing modules:
- It checks again if path2root is in sys.path, presumably for safety.
- It imports the diarization_lib module from the storage.kit.VBx package.
- It imports the BuiltinDataset class from the storage.builtin_datasets package.
'''

def _generate_channels_and_index(wp5_outputs):
    channels = {}
    for con in wp5_outputs['conversations']:
        for channel in con['channels']:
            channels[channel['id']] = channel

    # build channel-2-index map
    channel2index = {}
    for con in wp5_outputs['conversations']:
        for channel in con['channels']:
            channel2index[channel['id']] = len(channel2index)
    
    return channels, channel2index
'''
- Creates two dictionaries:
    - channels: Maps channel IDs to their corresponding channel information (extracted from wp5_outputs).
    - channel2index: Maps channel IDs to unique numerical indices, representing their order in the data.

Functionality:
- Iterate through conversations:
    - Loops through each conversation in the wp5_outputs['conversations'] list.
- Extract channels:
    - For each conversation, iterates through its channels list.
- Build channels dictionary:
    - For each channel, adds an entry to the channels dictionary with:
        - Key: The channel's ID.
        - Value: The channel's information dictionary (presumably from channel).
- Build channel to index map:
    - Creates an empty channel2index dictionary.
- Assign unique indices:
    - Loops through each conversation and its channels again.
    - For each channel, adds an entry to the channel2index dictionary with:
        - Key: The channel's ID.
        - Value: The current length of the channel2index dictionary (acting as a unique index).
- Return results:
    -Returns a tuple containing both the channels and channel2index dictionaries.
'''

def _cluster_from_voice_prints_matrix(channel2index, wp5_outputs, threhold, calibration):
    # cluster
    voiceprintsMatrix = np.zeros((len(channel2index), len(channel2index)))
    for u, row in wp5_outputs['voiceprintsMatrix'].items():
        u_index = channel2index[u]
        for v, s in row.items():
            v_index = channel2index[v]
            voiceprintsMatrix[u_index, v_index] = s

    for con in wp5_outputs['conversations']:
        channel_ids = [channel['id'] for channel in con['channels']]
        for s in channel_ids:
            for l in channel_ids:
                if s != l:
                    s_index = channel2index[s]
                    l_index = channel2index[l]
                    voiceprintsMatrix[s_index, l_index] = -np.inf

    if calibration:
        thr, scr_cal = diarization_lib.twoGMMcalib_lin(voiceprintsMatrix[np.where(np.isfinite(voiceprintsMatrix))])
    else:
        thr = 0
    labels = diarization_lib.AHC(voiceprintsMatrix, thr + threhold)

    return labels 
'''
Takes a voice print matrix representing pairwise similarities between channels and conversation information as input.
Applies a clustering algorithm (AHC) to group channels (speakers) based on their voice prints.
Employs a thresholding strategy to improve clustering accuracy.

Steps:
- Initialize voice print matrix:
    - Creates a square matrix (voiceprintsMatrix) of zeros with dimensions equal to the number of channels.
- Populate voice print matrix:
    - Iterates through each entry in the voiceprintsMatrix provided in wp5_outputs.
    - Looks up the indices of the corresponding channels using channel2index.
    - Sets the value at the corresponding matrix indices to the similarity score.
- Set self-similarity and inter-conversation similarity to negative infinity:
    - Iterates through each conversation in wp5_outputs.
    - Extracts channel IDs from the conversation.
    - Iterates through all pairs of channel IDs within the conversation and sets their similarity in the matrix to negative infinity.
- Threshold calibration (optional):
    - If calibration is True, uses a specific function (diarization_lib.twoGMMcalib_lin) to calculate a calibrated threshold based on the non-infinite values in the matrix.
    - Otherwise, sets the threshold to 0.
- Apply clustering:
    - Uses the diarization_lib.AHC function to perform Agglomerative Hierarchical Clustering (AHC) on the voice print matrix with the chosen threshold.
- Return cluster labels:
    - Returns the cluster labels assigned to each channel by the clustering algorithm.

This function relies on the channel2index dictionary created in another function for efficient indexing.
It uses a specific heuristic to handle self-similarity and inter-conversation similarity.
The calibration step (if enabled) aims to adjust the threshold based on data characteristics.
'''

def _generate_nodes(channels, channel2index, labels):
    nodes = {}
    for channel in channels:
        index = channel2index[channel]
        channel_info = channels[channel]
        if 'transcription' in channel_info:
            del channel_info['transcription']  # ignore the transcription in first field test

        c = labels[index]

        if c in nodes:
            nodes[c].append(channel_info)
        else:
            nodes[c] = [channel_info]
    return nodes
'''
Takes information about channels (speakers), their indices, and clustering labels as input.
Generates a dictionary where each key represents a cluster and the value is a list of channel information dictionaries belonging to that cluster.

Steps:
- Initialize empty nodes dictionary:
    - Creates an empty dictionary called nodes to store the generated clusters.
- Iterate through channels:
    - Loops through each channel (speaker) information dictionary in the channels input.
- Extract index and channel info:
    - Looks up the corresponding index of the channel using channel2index.
    - Extracts the actual channel information dictionary from the channels dictionary.
- Process transcription (optional):
    - Checks if the channel information contains a key named "transcription".
    - If present, it removes the "transcription" key-value pair (presumably for this specific test scenario).
- Get cluster label:
    - Retrieves the cluster label for the current channel from the labels list.
- Add channel info to cluster:
    - Checks if the current cluster label already exists as a key in the nodes dictionary.
        - If yes, appends the current channel information to the existing list of channels within that cluster.
        - If no, creates a new list with the current channel information and adds it to nodes with the cluster label as the key.
- Return nodes dictionary:
    -Returns the generated nodes dictionary containing the clustered speaker information.

This function assumes the presence of pre-processed channel information and clustering results.
It filters out "transcription" information for the current test scenario but this might be relevant in other contexts.
It generates a simple cluster representation using a dictionary structure.
'''

def _generate_nodes_aegis(channels, channel2index, labels):
    nodes = {}
    for channel in channels:
        index = channel2index[channel]
        channel_info = channels[channel]
        if 'transcription' in channel_info:
            del channel_info['transcription']  # ignore the transcription in first field test

        c = labels[index]

        if c in nodes:
            nodes[c].append(channel_info)
        else:
            nodes[c] = [channel_info]
    return nodes
'''
Creates a network representation by organizing channels (speakers) into nodes based on clustering results.
Specifically designed for the Aegis system or a similar context where transcriptions are temporarily excluded.

Steps:
- Initializes empty nodes dictionary:
    - Creates a dictionary named nodes to store the generated nodes.
- Iterates through channels:
    - Loops through each channel (speaker) information dictionary in the channels input.
- Extracts index and channel info:
    - Retrieves the channel's index from channel2index.
    - Obtains the channel's information from the channels dictionary.
- Removes transcription (specific to Aegis):
    - Deletes the "transcription" key-value pair from the channel information, likely due to a temporary constraint in the Aegis system or test setup.
- Gets cluster label:
    - Retrieves the cluster label assigned to the current channel from the labels list.
- Groups channels into nodes:
    - Checks if the cluster label already exists as a key in the nodes dictionary.
        - If yes, appends the channel information to the existing list of channels within that node.
        - If no, creates a new list with the channel information and adds it to nodes with the cluster label as the key.
- Returns nodes dictionary:
    - Returns the generated nodes dictionary, where each key represents a node (cluster) and the value is a list of channel information dictionaries belonging to that node.

Relies on pre-processed channel information and clustering results.
Excludes transcriptions for Aegis-specific reasons.
Creates a network representation with nodes as clusters of channels.
'''

# def _generate_nodes_aegis(channels):
#     nodes = {}
#     for channel in channels:
#         channel_info = channels[channel]
#         if 'transcription' in channel_info:
#             del channel_info['transcription']  # ignore the transcription in first field test

#         node_id = channel_info['number']

#         nodes[node_id] = channel_info
    
#     return nodes

def _generate_edges(channel2index, labels, wp5_outputs, directed):
    edges = {}
    for con in wp5_outputs['conversations']:
        channel_ids = [channel['id'] for channel in con['channels']]
        if 'date' in con:
            con_date = con['date']
        else:
            con_date = None
        # print(con_date)
        # print(channel_ids)
        for i in range(len(channel_ids)):
            s = channel_ids[i]
            for j in range(len(channel_ids)):
                if j == i:
                    continue
                l = channel_ids[j]
                if i < j or not directed:
                    s_cid = labels[channel2index[s]]
                    l_cid = labels[channel2index[l]]
                    if s_cid in edges:
                        if l_cid in edges[s_cid]:
                            edges[s_cid][l_cid]['weight'] += 1
                            if 'timestamps' in edges[s_cid][l_cid]:
                                temp_timestamps = edges[s_cid][l_cid]['timestamps']
                                temp_timestamps.append(con_date)
                                edges[s_cid][l_cid]['timestamps'] = temp_timestamps
                        else:
                            if con_date is not None:
                                edges[s_cid][l_cid] = {'weight' : 1, 'timestamps': [con_date]}
                            else:
                                edges[s_cid][l_cid] = {'weight' : 1}
                    else:
                        if con_date is not None:
                            edges[s_cid] = {l_cid: {'weight' : 1, 'timestamps': [con_date]}}
                        else:
                            edges[s_cid] = {l_cid: {'weight' : 1}}
    return edges
'''
Creates a network representation by defining edges between nodes (clusters of channels) based on their co-occurrence in conversations.
Allows for both directed and undirected edge creation.
Optionally includes timestamps for edges based on conversation dates.

Steps:
- Initializes empty edges dictionary:
    - Creates a dictionary named edges to store the generated edges.
- Iterates through conversations:
    - Loops through each conversation in the wp5_outputs['conversations'] list.
- Extracts channel IDs and date:
    - Retrieves the IDs of channels involved in the current conversation.
    - Extracts the conversation date if available, otherwise sets it to None.
- Iterates through channel pairs:
    - Loops through all possible pairs of channels within the conversation.
- Creates edges based on conditions:
    - If the network is directed, only creates edges from the first channel to the second (i < j).
    - If the network is undirected, creates edges in both directions (i < j or not directed).
    - Retrieves the cluster labels for the current channel pair using labels.
    - Checks if an edge already exists between those cluster labels:
        - If yes, increments the edge weight and appends the conversation date to the timestamps list (if applicable).
        - If no, creates a new edge with weight 1 and optionally includes the conversation date.
- Returns edges dictionary:
    - Returns the generated edges dictionary, where keys represent source nodes (cluster labels), values are dictionaries with keys as target nodes, and each inner dictionary contains edge weight and optional timestamps.

Relies on pre-processed channel information, clustering results, and conversation data.
Captures co-occurrence relationships between clusters as edges.
Supports both directed and undirected networks.
Allows for inclusion of temporal information (timestamps) for edges.
'''

def _generate_edges_aegis(channel2index, labels, wp5_outputs, directed):
    edges = {}
    for con in wp5_outputs['conversations']:
        channel_ids = [channel['id'] for channel in con['channels']]
        if 'date' in con:
            con_date = con['date']
        else:
            con_date = None
        print(con_date)
        print(channel_ids)
        for i in range(len(channel_ids)):
            s = channel_ids[i]
            for j in range(len(channel_ids)):
                if j == i:
                    continue
                l = channel_ids[j]
                if i < j or not directed:
                    s_cid = labels[channel2index[s]]
                    l_cid = labels[channel2index[l]]
                    # timestamp_val = (con_date, channel_ids)
                    timestamp_val = con_date
                    if s_cid in edges:
                        if l_cid in edges[s_cid]:
                            edges[s_cid][l_cid]['weight'] += 1
                            if 'timestamps' in edges[s_cid][l_cid]:
                                temp_timestamps = edges[s_cid][l_cid]['timestamps']
                                temp_timestamps = temp_timestamps.append(timestamp_val)
                                edges[s_cid][l_cid]['timestamps'] = temp_timestamps
                        else:
                            if con_date is not None:
                                edges[s_cid][l_cid] = {'weight' : 1, 'timestamps': [timestamp_val]}
                            else:
                                edges[s_cid][l_cid] = {'weight' : 1}
                    else:
                        if con_date is not None:
                            edges[s_cid] = {l_cid: {'weight' : 1, 'timestamps': [timestamp_val]}}
                        else:
                            edges[s_cid] = {l_cid: {'weight' : 1}}
    return edges
'''
- Builds a network representation for the Aegis system or a similar context.
- Creates edges between nodes (clusters of channels) based on co-occurrence in conversations.
- Allows for directed or undirected edges.
- Includes timestamps for edges based on conversation dates.
- Potentially prints debugging information.

Steps:
- Initializes edges dictionary:
    - Creates an empty dictionary edges to store the edges.
- Iterates through conversations:
    - Loops through each conversation in wp5_outputs['conversations'].
- Extracts channel IDs and date:
    - Retrieves channel IDs from the current conversation.
    - Extracts the conversation date if available, otherwise sets it to None.
    - Prints the date and channel IDs (likely for debugging).
- Iterates through channel pairs:
    - Loops through all possible pairs of channels within the conversation.
- Creates edges based on conditions:
    - If directed, creates edges only from the first channel to the second (i < j).
    - If undirected, creates edges in both directions (i < j or not directed).
    - Retrieves cluster labels for the channel pair using labels.
    - Checks if an edge already exists between those labels:
        - If yes, increments weight and appends the date to timestamps.
        - If no, creates a new edge with weight 1 and includes the date (if available).
- Returns edges dictionary:
    - Returns the generated edges dictionary representing the network.

- Similar to _generate_edges but potentially for Aegis-specific use.
- Prints debugging information (date and channel IDs).
'''


def _generate_phone_number_edges_aegis(wp5_outputs, directed):
    edges = {}

    for con in wp5_outputs['conversations']:
        channel_ids = [channel['id'] for channel in con['channels']]
        channel_numbers = [channel['number'] for channel in con['channels']]

        if 'date' in con:
            con_date = con['date']
        else:
            con_date = None

        for i in range(len(channel_numbers)):
            s = channel_numbers[i]
            for j in range(len(channel_numbers)):
                if j == i:
                    continue
                l = channel_numbers[j]
                if i < j or not directed:
                    s_cid = s
                    l_cid = l
                    # timestamp_val = (con_date, channel_ids)
                    timestamp_val = con_date
                    if s_cid in edges:
                        if l_cid in edges[s_cid]:
                            edges[s_cid][l_cid]['weight'] += 1
                            if 'timestamps' in edges[s_cid][l_cid]:
                                temp_timestamps = edges[s_cid][l_cid]['timestamps']
                                temp_timestamps.append(timestamp_val)
                                edges[s_cid][l_cid]['timestamps'] = temp_timestamps
                        else:
                            if con_date is not None:
                                edges[s_cid][l_cid] = {'weight' : 1, 'timestamps': [timestamp_val]}
                            else:
                                edges[s_cid][l_cid] = {'weight' : 1}
                    else:
                        if con_date is not None:
                            edges[s_cid] = {l_cid: {'weight' : 1, 'timestamps': [timestamp_val]}}
                        else:
                            edges[s_cid] = {l_cid: {'weight' : 1}}
    return edges
'''
- Builds a network representation (similar to previous functions) but connects nodes based on phone number co-occurrence in conversations.
- Designed for the Aegis system or a similar context.
- Allows for directed or undirected edges.
- Includes timestamps based on conversation dates (if available).

Steps:
- Initializes empty edges dictionary:
    - Creates an empty dictionary edges to store the edges.
- Iterates through conversations:
    - Loops through each conversation in wp5_outputs['conversations'].
- Extracts phone numbers and date:
    - Retrieves phone numbers and conversation date (if available) for each channel in the conversation.
- Iterates through phone number pairs:
    - Loops through all possible pairs of phone numbers within the conversation.
- Creates edges based on conditions:
    - Similar to previous functions, considers directed/undirected edges and checks for existing edges.
    - Uses phone numbers directly as node identifiers (s_cid and l_cid).
    - Includes conversation date (if available) in timestamps.
- Returns edges dictionary:
    - Returns the generated edges dictionary representing the network based on phone number co-occurrence.

Differs from previous functions by using phone numbers for node identification and edge creation.
Maintains similar structure for edge construction and timestamp handling.
Likely for specific use cases like analyzing phone call networks.
'''

def _construct_network(nodes, edges):
    network = []
    for node in nodes:
        network.append({'type': 'node',
                        'id': 'speaker_{}'.format(node),
                        'properties': {'type': 'cluster',
                                       'channels': nodes[node]}
                       })
                       
    for u in edges:
        for v in edges[u]:
            edge_properties = dict()
            edge_properties['type'] = 'conversations'
            edge_properties['weight'] = edges[u][v]['weight']
            if 'timestamps' in edges[u][v]:
                edge_properties['timestamps'] = edges[u][v]['timestamps']
            network.append({'type': 'edge',
                            'source': 'speaker_{}'.format(u),
                            'target': 'speaker_{}'.format(v),
                            'properties': edge_properties
                           })
    return network
'''
Takes nodes (speaker clusters) and edges (connections between them) as input.
Creates a network representation in a specific format likely suitable for visualization or network analysis tools.

Steps:
- Initializes empty network list:
    - Creates an empty list network to store the network elements.
- Processes nodes:
    - Iterates through each node (speaker cluster) in the nodes dictionary.
    - Adds a node element to the network list with the following properties:
        - type: Set to "node" indicating the element represents a node in the network.
        - id: Formatted as "speaker_{node_id}" where node_id is the original cluster identifier.
        - properties: A dictionary with information about the node:
            - type: Set to "cluster" indicating the node represents a cluster of speakers.
            - channels: A list containing the channel information associated with the cluster (extracted from nodes[node]).
- Processes edges:
    - Iterates through each source node (u) in the edges dictionary.
    - For each source node, iterates through its target nodes (v) in the corresponding inner dictionary.
    - Creates an edge element for each source-target pair and adds it to the network list with the following properties:
        - type: Set to "edge" indicating the element represents a connection between nodes.
        - source: Set to "speaker_{source_id}" where source_id is the original cluster identifier of the source node.
        - target: Set to "speaker_{target_id}" where target_id is the original cluster identifier of the target node.
        - properties: A dictionary with information about the edge:
            - type: Set to "conversations" indicating the edge represents co-occurrence in conversations.
            - weight: Set to the weight of the edge retrieved from edges[u][v]['weight'].
            - timestamps (optional): If present in edges[u][v], includes a list of timestamps associated with the edge.
- Returns network:
    - Returns the constructed network representation stored in the network list.

Converts speaker clusters and their connections into a network format with nodes and edges.
Uses specific naming conventions for node and edge identifiers.
Includes edge weight and optional timestamps for detailed analysis.
'''

def _construct_network_aegis(nodes, speaker_edges, phone_number_edges, directed):
    if directed == True:
        nx_graph = nx.DiGraph()
    else:
        nx_graph = nx.Graph()

    dict_node_phone_number = dict()
    for node in nodes:
        channels = nodes[node]

        phone_numbers = []
        for idx, channel in enumerate(channels):
            channel_info = channel
            # number = channel_info.pop('number', 'phone_number_{}'.format(node))
            number = channel_info['number']
            channels[idx] = channel_info
            phone_numbers.append(number)

        # print('phone_numbers:', phone_numbers)
        # print('channels:', channels)
        dict_node_phone_number[node] = phone_numbers
        # dict_node_phone_number[node] = list(set(phone_numbers))

        node_properties = {'type': 'cluster',
                           'channels': channels}

        nx_graph.add_node('speaker_{}'.format(node), type='node', properties=node_properties)
        
        for phone_number in phone_numbers:
            phone_node_properties = {'type': 'phone_number',
                                     'channels': channels}

            nx_graph.add_node(phone_number, type='node', properties=phone_node_properties)
            
    print(dict_node_phone_number)

    # for node in nx_graph.nodes(data=True):
    #     print(node)
        
    for u in speaker_edges:
        for v in speaker_edges[u]:
            timestamps = speaker_edges[u][v]['timestamps']
            # timestamps_no_channel_id = []
            # for timestamp in timestamps:
            #     date = timestamp[0]
            #     channel_id_1 = timestamp[1][0]
            #     channel_id_2 = timestamp[1][1]

            #     print(timestamp[0], timestamp[1][0], timestamp[1][1])

            u_phone_numbers = dict_node_phone_number[u]
            for u_phone_number in u_phone_numbers:
                temp_edge = ('speaker_{}'.format(u), u_phone_number)
                temp_edge_properties = {
                    'type': 'calling'
                }
                if temp_edge not in nx_graph.edges():
                    temp_edge_properties['weight'] = 1
                    temp_edge_properties['timestamps'] = timestamps
                    nx_graph.add_edge(temp_edge[0], temp_edge[1], type='edge', properties=temp_edge_properties)
                else:
                    temp_weight = nx_graph[temp_edge[0]][temp_edge[1]]['properties']['weight']
                    temp_weight = temp_weight + 1
                    nx_graph[temp_edge[0]][temp_edge[1]]['properties']['weight'] = temp_weight
                    temp_timestamps = [ts for ts in nx_graph[temp_edge[0]][temp_edge[1]]['properties']['timestamps']]
                    temp_timestamps = temp_timestamps + timestamps
                    nx_graph[temp_edge[0]][temp_edge[1]]['properties']['timestamps'] = temp_timestamps
            
            v_phone_numbers = dict_node_phone_number[v]
            for v_phone_number in v_phone_numbers:
                temp_edge = (v_phone_number, 'speaker_{}'.format(v))
                temp_edge_properties = {
                    'type': 'receiving'
                }
                if temp_edge not in nx_graph.edges():
                    temp_edge_properties['weight'] = 1
                    temp_edge_properties['timestamps'] = timestamps
                    nx_graph.add_edge(temp_edge[0], temp_edge[1], type='edge', properties=temp_edge_properties)
                else:
                    temp_weight = nx_graph[temp_edge[0]][temp_edge[1]]['properties']['weight']
                    temp_weight = temp_weight + 1
                    nx_graph[temp_edge[0]][temp_edge[1]]['properties']['weight'] = temp_weight
                    temp_timestamps = nx_graph[temp_edge[0]][temp_edge[1]]['properties']['timestamps']
                    temp_timestamps = temp_timestamps + timestamps
                    nx_graph[temp_edge[0]][temp_edge[1]]['properties']['timestamps'] = temp_timestamps


    for u in phone_number_edges:
        for v in phone_number_edges[u]:
            temp_edge = (u, v)
            timestamps = phone_number_edges[u][v]['timestamps']
            temp_edge_properties = {
                    'type': 'conversations'
                }
            if temp_edge not in nx_graph.edges():
                temp_edge_properties['weight'] = phone_number_edges[u][v]['weight']
                temp_edge_properties['timestamps'] = phone_number_edges[u][v]['timestamps']
                nx_graph.add_edge(temp_edge[0], temp_edge[1], type='edge', properties=temp_edge_properties)
            else:
                temp_weight = nx_graph[temp_edge[0]][temp_edge[1]]['properties']['weight']
                temp_weight = temp_weight + phone_number_edges[u][v]['weight']
                nx_graph[temp_edge[0]][temp_edge[1]]['properties']['weight'] = temp_weight
                temp_timestamps = nx_graph[temp_edge[0]][temp_edge[1]]['properties']['timestamps']
                temp_timestamps.append(timestamps)
                nx_graph[temp_edge[0]][temp_edge[1]]['properties']['timestamps'] = temp_timestamps

    network = []
    for node_id, node_data in nx_graph.nodes(data=True):
        node = {
            'type': node_data['type'],
            'id': node_id,
            'properties': node_data['properties']
        }
        network.append(node)
    
    for source_id, target_id, edge_data in nx_graph.edges(data=True):
        edge = {
            'type': edge_data['type'],
            'source': source_id,
            'target': target_id,
            'properties': edge_data['properties']
        }
        network.append(edge)
        weight = edge_data['properties']['weight']
        if weight > 1:
            print(edge)


    # for edge in nx_graph.edges(data=True):
    #     u = edge[0]
    #     v = edge[1]
    #     # print(edge, nx_graph[u]['properties']['channels']['id'], nx_graph[v]['properties']['channels']['id'])
    #     print(edge)
    #     # print(nx_graph.nodes(data=True)[u]['properties']['channels'], nx_graph.nodes(data=True)[v]['properties']['channels'])


    # for u in edges:
    #     for v in edges[u]:
    #         print('nodes[v]', nodes[v])
    #         edge_properties = dict()
    #         edge_properties['type'] = 'conversations'
    #         u_v_weight = edges[u][v]['weight']
    #         edge_properties['weight'] = edges[u][v]['weight']

    #         timestamps = edges[u][v]['timestamps']
    #         print('timestamps', timestamps)
    #         for timestamp in timestamps:
    #             print(timestamp[0], timestamp[1][0], timestamp[1][1])


    #         if 'timestamps' in edges[u][v]:
    #             edge_properties['timestamps'] = edges[u][v]['timestamps']

    #         u_phone_numbers = dict_node_phone_number[u]
    #         # print(u, u_phone_numbers)
    #         for u_phone_number in u_phone_numbers:
    #             network.append({'type': 'edge',
    #                             'source': 'speaker_{}'.format(u),
    #                             'target': u_phone_number,
    #                             'properties': edge_properties
    #                         })         

    #         v_phone_numbers = dict_node_phone_number[v]
    #         # print(v, v_phone_numbers)
    #         for v_phone_number in v_phone_numbers:
    #             network.append({'type': 'edge',
    #                             'source': v_phone_number,
    #                             'target': 'speaker_{}'.format(v),
    #                             'properties': edge_properties
    #                         })
            
    #         for i, j in itertools.product(u_phone_numbers, v_phone_numbers):
    #             network.append({'type': 'edge',
    #                             'source': i,
    #                             'target': j,
    #                             'properties': edge_properties
    #                         })
            
    return network
'''
Takes nodes (speaker clusters), speaker-to-speaker edges, phone number-to-phone number edges, and a directed/undirected flag as input.
Creates a network representation in a specific format likely suitable for visualization or network analysis tools, incorporating both speaker and phone number nodes and edges.
Includes edge weights and timestamps based on conversation data.

Steps:
- Initializes network based on directed/undirected flag:
    - Creates a nx_graph object as either a directed or undirected graph based on the directed parameter.
- Creates a dictionary mapping nodes to phone numbers:
    - Iterates through each node and extracts its associated channels.
    - For each channel, extracts the phone number and adds it to a list for that node.
    - Stores the mapping between nodes and their phone numbers in a dictionary dict_node_phone_number.
- Adds speaker nodes and their properties:
    - Iterates through each node:
        - Creates a node element with properties:
            - type: Set to "node" indicating a network node.
            - id: Formatted as "speaker_{node_id}" where node_id is the original cluster identifier.
            - properties: A dictionary containing information about the node:
                - type: Set to "cluster" indicating the node represents a cluster of speakers.
                - channels: The list of channels associated with the speaker cluster.
        - Adds the node element to the nx_graph.
- Adds phone number nodes and their properties:
    - Iterates through each node and its associated phone numbers:
        - Creates a node element for each phone number with properties:
            - type: Set to "phone_number" indicating the node represents a phone number.
            - channels: The list of channels associated with the speaker cluster (inherited from the corresponding speaker node).
        - Adds the phone number node element to the nx_graph.
- Adds speaker-to-speaker edges with calling/receiving directions:
    - Iterates through each speaker-to-speaker edge (speaker_edges):
        - For each source and target speaker:
            - Retrieves the associated phone numbers for both speakers.
            - For each source phone number:
                - Creates an edge between the source phone number and the target speaker:
                    - type: Set to "calling" indicating the source initiated the call.
                    - properties: Dictionary containing:
                        - weight: Initial weight of 1.
                        - timestamps: List of timestamps associated with the conversations.
                    - Adds the edge element to the nx_graph if it doesn't exist, otherwise updates its weight and timestamps.
                - Similarly, creates and adds edges in the opposite direction (target speaker to source phone number) with "receiving" type.
- Adds phone number-to-phone number edges:
    - Iterates through each phone number-to-phone number edge (phone_number_edges):
        - For each source and target phone number:
            - Creates an edge between the source and target phone numbers:
                - type: Set to "conversations" indicating co-occurrence in conversations.
                - properties: Dictionary containing:
                    - weight: Edge weight from the input dictionary.
                    - timestamps: List of timestamps associated with the conversations.
                - Adds the edge element to the nx_graph if it doesn't exist, otherwise updates its weight and timestamps.
- Converts networkx graph to desired format:
    - Iterates through nodes and edges in the nx_graph:
        - Creates node and edge dictionaries with relevant information extracted from the networkx elements.
        - Appends these dictionaries to a network list.
- Prints edges with weight greater than 1 (potentially for debugging):
    - Iterates through edges and prints those with weight greater than 1.
- Returns the constructed network representation:
    - Returns the network list containing node and edge dictionaries.

Combines speaker-based and phone number-based network representations.
Captures calling/receiving relationships for speaker-to-speaker edges.
Includes edge weights and timestamps for detailed analysis.
Uses specific naming conventions for nodes and edges.
'''

# def _construct_network_aegis(nodes, edges):
#     network = []
#     for node in nodes:
#         network.append({'type': 'node',
#                         'id': nodes[node]['number'],
#                         'properties': {'type': 'phone_number',
#                                        'channels': nodes[node]}
#                        })
#     for u in edges:
#         for v in edges[u]:
#             edge_properties = dict()
#             edge_properties['type'] = 'conversations'
#             edge_properties['weight'] = edges[u][v]['weight']
#             if 'timestamps' in edges[u][v]:
#                 edge_properties['timestamps'] = edges[u][v]['timestamps']
#             network.append({'type': 'edge',
#                             'source': u,
#                             'target': v,
#                             'properties': edge_properties
#                            })
#     return network

def parse_wp5_output(wp5_outputs, threhold=50, calibration=False, directed=False):
    """
    build network from output of wp5
    :param wp5_outputs: dictionary converted from WP5's JSON object
    :param threhold:
    :param calibration:
    :param directed:
    :return:
    """

    # build channel-2-index map
    channels, channel2index = _generate_channels_and_index(wp5_outputs)
    # print(channels)

    # cluster
    labels = _cluster_from_voice_prints_matrix(channel2index, wp5_outputs, threhold, calibration)
    # print(labels)

    # generate nodes
    nodes = _generate_nodes(channels, channel2index, labels)
    # print("=================nodes==================")
    # print(nodes)

    # generate edges:
    edges = _generate_edges(channel2index, labels, wp5_outputs, directed)
    # print("=================edges==================")
    # print(edges)

    # construct network
    network = _construct_network(nodes, edges)
    # print("=================network==================")
    # print(network)

    return network
'''
Takes the output of WP5 (likely a system for voice analysis and speaker identification) as input.
Constructs a network representation based on identified speaker clusters and their relationships.

Parameters:
    - wp5_outputs: A dictionary containing WP5's output data.
    - threshold: A threshold value used for clustering (likely based on voice similarity).
    - calibration: A boolean flag indicating whether to apply calibration to the data.
    - directed: A boolean flag specifying whether to create a directed or undirected network.

Steps:
- Creates a channel-to-index mapping:
    - Processes wp5_outputs to generate a list of channels (channels) and a dictionary mapping channels to indices (channel2index).
- Performs clustering:
    - Calls _cluster_from_voice_prints_matrix to create speaker clusters based on voice similarity using the threshold and calibration settings.
    - Stores the cluster labels for each channel in the labels list.
- Generates nodes:
    - Calls _generate_nodes to create a list of nodes (nodes) representing speaker clusters, likely using information from channels, channel2index, and labels.
- Generates edges:
    - Calls _generate_edges to create a list of edges (edges) representing relationships between speakers, likely based on co-occurrence in conversations or calls.
    - The directed flag determines whether to create directed edges (indicating caller-callee relationships) or undirected edges (representing general connections).
- Constructs the network:
    - Calls _construct_network (presumably a separate function) to build the final network structure using the generated nodes and edges.
    - The specific implementation of _construct_network would determine the format and properties of the network (e.g., graph data structure, edge weights, etc.).
- Returns the network:
    - Returns the constructed network representation for further analysis or visualization.

Relies on other functions for clustering, node/edge generation, and network construction.
Creates a network based on speaker clusters and their relationships.
Allows for directed or undirected network representation.
Can be customized through parameters for clustering and edge creation.
'''


def parse_wp5_output_for_aegis(wp5_outputs, threhold=50, calibration=False, directed=False):
    """
    build network from output of wp5
    :param wp5_outputs: dictionary converted from WP5's JSON object
    :param directed:
    :return:
    """

    # build channel-2-index map
    channels, channel2index = _generate_channels_and_index(wp5_outputs)
    # print(channels)

    # cluster
    labels = _cluster_from_voice_prints_matrix(channel2index, wp5_outputs, threhold, calibration)
    print('labels:', labels)

    # generate nodes
    nodes = _generate_nodes_aegis(channels, channel2index, labels)
    print("=================nodes==================")
    print(nodes)

    # generate edges:
    # edges = _generate_edges(channel2index, labels, wp5_outputs, directed)
    edges = _generate_edges_aegis(channel2index, labels, wp5_outputs, directed)
    print("=================edges==================")
    print(edges)

    phone_number_edges = _generate_phone_number_edges_aegis(wp5_outputs, directed)
    print("=================phone_number_edges==================")
    print(phone_number_edges)

    # construct network
    network = _construct_network_aegis(nodes, edges, phone_number_edges, directed)
    # print("=================network==================")
    # print(network)

    return network
'''
Processes the output of WP5 (voice analysis and identification system) to build a network representation suitable for Aegis.
This network incorporates both speaker clusters and phone numbers as nodes, along with different types of edges based on speaker co-occurrence and phone number co-occurrence in conversations.

Parameters:
- wp5_outputs: A dictionary containing WP5's output data.
- threshold: Threshold value for speaker clustering (likely based on voice similarity).
- calibration: Boolean flag for applying calibration to data.
- directed: Boolean flag for creating directed or undirected network.

Steps:
- Channel-to-index mapping:
    - Similar to parse_wp5_output, generates a list of channels (channels) and a dictionary mapping channels to indices (channel2index).
- Speaker clustering:
    - Calls _cluster_from_voice_prints_matrix to create speaker clusters using the threshold and calibration settings.
    - Stores cluster labels for each channel in labels.
- Generating speaker nodes:
    - Calls _generate_nodes_aegis to create a list of nodes (nodes) representing speaker clusters, potentially considering additional information like channels.
- Generating speaker-to-speaker edges:
    - Calls _generate_edges_aegis (different from _generate_edges) to create speaker-to-speaker edges (edges) based on co-occurrence in conversations.
    - Considers directed/undirected based on the directed flag.
    - This function likely focuses on speaker relationships and might consider factors like call direction.
- Generating phone number edges:
    - Calls _generate_phone_number_edges_aegis to create edges (phone_number_edges) based on phone number co-occurrence in conversations.
    - Considers directed/undirected based on the directed flag.
    - This function likely builds connections between phone numbers themselves.
- Constructing Aegis network:
    - Calls _construct_network_aegis (different from _construct_network) to build the final network incorporating:
    - Speaker nodes from nodes.
    - Speaker-to-speaker edges from edges.
    - Phone number edges from phone_number_edges.
    - The specific network format and properties depend on the implementation of _construct_network_aegis.
- Returning the network:
    - Returns the constructed network representation for further analysis or visualization within Aegis.

Builds a network with speaker clusters, phone numbers, and different edge types for Aegis analysis.
Leverages separate functions for speaker clustering, node/edge generation, and network construction.
Allows for directed/undirected networks based on the directed flag.
Likely uses speaker co-occurrence, phone number co-occurrence, and potentially call direction information.
'''


def dataset_from_wp5_output(network):
    """

    :param network: list of dictionary, each is a node or an edge
    :return:
    """
    dataset = BuiltinDataset(path_2_data=None, uploaded=False, from_file=False)
    dataset.nodes = {}
    dataset.edges = []
    dataset.adj_list = {}
    dataset.in_adj_list = {}
    dataset.node_types = {}
    dataset.edge_types = {}
    dataset.recent_changes = []
    for element in network:
        if element['type'] == 'node':
            node = element['properties']
            if 'community' in element:
                node['community'] = element['community']
                node['community_confidence'] = element['community_confidence']
            if 'social_influence_score' in element:
                node['social_influence_score'] = element['social_influence_score']
                node['normalized_social_influence'] = element['normalized_social_influence']
            dataset.nodes[element['id']] = node
            if 'type' in node:
                node_type = node['type']
                if node_type in dataset.node_types:
                    dataset.node_types[node_type] += 1
                else:
                    dataset.node_types[node_type] = 1

        elif element['type'] == 'edge':
            edge = {'source': element['source'], 'target': element['target'],
                    'observed': True, 'properties': element['properties']}
            if 'observed' in element:
                if element['observed'] == 'false':
                    edge['observed'] = 'false'
            dataset.edges.append(edge)
            e_index = len(dataset.edges) - 1
            source = edge['source']
            if source in dataset.adj_list:
                dataset.adj_list[source].append(e_index)
            else:
                dataset.adj_list[source] = [e_index]
            target = edge['target']
            if target in dataset.in_adj_list:
                dataset.in_adj_list[target].append(e_index)
            else:
                dataset.in_adj_list[target] = [e_index]

            if 'type' in element['properties']:
                edge_type = element['properties']['type']
                if edge_type in dataset.edge_types:
                    dataset.edge_types[edge_type] += 1
                else:
                    dataset.edge_types[edge_type] = 1
        else:
            continue
    return dataset
'''
Takes a network representation generated from WP5 output (speaker clusters and relationships) as input.
Constructs a BuiltinDataset object, likely for use within a specific analysis framework.
Organizes the network data into a structured format with nodes, edges, and additional metadata for efficient analysis.

Steps:
- Creates a BuiltinDataset object:
    - Initializes a BuiltinDataset instance to hold the network data.
    - Sets appropriate attributes indicating the data is not uploaded from a file or external source.
- Populates node and edge data:
    - Iterates through each element in the input network:
        - Extracts node properties and adds them to the dataset.nodes dictionary.
        - Optionally adds community and social influence information if available in the element.
        - Updates the dataset.node_types dictionary to count the frequency of each node type.
    - If the element is an edge:
        - Extracts edge properties and adds them to the dataset.edges list.
        - Updates the dataset.adj_list and dataset.in_adj_list dictionaries to create adjacency lists for efficient edge lookup.
        - Updates the dataset.edge_types dictionary to count the frequency of each edge type.
- Returns the dataset:
    - Returns the constructed BuiltinDataset object containing the organized network data for further analysis.

Converts a network representation into a specific dataset format.
Stores nodes, edges, and metadata for analysis.
Creates adjacency lists for efficient edge traversal.
Maintains counts of node and edge types.
'''
