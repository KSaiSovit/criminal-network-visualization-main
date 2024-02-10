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
import itertools
import networkx.algorithms.community as methods
import networkx
from sklearn.cluster import SpectralClustering
from sklearn.cluster import AgglomerativeClustering

# find path to root directory of the project so as to import from other packages
tokens = os.path.abspath(__file__).split('/')
# print('tokens = ', tokens)
path2root = '/'.join(tokens[:-2])
# print('path2root = ', path2root)
if path2root not in sys.path:
    sys.path.append(path2root)

import analyzer.common.helpers as helpers


def _generate_communities_and_membership(nx_communities, node_ids):
    communities = []
    membership = {}
    for c in range(len(nx_communities)):
        for u in nx_communities[c]:
            nid = node_ids[u]
            if nid in membership:
                membership[nid][c] = 1.0
            else:
                membership[nid] = {c: 1.0}
        communities.append(dict([(node_ids[u], 1.0) for u in nx_communities[c]]))
    return communities, membership
'''
Processes a list of communities detected in a graph and generates two data structures:
    - A list of communities represented as dictionaries of node IDs and their membership values.
    - A dictionary mapping node IDs to dictionaries of community memberships.

Inputs:
- nx_communities
- node_ids

Steps:
- Initializes empty data structures
    - communities
    - membership
- Iterates through communities
- Returns the processes data
'''

def k_clique_communities(network, params):
    """
    wrapper for NetworkX's k_clique_communities algorithm
    :param network:
    :param params:
    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'communities': communities - list of communities found, each is a dictionary of member nodes' id, and their membership
            'membership': membership - dictionary, membership[u] is a dictionary of communities of u and its membership in those communities
        }
    """
    try:
        graph, node_ids = helpers.convert_to_nx_undirected_graph(network)
        # If no parameter were given, use 3 as default.
        # May not be the most elegant solution but is the easiest for now.
        try:
            k = params['K']
        except KeyError:
            k = 3
        nx_comms = list(methods.k_clique_communities(graph, k))
        communities, membership = _generate_communities_and_membership(nx_comms, node_ids)
        result = {'success': 1, 'message': 'the task is performed successfully', 'communities': communities,
                  'membership': membership}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network',
                  'communities': None,
                  'membership': None}
        return result
'''
This function acts as a wrapper around the NetworkX k_clique_communities algorithm to find communities in a network.

Finds communities in a network based on the k-clique communities detection algorithm.
Converts the results into a specific dictionary format for further processing.
Handles potential errors and returns meaningful messages.

Inputs:
- network
- params (optional)

Outputs:
- A dictionary with the following keys:
    - success
    - message
    - communities
    - membership

Steps:
- Convert to NetworkX graph
- Extract k parameter
- FInd k-clique communities
- Process and return results

The function assumes helpers.convert_to_nx_undirected_graph and _generate_communities_and_membership are defined elsewhere.
It provides basic error handling with generic messages. More specific error handling could be added.
The default k value of 3 might not be suitable for all networks.
'''


def greedy_modularity_communities(network, params):
    """
    wrapper for NetworkX's greedy_modularity_communities algorithm
    :param network:
    :param params:
    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'communities': communities - list of communities found, each is a dictionary of member nodes' id, and their membership
            'membership': membership - dictionary, membership[u] is a dictionary of communities of u and its membership in those communities
        }
    """
    try:
        graph, node_ids = helpers.convert_to_nx_undirected_graph(network)
        nx_comms = list(methods.greedy_modularity_communities(graph))
        communities, membership = _generate_communities_and_membership(nx_comms, node_ids)
        result = {'success': 1, 'message': 'the task is performed successfully', 'communities': communities,
                  'membership': membership}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network',
                  'communities': None,
                  'membership': None}
        return result
'''
This function serves as a wrapper around the NetworkX greedy_modularity_communities algorithm to detect communities in a network. It shares many similarities with the previously analyzed k_clique_communities function.

Identifies communities in a network using the greedy modularity community detection algorithm.
Formats the results into a consistent dictionary structure for further use.
Handles potential errors gracefully with informative messages.

Inputs:
- network
- params (optional)

Outputs:
- A dictionary with the following keys:
    - success
    - message
    - communities
    - membership

Steps:
- Convert to NetworkX graph
- Find communities
- Process and return results

Similarities and Differences with k_clique_communities:
    - Both functions serve as wrappers for specific community detection algorithms from NetworkX.
    - They share the same structure for input and output dictionaries.
    - They follow similar error handling approaches.

    - The key difference lies in the employed community detection algorithms:
        - k_clique_communities uses the k-clique approach, focusing on densely connected subgraphs.
        - greedy_modularity_communities optimizes modularity, aiming for balanced community divisions.
'''


