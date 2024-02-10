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
import sys
import os
import networkx.algorithms.link_prediction as methods
import networkx.algorithms.community as community_methods
from operator import itemgetter

# find path to root directory of the project so as to import from other packages
tokens = os.path.abspath(__file__).split('/')
# print('tokens = ', tokens)
path2root = '/'.join(tokens[:-2])
# print('path2root = ', path2root)
if path2root not in sys.path:
    sys.path.append(path2root)

import analyzer.common.helpers as helpers


def _get_sources(nx_graph, params, node_index):
    if 'sources' in params:
        sources = params['sources']
        sources = [node_index[u] for u in sources]
    else:
        sources = nx_graph.nodes

    return sources
'''
Extracts a list of nodes representing the starting points for an analysis or calculation on a NetworkX graph.
Handles two potential ways to specify the source nodes:
    - Through an explicit list provided in the params dictionary under the key "sources".
    - By default, considering all nodes in the graph (equivalent to using nx_graph.nodes).

Inputs:
- nx_graph
- params
- node_index

Output: A list of source nodes, represented by their internal IDs or user-friendly names depending on the context.

Steps:
- Check for explicit source list in paramseters
- Return the list of source nodes

This function provides sources through parameters or using all nodes as defaults.
The context determines whether internal IDs or user-friendly names are used in the returned list.
This functionality could be beneficial for various graph analysis tasks that require starting points within the network.
'''


def _get_candidates(nx_graph, sources):
    """
    find candidate (new) links for a list of nodes
    :param network: networkx network
    :param sources: list of node id
    :return:
    """
    candidates = []

    if sources is None:
        sources = nx_graph.nodes
    # TODO: to add more selection for identifying the candidates
    for u in sources:
        neighbors = nx_graph.neighbors(u)
        second_hop_neighbors = set()
        for v in neighbors:
            second_hop_neighbors = second_hop_neighbors.union(set(nx_graph.neighbors(v)))
        second_hop_neighbors = second_hop_neighbors.difference(neighbors)
        if u in second_hop_neighbors:
            second_hop_neighbors.remove(u)
        candidates.extend([(u, v) for v in second_hop_neighbors])

    return candidates
'''

This function identifies potential new links (edges) for a list of nodes within a network represented by a NetworkX graph.

Identifies nodes that are two hops away from the provided source nodes but are not directly connected to them.
These "candidate" nodes represent potential connections that might be missing in the current network.
This functionality could be useful for tasks like link prediction or uncovering hidden relationships in networks.

Inputs:
- nx_graphs
- sources

Outputs: A list of tuples, where each tuple represents a potential new link as (source_node_id, candidate_node_id).

Steps:
- Handle optional sources
- Iterate through source nodes
- Return candidate links

The function focuses on nodes within two hops of the provided sources, suggesting a specific search depth.
It excludes links that already exist or would create self-loops.
'''


def _select_top_k(candidates, k=3):
    candidates.sort(key=itemgetter(1), reverse=True)
    return [u[0] for u in candidates[:k]]
'''
This function selects the top K candidates from a given list while considering a specific sorting criterion.

Takes a list of candidates and selects the top K elements based on their values for a particular attribute (represented by the second element in each candidate tuple).
This functionality is commonly used in various scenarios where ranking or selecting the most relevant items is necessary.

Inputs:
- candidates
- k

Output: A list containing the IDs (first element) of the top K candidates, extracted from their respective tuples.

Steps:
- Sort candidates
- Select top k IDs
- Extract IDs
- Return top k IDs

This function assumes the ranking is based on the second element within each candidate tuple. Modify the key argument in sort if a different attribute is used.
The default value of k ensures at least 3 candidates are selected, even if fewer exist.
This is a generic function that can be applied in various contexts where selecting top-ranked items based on an attribute is required.
'''


def _generate_link_predictions(scores, params, sources, node_ids):
    preds = dict([(node_ids[u], []) for u in sources])

    for u, v, p in scores:
        # print('(%d, %d) -> %.8f' % (u, v, p))
        preds[node_ids[u]].append((node_ids[v], p))

    for u in preds:
        if 'top_k' in params:
            preds[u] = _select_top_k(preds[u], params['top_k'])
        else:
            preds[u] = _select_top_k(preds[u])

    return preds
