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
from copy import deepcopy
import sys, scipy.special, json, re
import numpy as np


def is_valid_node(node_properties, params):
    """
    check if a node with node_properties satisfy the selection criteria
    :param node_properties: dictionary containing information about the node
    :param params: dictionary containing information about the selection criteria
    :return:
    """
    # TODO: to be refactored
    if params is None:
        return True
    else:
        for p in params:
            if p not in node_properties:
                return False
            value = params[p]
            if node_properties[p] != value:
                return False
        return True
'''
Determines if a given node adheres to specific selection requirements.

Parameters:
- node_properties: A dictionary containing key-value pairs describing the node's attributes.
- params: An optional dictionary specifying the selection criteria, also as key-value pairs.

Logic:
- Handle empty parameter case:
    - If params is None (no criteria provided), the function considers the node valid and returns True.
- Check for missing properties:
    - Iterates through each key-value pair in params.
    - If a key in params is not present in node_properties, the node is considered invalid and False is returned.
- Verify property values:
    - For each matching key in both dictionaries, the function compares the corresponding values.
    - If any value in node_properties doesn't match the corresponding value in params, the node is considered invalid and False is returned.
- Valid node:
    - If all checks pass, the node satisfies the criteria and the function returns True.
'''


def is_valid_edge(edge_properties, params):
    """
    check if a node with node_properties satisfy the selection criteria
    :param edge_properties: dictionary containing information about the node
    :param params: dictionary containing information about the selection criteria
    :return:
    """
    # TODO: to be refactored
    if params is None:
        return True
    else:
        for p in params:
            if p not in edge_properties:
                return False
            value = params[p]
            if edge_properties[p] != value:
                return False
        return True
'''
Determines if a given edge adheres to specific selection criteria based on its properties and provided parameters.

Parameters:
- edge_properties: A dictionary containing key-value pairs describing the edge's attributes.
- params: An optional dictionary specifying the selection criteria, also as key-value pairs.

Logic:
- This function is almost identical to is_valid_node, with the only difference being the first line's comment:
    - is_valid_node: "check if a node with node_properties satisfy the selection criteria"
    - is_valid_edge: "check if a node with node_properties satisfy the selection criteria" (should likely be "edge" instead of "node")
- Therefore, the remaining logic and explanation provided for is_valid_node directly apply to is_valid_edge as well.
'''


def min_max_scaling(value, min_value, max_value, value_range=(0, 1)):
    """
    Normalize a value using min-max feature scaling in a given range.
    :param value: A number to map to the given range.
    :param min_value: Minimum of numbers in domain.
    :param max_value: Maximum of numbers in domain.
    :param value_range: Tuple defining the new range of values.
    :return:
    """
    return value_range[0] + (((value - min_value) * (value_range[1] - value_range[0])) / (max_value - min_value))
'''
Performs min-max scaling (also known as normalization) on a given value.
Rescales a value within a specific domain (defined by min_value and max_value) to a new range (defaulting to 0 to 1).
Used to standardize features for machine learning or other numerical analyses.

Parameters:
- value: The numerical value to be normalized.
- min_value: The minimum value in the original domain.
- max_value: The maximum value in the original domain.
- value_range (optional): A tuple specifying the desired new range (default: (0, 1)).

Steps:
- Calculates the normalized value:
    - Subtracts min_value from value to shift the value to start at 0.
    - Scales the shifted value proportionally to fit within the new range using the formula: ((value - min_value) * (value_range[1] - value_range[0])) / (max_value - min_value)
    - Adds value_range[0] to the scaled value to position it within the desired range.
- Returns the normalized value:
    - The function returns the transformed value, now mapped to the specified range.

Preserves the relative order of values within the original domain.
Ensures all values fall within the specified range, often beneficial for numerical algorithms.
Can be used to compare features with different scales or units.
'''


def compare_edge_type(properties1, properties2):
    print('properties1 = ', properties1)
    print('properties2 = ', properties2)
    if properties1 is None:
        properties1 = dict()
    if properties2 is None:
        properties2 = dict()
    if 'type' not in properties1:
        if 'type' not in properties2:
            return True
        else:
            return False
    else:
        if 'type' not in properties2:
            return False
        else:
            if properties1['type'] == properties2['type']:
                return True
            return False
'''
Determines if the edges represented by two dictionaries have the same type.

Parameters:
- properties1: A dictionary containing properties of the first edge.
- properties2: A dictionary containing properties of the second edge.

Output:
- Returns True if both edges have the same type (or neither has a type key), False otherwise.

Steps:
- Handle missing properties dictionaries:
    - If properties1 is None, an empty dictionary is assigned to it.
    - Similarly, if properties2 is None, an empty dictionary is assigned.
- Check for missing type key:
    - If the type key is absent in both dictionaries, they are considered the same type and True is returned.
    - If the type key is missing in only one dictionary, they are considered different types and False is returned.
- Compare edge types:
    - If both dictionaries have the type key, their values are compared.
    - If the types are equal, True is returned, indicating the edges are the same type.
    - Otherwise, False is returned.
'''


def old_network_to_new_network(nodes, edges):
    """
    Translate old network object format to new
    :param nodes: List of network nodes
    :param edges: List of network edges
    :returns: dict with new nodes and links
    """
    updated_nodes = deepcopy(nodes)
    updated_edges = deepcopy(edges)
    for n in updated_nodes:
        for p in n["properties"]:
            n[p] = n["properties"][p]
        del n["properties"]
    for e in updated_edges:
        for p in e["properties"]:
            e[p] = e["properties"][p]
        del e["properties"]
    return {
        "nodes": updated_nodes,
        "links": updated_edges
    }
'''
Converts a network representation from an old format, likely with separate "nodes" and "edges" lists, to a new format using a dictionary with "nodes" and "links" keys.
Simplifies the network structure by removing nested "properties" dictionaries within nodes and edges.

Parameters:
- nodes: A list containing dictionaries representing individual nodes in the old format.
- edges: A list containing dictionaries representing connections (edges) between nodes in the old format.

Output:
- A dictionary with two keys:
    - nodes: A list of dictionaries representing nodes in the new format, with their "properties" directly incorporated into the main dictionary.
    - links: A list of dictionaries representing connections (edges) in the new format, with their "properties" directly incorporated into the main dictionary.

Steps:
- Create copies of input data:
    - Uses deepcopy to create deep copies of the nodes and edges lists to avoid modifying the original input.
    - These copies are stored in updated_nodes and updated_edges variables.
- Transform individual nodes:
    - Iterates through each node in updated_nodes:
        - Iterates through each key-value pair in the "properties" dictionary of the node.
        - Adds the "property" key directly to the node dictionary with its corresponding value.
        - Deletes the nested "properties" dictionary, resulting in a flatter structure.
- Transform individual edges:
    - Similar to nodes, iterates through each edge in updated_edges and its "properties" dictionary.
    - Adds "property" keys directly to the edge dictionary and removes the nested dictionary.
- Return the new network:
    - Creates a dictionary with "nodes" and "links" keys.
    - Assigns the transformed updated_nodes and updated_edges lists to the respective keys.
    - Returns this dictionary representing the network in the new format.
'''