def asyn_lpa_communities(network, params):
    """
    wrapper for NetworkX's asynchronous label propagation algorithm
    :param network:
    :param params:
    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'communities': communities - list of communities found, each is a dictionary of member nodes' id, and their membership
            'membership': membership - dictionary, membership[u] is a dictionary of communities of u and its membership in those communities
        }
    """
    try:
        graph, node_ids = helpers.convert_to_nx_directed_graph(network)
        nx_comms = list(methods.asyn_lpa_communities(graph))
        communities, membership = _generate_communities_and_membership(nx_comms, node_ids)
        result = {'success': 1, 'message': 'the task is performed successfully', 'communities': communities,
                  'membership': membership}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network',
                  'communities': None,
                  'membership': None}
        return result
'''
This function serves as a wrapper for the NetworkX asyn_lpa_communities algorithm for community detection.

Uses the Asynchronous Label Propagation Algorithm (ALPA) to identify communities in a directed network.
Processes the results into a consistent dictionary format for further analysis.
Handles potential errors gracefully with informative messages.

Inputs:
- network
- params (optional)

Outputs:
- A dictionary with the following keys:
    - success
    - message
    - communities
    - membership

Steps:
- Convert to NetworkX graph
- Find communities
- Process and return results

Key Differences:
- This function specifically handles directed networks due to the ALPA algorithm's requirements.
- The conversion step and potential error messages reflect this difference.
'''


def label_propagation_communities(network, params):
    """
    wrapper for NetworkX's semi-synchronous label propagation algorithm
    :param network:
    :param params:
    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'communities': communities - list of communities found, each is a dictionary of member nodes' id, and their membership
            'membership': membership - dictionary, membership[u] is a dictionary of communities of u and its membership in those communities
        }
    """
    try:
        graph, node_ids = helpers.convert_to_nx_undirected_graph(network)
        nx_comms = list(methods.label_propagation_communities(graph))
        communities, membership = _generate_communities_and_membership(nx_comms, node_ids)
        result = {'success': 1, 'message': 'the task is performed successfully', 'communities': communities,
                  'membership': membership}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network',
                  'communities': None,
                  'membership': None}
        return result
'''
This function acts as a wrapper around the NetworkX label_propagation_communities algorithm to detect communities in an undirected network. Similar to the previous functions, it follows a structured approach and handles potential errors.

Identifies communities within an undirected network using the label propagation algorithm.
Converts the results into a consistent dictionary format for further processing.
Provides informative messages in case of errors.

Inputs:
- network
- params (optional)

Ouputs:
- A dictionary with the following keys:
    - success
    - message
    - communities
    - membership

Steps:
- Convert NetworkX graph
- Find communities
- Process and return results

Similarities and DIfferences:
- This function shares the same structure and error handling approach as the previously analyzed community detection functions.

- The key difference lies in the employed algorithm:
    - label_propagation_communities uses the label propagation algorithm, which iteratively propagates community labels based on node connections.
'''


def kernighan_lin_bipartition(network, params):
    """
    wrapper for NetworkX's Kernighan–Lin bipartition algorithm to partition a graph into two blocks
    :param network:
    :param params:
    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'communities': communities - list of communities found, each is a dictionary of member nodes' id, and their membership
            'membership': membership - dictionary, membership[u] is a dictionary of communities of u and its membership in those communities
        }
    """
    try:
        graph, node_ids = helpers.convert_to_nx_undirected_graph(network)
        nx_comms = list(methods.kernighan_lin_bisection(graph))
        communities, membership = _generate_communities_and_membership(nx_comms, node_ids)
        result = {'success': 1, 'message': 'the task is performed successfully', 'communities': communities,
                  'membership': membership}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network',
                  'communities': None,
                  'membership': None}
        return result
'''
This function acts as a wrapper for the NetworkX kernighan_lin_bisection algorithm, which performs graph bisection or partitioning into two distinct communities. Its structure and error handling follow a similar pattern as the previous community detection functions.

Bipartitions a given network into two separate communities using the Kernighan-Lin algorithm.
Processes the results into a consistent dictionary format for further use.
Provides informative messages in case of errors.

Inputs:
- network
- params (optional)

Outputs:
- A dictionary with the following keys:
    - success
    - message
    - communities
    - membership

Steps:
- Convert to NetworkX graph
- Find communities
- Process and return results

Key differences:
- This function specifically aims for bipartition (two communities) instead of general community detection like previous functions.
- The output communities and membership information reflect this bipartite structure.
- The underlying algorithm (Kernighan-Lin) optimizes for node movements that improve modularity, considering the two-community constraint.
'''