'''

The provided function takes calculated link prediction scores and processes them into a structured dictionary representing potential new links for each source node.

Converts raw link prediction scores (triples of source, target node, and score) into a dictionary format suitable for further analysis or interpretation.
Optionally filters and selects the top-scoring predictions for each source node based on a configurable parameter.

Inputs:
- scores
- params
- sources
- node_ids

Output:
- A dictionary named preds
    - Keys are source node IDs (either internal or user-friendly depending on node_ids).
    - Values are lists of tuples representing predicted links for that source node, where each tuple contains (target node ID, score).
    - Optionally, only the top K highest-scoring predictions are included if 'top_k' is specified in params.

Steps:
- Initialize prediction dictionary
- Iterate over link scores
- Apply top-K filtering (optional)
- Return predictions dictionary

The function leverages the node_ids dictionary to handle both internal node IDs and user-friendly names in predictions.
The optional 'top_k' parameter allows controlling the number of predictions returned for each source node.
This function provides a structured representation of link prediction results, facilitating further analysis or visualization.
'''


def _call_nx_community_detection_method(method_name, graph):
    """
    call networkx' community detection methods. 
    supported methods including 'modularity', 'asyn_lpa', 'label_propagation'
    :param method_name: the name of networkx' community detection algorithm
    :param graph: networkx graph
    :return:
    """
    supported_community_methods = ('modularity', 'asyn_lpa', 'label_propagation')

    if method_name not in supported_community_methods:
        return None

    if method_name is supported_community_methods[0]:
        return community_methods.greedy_modularity_communities(graph)
    elif method_name is supported_community_methods[1]:
        return community_methods.asyn_lpa_communities(graph)
    elif method_name is supported_community_methods[2]:
        return community_methods.label_propagation_communities(graph)
    else:
        return None
'''
This function acts as a wrapper for calling specific community detection algorithms provided by the NetworkX library.

Simplifies the usage of different NetworkX community detection algorithms within the codebase.
Provides a central location for handling supported methods and algorithm execution.

Inputs:
- method_name
- graph

Output:
- The result of the community detection algorithm, typically a dictionary containing community assignments for nodes.
- If the method_name is not supported, it returns None.

Steps:
- Check for supported methods
- Execute specific algorithm
    - If the method_name matches a supported one:
        - Uses conditional statements to directly call the corresponding NetworkX community detection function (e.g., community_methods.greedy_modularity_communities for 'modularity').
        - Returns the result of the called function, which typically contains community assignments for nodes.

This function promotes code maintainability and clarity by keeping track of supported methods and centralizing their execution.
The direct calls to NetworkX functions leverage their existing implementation and expertise.
The function gracefully handles unsupported algorithms by returning None.
'''


def resource_allocation_index(network, params):
    """
    predict links for a set of nodes using networkx' resource_allocation_index function
    :param network: networkx network
    :param params:
    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'predictions': predictions
        }
    """
    try:
        graph, node_ids = helpers.convert_to_nx_undirected_graph(network)
        node_index = [(node_ids[i], i) for i in range(len(node_ids))]
        node_index = dict(node_index)
        if params is None:
            params = {}

        sources = _get_sources(graph, params, node_index)
        candidates = _get_candidates(graph, sources)
        scores = methods.resource_allocation_index(graph, candidates)
        predictions = _generate_link_predictions(scores, params, sources, node_ids)
        result = {'success': 1, 'message': 'the task is performed successfully', 'predictions': predictions}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network', 'predictions': None}
        return result
'''
This function predicts potential new links using the resource allocation index method within a network represented by a NetworkX graph.

Leverages the resource allocation index algorithm to identify candidate links that are likely missing in the provided network.
Offers predictions in the form of a dictionary containing source-target node pairs and their associated scores.

Inputs:
- network
- params

Output:
- A doctionary with the following structure:
    - succes
    - message
    - predictions

Steps:
- Network conversion and preparation
- Identify source nodes
- Find candiate links
- Calculate link sources
- Generate predictions
- Return results

The function relies on several helper functions for network conversion, source selection, candidate identification, and prediction generation.
It handles both explicit source node selection and using all nodes as defaults.
The optional params dictionary allows for potential customization of predictions.
Error handling catches exceptions and returns an appropriate failure message.
'''


