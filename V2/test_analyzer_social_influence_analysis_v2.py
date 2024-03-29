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

from storage.builtin_datasets import BuiltinDatasetsManager
from analyzer.request_taker import InMemoryAnalyzer


def test_social_influence_analysis():
    connector = None  # no connection needed for this file-base datasets
    params = None  # no parameter defined for now

    data_manager = BuiltinDatasetsManager(connector, params)

    # adding builtin/existing datasets
    data_manager.add_dataset('bbc_islam_groups', 'BBC Islam Groups',
                             '%s/datasets/preprocessed/bbc_islam_groups.json' % path2root)
    data_manager.add_dataset('911_hijackers', '911 Hijackers',
                             '%s/datasets/preprocessed/911_hijackers.json' % path2root)
    data_manager.add_dataset('enron', 'Enron Email Network',
                             '%s/datasets/preprocessed/enron.json' % path2root)
    data_manager.add_dataset('moreno_crime', 'Moreno Crime Network',
                             '%s/datasets/preprocessed/moreno_crime.json' % path2root)

    data_manager.add_dataset('imdb', 'IMDB',
                             '%s/datasets/preprocessed/imdb.json' % path2root)

    network = data_manager.get_network('911_hijackers')
    # define task for testing
    task_id = "social_influence_analysis"
    task_options = {
        # "method": "pagerank",
        # "method": "authority",
        # "method": "betweenness",
        # "method": "closeness_centrality",
        "method": "katz_centrality",
        "parameters": {}
    }

    task = {"task_id": task_id,
            "network": network,
            "options": task_options}

    # call analyzer
    analyzer = InMemoryAnalyzer()
    result = analyzer.perform_analysis(task=task, params=None)
    print('result = ', result)


if __name__ == '__main__':
    test_social_influence_analysis()
'''
Steps:
- Import Libraries: (Not explicitly shown, but assumed)
    - Relevant libraries for data management, network analysis, and path manipulation.
- Set Up Data Manager:
    - Creates a BuiltinDatasetsManager instance.
    - Adds several built-in datasets from JSON files using their paths.
- Load Network:
    - Loads the '911_hijackers' network from the data manager.
- Define Analysis Task:
    - Specifies the task ID as 'social_influence_analysis'.
    - Sets the method to 'katz_centrality' (other methods are commented out).
    - Uses an empty dictionary for parameters (may vary depending on the method).
    - Creates a task dictionary with network and options.
- Perform Analysis:
    - Creates an InMemoryAnalyzer instance.
    - Calls the perform_analysis method with the defined task.
    - Prints the analysis result.
- Main Execution:
    - Calls the test_social_influence_analysis function if the script is run directly.
'''
