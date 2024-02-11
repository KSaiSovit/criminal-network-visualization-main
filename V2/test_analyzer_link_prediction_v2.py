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
path_root_dir = os.path.join(os.path.dirname(__file__), os.path.pardir)
if path_root_dir not in sys.path:
    sys.path.append(path_root_dir)

from storage.toy_datasets.toy_data_manager import ToyDataManager
from analyzer.request_taker import InMemoryAnalyzer


def test_link_prediction():
    data_manager = ToyDataManager(connector=None, params=None)
    network = data_manager.get_network(network='moreno_crime')

    test_network = {"edges": network.get('edges')[:1000], "nodes": network.get('nodes')[:1000]}

    # define task for testing
    task_id = "link_prediction"
    task_options = {
        # "method": "resource_allocation_index",
        "method": "jaccard_coefficient",
        # "method": "adamic_adar_index",
        # "method": "preferential_attachment",
        # "method": "count_number_soundarajan_hopcroft",
        # "method": "resource_allocation_index_soundarajan_hopcroft",
        # "method": "within_inter_cluster",
        "parameters": {
            # "community_detection_method": 'modularity',
            # "community_detection_method": 'asyn_lpa',
            # "community_detection_method": 'label_propagation',
            "sources": ['crime_466', 'crime_451', 'crime_258'],
            "top_k": 5
        }
    }

    task = {"task_id": task_id,
            "network": test_network,
            "options": task_options}

    # call analyzer
    analyzer = InMemoryAnalyzer()
    result = analyzer.perform_analysis(task=task, params=None)
    print('result = ', result)


if __name__ == '__main__':
    test_link_prediction()
'''
Performs link prediction on a specific network dataset and prints the results.
Demonstrates the usage of data managers and an analyzer component within a larger system.

Steps:
- Import libraries:
    - os for path manipulation
    - sys for modifying the system path
    - ToyDataManager for managing toy network datasets
    - InMemoryAnalyzer for performing network analysis tasks
- Set up path:
    - Determines the root directory of the project (similar to previous codes).
    - Appends it to sys.path if needed for module imports.
- Define test_link_prediction function:
    - Loads a toy network:
        - Creates a ToyDataManager instance.
        - Loads the 'moreno_crime' network from the toy datasets.
        - Extracts the first 1000 nodes and edges for testing.
    - Creates a task for link prediction:
        - Specifies the task ID as 'link_prediction'.
        - Sets the method to 'jaccard_coefficient' (other methods are commented out).
    - Provides parameters:
        - sources: A list of node IDs to predict potential links for.
        - top_k: The number of top-ranked potential links to return for each source node.
    - Calls the analyzer:
        - Creates an InMemoryAnalyzer instance.
        - Performs the analysis with the defined task and network.
        - Prints the raw analysis results.
- Main execution:
    - Calls the test_link_prediction function if the script is run directly.
'''