def jaccard_coefficient(network, params=None):
    """
    predict links for a set of nodes using networkx' jaccard_coefficient function
    :param network: networkx network
    :param params:
    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'predictions': predictions
        }
    """
    try:
        graph, node_ids = helpers.convert_to_nx_undirected_graph(network)
        node_index = [(node_ids[i], i) for i in range(len(node_ids))]
        node_index = dict(node_index)
        if params is None:
            params = {}

        sources = _get_sources(graph, params, node_index)
        candidates = _get_candidates(graph, sources)
        scores = methods.jaccard_coefficient(graph, candidates)
        predictions = _generate_link_predictions(scores, params, sources, node_ids)

        result = {'success': 1, 'message': 'the task is performed successfully', 'predictions': predictions}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network', 'predictions': None}
        return result
'''

This function is similar to the previous resource_allocation_index function. 

This function also aims to predict potential new links using a network analysis method, but it leverages the Jaccard coefficient instead of the resource allocation index.
It offers predictions in the same structured dictionary format as before.

Inputs:
- network
- params

Outputs:
- A doctionary with the following structure:
    - succes
    - message
    - predictions

Steps:
- Network conversion and preparation
- Identify source nodes
- Find candiate links
- Calculate link sources
    - Instead of methods.resource_allocation_index, the function now uses methods.jaccard_coefficient to compute scores based on shared neighbors between candidate nodes.
- Generate predictions
- Return results

The provided code demonstrates code reuse and modularity by using common helper functions and a consistent structure for different link prediction algorithms.
The main difference between the two functions lies in the underlying algorithm used for scoring potential links.
'''    



def adamic_adar_index(network, params):
    """
    predict links for a set of nodes using networkx' adamic_adar_index function
    :param network: networkx network
    :param params:
    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'predictions': predictions
        }
    """
    try:
        graph, node_ids = helpers.convert_to_nx_undirected_graph(network)
        node_index = [(node_ids[i], i) for i in range(len(node_ids))]
        node_index = dict(node_index)
        if params is None:
            params = {}

        sources = _get_sources(graph, params, node_index)
        candidates = _get_candidates(graph, sources)
        scores = methods.adamic_adar_index(graph, candidates)
        predictions = _generate_link_predictions(scores, params, sources, node_ids)

        result = {'success': 1, 'message': 'the task is performed successfully', 'predictions': predictions}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network', 'predictions': None}
        return result
'''

This function is similar to the previous resource_allocation_index and jaccard_coefficient functions.

This function also aims to predict potential new links using a network analysis method, but it leverages the Adamic-Adar index instead of the resource allocation index or Jaccard coefficient.
It offers predictions in the same structured dictionary format as before.

Differences:
- Each function uses a different link prediction algorithm:
    - resource_allocation_index: Resource allocation index
    - jaccard_coefficient: Jaccard coefficient
    - adamic_adar_index: Adamic-Adar index
- These algorithms differ in how they score potential links based on network structure and node properties.

Similarities:
- They share a common code structure and utilize several helper functions.
- They follow the same input and output format.
- They handle errors and provide informative messages.
'''


def preferential_attachment(network, params):
    """
    predict links for a set of nodes using networkx' preferential_attachment function to
    compute the preferential attachment score of all node pairs in network.
    :param network: networkx network
    :param params:
    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'predictions': predictions
        }
    """
    try:
        graph, node_ids = helpers.convert_to_nx_undirected_graph(network)
        node_index = [(node_ids[i], i) for i in range(len(node_ids))]
        node_index = dict(node_index)
        if params is None:
            params = {}

        sources = _get_sources(graph, params, node_index)
        candidates = _get_candidates(graph, sources)
        scores = methods.preferential_attachment(graph, candidates)
        predictions = _generate_link_predictions(scores, params, sources, node_ids)

        result = {'success': 1, 'message': 'the task is performed successfully', 'predictions': predictions}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network', 'predictions': None}
        return result
'''
Takes a network (represented as a networkx graph) and parameters as input.
Uses the networkx preferential_attachment function to predict potential links between nodes.
Returns a dictionary containing:
    - success: Indicates whether the prediction was successful (1) or not (0).
    - message: Provides a message based on the outcome.
    - predictions: Contains the predicted links in a specific format.

Steps:
- Conversion and PReparation
- Source and Candidate Identification
- Link Prediction
    - Uses the networkx preferential_attachment function to calculate scores for potential links between source and candidate nodes.
    - Based on these scores and provided parameters, generates final link predictions.
- Output
'''


