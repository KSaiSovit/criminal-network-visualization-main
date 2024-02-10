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
import networkx as nx

# find path to root directory of the project so as to import from other packages
tokens = os.path.abspath(__file__).split('/')
# print('tokens = ', tokens)
path2root = '/'.join(tokens[:-2])
# print('path2root = ', path2root)
if path2root not in sys.path:
    sys.path.append(path2root)

import analyzer.common.helpers as helpers


def pagerank(network, params):
    """
    wrapper for NetworkX's parerank function
    :param network:
    :param params:

    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'scores': a dictionary of pagerank score of nodes in network
        }
    """
    try:
        graph, node_ids = helpers.convert_to_nx_directed_graph(network)
        # print(graph)
        # print(node_ids)
        pr = nx.pagerank(graph)
        scores = [(node_ids[i], pr[i]) for i in range(len(node_ids))]
        # print(scores)
        scores = dict(scores)
        result = {'success': 1, 'message': 'the task is performed successfully', 'scores': scores}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network', 'scores': None}
        return result
'''
This function performs PageRank analysis on a network using NetworkX and returns the results as a dictionary.

Structure:
- It takes the network (as an edge list dictionary) and parameters (currently unused) as input.
- It converts the network to a NetworkX directed graph using helpers.convert_to_nx_directed_graph.
- It calculates PageRank scores using nx.pagerank and converts them to a dictionary with node IDs as keys and scores as values.
- It returns a dictionary with success status, message, and scores.
- It handles exceptions and returns an error message if the algorithm is not suitable for the network.
'''


def authority(network, params):
    """
    wrapper for NetworkX's hits function
    :param network:
    :param params:
    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'scores': a dictionary of pagerank score of nodes in network
        }
    """
    try:
        graph, node_ids = helpers.convert_to_nx_directed_graph(network)
        # print(graph)
        # print(node_ids)
        _, a = nx.hits(graph)
        scores = [(node_ids[i], a[i]) for i in range(len(node_ids))]
        # print(scores)
        scores = dict(scores)
        result = {'success': 1, 'message': 'the task is performed successfully', 'scores': scores}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network', 'scores': None}
        return result
'''
This function calculates authority scores for nodes in a network using NetworkX's HITS algorithm and returns the scores in a structured format.

Inputs:
- network: A network represented as an edge list dictionary.
- params: Additional parameters (currently unused).

Steps:
- Converts the network to a NetworkX directed graph using helpers.convert_to_nx_directed_graph.
- Calls NetworkX's hits function to compute hub and authority scores.
- Discards the hub scores and retains only the authority scores.
- Formats scores into a dictionary with node IDs as keys and authority scores as values.

Return Value:
- A dictionary containing:
- success: 1 if successful, 0 otherwise.
- message: A success message or error message.
- scores: The dictionary of node IDs and their authority scores.

Error Handling:
- Catches exceptions and returns an error message if the algorithm is not suitable for the network.
'''


def betweenness(network, params):
    """
    wrapper for NetworkX's betweeness_centrality function
    :param network:
    :param params:
    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'scores': a dictionary of pagerank score of nodes in network
        }

    """
    try:
        graph, node_ids = helpers.convert_to_nx_undirected_graph(network)  # TODO: to be refactor
        # print(graph)
        # print(node_ids)
        centralities = nx.betweenness_centrality(graph)
        scores = [(node_ids[i], centralities[i]) for i in range(len(node_ids))]
        # print(scores)
        scores = dict(scores)
        result = {'success': 1, 'message': 'the task is performed successfully', 'scores': scores}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network', 'scores': None}
        return result
'''
This function calculates betweenness centrality scores for nodes in a network using NetworkX's betweenness_centrality function.
Returns the scores in a consistent dictionary format.

Inputs:
- network: A network represented as an edge list dictionary.
- params: Additional parameters (currently unused).

Steps:
- Converts the network to an unweighted, undirected NetworkX graph (Note: This might need refactoring if weighted or directed networks are supported).
- Calculates betweenness centrality scores for each node using nx.betweenness_centrality.
- Formats scores into a dictionary with node IDs as keys and scores as values.

Return Value:
- A dictionary containing:
    - success: 1 if successful, 0 otherwise.
    - message: A success message or error message.
    - scores: The dictionary of node IDs and their betweenness centrality scores.

Error Handling:
    - Catches exceptions and returns an error message if the algorithm is not suitable for the network.
'''


def katz_centrality(network, params):
    """
    wrapper for NetworkX's katz_centrality function
    :param network:
    :param params:
    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'scores': a dictionary of pagerank score of nodes in network
        }

    """
    try:
        graph, node_ids = helpers.convert_to_nx_undirected_graph(network)  # TODO: to be refactor
        # print(graph)
        # print(node_ids)
        centralities = nx.katz_centrality(graph)
        scores = [(node_ids[i], centralities[i]) for i in range(len(node_ids))]
        # print(scores)
        scores = dict(scores)
        result = {'success': 1, 'message': 'the task is performed successfully', 'scores': scores}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network', 'scores': None}
        return result