def spectral_communities(network, params):
    """
    wrapper for NetworkX's k_clique_communities algorithm
    :param network:
    :param params:
    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'communities': communities - list of communities found, each is a dictionary of member nodes' id, and their membership
            'membership': membership - dictionary, membership[u] is a dictionary of communities of u and its membership in those communities
        }
    """
    try:
        graph, node_ids = helpers.convert_to_nx_undirected_graph(network)
        # If no parameter were given, use 3 as default.
        # May not be the most elegant solution but is the easiest for now.
        try:
            k = params['K']
        except KeyError:
            k = 3

        adj_matrix = networkx.adjacency_matrix(graph)
        clustering = SpectralClustering(n_clusters=k, assign_labels="discretize", random_state=0).fit(adj_matrix)
        # print(clustering.labels_)
        communities = [{}] * k
        membership = {}
        for u in range(len(clustering.labels_)):
            c = clustering.labels_[u]
            nid = node_ids[u]
            if nid in membership:
                membership[nid][c] = 1.0
            else:
                membership[nid] = {c: 1.0}
            communities[c][nid] = 1.0

        result = {'success': 1, 'message': 'the task is performed successfully', 'communities': communities,
                  'membership': membership}
        return result

    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network',
                  'communities': None,
                  'membership': None}
        return result
'''
This function, spectral_communities, aims to identify communities within a network using the spectral clustering algorithm.
It acts as a wrapper around the SpectralClustering class from the scikit-learn library.
The function processes the input network data, performs spectral clustering, and returns a dictionary containing the detected communities and membership information.

Inputs:
- network
- params (optional dictionary)

Outputs:
- A dictionary with the following keys:
    - success
    - message
    - communities
    - membership

Steps:
- COnvert to NetworkX graph
- Extract adjacency matrix
- Perform spectral clustering
- Process and format results
- Error Handling

Difference:
- This function uses spectral clustering, which analyzes the graph's spectral properties to identify communities.
- It leverages the SpectralClustering class from scikit-learn for clustering.
- The output format (communities and membership) resembles previous functions but reflects the spectral clustering approach.
'''


def hierarchical_communities(network, params):
    """
    wrapper for NetworkX's k_clique_communities algorithm
    :param network:
    :param params:
    :return: dictionary, in the form
        {
            'success': 1 if success, 0 otherwise
            'message': a string
            'communities': communities - list of communities found, each is a dictionary of member nodes' id, and their membership
            'membership': membership - dictionary, membership[u] is a dictionary of communities of u and its membership in those communities
        }
    """
    try:
        graph, node_ids = helpers.convert_to_nx_undirected_graph(network)
        # If no parameter were given, use 3 as default.
        # May not be the most elegant solution but is the easiest for now.
        try:
            k = params['K']
        except KeyError:
            k = 3
        adj_matrix = networkx.adjacency_matrix(graph)
        clustering = AgglomerativeClustering(n_clusters=k).fit(adj_matrix.toarray())
        # print(clustering.labels_)
        communities = [{}] * k
        membership = {}
        for u in range(len(clustering.labels_)):
            c = clustering.labels_[u]
            nid = node_ids[u]
            if nid in membership:
                membership[nid][c] = 1.0
            else:
                membership[nid] = {c: 1.0}
            communities[c][nid] = 1.0

        result = {'success': 1, 'message': 'the task is performed successfully', 'communities': communities,
                  'membership': membership}
        return result
        result = {'success': 1, 'message': 'the task is performed successfully', 'communities': communities,
                  'membership': membership}
        return result
    except Exception as e:
        print(e)
        result = {'success': 0, 'message': 'this algorithm is not suitable for the input network',
                  'communities': None,
                  'membership': None}
        return result