def count_number_soundarajan_hopcroft(network, params):
    """
    predict links for a set of nodes using networkx' cn_soundarajan_hopcroft function to 
    count the number of common neighbors
    :param network: networkx network
    :param params:
    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'predictions': predictions
        }
    """
    try:
        graph, node_ids = helpers.convert_to_nx_undirected_graph(network)
        node_index = [(node_ids[i], i) for i in range(len(node_ids))]
        node_index = dict(node_index)
        if params is None:
            params = {}

        try:
            community_detection_method = params['community_detection_method']
        except Exception as e:
            print('Community detection method is not defined.', e)
            return None

        nx_comms = _call_nx_community_detection_method(community_detection_method, graph)
        if nx_comms is None:
            print("Community detection method is not supported.")
            return None
        else:
            nx_comms = list(nx_comms)

        # initalize community information
        for node in graph.nodes():
            graph.nodes[node]['community'] = None

        # add community information
        for i in range(len(nx_comms)):
            for node in nx_comms[i]:
                if graph.nodes[node]['community'] is None:
                    graph.nodes[node]['community'] = i

        sources = _get_sources(graph, params, node_index)
        candidates = _get_candidates(graph, sources)
        scores = methods.cn_soundarajan_hopcroft(graph, candidates)
        predictions = _generate_link_predictions(scores, params, sources, node_ids)

        result = {'success': 1, 'message': 'the task is performed successfully', 'predictions': predictions}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network', 'predictions': None}
        return result
'''
This function focuses on counting the number of common neighbors between nodes to predict potential links.

- Takes a network (represented as a networkx graph) and parameters as input.
- Uses the networkx cn_soundarajan_hopcroft function to count the number of common neighbors for each pair of nodes.
- Predicts links based on this common neighbor count and provided parameters.
- Returns a dictionary containing:
    - success: Indicates whether the prediction was successful (1) or not (0).
    - message: Provides a message based on the outcome.
    - predictions: Contains the predicted links in a specific format.

Steps:
- Conversion and Preparation
- Community Detection
- Source and Candidate Identification
- Link Prediction
- Output Preparation

This function utilizes the concept of shared communities and common neighbors to identify potential links within a network. Note that the success relies heavily on the chosen community detection method and its effectiveness in capturing meaningful communities in the network.
'''


def resource_allocation_index_soundarajan_hopcroft(network, params):
    """
    predict links for a set of nodes using networkx' ra_index_soundarajan_hopcroft function to 
    compute the resource allocation index of all node pairs in network using community information.
    :param network: networkx network
    :param params:
    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'predictions': predictions
        }
    """
    try:
        graph, node_ids = helpers.convert_to_nx_undirected_graph(network)
        node_index = [(node_ids[i], i) for i in range(len(node_ids))]
        node_index = dict(node_index)
        if params is None:
            params = {}

        try:
            community_detection_method = params['community_detection_method']
        except Exception as e:
            print('Community detection method is not defined.', e)
            return None

        nx_comms = _call_nx_community_detection_method(community_detection_method, graph)
        if nx_comms is None:
            print("Community detection method is not supported.")
            return None
        else:
            nx_comms = list(nx_comms)

        # initalize community information
        for node in graph.nodes():
            graph.nodes[node]['community'] = None

        # add community information
        for i in range(len(nx_comms)):
            for node in nx_comms[i]:
                if graph.nodes[node]['community'] is None:
                    graph.nodes[node]['community'] = i

        sources = _get_sources(graph, params, node_index)
        candidates = _get_candidates(graph, sources)
        scores = methods.ra_index_soundarajan_hopcroft(graph, candidates)
        predictions = _generate_link_predictions(scores, params, sources, node_ids)

        result = {'success': 1, 'message': 'the task is performed successfully', 'predictions': predictions}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network', 'predictions': None}
        return result
