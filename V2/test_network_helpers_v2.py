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
import pytest
from conductor.src.helpers.network_helpers import network_to_split, split_to_network


def test_network_to_split_should_return_nodes_and_edges_dictionaries():
    """ network_to_split should return dictionary with nodes and edges keys """
    example_network = [
        {"type": "node", "id": "Satam_Suqami", "properties": {"type": "person", "name": "Satam Suqami", "flight": "AA #11 WTC North", "attend_Las_Vegas_Meeting": False}},
        {"type": "node", "id": "Wail_Alshehri", "properties": {"type": "person", "name": "Wail Alshehri", "flight": "AA #11 WTC North", "attend_Las_Vegas_Meeting": False}},
        {"type": "edge", "source": "Majed_Moqed", "target": "Khalid_Al-Mihdhar", "properties": {"type": "prior_contact", "observed": True, "weight": 1}},
        {"type": "edge", "source": "Majed_Moqed", "target": "Nawaf_Alhazmi", "properties": {"type": "prior_contact", "observed": True, "weight": 1}}
    ]
    result = network_to_split(example_network)
    assert example_network[0] in result["nodes"] and example_network[1] in result["nodes"]
    assert example_network[2] in result["edges"] and example_network[3] in result["edges"]

def test_split_to_network_should_return_list_of_nodes_and_edges_combined():
    """ split_to_network should combine edges and nodes """
    example_split = {
        "edges": [
            {"source": "Majed_Moqed", "target": "Khalid_Al-Mihdhar", "properties": {"type": "prior_contact", "observed": True, "weight": 1}},
            {"source": "Majed_Moqed", "target": "Nawaf_Alhazmi", "properties": {"type": "prior_contact", "observed": True, "weight": 1}}
        ],
        "nodes": [
            {"id": "Satam_Suqami", "properties": {"type": "person", "name": "Satam Suqami", "flight": "AA #11 WTC North", "attend_Las_Vegas_Meeting": False}},
            {"id": "Wail_Alshehri", "properties": {"type": "person", "name": "Wail Alshehri", "flight": "AA #11 WTC North", "attend_Las_Vegas_Meeting": False}}
        ]
    }
    result = split_to_network(example_split["nodes"], example_split["edges"])
    assert all(el in result for el in example_split["edges"] + example_split["nodes"])

'''
These test functions verify the functionalities of two helper functions, network_to_split and split_to_network, likely used in a network analysis context:

1. test_network_to_split_should_return_nodes_and_edges_dictionaries():
    - Ensures network_to_split correctly separates nodes and edges from a given network and returns them as separate dictionaries within a single dictionary.
    - Test Case:
        - Defines an example network with nodes and edges.
        - Calls network_to_split with the network.
        - Asserts that both the first and second nodes from the original network are present in the returned dictionary's "nodes" section.
        - Similarly, asserts that both the first and second edges are present in the "edges" section.
2. test_split_to_network_should_return_list_of_nodes_and_edges_combined():
    - Verifies that split_to_network combines separate dictionaries of nodes and edges into a single list representation of the network.
    - Test Case:
        - Defines an example dictionary with separate "nodes" and "edges" lists.
        - Calls split_to_network with the nodes and edges.
        - Asserts that all elements from both the original "nodes" and "edges" lists are present in the returned list (representing the combined network).
'''