'''
This function, similar to the previous community detection functions, utilizes a specific algorithm to identify communities within a network and returns results in a consistent format.

Leverages the hierarchical clustering approach to discover communities in an undirected network.
Processes the results into a standard dictionary structure for further use.
Handles potential errors with informative messages.

Inputs:
- network
- params (optional)

Outputs:
- A dictionary with the following keys:
    - success
    - message
    - communities
    - membership

Steps:
- Error Handling
- Convert to NetworkX Graph
- Extract Adjecency Matrix
- Perform Hierarchical Clustering
- Process and Format Results

Differences:
- This function employs hierarchical clustering, which starts with individual nodes and builds a hierarchy by merging them based on distances or similarities.
- It utilizes the AgglomerativeClustering class from scikit-learn for hierarchical clustering.
- The output resembles previous functions but reflects the hierarchical clustering approach (potentially nested communities).
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
    info = {'name': 'Community Detection',
            'methods': {
                'k_cliques': {
                    'name': 'K-clique',
                    'parameter': {
                        'K': {
                            'description': 'Size of smallest clique.',
                            'options': {'Integer': [3, 4, 5, 6, 7]}
                        }
                    }
                },
                'modularity': {
                    'name': 'Modularity Maximization',
                    'parameter': {}
                },
                'label_propagation': {
                    'name': 'Label Propagation',
                    'parameter': {}
                },
                'asyn_lpa': {
                    'name': 'Asynchronous Label Propagation',
                    'parameter': {}
                },
                'bipartition': {
                    'name': 'Kernighan–Lin Bipartition',
                    'parameter': {}
                },
                'spectral': {
                    'name': 'Spectral clustering',
                    'parameter': {
                        'K': {
                            'description': 'number of communities',
                            'options': {'Integer': [3, 4, 5, 6, 7]}
                        }
                    }
                },
                'hierarchical': {
                    'name': 'Hierarchical clustering',
                    'parameter': {
                        'K': {
                            'description': 'number of communities',
                            'options': {'Integer': [3, 4, 5, 6, 7]}
                        }
                    }
                }
            }
            }
    return info
'''

The provided get_info function aims to offer a comprehensive overview of the community detection methods available within its class. It returns a dictionary structure containing detailed information about each method's name, parameters, and their descriptions. 

Provides programmatic access to information about the supported community detection methods.
Facilitates exploration and understanding of the available functionalities.
Serves as a useful tool for developers or users interacting with the class.

Outputs:
- A dictionary named info with the following structure:
    - name
    - methods
        - name
        - parameter
            - Each parameter name serves as a key within this dictionary.
            - The corresponding value is another dictionary with the following keys:
                - description: A string explaining the purpose and usage of the parameter.
                - options: A dictionary specifying the accepted values for the parameter.
                    - Keys represent either allowed value types (e.g., "Integer") or specific values.
                    - Values in this dictionary represent human-readable names for the accepted options.


The function separates method information from overall task information using named keys.
It provides both internal method names and user-friendly full names for clarity.
Parameter descriptions and accepted values enhance understanding and usage.
The use of dictionaries allows for flexible representation of different method types and parameter scenarios.
'''


class CommunityDetector:
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
            'k_cliques': k_clique_communities,
            'modularity': greedy_modularity_communities,
            'asyn_lpa': asyn_lpa_communities,
            'label_propagation': label_propagation_communities,
            'bipartition': kernighan_lin_bipartition,
            'spectral': spectral_communities,
            'hierarchical': hierarchical_communities
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
This is a CommunityDetector class that acts as a central hub for performing community detection in networks using various algorithms. 

Encapsulates different community detection algorithms within a single class.
Provides a unified interface for selecting and executing an algorithm on a given network.
Handles algorithm selection, parameter passing, and result retrieval.

Class Attributes:
- algorithm: Stores the currently selected algorithm name (e.g., k_cliques).
- methods: A dictionary mapping algorithm names to their corresponding function objects (e.g., k_clique_communities).

Methods:
- __init__(self, algorithm):
    - Initializes the CommunityDetector object with a specified algorithm name.
    - Populates the methods dictionary with key-value pairs linking algorithm names to their respective function objects.
    - This method essentially allows choosing the desired community detection approach during object creation.
- perform(self, network, params):
    - Takes a network representation (network) and optional parameters (params) as input.
    - Retrieves the function object associated with the current algorithm from the methods dictionary.
    - Executes the retrieved function with the provided network and params.
    - Returns the result of the community detection algorithm (e.g., a dictionary containing detected communities and membership information).

The class offers flexibility by allowing different algorithms to be added or replaced by modifying the methods dictionary.
The perform method acts as a single entry point for executing any available community detection algorithm.
This design promotes code organization, reusability, and potential extensibility for incorporating new algorithms.
'''