'''
This function predicts potential links within a network using community information and a specific scoring method.

Takes a network (represented as a networkx graph) and parameters as input.
Uses the networkx ra_index_soundarajan_hopcroft function to compute the "resource allocation index" for each pair of nodes within the network, leveraging community information.
Predicts links based on these scores and provided parameters.
Returns a dictionary containing:
    - success: Indicates whether the prediction was successful (1) or not (0).
    - message: Provides a message based on the outcome.
    - predictions: Contains the predicted links in a specific format.

Steps:
- Conversion and Preparation
- Community Detection
- Source and Condidate Identification
- Link Prediction
    - Uses the networkx ra_index_soundarajan_hopcroft function to calculate the "resource allocation index" for each source-candidate pair. This index considers the communities each node belongs to and aims to capture how well-positioned they are to form a link.
    - Based on these scores and provided parameters, generates final link predictions.
- Output Preparation
'''


def within_inter_cluster(network, params):
    """
    predict links for a set of nodes using networkx' within_inter_cluster to 
    compute the ratio of within- and inter-cluster common neighbors of all node pairs in network.
    :param network: networkx network
    :param params:
    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'predictions': predictions
        }
    """
    try:
        graph, node_ids = helpers.convert_to_nx_undirected_graph(network)
        node_index = [(node_ids[i], i) for i in range(len(node_ids))]
        node_index = dict(node_index)
        if params is None:
            params = {}

        try:
            community_detection_method = params['community_detection_method']
        except Exception as e:
            print('Community detection method is not defined.', e)
            return None

        nx_comms = _call_nx_community_detection_method(community_detection_method, graph)
        if nx_comms is None:
            print("Community detection method is not supported.")
            return None
        else:
            nx_comms = list(nx_comms)

        # initalize community information
        for node in graph.nodes():
            graph.nodes[node]['community'] = None

        # add community information
        for i in range(len(nx_comms)):
            for node in nx_comms[i]:
                if graph.nodes[node]['community'] is None:
                    graph.nodes[node]['community'] = i

        sources = _get_sources(graph, params, node_index)
        candidates = _get_candidates(graph, sources)
        scores = methods.within_inter_cluster(graph, candidates)
        predictions = _generate_link_predictions(scores, params, sources, node_ids)

        result = {'success': 1, 'message': 'the task is performed successfully', 'predictions': predictions}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network', 'predictions': None}
        return result
'''
This function predicts potential links within a network using the concept of within-cluster and inter-cluster common neighbors.

Takes a network (represented as a networkx graph) and parameters as input.
Uses the networkx within_inter_cluster function to calculate a score for each pair of nodes, indicating the ratio of shared neighbors within the same community to shared neighbors across different communities.
Predicts links based on these scores and provided parameters.
Returns a dictionary containing:
    - success: Indicates whether the prediction was successful (1) or not (0).
    - message: Provides a message based on the outcome.
    - predictions: Contains the predicted links in a specific format.

Steps:
- Conversion and Preparation
- Community Detection
- Source and Candidate Identification
- Link Prediction
    - Uses the networkx within_inter_cluster function to calculate a score for each source-candidate pair. This score represents the ratio of the number of neighbors they share within the same community to the number they share across different communities.
    - Based on these scores and provided parameters, generates final link predictions. Nodes with a higher "within-cluster" score are more likely to be predicted as linked.
- Output
'''


def get_info():
    """
    get information about methods provided in this class
    :return: dictionary: Provides the name of the analysis task, available methods and information
                         about an methods parameter. Also provides full names of tasks, methods and parameter.
                         Information is provided in the following format:

                        {
                            'name': Full analysis task name as string
                            'methods': {
                                key: Internal method name (eg. 'asyn_lpa')
                                value: {
                                    'name': Full method name as string
                                    'parameter': {
                                        key: Parameter name
                                        value: {
                                            'description': Description of the parameter
                                            'options': {
                                                key: Accepted parameter value
                                                value: Full parameter value name as string
                                                !! If accepted values are integers key and value is 'Integer'. !!
                                            }
                                        }
                                    }
                                }
                            }
                        }

    """
    info = {'name': 'Link Prediction',
            'methods': {
                'resource_allocation_index': {
                    'name': 'Resource Allocation Index',
                    'parameter': {}
                },
                'jaccard_coefficient': {
                    'name': 'Jaccard Coefficient',
                    'parameter': {}
                },
                'adamic_adar_index': {
                    'name': 'Adamic Adar Index',
                    'parameter': {}
                },
                'count_number_soundarajan_hopcroft': {
                    'name': 'Soundarajan Hopcroft (Count Numbers)',
                    'parameter': {
                        'community_detection_method': {
                            'description': 'Community detection method',
                            'options': {'modularity': 'Modularity',
                                        'asyn_lpa': 'Asynchronous Label Propagation',
                                        'label_propagation': 'Label Propagation'}
                        }
                    }
                },
                'resource_allocation_index_soundarajan_hopcroft': {
                    'name': 'Resource Alocation Index (Soundarajan Hopcroft)',
                    'parameter': {
                        'community_detection_method': {
                            'description': 'Community detection method',
                            'options': {'modularity': 'Modularity',
                                        'asyn_lpa': 'Asynchronous Label Propagation',
                                        'label_propagation': 'Label Propagation'}
                        }
                    }
                },
                'within_inter_cluster': {
                    'name': 'Within- and Interclustering',
                    'parameter': {
                        'community_detection_method': {
                            'description': 'Community detection method',
                            'options': {'modularity': 'Modularity',
                                        'asyn_lpa': 'Asynchronous Label Propagation',
                                        'label_propagation': 'Label Propagation'}
                        }
                    }
                }
            }
            }
    return info
