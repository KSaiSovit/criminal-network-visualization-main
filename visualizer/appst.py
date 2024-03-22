import streamlit as st
import os
import sys
import json

# APPEND PATH TO ROOT TO ENSURE INTERNAL IMPORTS
tokens = os.path.abspath(__file__).split('/')
path2root = '/'.join(tokens[:-2])
if path2root not in sys.path:
    sys.path.append(path2root)

from visualizer.dash_style import Style
from storage.builtin_datasets import ActiveNetwork, BuiltinDatasetsManager
from visualizer import dash_formatter, io_utils

# GET LOCATION FOR PATH FINDING
LOCATION = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# INTERNAL DATASETS
DATASETS = [
    # ... (keep the existing dataset definitions)
]

# EXTERNAL DATASETS
EXTERNAL_DATASETS = []

# LOAD EXTERNAL DATASET
data_path = st.sidebar.text_input("Enter data folder path (optional)")
if data_path:
    EXTERNAL_DATASETS = io_utils.get_external_data(data_path)

# DATA INFO USED FOR NETWORK SELECTION DROPDOWN
DATA_INFO = {d['id']: {'path': d['path'], 'name': d['name']} for d in DATASETS + EXTERNAL_DATASETS}

# ADD DATASETS TO DATASET MANAGER
builtin_datasets = BuiltinDatasetsManager(connector=None, params=None)
for ds in DATASETS:
    builtin_datasets.add_dataset(ds['id'], ds['name'], ds['path'])
for ds in EXTERNAL_DATASETS:
    builtin_datasets.add_dataset(ds['id'], ds['name'], ds['path'])

# LAYOUT USED FOR CYTOSCAPE VISUALIZATION
ACTIVE_LAYOUT = {
    'name': 'cose-bilkent',
    'randomize': 'false',
    'refresh': 3,
    'maxSimulationTime': 5000,
}

# DISABLED ANALYSIS METHODS
DISABLED_ANALYSIS_METHODS = ['authority', 'count_number_soundarajan_hopcroft',
                             'resource_allocation_index_soundarajan_hopcroft',
                             'within_inter_cluster']

# INITIALIZE STYLE
style = Style(file=os.path.join(LOCATION, 'assets/cyto_style.json'))

# GLOBAL VARIABLES
network_properties = {}
labels = []
active_network = None

def main():
    st.title("Network Visualizer")

    # NETWORK SELECTION
    selected_network = st.sidebar.selectbox("Select a network", list(DATA_INFO.keys()), key="network_selection")
    if selected_network:
        active_network = ActiveNetwork(path=DATA_INFO[selected_network]['path'], layout=ACTIVE_LAYOUT)

    if active_network and active_network.elements:
        # DISPLAY NETWORK VISUALIZATION
        st.subheader(f"Visualizing: {DATA_INFO[selected_network]['name']}")
        # TODO: Implement network visualization using Streamlit components

        # ADVANCED SEARCH
        if st.button("Advanced Search"):
            nodes = builtin_datasets.search_nodes(node_ids=None, network=selected_network)['found']
            network_properties = {}
            for node in nodes:
                for key in node['properties']:
                    if key not in network_properties:
                        network_properties[key] = set()
                    network_properties[key].add(node['properties'][key])
            property_options = dash_formatter.dash_type_options([*network_properties])
            # TODO: Implement advanced search functionality using Streamlit components

        # EDGE PROBABILITY SLIDER
        edge_prob_value = st.slider("Edge Probability Threshold", 0.0, 1.0, 0.5, 0.01, key="edge_prob_slider")
        if edge_prob_value:
            style.set_edge_prob(edge_prob_value)
            # TODO: Update network visualization with the new edge probability threshold

    else:
        st.warning("Please select a network to visualize.")

if __name__ == "__main__":
    main()