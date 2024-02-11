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
import json

import networkx as nx
import numpy as np

from networkx.readwrite import json_graph

tokens = os.path.abspath(__file__).split('/')
path2root = '/'.join(tokens[:-2])
if path2root not in sys.path:
    sys.path.append(path2root)

print('converters: path2root = ', path2root)

if path2root not in sys.path:
    sys.path.append(path2root)

from storage import helpers

fp_input = 'datasets/preprocessed/israel_lea_inp_burglary_offender_id_network.json'
fn = fp_input.replace('.json', '')

with open(fp_input) as json_file:
    json_data = json.load(json_file)

input_graph = json_graph.node_link_graph(json_data)
print(nx.info(input_graph))


fp_output = fn + '_old_format.json'
fp = open(fp_output, 'w')

for node_id, node_data in input_graph.nodes(data=True):
    node = {
        'type': 'node',
        'id': node_id,
        'properties': node_data
    }
    node = json.dumps(node)
    fp.write('%s\n' % node)

for source_id, target_id, edge_data in input_graph.edges(data=True):
    edge = {
        'type': 'edge',
        'source': source_id,
        'target': target_id,
        'properties': edge_data
    }
    edge = json.dumps(edge)
    fp.write('%s\n' % edge)

fp.close()
'''
Converts a network stored in a JSON file to an older JSON format, likely for compatibility with specific tools or systems.

Steps:
- Import libraries:
    - os for path manipulation
    - sys for modifying the system path
    - json for working with JSON data
    - networkx for network analysis
    - numpy (not directly used in this code)
    - json_graph for reading and writing network data in JSON format
- Set up path:
    - Determines the root directory of the project using os.path.abspath(__file__) and tokens[:-2].
    - Appends this path to sys.path if not already present, ensuring modules can be imported correctly.
- Import helpers:
    - Imports functions from a helpers module within a storage package (likely for additional utilities).
- Load input network:
    - Specifies the path to the input JSON file: fp_input.
    - Extracts the filename without the extension: fn.
    - Opens the file and loads the JSON data using json.load.
    - Creates a NetworkX graph object from the JSON data using json_graph.node_link_graph.
    - Prints basic information about the graph using nx.info.
- Save as old format:
    - Creates a file path for the output JSON file: fp_output.
    - Opens the output file in write mode.
    - Iterates through each node in the input graph:
        - Creates a dictionary with node type, ID, and properties.
        - Converts the dictionary to a JSON string using json.dumps.
        - Writes the JSON string to the output file.
    - Iterates through each edge in the input graph:
        - Creates a dictionary with edge type, source, target, and properties.
        - Converts it to JSON and writes it to the output file.
    - Closes the output file.

Uses json_graph to handle network data in JSON format.
Relies on functions from a helpers module (not provided).
Assumes specific JSON structures for both input and output formats.
'''