'''
This function
Calculates Katz centrality scores for nodes in a network using NetworkX's katz_centrality function.
Returns the scores in a consistent dictionary format.

Inputs:
- network: A network represented as an edge list dictionary.
- params: Additional parameters (currently unused).

Steps:
- Converts the network to an unweighted, undirected NetworkX graph (Note: This might need refactoring if weighted or directed networks are supported).
- Calculates Katz centrality scores for each node using nx.katz_centrality.
- Formats scores into a dictionary with node IDs as keys and scores as values.

Return Value:
- A dictionary containing:
    - success: 1 if successful, 0 otherwise.
    - message: A success message or error message.
    - scores: The dictionary of node IDs and their Katz centrality scores.

Error Handling:
- Catches exceptions and returns an error message if the algorithm is not suitable for the network.
'''


def closeness_centrality(network, params):
    """
    wrapper for NetworkX's closeness_centrality function
    :param network:
    :param params:
     :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'scores': a dictionary of pagerank score of nodes in network
        }

    """
    try:
        graph, node_ids = helpers.convert_to_nx_undirected_graph(network)  # TODO: to be refactor
        # print(graph)
        # print(node_ids)
        centralities = nx.katz_centrality(graph)
        scores = [(node_ids[i], centralities[i]) for i in range(len(node_ids))]
        # print(scores)
        scores = dict(scores)
        result = {'success': 1, 'message': 'the task is performed successfully', 'scores': scores}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network', 'scores': None}
        return result
'''
This function
Calculates closeness centrality scores for nodes in a network using NetworkX's closeness_centrality function.
Returns the scores in a consistent dictionary format.

Inputs:
- network: A network represented as an edge list dictionary.
- params: Additional parameters (currently unused, but could be used for customization).

Steps:
- Network Conversion: Converts the network to a suitable graph representation for closeness centrality (likely unweighted, undirected). Consider refactoring this for flexibility.
- Closeness Centrality Calculation: Calls nx.closeness_centrality to compute closeness centrality scores for each node.
- Result Formatting: Organizes scores into a dictionary with node IDs as keys and scores as values.

Return Value:
- A dictionary containing:
    - success: 1 if successful, 0 otherwise.
    - message: A success or error message.
    - scores: The dictionary of node IDs and their closeness centrality scores.

Error Handling:
- Catches exceptions and returns an error message if the algorithm is not suitable for the network.
- Consider providing more specific error messages based on exception types.
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
                                            'fixed_options': {
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
    info = {'name': 'Social Influence Analysis',
            'methods': {
                'pagerank': {
                    'name': 'Pagerank',
                    'parameter': {}
                },
                'authority': {
                    'name': 'Authority',
                    'parameter': {}
                },
                'betweenness': {
                    'name': 'Betweeness Centrality',
                    'parameter': {}
                },
                'closeness_centrality': {
                    'name': 'Closeness Centrality',
                    'parameter': {}
                }
            }
            }
    return info
'''
This function
Returns information about the analysis tasks and methods available in the class.
Presents the information in a structured dictionary format.

Structure:
- The function defines a dictionary named info with two keys:
    - name: A string representing the overall analysis task name (e.g., "Social Influence Analysis").
    - methods: A dictionary where each key is an internal method name (e.g., "pagerank") and its value is another dictionary describing that method:
        - name: A string representing the full method name (e.g., "Pagerank").
        - parameter: A dictionary where each key is a parameter name and its value is another dictionary describing that parameter:
            - description: A string explaining the parameter's purpose.
            - fixed_options: A dictionary where each key is an accepted parameter value and its value is the full name of that value (e.g., for numerical options, the value could be "Integer").

This structure effectively organizes information about the methods and their parameters.
The dictionary format allows for easy expansion as new methods or parameters are added.
'''


class SocialInfluenceAnalyzer:
    """
    class for performing community detection
    """

    def __init__(self, algorithm):
        """
        init a community detector using the given `algorithm`
        :param algorithm:
        """
        self.algorithm = algorithm
        self.methods = {
            'pagerank': pagerank,
            'authority': authority,
            'betweenness': betweenness,
            'katz_centrality': katz_centrality,
            'closeness_centrality': closeness_centrality
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
This class serves as a social influence analyzer, providing various methods to calculate influence scores for nodes in a network.

Initialization:
- The __init__ method takes an algorithm as input and stores it as an attribute.
- It defines a methods dictionary mapping algorithm names to corresponding function references (e.g., pagerank).

Method Execution:
- The perform method takes a network (as an edge list) and parameters as input.
- It retrieves the chosen algorithm from the methods dictionary based on the stored algorithm attribute.
- It calls the chosen algorithm's function with the provided network and parameters.
- It returns the result of the algorithm function.

This design promotes modularity and reusability by having separate functions for each algorithm.
The class can be easily extended to support new algorithms by adding them to the methods dictionary.
'''