'''
This function is a documentation generator for a class containing methods for link prediction in networks. It returns a dictionary with information about the available methods and their parameters.

To provide information about the analysis tasks, methods, and parameters in the class.
To present this information in a structured and clear format.

Output:
- A dictionary with the following structure:
    - name
    - methods: a dict
        - Keys: The internal method name
        - Value:
            - name: The full name of the method
            - parameter: A dictionary containing info about each parameter
                - Key: THe name os the parameter
                - Value: A dictionary with:
                    - description: A text description of the parameter's pupose
                    - options: A dictionary with
                         - Key: value
                         - Value: THe full name of the value
'''


class LinkPredictor:
    """
    class for performing link prediction
    """

    def __init__(self, algorithm):
        """
        init a community detector using the given `algorithm`
        :param algorithm:
        """
        self.algorithm = algorithm
        self.methods = {
            'resource_allocation_index': resource_allocation_index,
            'jaccard_coefficient': jaccard_coefficient,
            'adamic_adar_index': adamic_adar_index,
            'preferential_attachment': preferential_attachment,
            'count_number_soundarajan_hopcroft': count_number_soundarajan_hopcroft,
            'resource_allocation_index_soundarajan_hopcroft': resource_allocation_index_soundarajan_hopcroft,
            'within_inter_cluster': within_inter_cluster
            # TODO: to add more methods from networkx, snap, and sklearn
        }

    def perform(self, network, params):
        """
        performing
        :param network:
        :param params:
        :return:
        """
        return self.methods[self.algorithm](network, params)

'''
This class is used for predicting potential links within a network.

Provides a tool for predicting future connections between nodes in a network based on the chosen algorithm and network characteristics.

Steps:
- Initialization
    - Takes an algorithm as input, presumably specifying the link prediction strategy to be used.
    - Stores the chosen algorithm internally for later use.
    - Defines a dictionary called methods that maps method names to corresponding prediction functions:
        - The method names align with known link prediction algorithms (e.g., "resource_allocation_index", "jaccard_coefficient").
        - Each associated function likely implements the specific prediction logic for its respective algorithm.
- Prediction methods
    - The class doesn't directly handle predictions itself. Instead, it relies on the external functions stored in the methods dictionary.
    - When you call a specific method on the LinkPredictor object (e.g., predictor.resource_allocation_index(network, params)), it retrieves the corresponding function from the dictionary and executes it.
    - Each method presumably takes the network data and potentially additional parameters as input and returns predictions in a specific format.

Second Function (perform)

This function takes two arguments:
    - network: This represents the network data, likely formatted as a networkx graph object.
    - params: This is a dictionary containing additional parameters specific to the chosen link prediction algorithm.

Steps:
- Retrieving the Chosen Algorithm
- Finding the Corresponding Function
- Executing the Prediction Function
    - If the algorithm exists in the methods dictionary, it retrieves the associated function.
    - The retrieved function is then called with the provided network and params as arguments.
    - This essentially delegates the actual link prediction task to the specific function designed for the chosen algorithm.
- Returning the Result:
    - The output of the called prediction function (presumably containing the link predictions) is returned by the perform method.
'''

