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

# find path to root directory of the project so as to import from other packages
# print('current script: visualizer/test_imdb_toy_dataset.py')
# print('os.path.abspath(__file__) = ', os.path.abspath(__file__))
tokens = os.path.abspath(__file__).split('/')
# print('tokens = ', tokens)
path2root = '/'.join(tokens[:-2])
# print('path2root = ', path2root)
if path2root not in sys.path:
    sys.path.append(path2root)

from storage.toy_datasets.toy_data_manager import ToyDataManager
from storage.builtin_datasets import BuiltinDatasetsManager
from analyzer.request_taker import InMemoryAnalyzer


def test_node_embedding():
    # data_manager = ToyDataManager(connector=None, params=None)
    connector = None  # no connection needed for this file-base datasets
    params = None  # no parameter defined for now
    data_manager = BuiltinDatasetsManager(connector, params)

    data_manager.add_dataset('montreal_gangs', 'Montreal Street Gangs',
                             '%s/datasets/preprocessed/montreal_gangs.json' % path2root)
    data_manager.add_dataset('noordintop', 'Noordin Top',
                             '%s/datasets/preprocessed/noordintop.json' % path2root)
    data_manager.add_dataset('rhodes_bombing', 'Rhodes Bombing',
                             '%s/datasets/preprocessed/rhodes_bombing.json' % path2root)
    data_manager.add_dataset('imdb', 'IMDB',
                             '%s/datasets/preprocessed/imdb.json' % path2root)
    data_manager.add_dataset('moreno_crime', 'Moreno Crime Network',
                             '%s/datasets/preprocessed/moreno_crime.json' % path2root)

    network = data_manager.get_network(network='moreno_crime')

    # define task for testing
    task_id = "node_embedding"
    task_options = {
        # "method": "svd",
        # "method": "nmf",
        # "method": "deepwalk",
        # "method": "node2vec",
        "method": "line",
        # "method": "sine",
        # "method": "role2vec",
        "parameters": {
            "K": 128
        }
    }

    task = {"task_id": task_id,
            "network": network,
            "options": task_options}

    # call analyzer
    analyzer = InMemoryAnalyzer()
    result = analyzer.perform_analysis(task=task, params=None)
    # print('result = ', result)
    print('len of vectors = ', len(result['vectors']))


if __name__ == '__main__':
    test_node_embedding()
'''
Generates node embeddings for a specific network dataset and prints the length of the resulting vectors.
Demonstrates the usage of data managers and an analyzer component within a larger system.

Steps:
- Import libraries:
    - os for path manipulation
    - sys for modifying the system path
    - ToyDataManager for managing toy network datasets (unused here)
    - BuiltinDatasetsManager for managing built-in network datasets
    - InMemoryAnalyzer for performing network analysis tasks
- Set up path:
    - Determines the root directory of the project (similar to previous codes).
    - Appends it to sys.path if needed for module imports.
- Define test_node_embedding function:
    - Creates a data manager:
        - Instantiates a BuiltinDatasetsManager to work with built-in datasets.
        - Adds several built-in datasets from JSON files, specifying their paths.
    - Loads a network:
        - Loads the 'moreno_crime' network from the data manager.
    - Creates a task for node embedding:
        - Specifies the task ID as 'node_embedding'.
        - Sets the method to 'line' (other methods are commented out).
        - Provides a parameter 'K': 128, likely for the dimensionality of the embeddings.
    - Calls the analyzer:
        - Creates an InMemoryAnalyzer instance.
        - Performs the analysis with the defined task and network.
        - Retrieves the 'vectors' from the result, containing the node embeddings.
        - Prints the length of the embeddings list.
- Main execution:
    - Calls the test_node_embedding function if the script is run directly.
'''
