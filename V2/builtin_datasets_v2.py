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
import base64
import sys
import os
import json
import networkx as nx
import io
import random
import copy
import ast
from copy import deepcopy
from pathlib import Path

# find path to root directory of the project so as to import from other packages
# to be refactored
# print('current script: storage/builtin_datasets.py')
# print('os.path.abspath(__file__) = ', os.path.abspath(__file__))
tokens = os.path.abspath(__file__).split('/')
# print('tokens = ', tokens)
path2root = '/'.join(tokens[:-2])
# print('path2root = ', path2root)
if path2root not in sys.path:
    sys.path.append(path2root)

from framework.interfaces import DataManager
from storage import helpers
from analyzer.request_taker import InMemoryAnalyzer
import visualizer.io_utils as converter

node_update_action = 'update_node'
node_add_action = 'add_node'
node_delete_action = 'delete_node'

edge_update_action = 'update_edge'
edge_add_action = 'add_edge'
edge_delete_action = 'delete_edge'

max_num_recent_changes = 20
max_num_recent_interactions = 20


class BuiltinDataset:
    def __init__(self, path_2_data, uploaded=False, from_file=True):
        # dataset info
        self.name = None
        self.nodes = {}
        self.edges = []
        self.adj_list = {}
        self.in_adj_list = {}
        self.node_types = {}
        self.edge_types = {}
        self.recent_changes = []
        self.meta_info = {}
        if from_file:
            if uploaded:
                file = path_2_data
                for line in file.splitlines():
                    line = line.strip()
                    if len(line) == 0:
                        continue
                    if line.startswith('#'):  # ignore the comments
                        continue
                    line_object = json.loads(line)
                    if line_object['type'] == 'node':
                        node = line_object['properties']
                        if 'community' in line_object:
                            node['community'] = line_object['community']
                            node['community_confidence'] = line_object['community_confidence']
                        if 'social_influence_score' in line_object:
                            node['social_influence_score'] = line_object['social_influence_score']
                            node['normalized_social_influence'] = line_object['normalized_social_influence']
                        self.nodes[line_object['id']] = node
                        if 'type' in node:
                            node_type = node['type']
                            if node_type in self.node_types:
                                self.node_types[node_type] += 1
                            else:
                                self.node_types[node_type] = 1

                    elif line_object['type'] == 'edge':
                        edge = {'source': line_object['source'], 'target': line_object['target'],
                                'observed': True, 'properties': line_object['properties']}
                        if 'observed' in line_object:
                            if line_object['observed'] == 'false':
                                edge['observed'] = 'false'
                        self.edges.append(edge)
                        e_index = len(self.edges) - 1
                        source = edge['source']
                        if source in self.adj_list:
                            self.adj_list[source].append(e_index)
                        else:
                            self.adj_list[source] = [e_index]
                        target = edge['target']
                        if target in self.in_adj_list:
                            self.in_adj_list[target].append(e_index)
                        else:
                            self.in_adj_list[target] = [e_index]

                        if 'type' in line_object['properties']:
                            edge_type = line_object['properties']['type']
                            if edge_type in self.edge_types:
                                self.edge_types[edge_type] += 1
                            else:
                                self.edge_types[edge_type] = 1
                    else:
                        continue
            else:
                file = open(path_2_data, 'r')
                decoded = file.read()
                if decoded.startswith("{\n"):
                    in_data = json.loads(decoded)
                    data_list = converter.new_to_old(in_data)
                    try:
                        self.meta_info['directed'] = in_data['directed']
                        self.meta_info['multigraph'] = in_data['multigraph']
                        self.meta_info['graph'] = in_data['graph']
                    except KeyError:
                        print(
                            'Input JOSN must have directed, multigraph and graph fields. See specification for information.')
                else:
                    # a = json.loads(decoded)
                    data_list = [json.loads(line.strip()) for line in decoded.split('\n') if
                                 len(line) != 0 and not line.startswith('#')]

                # print('decoded = ', decoded)
                for line_object in data_list:
                    if line_object['type'] == 'node':
                        node = line_object['properties']
                        node['id'] = line_object['id']
                        self.nodes[line_object['id']] = node
                        if 'type' in node:
                            node_type = node['type']
                            if node_type in self.node_types:
                                self.node_types[node_type] += 1
                            else:
                                self.node_types[node_type] = 1
                    elif line_object['type'] == 'edge':
                        edge = {'source': line_object['source'], 'target': line_object['target'],
                                'observed': True, 'properties': line_object['properties']}
                        self.edges.append(edge)
                        e_index = len(self.edges) - 1
                        source = edge['source']
                        if source in self.adj_list:
                            self.adj_list[source].append(e_index)
                        else:
                            self.adj_list[source] = [e_index]
                        target = edge['target']
                        if target in self.in_adj_list:
                            self.in_adj_list[target].append(e_index)
                        else:
                            self.in_adj_list[target] = [e_index]
                        if 'type' in line_object['properties']:
                            edge_type = line_object['properties']['type']
                            if edge_type in self.edge_types:
                                self.edge_types[edge_type] += 1
                            else:
                                self.edge_types[edge_type] = 1
                    else:
                        continue
                file.close()

        else:
            # create network on-the-fly
            # TODO: supposed to be refactored
            pass

    def _generate_edges_nodes_and_node_ids_for_analyzing(self, network_edges, params):
        nx_nodes = {}
        nx_edges = []
        nx_node_ids = []

        for e in network_edges:
            if e is None:
                continue
            if helpers.is_valid_edge(e, params):
                source = e['source']
                target = e['target']
                if source not in nx_nodes:
                    source_index = len(nx_node_ids)
                    nx_nodes[source] = source_index
                    nx_node_ids.append(source)
                else:
                    source_index = nx_nodes[source]

                if target not in nx_nodes:
                    target_index = len(nx_node_ids)
                    nx_nodes[target] = target_index
                    nx_node_ids.append(target)
                else:
                    target_index = nx_nodes[target]

                nx_edges.append((source_index, target_index))

        return nx_edges, nx_nodes, nx_node_ids

    def get_network(self, node_ids=None, params=None, return_edge_index=False):
        """
        mimic the get_network function of DataManager, i.e., getting ego-network surrounding node_ids
        :param node_ids:
        :param params:
        :return:
        """
        if node_ids is None:
            node_ids = list(self.nodes.keys())
        else:
            if len(list(node_ids)) == 0:
                node_ids = list(self.nodes.keys())
        edges = []
        for u in node_ids:
            if u in self.adj_list:
                edges.extend(self.adj_list[u])
        edges = [e for e in edges if helpers.is_valid_edge(self.edges[e], params)]
        involved_nodes = set([self.edges[e]['target'] for e in edges])
        node_ids = set(node_ids)
        involved_nodes = involved_nodes.union(node_ids)
        for v in involved_nodes:
            if v in self.adj_list:
                if v not in node_ids:
                    edges.extend([e for e in self.adj_list[v] if self.edges[e]['target'] in involved_nodes and
                                  helpers.is_valid_edge(self.edges[e]['target'], params)])
        nodes = [{'id': u, 'properties': self.nodes[u]} for u in involved_nodes if u in self.nodes]
        if not return_edge_index:
            edges = [self.edges[e] for e in edges]
        return {'edges': edges, 'nodes': nodes}

    def get_edges(self, node_ids=None, params=None):
        """
        mimic the get_edges function of DataManager
        :param node_ids:
        :param params:
        :return:
        """

        if node_ids is None:
            node_ids = list(self.nodes.keys())

        nx_edges, nx_nodes, _ = self._generate_edges_nodes_and_node_ids_for_analyzing(self.edges, params)
        nx_graph = nx.DiGraph()
        nx_graph.add_edges_from(nx_edges)

        nx_found_next_edges = []
        nx_not_found_next_edges = []
        for checking_node in node_ids:
            if checking_node in self.adj_list:
                if helpers.is_valid_node(checking_node, params):
                    nx_checking_node_id = nx_nodes.get(checking_node)
                    nx_next_edges = []
                    for edge in nx_graph.edges(nx_checking_node_id):
                        temp_edge = self.edges[nx_edges.index(edge)]
                        nx_next_edges.append(temp_edge)
                    nx_found_next_edges.append({'id': checking_node, 'edges': nx_next_edges})
            else:
                nx_not_found_next_edges.append(checking_node)

        return {'found': nx_found_next_edges, 'not_found': nx_not_found_next_edges}

    def get_neighbors(self, node_ids=None, params=None):
        """
        mimic the get_neighbors function of DataManager
        :param node_ids:
        :param params:
        :return:
        """
        if node_ids is None:
            node_ids = list(self.nodes.keys())

        nx_edges, nx_nodes, nx_node_ids = self._generate_edges_nodes_and_node_ids_for_analyzing(self.edges, params)
        nx_graph = nx.DiGraph()
        nx_graph.add_edges_from(nx_edges)

        nx_found_neighbors = []
        nx_not_found_neighbors = []

        for checking_node in node_ids:
            if checking_node in self.adj_list:
                if helpers.is_valid_node(checking_node, params):
                    nx_checking_node_id = nx_nodes.get(checking_node)
                    nx_neighbors = []
                    for nx_neighbor_node_id in nx_graph.neighbors(nx_checking_node_id):
                        neighbor_node_id = nx_node_ids[nx_neighbor_node_id]
                        temp_nx_edge = (nx_checking_node_id, nx_neighbor_node_id)
                        temp_edge_properties = self.edges[nx_edges.index(temp_nx_edge)].get('properties')

                        neighbor = {'neighbor_id': neighbor_node_id,
                                    'properties': self.nodes[neighbor_node_id],
                                    'edges_properties': temp_edge_properties}
                        nx_neighbors.append(neighbor)
                    nx_found_neighbors.append({'id': checking_node, 'neighbors': nx_neighbors})
            else:
                nx_not_found_neighbors.append(checking_node)

        # for u in node_ids:
        #     if u in self.adj_list:
        #         edges = [e for e in self.adj_list[u] if helpers.is_valid_edge(self.edges[e], params)]             
        #         edges = [e for e in edges if helpers.is_valid_node(self.nodes[self.edges[e]['target']], params)]

        #         if len(edges) > 0:
        #             groups = {}
        #             for e in edges:
        #                 v = self.edges[e]['target']
        #                 if v in groups:
        #                     groups[v].append(e)
        #                 else:
        #                     groups[v] = [e]
        #             neighbors = []
        #             for v in groups:
        #                 v_edges = groups[v]
        #                 v_edges = [self.edges[e]['properties'] for e in v_edges]
        #                 neighbor = {'neighbor_id': v, 'properties': self.nodes[v], 'edges': v_edges}
        #                 neighbors.append(neighbor)
        #             found.append({'id': u, 'neighbors': neighbors})
        #     else:
        #         not_found.append(u)

        return {'found': nx_found_neighbors, 'not_found': nx_not_found_neighbors}

    def search_nodes(self, node_ids=None, params=None):
        """
        mimic the search_nodes function of DataManager
        :param node_ids:
        :param params:
        :return:
        """
        if node_ids is None:
            node_ids = list(self.nodes.keys())
        found = []
        not_found = []
        for u in node_ids:
            if u in self.nodes:
                if helpers.is_valid_node(self.nodes[u], params):
                    found.append({'id': u, 'properties': self.nodes[u]})
            else:
                not_found.append(u)
        return {'found': found, 'not_found': not_found}

    def forget_changes(self):
        if len(self.recent_changes) > max_num_recent_changes:
            self.recent_changes = self.recent_changes[-max_num_recent_changes:]

    def update_a_node(self, node, properties):
        """

        :param node:
        :param properties:
        :return:
        """
        # print('node = ', node, ' properties = ', properties)
        if node not in self.nodes:
            return {'success': 0, 'message': 'node not found!'}
        else:
            node_properties = self.nodes[node]
            pre_properties = copy.deepcopy(node_properties)
            if node_properties is None:
                self.nodes[node] = properties
                if 'type' in properties:
                    node_type = properties['type']
                    if node_type in self.node_types:
                        self.node_types[node_type] += 1
                    else:
                        self.node_types[node_type] = 1
            else:
                type_change = False
                if 'type' in properties:
                    if 'type' in node_properties:
                        if properties['type'] != node_properties['type']:
                            type_change = True
                            node_type = node_properties['type']
                            # print('self.node_types =', self.node_types)
                            self.node_types[node_type] -= 1
                            if self.node_types[node_type] == 0:
                                del self.node_types[node_type]

                node_properties.clear()
                for p, value in properties.items():
                    node_properties[p] = value

                if type_change:
                    node_type = properties['type']
                    if node_type in self.node_types:
                        self.node_types[node_type] += 1
                    else:
                        self.node_types[node_type] = 1
            action = {'action': node_update_action, 'node': node, 'pre_properties': pre_properties}
            self.recent_changes.append(action)
            self.forget_changes()

            print('after update: node = ', node, 'properties = ', self.nodes[node])

            return {'success': 1, 'message': 'node updated successfully!'}

    def add_a_node(self, node, properties=None):
        """

        :param node:
        :param properties:
        :return:
        """
        if node in self.nodes:
            return {'success': 0, 'message': 'node already exists!'}
        else:
            self.nodes[node] = properties
            if 'type' in properties:
                node_type = properties['type']
                if node_type in self.node_types:
                    self.node_types[node_type] += 1
                else:
                    self.node_types[node_type] = 1
            action = {'action': node_add_action, 'node': node, 'properties': copy.deepcopy(properties)}
            self.recent_changes.append(action)
            self.forget_changes()
            return {'success': 1, 'message': 'node added successfully!'}

    def find_edge_index(self, source, target):
        """

        :param source:
        :param target:
        :return:
        """
        if source not in self.nodes:
            return -1
        if target not in self.nodes:
            return -1
        if source not in self.adj_list:
            return -1
        if target not in self.in_adj_list:
            return -1
        out_edges = self.adj_list[source]
        in_edges = self.in_adj_list[target]
        if len(out_edges) < len(in_edges):
            for e_index in out_edges:
                if self.edges[e_index]['target'] == target:
                    return e_index
            return -1
        else:
            for e_index in in_edges:
                if self.edges[e_index]['source'] == source:
                    return e_index
            return -1

    def update_an_edge(self, e_index=None, source=None, target=None, is_index=True, properties=None):
        """

        :param e_index:
        :param source:
        :param target:
        :param is_index:
        :param properties:
        :return:
        """
        if properties is None:
            return {'success': 0, 'message': 'nothing to update!'}
        if is_index:
            if e_index is None:
                return {'success': 0, 'message': 'is_index is True but e_index is None!'}
            edge_properties = self.edges[e_index]['properties']
            pre_properties = copy.deepcopy(edge_properties)
            if edge_properties is None:
                self.edges[e_index]['properties'] = properties
                if 'type' in properties:
                    edge_type = properties['type']
                    if edge_type in self.edge_types:
                        self.edge_types[edge_type] += 1
                    else:
                        self.edge_types[edge_type] = 1
            else:
                type_change = False
                if 'type' in properties:
                    if 'type' in edge_properties:
                        if properties['type'] != edge_properties['type']:
                            type_change = True
                            edge_type = edge_properties['type']
                            self.edge_types[edge_type] -= 1
                            if self.edge_types[edge_type] == 0:
                                del self.edge_types[edge_type]
                edge_properties.clear()
                for p, value in properties.items():
                    edge_properties[p] = value

                if type_change:
                    edge_type = properties['type']
                    if edge_type in self.edge_types:
                        self.edge_types[edge_type] += 1
                    else:
                        self.edge_types[edge_type] = 1
            action = {'action': edge_update_action,
                      'edge': {'e_index': e_index,
                               'source': self.edges[e_index]['source'],
                               'target': self.edges[e_index]['target']},
                      'pre_properties': pre_properties}
            self.recent_changes.append(action)
            self.forget_changes()
            return {'success': 1, 'message': 'edge updated successfully!'}
        else:
            if source is None or target is None:
                return {'success': 0, 'message': 'source or target is None!'}
            e_index = self.find_edge_index(source, target)
            if e_index < 0:
                return {'success': 0, 'message': 'edge not found!'}
            edge_properties = self.edges[e_index]['properties']
            pre_properties = copy.deepcopy(edge_properties)
            if edge_properties is None:
                self.edges[e_index]['properties'] = properties
                if 'type' in properties:
                    edge_type = properties['type']
                    if edge_type in self.edge_types:
                        self.edge_types[edge_type] += 1
                    else:
                        self.edge_types[edge_type] = 1
            else:
                type_change = False
                if 'type' in properties:
                    if 'type' in edge_properties:
                        if properties['type'] != edge_properties['type']:
                            type_change = True
                            edge_type = edge_properties['type']
                            self.edge_types[edge_type] -= 1
                            if self.edge_types[edge_type] == 0:
                                del self.edge_types[edge_type]

                for p, value in properties.items():
                    edge_properties[p] = value

                if type_change:
                    edge_type = properties['type']
                    if edge_type in self.edge_types:
                        self.edge_types[edge_type] += 1
                    else:
                        self.edge_types[edge_type] = 1
            # remember the action
            action = {'action': edge_update_action,
                      'edge': {'e_index': e_index, 'source': source, 'target': target},
                      'pre_properties': pre_properties}
            self.recent_changes.append(action)
            self.forget_changes()
            return {'success': 1, 'message': 'edge updated successfully!'}

    def add_an_edge(self, source, target, properties=None):
        """

        :param source:
        :param target:
        :param properties:
        :return:
        """
        if source not in self.nodes:
            return {'success': 0, 'message': 'source not found!'}
        if target not in self.nodes:
            return {'success': 0, 'message': 'target not found!'}
        e_index = self.find_edge_index(source=source, target=target)
        if e_index >= 0:
            if helpers.compare_edge_type(self.edges[e_index]['properties'], properties):
                return {'success': 0, 'message': 'edge already exists!'}
        e_index = len(self.edges)
        if source in self.adj_list:
            self.adj_list[source].append(e_index)
        else:
            self.adj_list[source] = [e_index]
        if target in self.in_adj_list:
            self.in_adj_list[target].append(e_index)
        else:
            self.in_adj_list[target] = [e_index]
        edge = {'source': source, 'target': target, 'properties': properties}
        self.edges.append(edge)
        if 'type' in properties:
            edge_type = properties['type']
            if edge_type in self.edge_types:
                self.edge_types[edge_type] += 1
            else:
                self.edge_types[edge_type] = 1
        # remember the action
        action = {'action': edge_add_action,
                  'edge': {'e_index': e_index, 'source': source, 'target': target},
                  'properties': copy.deepcopy(properties)}
        self.recent_changes.append(action)
        self.forget_changes()
        return {'success': 1, 'message': 'edge added successfully!'}

    def delete_an_edge(self, e_index=None, source=None, target=None, is_index=True):
        """

        :param e_index:
        :param source:
        :param target:
        :param is_index:
        :return:
        """
        # print('delete_an_edge:', e_index, source, target, is_index)
        if is_index:
            if e_index is None:
                return {'success': 0, 'message': 'is_index is True but e_index is None!'}
            edge = self.edges[e_index]
            properties = copy.deepcopy(self.edges[e_index]['properties'])
            source, target = edge['source'], edge['target']
            # print('deleting e = {} source = {} target = {}'.format(e_index, source, target))
            # remove from adj lists
            # print('source: ', source)
            # print('self.adj_list: ', self.adj_list)
            if source in self.nodes:
                self.adj_list[source].remove(e_index)

            # print('target: ', target)
            # print('self.in_adj_list', self.in_adj_list)
            if target in self.nodes:
                self.in_adj_list[target].remove(e_index)
            # change edge types
            edge_type = edge['properties']['type']
            self.edge_types[edge_type] -= 1
            if self.edge_types[edge_type] == 0:
                del self.edge_types[edge_type]
            # remove the edge
            self.edges[e_index] = None  # TODO ask?????
            # remember the action
            action = {'action': edge_delete_action,
                      'edge': {'e_index': e_index, 'source': source, 'target': target},
                      'properties': properties}
            self.recent_changes.append(action)
            self.forget_changes()
            return {'success': 1, 'message': 'edge deleted successfully!'}
        else:
            if source is None or target is None:
                return {'success': 0, 'message': 'source or target is None!'}
            e_index = self.find_edge_index(source, target)
            if e_index >= 0:
                properties = copy.deepcopy(self.edges[e_index]['properties'])
                # remove from adj lists
                if source in self.nodes:
                    self.adj_list[source].remove(e_index)
                if target in self.nodes:
                    self.in_adj_list[target].remove(e_index)
                # change edge types
                edge_type = self.edges[e_index]['properties']['type']
                self.edge_types[edge_type] -= 1
                if self.edge_types[edge_type] == 0:
                    del self.edge_types[edge_type]
                # remove the edge
                self.edges[e_index] = None
                # remember action
                action = {'action': edge_delete_action,
                          'edge': {'e_index': e_index, 'source': source, 'target': target},
                          'properties': properties}
                self.recent_changes.append(action)
                self.forget_changes()
                return {'success': 1, 'message': 'edge deleted successfully!'}
            else:
                return {'success': 0, 'message': 'edge does not exist!'}

    def delete_edges(self, deleted_edges, is_indexes=True):
        """
        delete a list of edges from a network
        :param deleted_edges:
        :param is_indexes:
        :return: List of errors
        """
        errors = []
        result_temp = None
        if is_indexes:
            for e_index in deleted_edges:
                result_temp = self.delete_an_edge(e_index=e_index, is_index=True)
                if not result_temp["success"]:
                    result_temp["e_index"] = e_index
                    errors.append(result_temp)
        else:
            for edge in deleted_edges:
                source, target = edge
                result_temp = self.delete_an_edge(source=source, target=target, is_index=False)
                if not result_temp["success"]:
                    result_temp["edge"] = edge
                    errors.append(result_temp)
        return errors

    def delete_a_node(self, node):
        """
        delete the node by node id
        :param node:
        :return:
        """
        # print('delete_a_node: ', node)
        if node not in self.nodes:
            return {'success': 0, 'message': 'node not found!'}
        # delete out-going edges
        if node in self.adj_list:
            self.delete_edges(copy.deepcopy(self.adj_list[node]), is_indexes=True)
            del self.adj_list[node]
        # delete in-coming edges
        if node in self.in_adj_list:
            self.delete_edges(copy.deepcopy(self.in_adj_list[node]), is_indexes=True)
            del self.in_adj_list[node]
        # change the types
        if 'type' in self.nodes[node]['type']:
            node_type = self.nodes[node]['type']
            self.node_types[node_type] -= 1
            if self.node_types[node_type] == 0:
                del self.node_types[node_type]
        # remember the action
        properties = copy.deepcopy(self.nodes[node])
        action = {'action': node_delete_action, 'node': node, 'properties': properties}
        self.recent_changes.append(action)
        self.forget_changes()
        # delete the node
        del self.nodes[node]

        return {'success': 1, 'message': 'node deleted successfully!'}

    def delete_nodes(self, nodes):
        """
        delete a list of nodes and their adjacent edges from a network
        :param nodes:
        :return: List of errors
        """
        errors = []
        result_temp = None
        for node in nodes:
            result_temp = self.delete_a_node(node)
            if not result_temp["success"]:
                result_temp["node"] = node
                errors.append(result_temp)
        return errors
        # print('after delete ', node)
        # self.print_dataset()
        # print('*******************')

    def save_nodes(self, nodes, params=None):
        """
        add or update information for a list of nodes in a network
        :param nodes: dictionary of node_id: properties
        :param params:
        :return:
        """
        errors = []
        result_temp = None
        for node, properties in nodes.items():
            if node in self.nodes:
                result_temp = self.update_a_node(node, properties=properties)
            else:
                result_temp = self.add_a_node(node, properties=properties)
            if not result_temp["success"]:
                result_temp["node"] = node
                errors.append(result_temp)
        return errors

    def save_edges(self, edges, params=None):
        """
        create or update information for a list of edges in a network
        :param edges: list of edge object with 'source', 'target' and 'properties' fields
        :param params:
        :return:
        """
        errors = []
        result_temp = None
        for edge in edges:
            source, target, properties = edge['source'], edge['target'], edge['properties']
            e_index = self.find_edge_index(source, target)
            if e_index < 0:
                result_temp = self.add_an_edge(source, target, properties=properties)
            else:
                result_temp = self.update_an_edge(e_index=e_index, is_index=True, properties=properties)
            if not result_temp["success"]:
                result_temp["edge"] = {"source": source, "target": target}
                errors.append(result_temp)
        return errors

    def dump_network(self, network, output_dir, params=None):
        """
        dump the whole network to a specified directory
        will fail if file already exists
        """
        if not params:
            params = {}
        try:
            if not params.get("output_format") == "json":
                raise NotImplementedError()
            if params.get("compressed"):
                raise NotImplementedError()
            output_path = Path(output_dir) / network
            with open(output_path, "x") as output_file:
                for node in self.nodes:
                    temp = {
                        "id": node,
                        "type": "node",
                        "properties": self.nodes[node].copy()
                    }
                    json.dump(temp, output_file)
                    output_file.write("\n")
                for edge in self.edges:  # type weight confidence
                    e_props = edge["properties"]
                    if params.get("edge_types") and not (e_props.get("type") in params["edge_types"]):
                        continue
                    if params.get("min_weight") and e_props.get("weight", 0) < params["min_weight"]:
                        continue
                    if params.get("min_confidence") and e_props.get("confidence", 0) < params["min_confidence"]:
                        continue
                    temp = edge.copy()
                    temp["type"] = "edge"
                    json.dump(temp, output_file)
                    output_file.write("\n")
            return 1
        except Exception:
            return 0

    def get_neighbor_counts(self, nodes):
        neighbor_counts = {}
        if nodes is not None:
            for node in nodes:
                if node in self.adj_list:
                    for e_index in self.adj_list[node]:
                        target = self.edges[e_index]['target']
                        if target in neighbor_counts:
                            neighbor_counts[target] += 1
                        else:
                            neighbor_counts[target] = 1
        return neighbor_counts

    def to_nxgraph(self):
        """
        convert to networkx graph
        :return:
        """
        graph = nx.MultiDiGraph()
        graph.add_nodes_from(list(self.nodes.keys()))
        
        for e in self.edges:
            if e is not None:
                if 'weight' in e['properties']:
                    graph.add_edge(e['source'], e['target'], weight=float(e['properties']['weight']))
                else:
                    graph.add_edge(e['source'], e['target'])

        return graph

    def print_dataset(self):
        print('nodes: ', self.nodes)
        print('edges: ', self.edges)
        # print('adj_list: ', self.adj_list)
        # print('in_adj_list ',self.in_adj_list)
        print('node_types: ', self.node_types)
        print('edge_types: ', self.edge_types)
        print('actions: ', self.recent_changes)
'''
get_network():

Inputs:
- node_ids: list of node IDs to get ego network for
- params: filters on nodes/edges
- return_edge_index: whether to return edge indexes or objects

Outputs:
- dict with subgraphs 'nodes' and 'edges'

Steps:
1. Get edges for input nodes
2. Find nodes involved
3. Extend with 1-hop neighbors
4. Filter
5. Return nodes and edges


update_a_node():

Inputs:
- node: node ID
- properties: dict of properties

Outputs:
- dict with success, message

Steps:
1. Check if node exists
2. Update node properties dict
3. Update node type counts
4. Log change
5. Return success/message


add_an_edge():

Inputs:
- source: source node ID
- target: target node ID
- properties: edge properties dict

Outputs:
- dict with success, message

Steps:
1. Check source and target nodes exist
2. Check edge doesn't already exist
3. Update adjacency lists
4. Add edge object
5. Update edge type counts
6. Log change
7. Return success/message


delete_a_node():

Inputs:
- node: node ID

Outputs:
- dict with success, message

Steps:
1. Check node exists
2. Delete adjacent edges
3. Remove from adjacency lists
4. Update node type counts
5. Log change
6. Delete node
7. Return success/message


save_nodes():

Inputs:
- nodes: dict of node properties by node ID
- params: filters

Outputs:
- list of errors

Steps:
1. Loop over input nodes
2. Call add/update functions
3. Collect any errors
'''


#####################################
active_element_default_values = {
    'label': 'not_defined',
    'type': 'not_defined',
    'selected': False,
    'expandable': False,
    'community': -1,
    'community_confidence': -1,
    'social_influence_score': -1,
    'visualisation_social_influence_score': -1,
    'predicted': False,
    'hidden': False,
    'highlighted': False,
    'num_incoming_neighbor_selected': 0,
    'incoming_neighbor_selected': False,
    'source_selected': False
}
'''
active_element_default_values dictionary:

- Label: not_defined (string)
- Type: not_defined (string)
- Selected: False (boolean)
- Expandable: False (boolean)
- Community: -1 (integer) - No assigned community
- Community Confidence: -1 (float) - No community confidence score
- Social Influence Score: -1 (float) - No social influence score
- Visualization Social Influence Score: -1 (float) - No visualization influence score
- Predicted: False (boolean) - Not predicted
- Hidden: False (boolean) - Not hidden
- Highlighted: False (boolean) - Not highlighted
- Num Incoming Neighbor Selected: 0 (integer) - No selected incoming neighbors
- Incoming Neighbor Selected: False (boolean) - Incoming neighbor not selected
- Source Selected: False (boolean) - Source not selected
'''


####################################


class ActiveNetwork(BuiltinDataset):
    """
    class for managing and manipulating network being processed by the visualizer
    """

    def __init__(self, path_2_data, uploaded=False, from_file=True, selected_nodes=None, initialize=False,
                 params=dict()):
        """

        :param path_2_data: path to data file
        :param uploaded: True if network is to be
        :param from_file: True if to read from local file, i.e., from path_2_data
        :param selected_nodes: list of selected nodes to initilize the active network
        :param initialize: True if to initialize the active network
        :param params: ditionary
        """
        BuiltinDataset.__init__(self, path_2_data, uploaded, from_file)
        self.active_nodes = {}  # dictionary of active nodes:{node_id: {'expandable':True/False,
        # 'element_index': index of
        # the corresponding element in self.elements}}

        self.active_edges = {}  # dictionary of active edge:{edge_index: {
        # 'element_index': index of
        # the corresponding element in self.elements}}

        self.elements = []
        #
        self.network_name = None
        self.node_label_field = None
        self.edge_label_field = None
        #
        self.analyzer = InMemoryAnalyzer()
        self.predicted_edges = {}  # dictionary {source:[]}
        self.active_predicted_edges = {}
        # dictionary of active predicted edge:{edge_index: {
        # 'element_index': index of
        # the corresponding element in self.elements}}

        self.last_analysis = None  # info about last analysis
        if initialize:
            self.initialize(selected_nodes, params)
        self.selected_nodes = set()
        self.selected_edges = set()
        self.recent_interactions = []
    '''
    Initializes an instance of the ActiveNetwork class

    Parameters:

        - path_2_data: (string) Path to the data file containing network information.
        - uploaded: (boolean, optional) Indicates whether the network data was uploaded (default: False).
        - from_file: (boolean, optional) Specifies whether to read data from the provided path (default: True).
        - selected_nodes: (list, optional) An initial list of selected nodes in the network (default: None).
        - initialize: (boolean, optional) Controls whether to perform initialization with selected nodes (default: False).
        - params: (dictionary, optional) Additional parameters for initialization.

    Initialization Steps:

        - Calls parent class constructor:
            - Inherits and initializes attributes from the BuiltinDataset class.
        - Initializes internal data structures:
            - active_nodes: Dictionary to store information about active nodes, including expandability and element index.
            - active_edges: Dictionary to store information about active edges, including element index.
            - elements: List representing the elements (nodes and edges) in the network.
            - network_name: Stores the network's name (if available).
            - node_label_field: Stores the attribute field containing node labels (if applicable).
            - edge_label_field: Stores the attribute field containing edge labels (if applicable).
            - analyzer: Creates an InMemoryAnalyzer instance for performing network analysis.
            - predicted_edges: Dictionary to store predicted edges, grouped by source node.
            - active_predicted_edges: Dictionary to track active predicted edges with element index information.
            - last_analysis: Stores information about the last analysis performed.

    Optional Initialization:
        - If initialize is True, calls the initialize method to set up the active network using the provided selected_nodes and params.

    Sets up other attributes:
        - selected_nodes: Set to store currently selected nodes.
        - selected_edges: Set to store currently selected edges.
        - recent_interactions: List to keep track of recent user interactions with the network.
    '''

    def truncate(self, core_nodes, max_num=5000):
        if len(self.active_nodes) < max_num:
            return
        sampled_nodes = random.sample(list(self.active_nodes.keys()), max_num)
        sampled_nodes = set(sampled_nodes)
        if core_nodes is not None:
            sampled_nodes = sampled_nodes.union(set(core_nodes))

        self.active_nodes = dict([(node, None) for node in sampled_nodes])
        self.active_edges = dict([(e, None) for e in self.active_edges if
                                  self.edges[e]['source'] in self.active_nodes and
                                  self.edges[e]['target'] in self.active_nodes])
    '''
    This function limits the number of active nodes in a network to a predefined maximum, while optionally incorporating specific core nodes into the active set.

    Parameters:
        - core_nodes: (list, optional) A list of core nodes to always keep active, even if exceeding the maximum.
        - max_num: (integer, optional) The maximum number of active nodes to maintain (default: 5000).

    Function Breakdown:
        - Checks if truncation is necessary:
            - If the current number of active nodes is less than or equal to the maximum, the function does nothing and returns.
        - Samples random nodes:
            - If truncation is required, it randomly selects a subset of max_num active node IDs from the existing self.active_nodes dictionary using random.sample.
        - Handles core nodes (optional):
            -If core_nodes is provided, it merges the set of random nodes with the set of core nodes, ensuring that these important nodes remain active.
        - Updates active node and edge data structures:
            - Creates a new dictionary self.active_nodes containing only the selected nodes as keys and None as values (placeholder data).
            - Filters the self.active_edges dictionary to retain only edges whose source and target nodes are both present in the updated self.active_nodes.
    '''

    ############################################
    def initialize(self, selected_nodes=None, params={}):
        # print('in initialize')
        # print('selected_nodes = ', selected_nodes)
        self.active_nodes = {}
        self.active_edges = {}
        self.elements = []
        self.predicted_edges = {}  # dictionary {source:[]}
        self.last_analysis = None  # info about last analysis

        if 'network_name' in params:
            self.network_name = params['network_name']
        else:
            self.network_name = 'sub-network'

        if 'node_label_field' in params:
            self.node_label_field = params['node_label_field']
        else:
            # TODO: to be refactored to remove hard coding
            self.node_label_field = 'name'

        if 'edge_label_field' in params:
            self.edge_label_field = params['edge_label_field']
        else:
            # TODO: to be refactored to remove hard coding
            self.edge_label_field = 'name'

        sub_network = self.get_network(selected_nodes, return_edge_index=True)
        # print(sub_network)
        self.active_edges = dict([(e, None) for e in sub_network['edges']])
        self.active_nodes = dict([(node['id'], None) for node in sub_network['nodes']])
        self.truncate(selected_nodes)
        # added node
        for node in self.active_nodes:
            node_info = self.nodes[node]
            node_info['id'] = node
            # if self.node_label_field is not None:
            #     if self.node_label_field not in node_info:
            #         node_info[self.node_label_field] = active_element_default_values[self.node_label_field]
            # else:
            #     node_info['id'] = node
            node_data = {'element_type': 'node',
                         'id': node,
                         'type': node_info['type'],
                         'label': active_element_default_values['label'],
                         'selected': active_element_default_values['selected'],
                         'expandable': active_element_default_values['expandable'],
                         'community': active_element_default_values['community'],
                         'community_confidence': active_element_default_values['community_confidence'],
                         'social_influence_score': active_element_default_values['social_influence_score'],
                         'visualisation_social_influence_score':
                             active_element_default_values['visualisation_social_influence_score'],
                         'hidden': active_element_default_values['hidden'],
                         'highlighted': active_element_default_values['highlighted'],
                         'num_incoming_neighbor_selected': active_element_default_values[
                             'num_incoming_neighbor_selected'],
                         'incoming_neighbor_selected': active_element_default_values['incoming_neighbor_selected'],
                         'info': node_info}
            # add node label
            if self.node_label_field is not None:
                if self.node_label_field in node_info:
                    node_data['label'] = node_info[self.node_label_field]
                else:
                    node_data['label'] = node_data['id']
            else:
                node_data['label'] = node_data['id']
            # check expandability
            expandable = False
            if node in self.adj_list:
                for e_index in self.adj_list[node]:
                    if e_index not in self.active_edges:
                        expandable = True
                        break
            node_data['expandable'] = expandable

            element = {'group': 'nodes', 'data': node_data}

            self.elements.append(element)
            self.active_nodes[node] = {'expandable': expandable, 'element_index': len(self.elements) - 1}

        if 'weight' in self.edges[0]['properties']:
            min_weight = float('inf')
            max_weight = 0
            for edge in self.edges:
                if 'weight' in edge['properties']:
                    if edge['properties']['weight'] < min_weight:
                        min_weight = edge['properties']['weight']
                    elif edge['properties']['weight'] > max_weight:
                        max_weight = edge['properties']['weight']

        for e_index in self.active_edges:
            edge_info = self.edges[e_index]
            edge_data = {'element_type': 'edge',
                         'id': e_index,
                         'source': edge_info['source'],
                         'target': edge_info['target'],
                         'type': active_element_default_values['type'],
                         'label': active_element_default_values['label'],
                         'selected': active_element_default_values['selected'],
                         'predicted': active_element_default_values['predicted'],
                         'hidden': active_element_default_values['hidden'],
                         'highlighted': active_element_default_values['highlighted'],
                         'source_selected': active_element_default_values['source_selected'],
                         'info': edge_info['properties']}
            # add type
            if 'type' in edge_info['properties']:
                edge_data['type'] = edge_info['properties']['type']
            if 'probability' in edge_info['properties']:
                edge_data['probability'] = edge_info['properties']['probability']
            if 'weight' in edge_info['properties'] and max_weight > min_weight:
                edge_data['normalized_weight'] = (edge_info['properties']['weight'] - min_weight) / (max_weight - min_weight)
            # add edge label
            if self.edge_label_field is not None:
                if self.edge_label_field in edge_info:
                    edge_data['label'] = edge_info[self.edge_label_field]
            else:
                edge_data['label'] = ''  # blank label

            element = {'group': 'edges', 'data': edge_data}
            self.elements.append(element)
            self.active_edges[e_index] = {'element_index': len(self.elements) - 1}

    '''
    This funtion
    Initializes the active network by setting up relevant data structures and populating them with information about nodes, edges, and their attributes.
    Optionally incorporates user-specified selected_nodes and parameters (params) to customize the starting configuration.

    Parameters:
    - selected_nodes: (list, optional) A list of node IDs to initially make active (default: None).
    - params: (dictionary, optional) Parameters for customization (e.g., network_name, node_label_field, edge_label_field).

    Function Workflow:

    - Initialization:
        - Clears existing active nodes, edges, and elements.
        - Sets up dictionaries for predicted_edges and last_analysis.
    - Parameter Handling:
        - Extracts optional parameters like network_name, node_label_field, and edge_label_field from params or uses defaults.
    - Subnetwork Retrieval:
        - Calls get_network (assumed to be implemented elsewhere) to fetch a subnetwork based on selected_nodes and retrieves edge indices as well.
        - Populates active_edges and active_nodes dictionaries with subnetwork information.
    - Truncation (if applicable):
        - Calls truncate (assumed to be implemented elsewhere) to potentially limit the number of active nodes, ensuring important core_nodes (if provided) are included.
    - Node Processing:
        - Iterates through active nodes:
            - Fetches node information from the overall network data (nodes).
            - Assigns default values for missing node attributes using active_element_default_values.
            - Constructs a node data dictionary with element type, ID, type, label, selection status, expandability, community information, social influence scores, and hidden/highlighted flags.
            - Incorporates node label (if applicable) using the specified node_label_field.
            - Sets expandability based on the presence of unexpanded neighbors in the active network.
            - Creates a node element dictionary and adds it to the elements list.
            - Updates the active_nodes dictionary with expandability and element index information.
    - Edge Processing:
        - Iterates through active edges:
            - Retrieves edge information from the overall network data (edges).
            - Constructs an edge data dictionary with element type, ID, source, target, type, label, selection status, predicted status, hidden/highlighted flags, source selection status, and edge properties.
            - Includes edge type (if applicable) from edge properties.
            - Incorporates edge label (if applicable) using the specified edge_label_field.
            - Normalizes edge weight (if applicable) based on minimum and maximum values for visual consistency.
            - Creates an edge element dictionary and adds it to the elements list.
            - Updates the active_edges dictionary with element index information.
    '''

    def get_active_node_types(self):
        """
        get types of active nodes
        :return: list of type, each type is a string
        """
        types = set()
        for _, node_info in self.active_nodes.items():
            types.add(self.elements[node_info['element_index']]['data']['type'])
        return list(types)
    '''
    This function retrieves the distinct types of active nodes present in the active network.

    Parameters:
    - self: An instance of the class containing the function (likely the ActiveNetwork class).

    Return Value:
    - A list of strings, where each string represents a unique type found among the active nodes.

    Function Breakdown:

    - Initialize an empty set:
        - Creates an empty set called types to store the unique node types.
    - Iterate through active nodes:
        - Loops through each key-value pair in the active_nodes dictionary.
            - The key represents the node ID, and the value represents a dictionary containing node information.
    - Extract node type:
        - Within the loop, accesses the element_index value from the node_info dictionary.
        - Uses this index to retrieve the corresponding element dictionary from the elements list.
        - Extracts the type value from the data dictionary within the element.
    - Add type to set:
        - Adds the extracted type string to the types set.
        - Using a set ensures that only unique types are added.
    - Convert set to list:
        - Converts the types set to a list using list(types).
        - This returns the final list of distinct node types.
    '''

    def get_active_edge_types(self):
        """
        get types of active edges
        :return: list of type, each type is a string
        """
        types = set()
        for _, edge_info in self.active_edges.items():
            types.add(self.elements[edge_info['element_index']]['data']['type'])
        if len(self.predicted_edges) > 0:
            types.add('predicted')
        return list(types)
    '''
    This function retrieves the distinct types of active edges present in the active network, including predicted edges.

    Parameters:
    - self: An instance of the class containing the function (likely the ActiveNetwork class).

    Return Value:
    - A list of strings, where each string represents a unique type found among the active edges.

    Function Breakdown:
    
    - Initialize an empty set:
        - Creates an empty set called types to store the unique edge types.
    - Iterate through active edges:
        - Loops through each key-value pair in the active_edges dictionary.
            - The key represents the edge ID, and the value represents a dictionary containing edge information.
        - Extracts the element_index value from the edge_info dictionary.
        - Uses this index to retrieve the corresponding element dictionary from the elements list.
        - Extracts the type value from the data dictionary within the element.
        - Adds the extracted type string to the types set.
    - Check for predicted edges:
        - If the predicted_edges dictionary is not empty, indicating the presence of predicted edges, adds the string 'predicted' to the types set.
    - Convert set to list:
        - Converts the types set to a list using list(types).
        - This returns the final list of distinct edge types, including 'predicted' if applicable.
    '''

    def get_active_element_types(self, element=None):
        """
        get types of active nodes or active edges
        :param element:
        :return:
        """
        if element is None:
            return {'node': self.get_active_node_types(), 'edge': self.get_active_edge_types()}
        elif element == 'node':
            return self.get_active_node_types()
        elif element == 'edge':
            return self.get_active_edge_types()
        else:
            return None
    '''
    This function retrieves the distinct types of active elements (nodes or edges) present in the active network, optionally allowing specification of a particular element type.

    Parameters:
    - self: Instance of the class containing the function (likely the ActiveNetwork class).
    - element (optional): String specifying the element type to consider ('node', 'edge', or None).
        - If None (default), returns types for both nodes and edges.

    Return Value:
    - If element is None:
        - Returns a dictionary with keys 'node' and 'edge', where each value is a list of unique types for the respective element type.
    - If element is 'node' or 'edge':
        - Returns a list of unique types for the specified element type.
    - If element is invalid:
        - Returns None.

    Steps:

    - Handle No Element Type Specified:
        - If element is None, directly call the appropriate internal functions:
            - self.get_active_node_types() and self.get_active_edge_types().
            - Combine the results into a dictionary with keys 'node' and 'edge' and return it.
    - Handle Specific Element Type:
        - If element is either 'node' or 'edge':
            - Call the corresponding internal function based on the provided type:
                - self.get_active_node_types() for 'node'.
                - self.get_active_edge_types() for 'edge'.
            - Return the list of unique types obtained from the internal function.
    - Handle Invalid Element Type:
        - If element is neither None nor a valid type string, return None.
    '''

    def hide_elements(self, hide_all=False, node_types=None, edge_types=None,
                      element_indexes=None, nodes=None, edges=None):
        """

        :param hide_all:
        :param node_types: list of node types to hide
        :param edge_types: list of edge types to hide
        :param element_indexes:  list of element indexes to hide
        :param nodes: list of node ids to hide
        :param edges: list of edge ids to hide
        :return:
        """

        flag = True

        if hide_all:
            flag = False

        if node_types is not None:
            node_types = set(node_types)
            flag = False

        if edge_types is not None:
            edge_types = set(edge_types)
            flag = False

        if element_indexes is not None:
            element_indexes = set(element_indexes)
            flag = False

        if nodes is not None:
            nodes = set(nodes)
            flag = False

        if edges is not None:
            edges = set(edges)
            flag = False

        if flag:
            return

        for e in range(len(self.elements)):
            if hide_all:
                self.elements[e]['data']['hidden'] = True
            elif element_indexes is not None:
                if e in element_indexes:
                    self.elements[e]['data']['hidden'] = True
            elif edge_types is not None:
                if self.elements[e]['data']['type'] in edge_types:
                    self.elements[e]['data']['hidden'] = True
            elif node_types is not None:
                if self.elements[e]['data']['type'] in node_types:
                    self.elements[e]['data']['hidden'] = True
            elif nodes is not None:
                if self.elements[e]['data']['element_type'] == 'node':
                    if self.elements[e]['data']['id'] in nodes:
                        self.elements[e]['data']['hidden'] = True
            elif edges is not None:
                if self.elements[e]['data']['element_type'] == 'edge':
                    if self.elements[e]['data']['id'] in edges:
                        self.elements[e]['data']['hidden'] = True
            else:
                pass
    '''
    Hides specified elements within the active network based on various criteria.
    Offers fine-grained control to selectively hide elements by type, ID, or index.

    Parameters:
    - self: Instance of the class containing the function (likely the ActiveNetwork class).
    - hide_all (optional, boolean): If True, hides all elements.
    - node_types (optional, list): List of node types to hide.
    - edge_types (optional, list): List of edge types to hide.
    - element_indexes (optional, list): List of element indexes to hide.
    - nodes (optional, list): List of node IDs to hide.
    - edges (optional, list): List of edge IDs to hide.

    Return Value:
        - None (modifies elements in place).

    Steps:

    - Input Validation and Conversion:
        - Converts lists of types, indexes, nodes, and edges to sets for efficient lookups.
        - Uses a flag to track if any valid hiding criteria are provided.
    - Early Return Check:
        - If no valid hiding criteria are specified (flag remains True), returns early to avoid unnecessary processing.
    - Element Iteration and Hiding:
        - Iterates through each element in the self.elements list:
            - If hide_all is True, sets the hidden flag to True for the element.
            - Otherwise, checks the provided criteria in a specific order:
                - If the element index is in element_indexes, hides it.
                - If the element type matches a type in edge_types or node_types, hides it.
                - If the element is a node and its ID is in nodes, hides it.
                - If the element is an edge and its ID is in edges, hides it.
    '''

    def unhide_elements(self, unhide_all=False, node_types=None, edge_types=None,
                        element_indexes=None, nodes=None, edges=None):
        """

        :param unhide_all:
        :param node_types: list of node types to unhide
        :param edge_types: list of edge types to unhide
        :param element_indexes:  list of element indexes to unhide
        :param nodes: list of node ids to unhide
        :param edges: list of edge ids to unhide
        :return:
        """

        flag = True

        if unhide_all:
            flag = False

        if node_types is not None:
            node_types = set(node_types)
            flag = False

        if edge_types is not None:
            edge_types = set(edge_types)
            flag = False

        if element_indexes is not None:
            element_indexes = set(element_indexes)
            flag = False

        if nodes is not None:
            nodes = set(nodes)
            flag = False

        if edges is not None:
            edges = set(edges)
            flag = False

        if flag:
            return

        for e in range(len(self.elements)):
            if unhide_all:
                self.elements[e]['data']['hidden'] = False
            elif element_indexes is not None:
                if e in element_indexes:
                    self.elements[e]['data']['hidden'] = False
            elif edge_types is not None:
                if self.elements[e]['data']['type'] in edge_types:
                    self.elements[e]['data']['hidden'] = False
            elif node_types is not None:
                if self.elements[e]['data']['type'] in node_types:
                    self.elements[e]['data']['hidden'] = False
            elif nodes is not None:
                if self.elements[e]['data']['element_type'] == 'node':
                    if self.elements[e]['data']['id'] in nodes:
                        self.elements[e]['data']['hidden'] = False
            elif edges is not None:
                if self.elements[e]['data']['element_type'] == 'edge':
                    if self.elements[e]['data']['id'] in edges:
                        self.elements[e]['data']['hidden'] = False
            else:
                pass
    '''
    This function unhides specified elements within the active network based on various criteria. It offers fine-grained control to selectively unhide elements by type, ID, or index.

    Parameters:
    - self: Instance of the class containing the function (likely the ActiveNetwork class).
    - unhide_all (optional, boolean): If True, unhides all elements.
    - node_types (optional, list): List of node types to unhide.
    - edge_types (optional, list): List of edge types to unhide.
    - element_indexes (optional, list): List of element indexes to unhide.
    - nodes (optional, list): List of node IDs to unhide.
    - edges (optional, list): List of edge IDs to unhide.

    Return Value:
    - None (modifies elements in place).

    Steps:
    - Input Validation and Conversion:
        - Converts lists of types, indexes, nodes, and edges to sets for efficient lookups.
        - Uses a flag to track if any valid unhiding criteria are provided.
    - Early Return Check:
        - If no valid unhiding criteria are specified (flag remains True), returns early to avoid unnecessary processing.
    - Element Iteration and Unhiding:
        - Iterates through each element in the self.elements list:
            - If unhide_all is True, sets the hidden flag to False for the element.
            - Otherwise, checks the provided criteria in a specific order:
                - If the element index is in element_indexes, unhides it.
                - If the element type matches a type in edge_types or node_types, unhides it.
                - If the element is a node and its ID is in nodes, unhides it.
                - If the element is an edge and its ID is in edges, unhides it.
    '''

    def highlight_elements(self, highlight_all=False, node_types=None, edge_types=None,
                           element_indexes=None, nodes=None, edges=None):
        """

        :param highlight_all:
        :param node_types: list of node types to highlight
        :param edge_types: list of edge types to highlight
        :param element_indexes:  list of element indexes to highlight
        :param nodes: list of node ids to highlight
        :param edges: list of edge ids to highlight
        :return:
        """

        flag = True

        if highlight_all:
            flag = False

        if node_types is not None:
            node_types = set(node_types)
            flag = False

        if edge_types is not None:
            edge_types = set(edge_types)
            flag = False

        if element_indexes is not None:
            element_indexes = set(element_indexes)
            flag = False

        if nodes is not None:
            nodes = set(nodes)
            flag = False

        if edges is not None:
            edges = set(edges)
            flag = False

        if flag:
            return

        for e in range(len(self.elements)):
            if highlight_all:
                self.elements[e]['data']['highlighted'] = True
            elif element_indexes is not None:
                if e in element_indexes:
                    self.elements[e]['data']['highlighted'] = True
            elif edge_types is not None:
                if self.elements[e]['data']['type'] in edge_types:
                    self.elements[e]['data']['highlighted'] = True
            elif node_types is not None:
                if self.elements[e]['data']['type'] in node_types:
                    self.elements[e]['data']['highlighted'] = True
            elif nodes is not None:
                if self.elements[e]['data']['element_type'] == 'node':
                    if self.elements[e]['data']['id'] in nodes:
                        self.elements[e]['data']['highlighted'] = True
            elif edges is not None:
                if self.elements[e]['data']['element_type'] == 'edge':
                    if self.elements[e]['data']['id'] in edges:
                        self.elements[e]['data']['highlighted'] = True
            else:
                pass
    '''
    This function highlights specified elements within the active network based on different criteria. It offers granular control to selectively highlight elements by type, ID, or index.

    Parameters:
    - self: Instance of the class containing the function (likely the ActiveNetwork class).
    - highlight_all (optional, boolean): If True, highlights all elements.
    - node_types (optional, list): List of node types to highlight.
    - edge_types (optional, list): List of edge types to highlight.
    - element_indexes (optional, list): List of element indexes to highlight.
    - nodes (optional, list): List of node IDs to highlight.
    - edges (optional, list): List of edge IDs to highlight.

    Return Value:
    - None (modifies elements in place).

    Steps:
    - Input Validation and Conversion:
        - Converts lists of types, indexes, nodes, and edges to sets for efficient lookups.
        - Uses a flag to track if any valid highlighting criteria are provided.
    - Early Return Check:
        - If no valid highlighting criteria are specified (flag remains True), returns early to avoid unnecessary processing.
    - Element Iteration and Highlighting:
        - Iterates through each element in the self.elements list:
            - If highlight_all is True, sets the highlighted flag to True for the element.
            - Otherwise, checks the provided criteria in a specific order:
                - If the element index is in element_indexes, highlights it.
                - If the element type matches a type in edge_types or node_types, highlights it.
                - If the element is a node and its ID is in nodes, highlights it.
                - If the element is an edge and its ID is in edges, highlights it.
    '''

    def unhighlight_elements(self, unhighlight_all=False, node_types=None, edge_types=None,
                             element_indexes=None, nodes=None, edges=None):
        """

        :param unhighlight_all:
        :param node_types: list of node types to unhighlight
        :param edge_types: list of edge types to unhighlight
        :param element_indexes:  list of element indexes to unhighlight
        :param nodes: list of node ids to unhighlight
        :param edges: list of edge ids to unhighlight
        :return:
        """

        flag = True

        if unhighlight_all:
            flag = False

        if node_types is not None:
            node_types = set(node_types)
            flag = False

        if edge_types is not None:
            edge_types = set(edge_types)
            flag = False

        if element_indexes is not None:
            element_indexes = set(element_indexes)
            flag = False

        if nodes is not None:
            nodes = set(nodes)
            flag = False

        if edges is not None:
            edges = set(edges)
            flag = False

        if flag:
            return

        for e in range(len(self.elements)):
            if unhighlight_all:
                self.elements[e]['data']['highlighted'] = False
            elif element_indexes is not None:
                if e in element_indexes:
                    self.elements[e]['data']['highlighted'] = False
            elif edge_types is not None:
                if self.elements[e]['data']['type'] in edge_types:
                    self.elements[e]['data']['highlighted'] = False
            elif node_types is not None:
                if self.elements[e]['data']['type'] in node_types:
                    self.elements[e]['data']['highlighted'] = False
            elif nodes is not None:
                if self.elements[e]['data']['element_type'] == 'node':
                    if self.elements[e]['data']['id'] in nodes:
                        self.elements[e]['data']['highlighted'] = False
            elif edges is not None:
                if self.elements[e]['data']['element_type'] == 'edge':
                    if self.elements[e]['data']['id'] in edges:
                        self.elements[e]['data']['highlighted'] = False
            else:
                pass
    '''
    This function unhighlights specified elements within the active network based on different criteria. It offers fine-grained control to selectively unhighlight elements by type, ID, or index.

    Parameters:
    - self: Instance of the class containing the function (likely the ActiveNetwork class).
    - unhighlight_all (optional, boolean): If True, unhighlights all elements.
    - node_types (optional, list): List of node types to unhighlight.
    - edge_types (optional, list): List of edge types to unhighlight.
    - element_indexes (optional, list): List of element indexes to unhighlight.
    - nodes (optional, list): List of node IDs to unhighlight.
    - edges (optional, list): List of edge IDs to unhighlight.

    Return Value:
    - None (modifies elements in place).

    Steps:
    - Input Validation and Conversion:
        - Converts lists of types, indexes, nodes, and edges to sets for efficient lookups.
        - Uses a flag to track if any valid unhighlighting criteria are provided.
    - Early Return Check:
        - If no valid unhighlighting criteria are specified (flag remains True), returns early to avoid unnecessary processing.
    - Element Iteration and Unhighlighting:
        - Iterates through each element in the self.elements list:
            - If unhighlight_all is True, sets the highlighted flag to False for the element.
            - Otherwise, checks the provided criteria in a specific order:
                - If the element index is in element_indexes, unhighlights it.
                - If the element type matches a type in edge_types or node_types, unhighlights it.
                - If the element is a node and its ID is in nodes, unhighlights it.
                - If the element is an edge and its ID is in edges, unhighlights it.
    '''

    def get_active_network_info(self):
        """
        get meta info about the active part of the network
        :return:
        """
        # num_nodes = len([e for e in self.elements if e['element_type': 'node'] == 'node'])
        # num_edges = len(self.elements) - num_nodes
        num_nodes = len(self.active_nodes)
        num_edges = len(self.active_edges)

        return {'network_name': self.network_name, 'num_nodes': num_nodes, 'num_edges': num_edges}
    '''
    Gathers and returns basic information about the active portion of the network.

    Parameters:
    - self: Instance of the class containing the function (likely the ActiveNetwork class).

    Output:
    - A dictionary containing three key-value pairs:
        - network_name: The name of the network.
        - num_nodes: The number of active nodes in the network.
        - num_edges: The number of active edges in the network.

    Steps:
    - Count Active Elements:
        - Leverages pre-calculated counts for efficiency:
            - num_nodes is retrieved directly from the self.active_nodes attribute.
            - num_edges is retrieved directly from the self.active_edges attribute.
    - Construct Information Dictionary:
        - Creates a dictionary with the following key-value pairs:
            - network_name: Value obtained from self.network_name.
            - num_nodes: The calculated number of active nodes.
            - num_edges: The calculated number of active edges.
    - Return Information:
        - Returns the constructed dictionary containing the network information.

    Relies on pre-calculated counts of active nodes and edges, likely for efficiency.
    Provides essential summary statistics about the active network.
    '''


    def get_selected_nodes(self):
        """

        :return: list of all selected nodes
        """
        # print('selected nodes = ', self.selected_nodes)
        return list(self.selected_nodes)
    '''
    Retrieves a list of all currently selected nodes within the network.

    Parameters:
    - self: Instance of the class containing the function (likely the ActiveNetwork class).

    Output:
    - A list containing the IDs of all selected nodes (presumably copied from the self.selected_nodes attribute).

    Steps:
    - Access Selected Nodes:
        - Retrieves the self.selected_nodes attribute, which presumably holds the internal representation of selected nodes.
    - Return as List:
        - Creates a new list by copying the elements from self.selected_nodes using the list() function.

    Provides a way to obtain information about currently selected nodes.
    Assumes the existence of a self.selected_nodes attribute to store selection information.
    '''

    def get_selected_edges(self):
        """

        :return: list of selected edges
        """
        return list(self.selected_edges)
    '''
    Retrieves a list of all currently selected edges within the network.

    Parameters:
    - self: Instance of the class containing the function (likely the ActiveNetwork class).

    Output:
    - A list containing the IDs of all selected edges (presumably copied from the self.selected_edges attribute).

    Steps:
    - Access Selected Edges:
        - Retrieves the self.selected_edges attribute, which presumably holds the internal representation of selected edges.
    - Return as List:
        - Creates a new list by copying the elements from self.selected_edges using the list() function.

    Provides a way to obtain information about currently selected edges.
    Assumes the existence of a self.selected_edges attribute to store selection information.
    '''

    def expand_nodes(self, node_ids, get_change=False):
        """
        adding the neighbors of nodes in node_ids into element list
        :param node_ids:
        :return:
        """

        sub_network = self.get_network(node_ids, return_edge_index=True)
        added_edges = set([e_index for e_index in sub_network['edges'] if e_index not in self.active_edges])
        added_nodes = set([node['id'] for node in sub_network['nodes'] if node['id'] not in self.active_nodes])

        if 'weight' in self.edges[0]['properties']:
            min_weight = float('inf')
            max_weight = 0
            for edge in self.edges:
                if 'weight' in edge['properties']:
                    if edge['properties']['weight'] < min_weight:
                        min_weight = edge['properties']['weight']
                    elif edge['properties']['weight'] > max_weight:
                        max_weight = edge['properties']['weight']

        if get_change:
            # check expandability of existing nodes
            changed_expandability_nodes = set()
            for node in self.active_nodes:
                expandable = False
                if node in self.adj_list:
                    for e_index in self.adj_list[node]:
                        if e_index in self.active_edges:
                            continue
                        if e_index in added_edges:
                            continue
                        expandable = True
                        break
                an_info = self.active_nodes[node]  # active node's info
                if an_info['expandable'] != expandable:
                    changed_expandability_nodes.add(node)
            # added elements
            added_elements = []
            added_elements_indexes = {}
            for node in added_nodes:
                # added node
                node_info = self.nodes[node]
                node_data = {'element_type': 'node',
                             'id': node,
                             'type': node_info['type'],
                             'label': active_element_default_values['label'],
                             'selected': active_element_default_values['selected'],
                             'expandable': active_element_default_values['expandable'],
                             'community': active_element_default_values['community'],
                             'community_confidence': active_element_default_values['community_confidence'],
                             'social_influence_score': active_element_default_values['social_influence_score'],
                             'visualisation_social_influence_score':
                                 active_element_default_values['visualisation_social_influence_score'],
                             'hidden': active_element_default_values['hidden'],
                             'highlighted': active_element_default_values['highlighted'],
                             'num_incoming_neighbor_selected': active_element_default_values[
                                 'num_incoming_neighbor_selected'],
                             'incoming_neighbor_selected': active_element_default_values['incoming_neighbor_selected'],
                             'info': node_info}

                # add label
                if self.node_label_field is not None:
                    if self.node_label_field in node_info:
                        node_data['label'] = node_info[self.node_label_field]
                else:
                    node_data['label'] = node_data['id']
                # check expandability
                expandable = False
                if node in self.adj_list:
                    for e_index in self.adj_list[node]:
                        if e_index in self.active_edges:
                            continue
                        if e_index in added_edges:
                            continue
                        expandable = True
                        break

                node_data['expandable'] = expandable
                element = {'group': 'nodes', 'data': node_data}
                added_elements.append(element)
                added_elements_indexes[node] = len(added_elements) - 1

            for e_index in added_edges:
                edge_info = self.edges[e_index]
                edge_data = {'element_type': 'edge',
                             'id': e_index, 'source': edge_info['source'],
                             'type': active_element_default_values['type'],
                             'label': active_element_default_values['label'],
                             'selected': False,
                             'predicted': active_element_default_values['predicted'],
                             'target': edge_info['target'],
                             'hidden': active_element_default_values['hidden'],
                             'highlighted': active_element_default_values['highlighted'],
                             'source_selected': active_element_default_values['source_selected'],
                             'info': edge_info['properties']}
                # add type
                if 'type' in edge_info['properties']:
                    edge_data['type'] = edge_info['properties']['type']

                # add probability
                if 'probability' in edge_info['properties']:
                    edge_data['probability'] = edge_info['properties']['probability']

                # add weight
                if 'weight' in edge_info['properties'] and max_weight > min_weight:
                    edge_data['normalized_weight'] = (edge_info['properties']['weight'] - min_weight) / (
                                max_weight - min_weight)

                # add label
                if self.edge_label_field is not None:
                    if self.edge_label_field in edge_info:
                        edge_data['label'] = edge_info[self.edge_label_field]
                else:
                    edge_data['label'] = ''  # blank label

                # add source selected
                source = edge_info['source']
                if source in self.active_nodes:
                    source_element_index = self.active_nodes[source]['element_index']
                    source_element = self.elements[source_element_index]['data']
                    if source_element['selected']:
                        edge_data['source_selected'] = True

                element = {'group': 'edges', 'data': edge_data}
                added_elements.append(element)

                # change incoming neighbor selected in target
                source = edge_info['source']
                if source in self.active_nodes:
                    source_element_index = self.active_nodes[source]['element_index']
                    source_element = self.elements[source_element_index]['data']
                    if source_element['selected']:

                        target = edge_info['target']
                        if target in added_elements_indexes:
                            added_elements[added_elements_indexes[target]]['data'][
                                'num_incoming_neighbor_selected'] += 1
                            added_elements[added_elements_indexes[target]]['data']['incoming_neighbor_selected'] = True

            result = {'success': 1, 'message': 'Successful', 'changed_expandability': changed_expandability_nodes,
                      'added_nodes': added_nodes, 'added_edges': added_edges, 'added_elements': added_elements}
            return result

        else:  # update directly
            self.erase_previous_analysis_result(task_id='social_influence_analysis')
            self.erase_previous_analysis_result(task_id='community_detection')
            self.erase_previous_analysis_result(task_id='link_prediction')
            self.last_analysis = None
            # check expandability of existing nodes
            for node in self.active_nodes:
                expandable = False
                if node in self.adj_list:
                    for e_index in self.adj_list[node]:
                        if e_index in self.active_edges:
                            continue
                        if e_index in added_edges:
                            continue
                        expandable = True
                        break
                an_info = self.active_nodes[node]  # active node's info
                self.elements[an_info['element_index']]['data']['expandable'] = expandable
                an_info['expandable'] = expandable

            for node in added_nodes:
                # added node
                node_info = self.nodes[node]
                node_data = {'element_type': 'node',
                             'id': node,
                             'type': node_info['type'],
                             'selected': active_element_default_values['selected'],
                             'expandable': active_element_default_values['expandable'],
                             'community': active_element_default_values['community'],
                             'community_confidence': active_element_default_values['community_confidence'],
                             'social_influence_score': active_element_default_values['social_influence_score'],
                             'visualisation_social_influence_score':
                                 active_element_default_values['visualisation_social_influence_score'],
                             'hidden': active_element_default_values['hidden'],
                             'highlighted': active_element_default_values['highlighted'],
                             'num_incoming_neighbor_selected': active_element_default_values[
                                 'num_incoming_neighbor_selected'],
                             'incoming_neighbor_selected': active_element_default_values['incoming_neighbor_selected'],
                             'info': node_info}
                # add label
                if self.node_label_field is not None:
                    if self.node_label_field in node_info:
                        node_data['label'] = node_info[self.node_label_field]
                else:
                    node_data['label'] = node_data['id']
                # check expandability
                expandable = False
                if node in self.adj_list:
                    for e_index in self.adj_list[node]:
                        if e_index in self.active_edges:
                            continue
                        if e_index in added_edges:
                            continue
                        expandable = True
                        break
                node_data['expandable'] = expandable
                element = {'group': 'nodes', 'data': node_data}
                self.elements.append(element)
                self.active_nodes[node] = {'expandable': expandable, 'element_index': len(self.elements) - 1}

            for e_index in added_edges:
                # added edge
                edge_info = self.edges[e_index]
                edge_data = {'element_type': 'edge',
                             'id': e_index, 'source': edge_info['source'],
                             'type': active_element_default_values['type'],
                             'label': active_element_default_values['label'],
                             'selected': active_element_default_values['selected'],
                             'predicted': active_element_default_values['predicted'],
                             'target': edge_info['target'],
                             'hidden': active_element_default_values['hidden'],
                             'highlighted': active_element_default_values['highlighted'],
                             'source_selected': active_element_default_values['source_selected'],
                             'info': edge_info['properties']}
                # add type
                if 'type' in edge_info['properties']:
                    edge_data['type'] = edge_info['properties']['type']
                if 'probability' in edge_info['properties']:
                    edge_data['probability'] = edge_info['properties']['probability']
                # add label
                if self.edge_label_field is not None:
                    if self.edge_label_field in edge_info:
                        edge_data['label'] = edge_info[self.edge_label_field]

                if 'weight' in edge_info['properties'] and max_weight > min_weight:
                    edge_data['normalized_weight'] = (edge_info['properties']['weight'] - min_weight) / (
                                max_weight - min_weight)

                else:
                    edge_data['label'] = ''  # blank label
                element = {'group': 'edges', 'data': edge_data}

                # add source selected
                source = edge_info['source']
                if source in self.active_nodes:
                    source_element_index = self.active_nodes[source]['element_index']
                    source_element = self.elements[source_element_index]['data']
                    if source_element['selected']:
                        edge_data['source_selected'] = True

                self.elements.append(element)
                self.active_edges[e_index] = {'element_index': len(self.elements) - 1}

                # change incoming neighbor selected in target
                source = edge_info['source']
                if source in self.active_nodes:
                    source_element_index = self.active_nodes[source]['element_index']
                    source_element = self.elements[source_element_index]['data']
                    if source_element['selected']:
                        target = edge_info['target']
                        if target in self.active_nodes:
                            target_element_index = self.active_nodes[target]['element_index']
                            target_element = self.elements[target_element_index]['data']
                            target_element['num_incoming_neighbor_selected'] += 1
                            target_element['incoming_neighbor_selected'] = True

            result = {'success': 1, 'message': 'Successful'}
            return result
    '''
    Expands a network by adding the neighbors of specified nodes (provided in node_ids).

    Parameters:
    - self: Instance of the class containing the function (likely the ActiveNetwork class).
    - node_ids: List of node IDs to expand.
    - get_change: Boolean flag indicating whether to track changes in expandability of existing nodes (optional).

    Output:
    - A dictionary containing information about the expansion:
        - success: Whether the expansion was successful (always 1 in this implementation).
        - message: A success message.
        - changed_expandability: (if get_change is True) dictionary of nodes whose expandability changed.
        - added_nodes: List of IDs of added nodes.
        - added_edges: List of IDs of added edges.
        - added_elements: List of dictionaries representing the added elements (nodes and edges).

    Steps:
    - Extract Subnetwork:
        - Retrieves the subnetwork around node_ids, including both nodes and edges (using get_network).
    - Identify New Elements:
        - Identifies new nodes and edges not already present in the active network (using set operations).
    - Process New Nodes:
        - Creates data dictionaries for each new node, including essential attributes and expandable flag.
        - Updates expandability based on adjacency information.
        - Adds new node data to the elements list and updates the active_nodes dictionary.
    - Process New Edges:
        - Creates data dictionaries for each new edge, including essential attributes and additional data like normalized weight (if applicable).
        - Updates source selected flag based on source node selection.
        - Handles incoming neighbor selection updates in target nodes.
        - Adds new edge data to the elements list and updates the active_edges dictionary.
    - Update Expandability (Optional):
        - If get_change is True, checks if existing nodes' expandability changed due to the expansion.
        - Updates the active_nodes dictionary with the new expandability values.
    - Return Results:
        - Returns a dictionary containing information about the successful expansion and added elements.
    '''

    def remove_element(self, element_indexes):
        """
        remove the elements at position element_indexes from element list
        :param element_indexes:
        :return:
        """
        # print('element_indexes = ', element_indexes)
        element_indexes.sort(reverse=True)  # to save computation when left shifting the elements
        # print('element_indexes = ', element_indexes)
        for element_index in element_indexes:
            # print('\t', element_index, '\t', len(self.elements), '\t', element_indexes)
            element = self.elements[element_index]
            if element['data']['element_type'] == 'node':
                # remove an active node
                self.active_nodes.pop(element['data']['id'])
            else:
                # remove an active edge
                if not element['data']['predicted']:
                    # an observed edge
                    self.active_edges.pop(element['data']['id'])
                else:
                    source = element['data']['source']
                    self.predicted_edges[source].remove(element_index)

            if element_index < len(self.elements) - 1:  # not the last element
                # then shift the subsequent elements to the left
                for i in range(element_index, len(self.elements) - 1, 1):
                    self.elements[i] = self.elements[i + 1]
                    # update the element_index in active nodes and active edges
                    if self.elements[i]['data']['element_type'] == 'node':
                        node_id = self.elements[i]['data']['id']
                        self.active_nodes[node_id]['element_index'] = i
                    else:
                        if not self.elements[i]['data']['predicted']:
                            e_index = self.elements[i]['data']['id']
                            self.active_edges[e_index]['element_index'] = i
                        else:
                            source = self.elements[i]['data']['source']
                            self.predicted_edges[source].remove(i + 1)
                            self.predicted_edges[source].append(i)
                            pass
            else:
                # TODO: check this
                pass
            del self.elements[-1]
    """
    This function removes elements from a data structure called element_list based on provided indices. It also updates related data structures like active_nodes and active_edges and handles predicted edges separately.

    Parameters:
    - element_indexes: A list of integer indices specifying the elements to remove.

    Steps:
    - Sort Indices:
        - Sorts the element_indexes list in descending order to avoid shifting issues (explained later).
    - Iterate over Indices:
        - Loops through each index in element_indexes:
        - Retrieves the element data at the specified index.
        - Checks the element type ("node" or "edge") using element['data']['element_type'].
    - Remove Nodes:
        - If it's a node:
            - Removes the node from active_nodes using its ID.
    - Remove Observed Edges:
        - If it's an observed edge (not predicted):
            - Removes the edge from active_edges using its ID.
    - Remove Predicted Edges:
        - If it's a predicted edge:
            - Removes the element index from the predicted_edges list for its source node.
    - Shift Remaining Elements (if not last):
        - If the index isn't the last element:
            - Loops through subsequent elements:
                - Shifts each element one position to the left (effectively removing the current element).
                - Updates the element index in active_nodes or active_edges (if applicable).
                    - For nodes, updates the element_index attribute in the active_nodes dictionary.
                    - For observed edges, updates the element_index attribute in the active_edges dictionary.
                    - For predicted edges, removes the old index from the predicted_edges list for its source node and adds the new shifted index.
    - Delete Last Element:
        - If the index is the last element:
            - There's currently a TODO comment in the code, suggesting this case might need further attention.
    - Delete Final Removed Element:
        - Deletes the last element from element_list itself, effectively finalizing the removal.
    
    Sorting indices in descending order optimizes shifting operations by avoiding overwriting elements to be removed.
    The function handles different element types (nodes and edges) and predicted edges separately.
    It updates related data structures (active_nodes, active_edges, and predicted_edges) to maintain consistency.
    The TODO comment suggests potential improvement for handling the last element case.
    """

    def deactivate_nodes(self, node_ids, get_change=False):
        """
        removing the nodes and its adjacent edges from the active network
        :param node_ids:
        :return:
        """
        sub_network = self.get_network(node_ids, return_edge_index=True)
        node_ids = set(node_ids)
        removed_edges = set([e_index for e_index in sub_network['edges'] if
                             (self.edges[e_index]['source'] in node_ids or
                              self.edges[e_index]['target'] in node_ids) and e_index in self.active_edges])

        if get_change:
            # check expandability of existing nodes
            changed_expandability_nodes = set()
            # check incomming neighbor selected
            changed_incoming_neighbor_selected_nodes = set()

            removed_elements = []
            for e_index in removed_edges:
                removed_elements.append(self.active_edges[e_index]['element_index'])
                source, target = self.edges[e_index]['source'], self.edges[e_index]['target']
                # check incomming neighbor selected
                if source in node_ids:
                    source_element_index = self.active_nodes[source]['element_index']
                    source_element = self.elements[source_element_index]['data']
                    if source_element['selected']:
                        if target in self.active_nodes:
                            target_element_index = self.active_nodes[target]['element_index']
                            if self.elements[target_element_index]['data']['num_incoming_neighbor_selected'] == 1:
                                changed_incoming_neighbor_selected_nodes.add(target)
                # check expandability of existing nodes
                if source in self.active_nodes:
                    if target in node_ids:
                        if not self.active_nodes[source]['expandable']:
                            changed_expandability_nodes.add(source)
            for node in node_ids:
                if node in self.active_nodes:
                    removed_elements.append(self.active_nodes[node]['element_index'])

            result = {'success': 1, 'message': 'Successful',
                      'changed_incoming_neighbor_selected': changed_incoming_neighbor_selected_nodes,
                      'changed_expandability': changed_expandability_nodes,
                      'removed_elements': removed_elements, 'removed_edges': removed_edges}
            return result
        else:  # update directly
            self.erase_previous_analysis_result(task_id='social_influence_analysis')
            self.erase_previous_analysis_result(task_id='community_detection')
            self.erase_previous_analysis_result(task_id='link_prediction')
            self.last_analysis = None
            #####################
            removed_elements = []
            for e_index in removed_edges:
                # the edge element to be removed
                removed_elements.append(self.active_edges[e_index]['element_index'])

                source, target = self.edges[e_index]['source'], self.edges[e_index]['target']
                # check incomming neighbor selected
                if source in node_ids:
                    source_element_index = self.active_nodes[source]['element_index']
                    source_element = self.elements[source_element_index]['data']
                    if source_element['selected']:
                        if target in self.active_nodes:
                            target_element_index = self.active_nodes[target]['element_index']
                            target_element = self.elements[target_element_index]['data']
                            num_incoming_neighbor_selected = target_element['num_incoming_neighbor_selected']
                            if num_incoming_neighbor_selected > 0:
                                num_incoming_neighbor_selected -= 1
                            target_element['num_incoming_neighbor_selected'] = num_incoming_neighbor_selected
                            if num_incoming_neighbor_selected == 0:
                                target_element['incoming_neighbor_selected'] = False

                # check the expandability of existing nodes
                if source in self.active_nodes:
                    if target in node_ids:
                        if not self.active_nodes[source]['expandable']:
                            an_info = self.active_nodes[source]
                            an_info['expandable'] = True
                            self.elements[an_info['element_index']]['data']['expandable'] = True

            for node in node_ids:
                if node in self.active_nodes:
                    removed_elements.append(self.active_nodes[node]['element_index'])
                    # remove the node from selected nodes
                    if node in self.selected_nodes:
                        self.selected_nodes.remove(node)
            self.remove_element(removed_elements)
            result = {'success': 1, 'message': 'Successful'}
            return result
    '''
    Removes specified nodes and their adjacent edges from the active network.
    Updates related data structures and tracks changes in node expandability and incoming neighbor selection status.

    Parameters:
    - self: Instance of the class containing the function.
    - node_ids: List of node IDs to deactivate.
    - get_change (optional, default=False): Boolean indicating whether to track changes in expandability and incoming neighbor selection.

    Steps:
    - Identify Edges to Remove:
        - Retrieves edges connected to the specified nodes using get_network.
        - Filters edges to those within the active network.
    - Conditional Execution Based on get_change:
        - If get_change is True:
            - Tracks changes in incoming neighbor selection and expandability.
            - Creates a result dictionary with detailed information about changes.
        - If get_change is False:
            - Erases previous analysis results.
            - Directly updates data structures.
    - Remove Edges:
        - Iterates through identified edges:
            - Appends edge element index to removed_elements.
            - Updates num_incoming_neighbor_selected and incoming_neighbor_selected flags for target nodes if necessary.
            - Updates expandability flags for source nodes if necessary.
    - Remove Nodes:
        - Iterates through specified node IDs:
            - Appends node element index to removed_elements.
            - Removes node from selected_nodes if present.
    - Call remove_element:
        - Invokes remove_element (presumably defined elsewhere) to remove elements based on removed_elements.
    - Return Result:
        - Returns a dictionary indicating success and providing details about removed elements and changes (if get_change was True).

    Maintains consistency in related data structures.
    Provides optional tracking of changes for further analysis.
    '''

    def deactivate_edges(self, edge_ids, get_change=False):
        """
        removing the edges from active network
        :param edge_ids:
        :return:
        """
        edge_ids = set(edge_ids)
        removed_edges = set([e_index for e_index in edge_ids if e_index in self.active_edges])

        if get_change:
            removed_elements = []
            changed_incoming_neighbor_selected_nodes = set()
            for e_index in removed_edges:
                removed_elements.append(self.active_edges[e_index]['element_index'])
                source, target = self.edges[e_index]['source'], self.edges[e_index]['target']
                # check incomming neighbor selected
                if source in self.active_nodes:
                    source_element_index = self.active_nodes[source]['element_index']
                    source_element = self.elements[source_element_index]['data']
                    if source_element['selected']:
                        if target in self.active_nodes:
                            target_element_index = self.active_nodes[target]['element_index']
                            if self.elements[target_element_index]['data']['num_incoming_neighbor_selected'] == 1:
                                changed_incoming_neighbor_selected_nodes.add(target)

            result = {'success': 1, 'message': 'Successful',
                      'changed_incoming_neighbor_selected': changed_incoming_neighbor_selected_nodes,
                      'removed_elements': removed_elements, 'removed_edges': removed_edges}
            return result
        else:  # update directly
            self.erase_previous_analysis_result(task_id='social_influence_analysis')
            self.erase_previous_analysis_result(task_id='community_detection')
            self.erase_previous_analysis_result(task_id='link_prediction')
            self.last_analysis = None
            #####################
            removed_elements = []
            for e_index in removed_edges:
                # the edge element to be removed
                removed_elements.append(self.active_edges[e_index]['element_index'])

                source, target = self.edges[e_index]['source'], self.edges[e_index]['target']
                # check incomming neighbor selected
                if source in self.active_nodes:
                    source_element_index = self.active_nodes[source]['element_index']
                    source_element = self.elements[source_element_index]['data']
                    if source_element['selected']:
                        if target in self.active_nodes:
                            target_element_index = self.active_nodes[target]['element_index']
                            target_element = self.elements[target_element_index]['data']
                            num_incoming_neighbor_selected = target_element['num_incoming_neighbor_selected']
                            if num_incoming_neighbor_selected > 0:
                                num_incoming_neighbor_selected -= 1
                            target_element['num_incoming_neighbor_selected'] = num_incoming_neighbor_selected
                            if num_incoming_neighbor_selected == 0:
                                target_element['incoming_neighbor_selected'] = False
                # remove the edge from the selected set
                if e_index in self.selected_edges:
                    self.selected_edges.remove(e_index)

            self.remove_element(removed_elements)
            result = {'success': 1, 'message': 'Successful'}
            return result
    '''
    Removes specified edges from the active network.
    Optionally tracks changes in the num_incoming_neighbor_selected flag of affected nodes.
    Updates related data structures like selected_edges.

    Parameters:
    - self: Instance of the class containing the function.
    - edge_ids: List of edge IDs to deactivate.
    - get_change (optional, default=False): Boolean indicating whether to track changes in num_incoming_neighbor_selected.

    Steps:
    - Identify Valid Edges:
        - Converts edge_ids to a set for efficient operations.
        - Filters edge_ids to those present in the active_edges dictionary.
    - Conditional Execution Based on get_change:
        - If get_change is True:
            - Tracks changes in num_incoming_neighbor_selected for affected target nodes.
            - Creates a result dictionary with details about changes and removed elements.
        - If get_change is False:
    - Erases previous analysis results (if applicable).
        - Updates data structures directly.
    - Remove Edges:
        - Iterates through identified edges:
            - Appends edge element index to removed_elements.
            - Updates num_incoming_neighbor_selected and incoming_neighbor_selected flags for target nodes if necessary.
            - Removes edge from selected_edges if present.
    - Call remove_element:
        - Invokes remove_element (presumably defined elsewhere) to remove elements based on removed_elements.
    - Return Result:
        - Returns a dictionary indicating success and providing details about removed elements and changes (if get_change was True).

    Removes edges from the active network.
    Optionally tracks changes in num_incoming_neighbor_selected for analysis.
    Maintains consistency in related data structures.
    '''

    def remove_predicted_edges(self, source_ids=None):
        """
        remove predicted edges starting from nodes in source_ids
        :param source_ids:
        :return:
        """
        for node in source_ids:
            if node in self.predicted_edges:
                # print('edges to be removed: ', self.predicted_edges[node])
                self.remove_element(copy.deepcopy(self.predicted_edges[node]))
                del self.predicted_edges[node]
    '''
    Removes predicted edges from the network, optionally targeting edges originating from specific nodes.

    Parameters:
    - self: Instance of the class containing the function.
    - source_ids (optional): List of node IDs specifying the sources of predicted edges to remove. If None, removes all predicted edges.

    Steps:
    - Iterate Over Source Nodes (if source_ids provided):
        - If source_ids is specified, loops through each provided node ID.
    - Check for Predicted Edges:
        - For each iterated node:
            - Checks if the node exists in the predicted_edges dictionary (which stores predicted edges grouped by source node).
    - Remove Predicted Edges (if exist):
        - If predicted edges exist for the node:
            - Print (commented out): Originally prints the edges to be removed (useful for debugging).
            - Remove Edges: Calls remove_element to remove the edges, using a deep copy to avoid modifying the original data.
            - Delete Entry: Deletes the corresponding entry for the node from the predicted_edges dictionary.
    - No Source IDs (if applicable):
        - If source_ids is not provided, the function performs step 3 directly for all entries in the predicted_edges dictionary.

    Removes predicted edges by source node or from all sources if no source IDs are specified.
    Uses remove_element for efficient edge removal and data structure updates.
    Optionally uses deep copy to prevent unintended modifications.
    '''

    def toggle_node_selection(self, node_id):
        """
        change the selected property of node and its outgoing edges
        :param node_id:
        :return:
        """
        if node_id not in self.active_nodes:
            pass
        # change at node
        element_index = self.active_nodes[node_id]['element_index']
        element = self.elements[element_index]
        element['data']['selected'] = not element['data']['selected']
        selected = element['data']['selected']

        # change at adjacent true edge and neighbors
        if node_id in self.adj_list:
            for e_index in self.adj_list[node_id]:
                if e_index not in self.active_edges:
                    continue
                # change at edge
                edge_element_index = self.active_edges[e_index]['element_index']
                edge_element = self.elements[edge_element_index]['data']
                edge_element['source_selected'] = selected

                #
                target = self.edges[e_index]['target']
                if target in self.active_nodes:
                    target_element_index = self.active_nodes[target]['element_index']
                    target_element = self.elements[target_element_index]['data']
                    if selected:
                        target_element['num_incoming_neighbor_selected'] += 1
                        target_element['incoming_neighbor_selected'] = True
                    else:
                        target_element['num_incoming_neighbor_selected'] -= 1
                        if target_element['num_incoming_neighbor_selected'] <= 0:
                            target_element['num_incoming_neighbor_selected'] = 0
                            target_element['incoming_neighbor_selected'] = False

        # change at predicted edges
        if node_id in self.predicted_edges:
            for element_index in self.predicted_edges[node_id]:
                element = self.elements[element_index]
                element['data']['source_selected'] = not element['data']['source_selected']

        if selected:
            self.selected_nodes.add(node_id)
            return 'selected'
        else:
            self.selected_nodes.remove(node_id)
            return 'unselected'
    '''
    This function toggles the selected property of a given node and updates related information for its adjacent edges and neighboring nodes. It also handles predicted edges emanating from the selected node.

    Parameters:
    - self: Instance of the class containing the function.
    - node_id: ID of the node to toggle selection for.

    Steps:
    - Check Node Existence:
        - Ensures the node exists in the active_nodes dictionary before proceeding.
    - Update Node Selection:
        - Retrieves the element index and data for the node.
        - Inverts the selected flag in the node's data.
        - Stores the new selection state (selected).
    - Update Adjacent Edges and Neighbors:
        - If the node has adjacent edges (adj_list):
    - Iterates through each edge index:
        - Checks if the edge exists in active_edges.
        - Updates the source_selected flag in the edge's data according to the new selection state.
        - Retrieves the target node ID from the edge data.
        - If the target node exists in active_nodes:
            - Updates the num_incoming_neighbor_selected and incoming_neighbor_selected flags in the target node's data based on the selection change.
    - Update Predicted Edges:
        - If the node has predicted edges (predicted_edges):
            - Iterates through each predicted edge element index:
                - Updates the source_selected flag in the predicted edge's data.
    - Update Selected Nodes:
        - Adds or removes the node ID from the selected_nodes set based on the new selection state.
    - Return Value:
        - Returns a string indicating the new selection state ("selected" or "unselected").

    Toggles node selection and updates related data structures.
    Handles both observed and predicted edges.
    '''

    def toggle_edge_selection(self, edge_id):
        """
        change the selected property of node and its outgoing edges
        :param edge_id:
        :return:
        """
        if edge_id is None:
            return
        if type(edge_id) == str:
            try:
                edge_id = int(edge_id)
            except ValueError:
                print('cannot cast "{}" to a number'.format(edge_id))
                print('looks like the clicked-on edge is a predicted one!')
                return
        if edge_id in self.active_edges:
            # change at edge
            # print('before: ', self.selected_edges)
            element_index = self.active_edges[edge_id]['element_index']
            element = self.elements[element_index]
            element['data']['selected'] = not element['data']['selected']
            selected = element['data']['selected']
            if selected:
                self.selected_edges.add(edge_id)
                return 'selected'
            else:
                self.selected_edges.remove(edge_id)
                return 'unselected'
            # print('after: ', self.selected_edges)
    '''
    This function toggles the selected property of a given edge ID and updates the selected_edges set accordingly. It also handles potential type conversion errors for edge IDs.

    Parameters:
    - self: Instance of the class containing the function.
    - edge_id: ID of the edge to toggle selection for.

    Steps:
    - Handle None and String Input:
        - Checks if edge_id is None, returning immediately in that case.
        - If edge_id is a string, attempts to convert it to an integer.
        - Handles potential ValueError during conversion, indicating a potential predicted edge and returning without further action.
    - Validate Edge Existence:
        - Ensures the provided edge_id exists in the active_edges dictionary.
    - Update Edge Selection:
        - Retrieves the element index and data for the edge.
        - Inverts the selected flag in the edge's data.
        - Stores the new selection state (selected).
    - Update Selected Edges:
        - Adds or removes the edge_id from the selected_edges set based on the new selection state.
    - Return Value:
        - Returns a string indicating the new selection state ("selected" or "unselected").

    Toggles edge selection.
    Handles potential invalid edge IDs and type conversions.
    '''

    def erase_previous_analysis_result(self, task_id, node_ids=None):
        """
        :param task_id:
        :param node_ids:
        :return:
        """
        if task_id == 'social_influence_analysis':
            for element in self.elements:
                if element['data']['element_type'] == 'node':
                    element['data']['social_influence_score'] = active_element_default_values['social_influence_score']
                    element['data']['visualisation_social_influence_score'] = \
                        active_element_default_values['visualisation_social_influence_score']
        elif task_id == 'community_detection':
            for element in self.elements:
                if element['data']['element_type'] == 'node':
                    element['data']['community'] = active_element_default_values['community']
                    element['data']['community_confidence'] = active_element_default_values['community_confidence']
        elif task_id == 'link_prediction':
            if node_ids is None:
                node_ids = set(self.active_nodes.keys())
            self.remove_predicted_edges(node_ids)
        elif task_id == 'node_embedding':
            return
        else:
            print('task {} is not supported', task_id)
    '''
    This function clears the results of previous analysis based on the specified task_id and optionally a set of node_ids.

    Parameters:
    - self: Instance of the class containing the function.
    - task_id: String identifier of the analysis task for which to erase results.
    - node_ids (optional): Set of node IDs (relevant for specific tasks).

    Steps:
    - Identify Task:
        - Uses conditional statements to identify the type of analysis based on task_id:
        - Social Influence Analysis: Resets social_influence_score and visualisation_social_influence_score for all nodes.
        - Community Detection: Resets community and community_confidence for all nodes.
        - Link Prediction: Calls remove_predicted_edges to remove predicted edges, optionally using the provided node_ids.
        - Node Embedding: Does nothing currently (placeholder).
        - Unsupported Task: Prints an error message.
    - Update Data Elements:
        - Iterates through elements in the data structure and updates relevant fields based on the chosen task.
    '''

    def get_active_edges(self, no_hidden_edges=True):
        """
        get list of edges
        :return:
        """
        if no_hidden_edges:
            edges = []
            for j in self.active_edges:
                element_index = self.active_edges[j]['element_index']
                element = self.elements[element_index]
                if not element['data']['hidden']:
                    edges.append(self.edges[j])
            return edges

        else:
            edges = [self.edges[j] for j in self.active_edges]
            return edges
    '''
    This function retrieves a list of active edges, optionally filtering out hidden edges.

    Parameters:
    - self: Instance of the class containing the function.
    - no_hidden_edges (optional, default=True): Boolean indicating whether to exclude hidden edges from the result.

    Steps:
    - Check for Hidden Edge Exclusion:
        - If no_hidden_edges is True:
            - Initializes an empty list edges to store the filtered edges.
            - Iterates through the active_edges dictionary:
                - Retrieves the element index for the current edge.
                - Accesses the corresponding element data.
                - Checks if the hidden flag in the element data is False (indicating a non-hidden edge).
                - If the edge is not hidden, appends it to the edges list.
            - Returns the filtered edges list.
    - Include All Active Edges:
        - If no_hidden_edges is False:
            - Directly constructs a list of edges using a list comprehension, including all edges from active_edges.
            - Returns this unfiltered list of edges.
    '''

    def compare_tasks(self, task):
        # TODO: to check more on parameters

        if self.last_analysis is None:
            return False
        if self.last_analysis['task_id'] == 'link_prediction':
            return False
        if self.last_analysis['task_id'] != task['task_id']:
            return False
        if self.last_analysis['options']['method'] != task['options']['method']:
            return False
        if task['task_id'] == 'community_detection':
            if 'K' in task['options']['parameters']:
                if 'K' in self.last_analysis['options']['parameters']:
                    if self.last_analysis['options']['parameters']['K'] != task['options']['parameters']['K']:
                        return False
        return True
    '''
    This function compares two tasks to determine if they are equivalent. This is likely used to avoid redundant computations or analyses.

    Parameters:
    - self: Instance of the class containing the function.
    - task: A dictionary representing a task to be compared.

    Steps:
    - Handle Initial Conditions:
        - If self.last_analysis is None (meaning no previous analysis exists), the function immediately returns False.
        - If the task_id of the previous analysis is 'link_prediction', the function returns False, as these tasks are always considered different.
    - Compare Basic Task Properties:
        - Checks if the task_id of the current and previous analyses are the same. If not, they are considered different and the function returns False.
        - Compares the method used in both tasks. If they differ, the function returns False.
    - Handle Special Case for Community Detection:
        - If the task_id is 'community_detection':
            - Checks if the K parameter exists in both tasks' options.
            - If K exists in both, compares their values. If they differ, the tasks are considered different and the function returns False.
    - Declare Tasks Equivalent:
        - If all the above conditions are met, the function concludes that the two tasks are equivalent and returns True.

    Compares tasks based on task_id, method, and (for community detection) the K parameter.
    Provides early exits for special cases (no previous analysis, link prediction).
    '''

    def apply_analysis(self, task_id, method, params, get_result=False, add_default_params=True):
        """
        perform analysis on the active network and update the according properties of elements

        :param task_id:
        :param method:
        :param params:
        :param get_result:
        :param add_default_params:
        :return:
        """

        network = {'edges': self.get_active_edges()}
        if add_default_params:
            if task_id == 'link_prediction':
                params['sources'] = list(self.selected_nodes)

        options = {'method': method, 'parameters': params}

        task = {'task_id': task_id,
                'network': network,
                'options': options}

        # print(task)
        if get_result:
            result = self.analyzer.perform_analysis(task=task, params=None)
            return result

        if self.compare_tasks(task):
            pass
        result = self.analyzer.perform_analysis(task=task, params=None)
        if result['success'] == 0:
            # print(result['message'])
            return
        self.last_analysis = {'task_id': task['task_id'], 'options': task['options']}
        #################################
        if task_id == 'social_influence_analysis':
            # erase previous result
            self.erase_previous_analysis_result(task_id='social_influence_analysis')
            self.erase_previous_analysis_result(task_id='community_detection')
            scores = result['scores']
            score_values = [score for _, score in scores.items()]
            min_score = min(score_values)
            max_score = max(score_values)
            # update the new result
            for node in scores:
                if node in self.active_nodes:
                    element_index = self.active_nodes[node]['element_index']
                    element = self.elements[element_index]
                    score = scores[node]
                    element['data']['social_influence_score'] = score
                    element['data']['visualisation_social_influence_score'] = helpers.min_max_scaling(score,
                                                                                                      min_score,
                                                                                                      max_score,
                                                                                                      (0.2, 0.99))

        #################################
        elif task_id == 'community_detection':
            # erase previous result
            self.erase_previous_analysis_result(task_id='social_influence_analysis')
            self.erase_previous_analysis_result(task_id='community_detection')
            # update the new result
            membership = result['membership']
            for node in membership:
                if node in self.active_nodes:
                    element_index = self.active_nodes[node]['element_index']
                    element = self.elements[element_index]
                    c, m = list(membership[node].items())[0]
                    element['data']['community'] = c
                    element['data']['community_confidence'] = m

        #################################
        elif task_id == 'link_prediction':
            # self.erase_previous_analysis_result('link_prediction', params['sources'])
            self.erase_previous_analysis_result('link_prediction')
            predictions = result['predictions']
            for source in predictions:
                # erase previous result
                self.remove_predicted_edges([source])
                if len(predictions[source]) > 0:
                    self.predicted_edges[source] = []
                # update the new result
                for target in predictions[source]:
                    predicted_edge_data = {'element_type': 'edge',
                                           'id': '{}_{}'.format(source, target),
                                           'source': source,
                                           'target': target,
                                           'type': 'predicted',
                                           'selected': False,
                                           'label': '',
                                           'predicted': True,
                                           'hidden': active_element_default_values['hidden'],
                                           'highlighted': active_element_default_values['highlighted'],
                                           'source_selected': True,
                                           'info': {'type': 'predicted'}}
                    predicted_element = {'group': 'edges', 'data': predicted_edge_data}
                    self.elements.append(predicted_element)
                    self.predicted_edges[source].append(len(self.elements) - 1)
        #################################
        elif task_id == 'node_embedding':
            pass
        #################################
        else:
            pass
    '''
    This function coordinates the execution of different network analysis tasks, updating the data structure with results and avoiding redundant computations.

    Parameters:
    - self: Instance of the class containing the function.
    - task_id: String identifier of the analysis task to perform.
    - method: The specific method to use for the analysis task.
    - params: A dictionary containing parameters for the analysis task.
    - get_result (optional, default=False): Boolean indicating whether to return the raw analysis result.
    - add_default_params (optional, default=True): Boolean controlling whether to add default parameters.

    Steps:
    - Construct Analysis Task:
        - Retrieves active edges using get_active_edges().
        - Optionally adds default parameters (e.g., for link prediction).
        - Compiles the task dictionary containing task ID, network, and options.
    - Perform Analysis (if not already done):
        - If get_result is True, directly calls the analyzer and returns the result.
        - If the current task is equivalent to the previous analysis (based on compare_tasks), skips execution.
        - Otherwise, calls the analyzer to perform the analysis and checks for success.
    - Handle Analysis Results:
        - Stores the task details in self.last_analysis.
        - Uses conditional statements to handle different task types:
            - Social Influence Analysis:
                - Erases previous results for social influence and community detection.
                - Updates node scores and scaled scores in the data structure.
            - Community Detection:
                - Erases previous results for social influence and community detection.
                - Updates node communities and confidence scores in the data structure.
            - Link Prediction:
                - Erases previous link prediction results.
                - Adds predicted edges to the data structure with appropriate metadata.
            - Node Embedding (placeholder):
                - Currently does nothing.

    Centralizes analysis execution and result updating.
    Manages analysis history to avoid redundant computations.
    Handles different task types with specific result handling logic.
    '''

    def dump_network(self, filename, output_dir):
        """
        dump the whole network to a specified directory
        will fail if file already exists
        """
        try:
            output_path = Path(output_dir) / filename
            # with open(output_path, "x") as output_file:
            with open(output_path, "w") as output_file:
                ##############################
                # all the nodes
                for node in self.nodes:
                    node_info = {
                        'id': node,
                        'type': 'node',
                        'properties': self.nodes[node]
                    }
                    json.dump(node_info, output_file)
                    output_file.write('\n')
                ##############################
                # all the edges
                for edge in self.edges:  # type weight confidence
                    edge_info = edge.copy()
                    edge_info['type'] = 'edge'
                    json.dump(edge_info, output_file)
                    output_file.write('\n')
                ##############################
                # all the active nodes
                for node in self.active_nodes:
                    node_info = {
                        'id': node,
                        'type': 'active_node',
                        'properties': self.active_nodes[node]
                    }
                    json.dump(node_info, output_file)
                    output_file.write('\n')
                ##############################
                # all the active edges:
                for edge in self.active_edges:
                    edge_info = {
                        'id': edge,
                        'type': 'active_edge',
                        'properties': self.active_edges[edge]
                    }
                    json.dump(edge_info, output_file)
                    output_file.write('\n')
                ##############################
                # all predicted edges
                for node in self.predicted_edges:
                    node_info = {
                        'id': node,
                        'type': 'predicted_edge',
                        'edges': self.predicted_edges[node]
                    }
                    json.dump(node_info, output_file)
                    output_file.write('\n')
                ##############################
                # all the elements
                for element in self.elements:
                    elment_info = {
                        'type': 'active_element',
                        'properties': element
                    }
                    json.dump(elment_info, output_file)
                    output_file.write('\n')
                ##############################
                # last analysis
                analysis_info = {
                    'type': 'last_analysis',
                    'properties': self.last_analysis
                }
                json.dump(analysis_info, output_file)
                output_file.write('\n')
                ##############################
            return 1
        except Exception as e:
            return e
    '''
    Saves the entire network structure, including nodes, edges, and analysis data, to a JSON file in a specified directory.

    Parameters:
    - self: Instance of the class containing the function.
    - filename: String containing the desired filename for the output file.
    - output_dir: String specifying the directory where the file should be saved.

    Steps:
    - Construct Output Path:
        - Combines the provided filename and output directory to create the full file path.
    - Open Output File:
        - Opens the output file in write mode ("w").
    - Serialize Network Data:
        - Iterates through various network components, serializing each one as a JSON object and writing it to the file:
            - Nodes
            - Edges
            - Active nodes
            - Active edges
            - Predicted edges
            - Elements
            - Last analysis data
    - Handle Errors:
        - Uses a try-except block to catch any exceptions that might occur during the process.
        - If successful, returns 1.
        - If an exception occurs, returns the exception object for further handling.

    Serializes the network structure as a collection of JSON objects.
    Writes each object to a separate line in the file.
    Includes various network components for comprehensive preservation.
    Employs error handling to manage potential issues.
    '''

    def serialize_network(self):
        """
        serialize the whole network into a byte array
        """

        # try:
        mem = io.BytesIO()
        ##############################
        # all the nodes
        for node in self.nodes:
            if node:
                node_info = {
                    'id': node,
                    'type': 'node',
                    'properties': self.nodes[node]
                }
                node_str = '{}\n'.format(json.dumps(node_info))
                mem.write(node_str.encode('utf-8'))
        ##############################
        # all the edges
        for edge in self.edges:
            if edge:
            # type weight confidence
                edge_info = edge.copy()
                edge_info['type'] = 'edge'
                edge_str = '{}\n'.format(json.dumps(edge_info))
                mem.write(edge_str.encode('utf-8'))
        ##############################
        # all the active nodes
        for node in self.active_nodes:
            if node:
                node_info = {
                    'id': node,
                    'type': 'active_node',
                    'properties': self.active_nodes[node]
                }
                node_str = '{}\n'.format(json.dumps(node_info))
                mem.write(node_str.encode('utf-8'))
        ##############################
        # all the active edges:
        for edge in self.active_edges:
            if edge:
                edge_info = {
                    'id': edge,
                    'type': 'active_edge',
                    'properties': self.active_edges[edge]
                }
                edge_str = '{}\n'.format(json.dumps(edge_info))
                mem.write(edge_str.encode('utf-8'))
        ##############################
        # all predicted edges
        for node in self.predicted_edges:
            if node:
                node_info = {
                    'id': node,
                    'type': 'predicted_edge',
                    'edges': self.predicted_edges[node]
                }
                node_str = '{}\n'.format(json.dumps(node_info))
                mem.write(node_str.encode('utf-8'))
        ##############################
        # all the elements
        for element in self.elements:
            if element:
                elment_info = {
                    'type': 'active_element',
                    'properties': element
                }
                element_str = '{}\n'.format(json.dumps(elment_info))
                mem.write(element_str.encode('utf-8'))
        ##############################
        # last analysis
        analysis_info = {
            'type': 'last_analysis',
            'properties': self.last_analysis
        }
        analysis_str = '{}\n'.format(json.dumps(analysis_info))
        mem.write(analysis_str.encode('utf-8'))
        ##############################
        mem.seek(0)
        return {'success': 1, 'mem_object': mem}
        # except Exception as e:
        #    return {'success': 0, 'exception': e}
    '''
    This function serializes the entire network structure, including nodes, edges, and analysis data, into a byte array format. This byte array can be used for further processing or storage.

    Parameters:
    - self: An instance of the class containing the function.

    Output:
    - A dictionary with two keys:
        - success: An integer indicating whether the serialization was successful (1) or not (0).
        - mem_object: A io.BytesIO object containing the serialized network data as a byte array, if successful.

    Steps:
    - Create Byte Array Object:
        - Initializes an io.BytesIO object named mem to store the serialized data.
    - Serialize Network Components:
        - Iterates through various network components, serializing each one as a JSON object and writing it to the byte array:
            - Nodes:
                - Skips empty nodes (if node).
                - Creates a JSON object with node ID, type, and properties.
                - Serializes the object to a string with a newline character.
                - Writes the string (encoded as UTF-8) to the byte array.
            - Edges, Active Nodes, Active Edges, Predicted Edges, Elements:
                - Similar logic as for nodes, checking for empty values and adding type information.
            - Last Analysis:
                - Creates a JSON object with type and properties.
                - Serializes and writes it to the byte array.
    - Return Serialized Data:
        - Sets the mem object's position to the beginning (seek(0)).
        - Returns a dictionary with success as 1 and mem_object containing the serialized byte array.
    '''

    def serialize_network_new_format(self):
        """
        serialize the whole network into a byte array
        """
        mem = io.BytesIO()

        data = {}

        if self.meta_info:
            data.update(self.meta_info)

        ##############################
        # all the nodes

        data['nodes'] = []

        for node in self.nodes:
            if node:
                data['nodes'].append(self.nodes[node])

        data['links'] = []

        ##############################
        # all the edges
        for edge in self.edges:
            if edge:
                d = edge['properties']
                d['source'] = edge['source']
                d['target'] = edge['target']
                data['links'].append(d)

        string_data = json.dumps(data, indent=4)
        mem.write(string_data.encode('utf-8'))
        ##############################
        mem.seek(0)
        return {'success': 1, 'mem_object': mem}
        # except Exception as e:
        #    return {'success': 0, 'exception': e}
    '''
    This function serializes the entire network structure, including nodes, edges, and (optionally) meta information, into a byte array in a new format. This byte array can be used for further processing or storage.

    Parameters:
    - self: An instance of the class containing the function.

    Output:
    - A dictionary with two keys:
        - success: An integer indicating whether the serialization was successful (1) or not (0).
        - mem_object: A io.BytesIO object containing the serialized network data as a byte array, if successful.

    Steps:
    - Create Byte Array Object:
        - Initializes an io.BytesIO object named mem to store the serialized data.
    - Initialize Data Dictionary:
        - Creates an empty dictionary data to hold the serialized network information.
    - Include Meta Information (Optional):
        - Checks if self.meta_info exists (assuming it contains network metadata).
        - If so, merges the metadata into the data dictionary.
    - Serialize Nodes:
        - Creates a list named nodes within the data dictionary.
        - Iterates through each node in self.nodes.
            - Skips empty nodes (if node).
            - Appends the corresponding node's data (presumably a dictionary) to the nodes list.
    - Serialize Edges:
        - Creates a list named links within the data dictionary.
        - Iterates through each edge in self.edges.
            - Skips empty edges (if edge).
            - Extracts the edge properties into a dictionary d.
            - Adds source and target keys to d from the edge data.
            - Appends d to the links list.
    - Create and Write JSON String:
        - Serializes the data dictionary to a JSON string with indentation for readability (indent=4).
        - Encodes the string as UTF-8 and writes it to the mem byte array.
    - Return Serialized Data:
        -Sets the mem object's position to the beginning (seek(0)).
        - Returns a dictionary with success as 1 and mem_object containing the serialized byte array.

    Serializes the network data in a dictionary-based format with separate lists for nodes and edges.
    Includes source and target keys explicitly for edges.
    Provides optional inclusion of meta information.
    Uses JSON for human-readable and interoperable format.
    Returns a dictionary indicating success and providing the serialized data.
    '''

    def load_from_file(self, path_2_data):
        try:
            # reset the current containers
            self.nodes = {}
            self.edges = []
            self.adj_list = {}
            self.node_types = set()
            self.edge_types = set()

            self.active_nodes = {}
            self.active_edges = {}

            self.elements = []
            #
            self.network_name = None
            self.node_label_field = None
            self.edge_label_field = None
            #
            self.predicted_edges = {}
            self.last_analysis = None
            self.selected_nodes = set()
            self.selected_edges = set()
            self.recent_interactions = []

            # load from file

            file = open(path_2_data, 'r')
            for line in file:
                if line.startswith('#'):  # ignore the comments
                    continue
                line_object = json.loads(line.strip())
                #####################################
                # nodes
                if line_object['type'] == 'node':
                    node = line_object['properties']
                    self.nodes[line_object['id']] = node
                    if 'type' in node:
                        self.node_types.add(node['type'])
                #####################################
                # edges
                elif line_object['type'] == 'edge':
                    edge = {'source': line_object['source'], 'target': line_object['target'],
                            'observed': True, 'properties': line_object['properties']}
                    self.edges.append(edge)
                    e_index = len(self.edges) - 1
                    source = edge['source']
                    if source in self.adj_list:
                        self.adj_list[source].append(e_index)
                    else:
                        self.adj_list[source] = [e_index]
                    if 'type' in line_object['properties']:
                        self.edge_types.add(line_object['properties']['type'])
                #####################################
                # active nodes
                elif line_object['type'] == 'active_node':
                    node = line_object['properties']
                    self.active_nodes[line_object['id']] = node

                #####################################
                # active edges
                elif line_object['type'] == 'active_edge':
                    edge = line_object['properties']
                    self.active_edges[line_object['id']] = edge
                    pass
                #####################################
                # predicted edges
                elif line_object['type'] == 'predicted_edge':
                    node = line_object['id']
                    edges = line_object['edges']
                    self.predicted_edges[node] = edges
                #####################################
                # active elements
                elif line_object['type'] == 'active_element':
                    element = line_object['properties']
                    self.elements.append(element)
                #####################################
                # last analysis
                elif line_object['type'] == 'last_analysis':
                    self.last_analysis = line_object['properties']
                #####################################
                else:
                    continue
            self.edge_types = list(self.edge_types)
            self.node_types = list(self.node_types)
        except Exception as e:
            return e
    '''
    This function loads the network structure and data from a specified file in JSON format. It populates various internal data structures to represent the loaded network.

    Parameters:
    - self: An instance of the class containing the function.
    - path_2_data: String indicating the path to the file containing the network data.

    Output:
    - If successful, it returns None.
    - If an exception occurs during loading, it returns the exception object.

    Steps:
    - Reset Network Containers:
        - Empties various data structures (nodes, edges, active nodes, etc.) to prepare for loading new data.
    - Open and Read File:
        - Opens the specified file in read mode ('r').
        - Iterates through each line in the file.
    - Process Line:
        - Skips comments starting with #.
        - Loads the line content as a JSON object (line_object).
    - Handle Object Type:
        - Uses conditional statements to handle different object types based on the type field:
            - Node:
                - Adds the node data to the nodes dictionary with its ID as the key.
                - Updates node_types if a type field exists in the node data.
            - Edge:
                - Creates an edge dictionary with source, target, observed flag, and properties.
                - Adds the edge to the edges list and updates the adjacency list (adj_list).
                - Updates edge_types if a type field exists in the edge properties.
            - Active Node:
                - Adds the active node data to the active_nodes dictionary with its ID as the key.
            - Active Edge:
                - Adds the active edge data to the active_edges dictionary with its ID as the key.
            - Predicted Edge:
                - Adds the predicted edges for a specific node to the predicted_edges dictionary.
            - Active Element:
                - Appends the active element data to the elements list.
            - Last Analysis:
                - Updates the last_analysis data structure with the loaded properties.
            - Others:
                - Skips any unrecognized object types.
    - Convert Sets to Lists:
        - Converts node_types and edge_types sets to lists for internal usage.
    - Handle Exceptions:
        - Uses a try-except block to catch any exceptions during the loading process.
        - If an exception occurs, returns the exception object.

    Loads network data from a JSON file line by line.
    Handles different object types (nodes, edges, active elements, etc.) based on a "type" field.
    Updates various internal data structures to represent the loaded network.
    Returns successfully if loading is complete, otherwise returns the encountered exception.
    '''

    def deserialize_network(self, uploaded_file, initialize=True):
        """

        :param uploaded_file:
        :return:
        """
        # try:
        # reset the current containers
        self.nodes = {}
        self.edges = []
        self.adj_list = {}
        self.node_types = {}
        self.edge_types = {}

        self.active_nodes = {}
        self.active_edges = {}

        self.elements = []
        #
        self.network_name = None
        self.node_label_field = None
        self.edge_label_field = None
        #
        self.predicted_edges = {}
        self.last_analysis = None
        self.selected_nodes = set()
        self.selected_edges = set()
        self.recent_interactions = []
        #
        self.meta_info = {}

        # load from file

        print('\t\t DESERIALIZING')

        content_type, content_string = uploaded_file.split(',')
        decoded = base64.b64decode(content_string).decode('utf-8')

        # convert from new to old format
        if decoded.startswith("{\n"):
            in_data = json.loads(decoded)
            data_list = converter.new_to_old(in_data)
            try:
                self.meta_info['directed'] = in_data['directed']
                self.meta_info['multigraph'] = in_data['multigraph']
                self.meta_info['graph'] = in_data['graph']
            except KeyError:
                print('Input JOSN must have directed, multigraph and graph fields. See specification for information.')
        else:
            # a = json.loads(decoded)
            data_list = [json.loads(line.strip()) for line in decoded.split('\n') if len(line)!=0 and not line.startswith('#')]

        # print('decoded = ', decoded)
        for line_object in data_list:
            #####################################
            # nodes
            if line_object['type'] == 'node':
                node = line_object['properties']
                self.nodes[line_object['id']] = node
                if 'type' in node:
                    node_type = node['type']
                    if node_type in self.node_types:
                        self.node_types[node_type] += 1
                    else:
                        self.node_types[node_type] = 1
            #####################################
            # edges
            elif line_object['type'] == 'edge':
                edge = {'source': line_object['source'], 'target': line_object['target'],
                        'observed': True, 'properties': line_object['properties']}
                self.edges.append(edge)
                e_index = len(self.edges) - 1
                source, target = edge['source'], edge['target']
                if source in self.adj_list:
                    self.adj_list[source].append(e_index)
                else:
                    self.adj_list[source] = [e_index]

                if target in self.in_adj_list:
                    self.in_adj_list[target].append(e_index)
                else:
                    self.in_adj_list[target] = [e_index]

                if 'type' in line_object['properties']:
                    edge_type = line_object['properties']['type']
                    if edge_type in self.edge_types:
                        self.edge_types[edge_type] += 1
                    else:
                        self.edge_types[edge_type] = 1
            #####################################
            # active nodes
            elif line_object['type'] == 'active_node':
                node = line_object['properties']
                self.active_nodes[line_object['id']] = node

            #####################################
            # active edges
            elif line_object['type'] == 'active_edge':
                edge = line_object['properties']
                self.active_edges[line_object['id']] = edge
                pass
            #####################################
            # predicted edges
            elif line_object['type'] == 'predicted_edge':
                node = line_object['id']
                edges = line_object['edges']
                self.predicted_edges[node] = edges
            #####################################
            # active elements
            elif line_object['type'] == 'active_element':
                element = line_object['properties']
                self.elements.append(element)
                # selected nodes
                if element['data']['element_type'] == 'node':
                    if element['data']['selected']:
                        self.selected_nodes.add(element['data']['id'])
                else:
                    if element['data']['selected']:
                        self.selected_edges.add(element['data']['id'])
            #####################################
            # last analysis
            elif line_object['type'] == 'last_analysis':
                self.last_analysis = line_object['properties']
            #####################################
            else:
                continue
        # self.edge_types = list(self.edge_types)
        # self.node_types = list(self.node_types)
        # except Exception as e:
        #    return e

        # initialize the active if it is blank
        if initialize:
            if len(self.elements) == 0:
                self.initialize()
    '''
    This function deserializes network data from a provided uploaded file in JSON format and populates the internal data structures of the class to represent the loaded network.

    Parameters:
    - self: An instance of the class containing the function.
    - uploaded_file: A file object representing the uploaded data.
    - initialize: Boolean flag indicating whether to initialize active elements if none are found (True by default).

    Output:
    - None (implicitly indicates successful deserialization).
    
    Steps:
    - Reset Network Containers:
        - Clears various data structures (nodes, edges, active_nodes, etc.) to prepare for loading new data.
    - Process Uploaded File:
        - Decodes the file content from base64 and converts it to a string.
        - Checks if the JSON starts with an object ("{\n") to determine format:
            - New format:
                - Converts the JSON string to a dictionary using json.loads.
                - Uses the converter.new_to_old function to convert to the old format (internal list of dictionaries).
                - Extracts metadata (directed, multigraph, graph) if present.
            - Old format:
                - Splits the decoded string by newline, removes empty lines and comments, and loads each line as a JSON dictionary.
    - Iterate Through Data Lines:
        - For each line object (dictionary):
            - Handle object type based on the type field:
                - Node:
                    - Adds the node data to the nodes dictionary with its ID as the key.
                    - Updates node_types dictionary with the node's type (if present).
                - Edge:
                    - Creates an edge dictionary with source, target, observed flag, and properties.
                    - Adds the edge to the edges list and updates the adjacency lists (adj_list, in_adj_list).
                    - Updates edge_types dictionary with the edge's type (if present).
                - Active Node:
                    - Adds the active node data to the active_nodes dictionary with its ID as the key.
                - Active Edge:
                    - Adds the active edge data to the active_edges dictionary with its ID as the key.
                - Predicted Edge:
                    - Adds the predicted edges for a specific node to the predicted_edges dictionary.
                - Active Element:
                    - Appends the active element data to the elements list.
                    - Updates selected_nodes and selected_edges sets based on the element's data.
                - Last Analysis:
                    - Updates the last_analysis data structure with the loaded properties.
                - Others:
                    - Skips unrecognized object types.
    - Initialize Active Elements if Needed:
        - If initialize is True and no elements are found, calls the initialize function (presumably to set default active elements).

    Deserializes network data from an uploaded file in either new or old JSON format.
    Handles different object types (nodes, edges, active elements, etc.) based on a "type" field.
    Updates various internal data structures to represent the loaded network.
    Optionally initializes active elements if none are found during deserialization.
    '''

    def print_elements(self):
        for e in self.elements:
            print(e)
    '''
    This function iterates through all elements stored in the elements attribute of the class instance and prints each element to the console.

    Parameters:
    - self: This refers to the current instance of the class where the function is called.

    Steps:
    - Looping Through Elements:
        - The for e in self.elements: line starts a loop that iterates over each element within the elements attribute of the current class instance (self).
    - Printing Each Element:
        - Inside the loop, the line print(e) simply prints the current element (e) to the console.
    - Assumptions:
        - The elements attribute is assumed to be a list or iterable containing the elements to be printed.
        - Each element (e) is assumed to have a string representation that can be directly printed.
    '''

    def forget_interactions(self):
        if len(self.recent_interactions) > max_num_recent_interactions:
            self.recent_interactions = self.recent_interactions[-max_num_recent_interactions:]
    '''
    This function manages a history of interactions stored in the recent_interactions attribute of the class instance.

    Steps:
    - Check Interaction History Length:
        - The code starts by checking if the length of the recent_interactions list is greater than max_num_recent_interactions. This max_num_recent_interactions variable is likely defined elsewhere in the class and specifies the maximum number of interactions to remember.
    - Truncate Interaction History (if needed):
        - If the interaction history is longer than the allowed limit, the function uses slicing to keep only the most recent max_num_recent_interactions items. The slicing expression [-max_num_recent_interactions:] selects elements from the end of the list up to the specified number from the end.

    Assumptions:
    - max_num_recent_interactions is a defined variable within the class.
    - recent_interactions is a list-like object that supports slicing.
    '''

    def update_an_active_node(self, node, properties):
        """
        update properties of an active node
        :param node:id of the node to be updated
        :param properties: dictionary
        :return:
        """
        print('********************************************')
        print('update_an_active_node: node = ', node)
        print('update_an_active_node: properties = ', properties)
        if node not in self.active_nodes:
            return {'success': 0, 'message': 'node is not active!'}
        else:
            pre_properties = copy.deepcopy(self.nodes[node])
            # update in the underlying network
            result = self.update_a_node(node, properties=properties)
            # print(result)
            if result['success'] == 1:
                # update the corresponding active element
                element_index = self.active_nodes[node]['element_index']
                # update the type
                if 'type' in properties:
                    self.elements[element_index]['data']['type'] = properties['type']
                # add name field as 'label' to resemble changes in visualizer.
                if 'name' in properties:
                    self.elements[element_index]['data']['label'] = properties['name']
                if self.node_label_field is not None:
                    if self.node_label_field in properties:
                        self.elements[element_index]['data']['label'] = properties[self.node_label_field]

                # remember the interaction
                interaction = {'action': node_update_action, 'node': node, 'pre_properties': pre_properties}
                self.recent_interactions.append(interaction)
                self.forget_interactions()
                return {'success': 1, 'message': 'node updated successfully!'}
            else:
                return result
    '''
    This function updates the properties of an active node, taking into account both the underlying network data and the visual representation of the active element.

    Parameters:
    - self: An instance of the class containing the function.
    - node: ID of the node to be updated.
    - properties: Dictionary containing new properties for the node.

    Output:
    - Dictionary with keys:
        - success: Integer indicating success (1) or failure (0).
        - message: String describing the outcome.

    Steps:
    - Logging and Input Validation:
        - Prints debug messages with input parameters.
        - Checks if the node ID exists in active_nodes. If not, returns an error message.
    - Update Underlying Network:
        - Makes a deep copy of the current node properties before update.
        - Calls update_a_node (presumably from the same class) to update the node in the underlying network structure.
        - If the update in the network is successful:
            - Retrieves the index of the corresponding active element based on the node ID.
            - Updates the element's type and label fields based on the provided properties (type and name keys).
            - If a node_label_field is defined, also updates the label using the corresponding value from the properties.
            - Records the interaction (update action, node, previous properties) in the recent_interactions list.
            - Trims the interaction history if it exceeds the limit.
            - Returns a success message.
        - Otherwise, propagates the error message from the network update.
    
    This function acts as a bridge between updating the node in the network and updating the corresponding visual representation of the active element.
    '''

    def add_an_active_node(self, node, properties):
        """
        add a node into active network
        :param node: id of the node
        :param properties: dictionary
        :return:
        """
        # try to add the node into the underlying network
        result = self.add_a_node(node, properties=properties)
        if result['success'] == 1:
            if 'name' not in properties:
                properties['name'] = ''
            # activate the node
            node_data = {'element_type': 'node',
                         'id': node,
                         'type': properties['type'],
                         'label': properties['name'],
                         'selected': active_element_default_values['selected'],
                         'expandable': active_element_default_values['expandable'],
                         'community': active_element_default_values['community'],
                         'community_confidence': active_element_default_values['community_confidence'],
                         'social_influence_score': active_element_default_values['social_influence_score'],
                         'visualisation_social_influence_score':
                             active_element_default_values['visualisation_social_influence_score'],
                         'hidden': active_element_default_values['hidden'],
                         'highlighted': active_element_default_values['highlighted'],
                         'num_incoming_neighbor_selected': active_element_default_values[
                             'num_incoming_neighbor_selected'],
                         'incoming_neighbor_selected': active_element_default_values['incoming_neighbor_selected'],
                         'info': properties}
            # add label
            if self.node_label_field is not None:
                if self.node_label_field in properties:
                    node_data['label'] = properties[self.node_label_field]
                else:
                    node_data['label'] = node
            else:
                node_data['label'] = node_data['id']
            # check expandability
            node_data['expandable'] = False
            element = {'group': 'nodes', 'data': node_data}
            self.elements.append(element)
            self.active_nodes[node] = {'expandable': False, 'element_index': len(self.elements) - 1}

            interaction = {'action': node_add_action, 'node': node, 'properties': copy.deepcopy(properties)}
            self.recent_interactions.append(interaction)
            self.forget_interactions()
            return {'success': 1, 'message': 'node  added successfully!'}
        else:
            return result
    '''
    Adds a new node to the underlying network and activates it, making it visible and interactive in the visual representation.

    Parameters:
    - self: An instance of the class containing the function.
    - node: ID of the node to be added.
    - properties: Dictionary containing properties for the node.

    Ouput:
    - Dictionary with keys:
        - success: Integer indicating success (1) or failure (0).
        -message: String describing the outcome.

    Steps:
    - Add Node to Underlying Network:
        - Calls self.add_a_node (presumably from the same class) to add the node to the network structure.
        - If the addition is successful:
    - Activate Node:
        - Creates a node_data dictionary containing information needed for visual representation:
            - Type, label, selection status, expandability, community information, social influence scores, visibility, highlighting, incoming neighbor properties, and all node properties.
        - Sets the label based on node_label_field if applicable, otherwise uses the node ID as the label.
        - Sets expandable to False (assumed non-expandable by default).
        - Creates an element dictionary for the node and adds it to the elements list.
        - Adds the node to the active_nodes dictionary along with its expandability and element index.
    - Record Interaction:
        - Adds an interaction record to recent_interactions for undo/redo functionality.
        - Trims the interaction history if it exceeds the limit.
    - Return Result:
        - Returns a success message if node addition and activation were successful.
        - Otherwise, propagates the error message from the network addition.

    Bridges between network structure and visual representation for node additions.
    Manages expandability and labeling based on configuration.
    Supports undo/redo functionality through interaction history.
    '''

    def update_an_active_edge(self, edge_id, properties):
        """
        update properties of an active edge
        :param edge_id: integer, id of the edge
        :param properties: dictionary
        :return:
        """
        if edge_id not in self.active_edges:
            return {'success': 0, 'message': 'edge is not active!'}
        else:
            edge = self.edges[edge_id]
            pre_properties = copy.deepcopy(self.edges[edge_id]['properties'])
            source, target = edge['source'], edge['target']
            result = self.update_an_edge(edge_id, properties=properties, is_index=True)
            if result['success'] == 1:
                # update the type
                if 'type' in properties:
                    element_index = self.active_edges[edge_id]['element_index']
                    self.elements[element_index]['data']['type'] = properties['type']
                # update the probability
                if 'probability' in properties:
                    element_index = self.active_edges[edge_id]['element_index']
                    self.elements[element_index]['data']['probability'] = properties['probability']
                # remember the interaction
                interaction = {'action': edge_update_action,
                               'edge': {'e_index': edge_id, 'source': source, 'target': target},
                               'pre_properties': pre_properties}
                self.recent_interactions.append(interaction)
                self.forget_interactions()
                return {'success': 1, 'message': 'node updated successfully!'}
            else:
                return result
    '''
    Updates the properties of an active edge in both the underlying network and its visual representation.

    Parameters:
    - self: An instance of the class containing the function.
    - edge_id: Integer representing the ID of the edge to be updated.
    - properties: Dictionary containing the new properties for the edge.

    Output:
    - Dictionary with keys:
        - success: Integer indicating success (1) or failure (0).
        - message: String describing the outcome.

    Steps:
    - Check Edge Activity:
        - If the edge ID is not found in active_edges, returns an error message indicating the edge is not active.
    - Update Underlying Edge:
        - Retrieves the edge information and creates a copy of its current properties.
        - Calls self.update_an_edge (presumably from the same class) to update the edge in the underlying network structure.
        - If the update in the network is successful:
    - Update Visual Representation:
        - Updates the type and probability fields of the corresponding active element based on the provided properties.
    - Record Interaction:
        - Adds an interaction record to recent_interactions for undo/redo functionality.
        - Trims the interaction history if it exceeds the limit.
    - Return Result:
        - Returns a success message if the update was successful.
        - Otherwise, propagates the error message from the network update.

    Bridges between network structure and visual representation for edge updates.
    Manages type and probability fields for visual elements.
    Supports undo/redo functionality through interaction history.
    '''

    def add_an_active_edge(self, source, target, properties):
        """
        add an edge into the active network
        :param source: id of the source node
        :param target: id of the target node
        :param properties: dictionary
        :return:
        """
        if source not in self.active_nodes:
            return {'success': 0, 'message': 'source not active!'}
        if target not in self.active_nodes:
            return {'success': 0, 'message': 'target not active!'}
        # trying to add the edge into the underlying network
        result = self.add_an_edge(source, target, properties=properties)
        if result['success'] == 1:
            # active the edge
            e_index = len(self.edges) - 1
            edge_info = self.edges[e_index]
            edge_data = {'element_type': 'edge',
                         'id': e_index,
                         'source': edge_info['source'],
                         'target': edge_info['target'],
                         'type': active_element_default_values['type'],
                         'label': active_element_default_values['label'],
                         'selected': active_element_default_values['selected'],
                         'predicted': active_element_default_values['predicted'],
                         'hidden': active_element_default_values['hidden'],
                         'highlighted': active_element_default_values['highlighted'],
                         'source_selected': active_element_default_values['source_selected'],
                         'info': edge_info['properties']}
            # add type
            if 'type' in edge_info['properties']:
                edge_data['type'] = edge_info['properties']['type']
            # add edge label
            if self.edge_label_field is not None:
                if self.edge_label_field in edge_info:
                    edge_data['label'] = edge_info[self.edge_label_field]
            else:
                edge_data['label'] = ''  # blank label

            element = {'group': 'edges', 'data': edge_data}
            self.elements.append(element)
            self.active_edges[e_index] = {'element_index': len(self.elements) - 1}

            interaction = {'action': edge_add_action,
                           'edge': {'e_index': e_index, 'source': source, 'target': target},
                           'properties': properties}
            self.recent_interactions.append(interaction)
            self.forget_interactions()
    '''
    Adds a new edge between two active nodes to the network.
    Makes the added edge visually active and interactive.

    Parameters:
    - self: An instance of the class containing the function.
    - source: ID of the source node for the edge.
    - target: ID of the target node for the edge.
    - properties: Dictionary containing additional properties for the edge (optional).

    Output:
    - Dictionary with keys:
        - success: Integer indicating success (1) or failure (0).
        - message: String describing the outcome.

    Steps:
    - Check Node Activity:
        - Verifies if both source and target nodes are active (present in active_nodes).
        - If either node is not active, returns an error message.
    - Add Edge to Underlying Network:
        - Calls self.add_an_edge (presumably from the same class) to add the edge to the underlying network structure.
        - If the network addition is successful:
    - Activate Edge Visually:
        - Retrieves the newly added edge information from self.edges.
        - Creates an edge_data dictionary containing information for visual representation:
            - Element type (edge).
            - Edge ID, source, target, type, label, selection status, prediction status, hidden status, highlighted status, source selection status, and edge properties.
        - Sets the edge type based on available properties in edge_info.
        - Sets the edge label based on edge_label_field if applicable, otherwise uses an empty string.
        - Creates an element dictionary and adds it to the elements list.
        - Adds the edge to the active_edges dictionary along with its element index.
    - Record Interaction:
        - Adds an interaction record to recent_interactions for undo/redo functionality.
        - Trims the interaction history if it exceeds the limit.
    - Return Result:
        - Returns a success message if the edge addition and activation were successful.

    Ensures both source and target nodes are active before adding the edge.
    Manages edge type, label, and visibility in the visual representation.
    Supports undo/redo through interaction history.
    '''

    def delete_an_active_edge(self, edge_id):
        """
        delete an edge from the active network
        :param edge_id: integer, id of the edge
        :return:
        """
        if edge_id not in self.active_edges:
            return {'success': 0, 'message': 'edge is not active!'}
        else:
            # deactivate the edge
            element_index = self.active_edges[edge_id]['element_index']
            self.selected_edges.remove(edge_id)
            self.remove_element([element_index])
            # deleted the edge from the underlying network
            edge = self.edges[edge_id]
            source, target = edge['source'], edge['target']
            properties = copy.deepcopy(edge['properties'])

            self.delete_an_edge(edge_id, is_index=True)

            interaction = {'action': edge_delete_action,
                           'edge': {'e_index': edge_id, 'source': source, 'target': target},
                           'properties': properties}
            self.recent_interactions.append(interaction)
            self.forget_interactions()
    '''
    Deletes an active edge from both the underlying network data and its visual representation.

    Parameters:
    - self: An instance of the class containing the function.
    - edge_id: Integer representing the ID of the edge to be deleted.

    Output:
    - Dictionary with keys:
        - success: Integer indicating success (1) or failure (0).
        - message: String describing the outcome.

    Steps:
    - Check Edge Activity:
        - If the edge ID is not found in active_edges, returns an error message indicating the edge is not active.
    - Deactivate Edge Visually:
        - Retrieves the element index of the edge from active_edges.
        - Removes the edge ID from the selected_edges list (presumably for visual selection).
        - Calls self.remove_element (presumably from the same class) to remove the edge's visual element.
    - Delete Edge from Underlying Network:
        - Retrieves the edge information from self.edges.
        - Stores the edge's source, target, and properties for interaction history.
        - Calls self.delete_an_edge (presumably from the same class) to delete the edge from the underlying network structure.
    - Record Interaction:
        - Adds an interaction record to recent_interactions for undo/redo functionality.
        - Trims the interaction history if it exceeds the limit.
    - Return Result:
        - Returns a success message if the edge deletion was successful.

    Ensures the edge is active before deletion.
    Manages visual representation and underlying network structure.
    Supports undo/redo through interaction history.
    '''

    def delete_an_active_node(self, node):
        """
        delete a node from the active network
        :param node:
        :return:
        """
        if node not in self.active_nodes:
            return {'success': 0, 'message': 'node is not active!'}
        else:
            # deactivate the node
            self.deactivate_nodes([node])
            # delete the node from the underlying network
            properties = copy.deepcopy(self.nodes[node])

            self.delete_a_node(node)

            interaction = {'action': node_delete_action, 'node': node, 'properties': properties}
            self.recent_interactions.append(interaction)
            self.forget_interactions()
    '''
    This function removes a node from the active network, both visually and from the underlying data structure.

    Parameters:
    - self: An instance of the class containing the function.
    - node: ID of the node to be deleted.

    Output:
    - Dictionary with keys:
        - success: Integer indicating success (1) or failure (0).
        - message: String describing the outcome.

    Steps:
    - Check Node Activity:
        - Verifies if the node is present in active_nodes.
        - If not, returns an error message indicating the node is not active.
    - Deactivate Node Visually:
        - Calls self.deactivate_nodes (presumably from the same class) to handle visual deactivation, likely removing it from the visualization.
    - Delete Node from Underlying Network:
        - Makes a deep copy of the node's properties for later use.
        - Calls self.delete_a_node (presumably from the same class) to delete the node from the underlying network structure.
    - Record Interaction:
        - Adds an interaction record to recent_interactions for undo/redo functionality.
        - Stores the deleted node's ID and its properties.
        - Trims the interaction history if it exceeds the limit.
    - Return Result:
        - Returns a success message if the node deletion was successful.
    '''

    def merge_active_nodes(self, nodes, new_node, new_properties):
        """
        merge a list of active nodes
        :param nodes: list of node ids
        :param new_node: id of the new node
        :param new_properties: dictionary, properties of the new node
        :return:
        """
        print('nodes = ', nodes)
        print('new_node = ', new_node)
        print('new_properties = ', new_properties)
        # get affected edges
        affected_edges = []
        nodes = set(nodes)
        for node in nodes:
            if node not in self.active_nodes:
                continue
            if node in self.adj_list:
                for e in self.adj_list[node]:
                    if e in self.active_edges:
                        affected_edges.append(e)
            if node in self.in_adj_list:
                for e in self.in_adj_list[node]:
                    if e in self.active_edges:
                        affected_edges.append(e)
        # replace affected edges by new edges
        new_edges = []
        affected_edges = set(affected_edges)
        for e in affected_edges:
            # deactivate the edges:

            # Disabled edge deactivation because of a bug where edges where removed, even thought, they had
            # nothing to do with the merged nodes. Everything seems to work now as intended ...
            # if e in self.active_edges:
                # self.remove_element([self.active_edges[e]['element_index']])
                # self.deactivate_edges([self.active_edges[e]['element_index']])
            # create a new edge
            source, target = self.edges[e]['source'], self.edges[e]['target']
            properties = copy.deepcopy(self.edges[e]['properties'])
            if source in nodes:
                source = new_node
            if target in nodes:
                target = new_node
            new_edges.append((source, target, properties))
        # delete the nodes
        for node in nodes:
            self.delete_an_active_node(node)
        # add the new node
        self.add_an_active_node(new_node, new_properties)
        # add the new edges
        for edge in new_edges:
            source, target, properties = edge[0], edge[1], edge[2]
            self.add_an_active_edge(source, target, properties)
        # set the node to selected
        self.toggle_node_selection(new_node)
    '''
    Merges a list of active nodes into a single new node within the active network.
    Updates edges connected to the merged nodes accordingly.

    Parameters:
    - self: An instance of the class containing the function.
    - nodes: List of node IDs to be merged.
    - new_node: ID of the new node that will represent the merged nodes.
    - new_properties: Dictionary containing properties for the new node.

    Output:
    - Doesn't explicitly return a value, but modifies the active network.

    Steps:
    - Print Node and Edge Information:
        - Prints the input nodes, new_node, and new_properties for potential debugging.
    - Identify Affected Edges:
        - Creates a list called affected_edges to store edges connected to the nodes being merged.
    - Iterates through the nodes:
        - Skips inactive nodes.
        - Checks both outgoing edges (adj_list) and incoming edges (in_adj_list).
        - Adds edges to affected_edges if they are active.
    - Replace Affected Edges:
        - Creates a list called new_edges to store edges with updated endpoints.
        - Iterates through affected edges:
            - Deactivation (Disabled):
                - There's a commented-out section for deactivating edges, but it's disabled due to a previous bug.
            - Create New Edge:
                - Retrieves source, target, and properties of the original edge.
                - Replaces source or target with the new_node if they are among the merged nodes.
                - Adds the updated edge to new_edges.
    - Delete Merged Nodes:
        - Iterates through the nodes list and calls delete_an_active_node for each node.
    - Add New Node:
        - Calls add_an_active_node to create the new node with the provided new_properties.
    - Add New Edges:
        - Iterates through the new_edges list and calls add_an_active_edge to create each updated edge.
    - Select New Node:
        - Calls toggle_node_selection to visually select the newly created node.

    Maintains consistency between network structure and visual representation.
    Updates edges to reflect node merging.
    Incorporates undo/redo functionality (likely through delete_an_active_node and add_an_active_node).
    '''


class BuiltinDatasetsManager(DataManager):
    """
    class for managing builtin datasets
    """

    def __init__(self, connector, params, load_on_construcion=False):
        super(BuiltinDatasetsManager, self).__init__(connector, params)
        self.datasets = {}
        if load_on_construcion:
            self.add_dataset('bbc_islam_groups', 'BBC Islam Groups',
                             '%s/datasets/preprocessed/bbc_islam_groups.json' % path2root)
            self.add_dataset('911_hijackers', '911 Hijackers',
                             '%s/datasets/preprocessed/911_hijackers.json' % path2root)
            # data_manager.add_dataset('enron', 'Enron Email Network',
            #                         '%s/datasets/preprocessed/enron.json' % path2root)
            # data_manager.add_dataset('moreno_crime', 'Moreno Crime Network',
            #                         '%s/datasets/preprocessed/moreno_crime.json' % path2root)
            #
            # data_manager.add_dataset('imdb', 'IMDB',
            #                         '%s/datasets/preprocessed/imdb.json' % path2root)

            self.add_dataset('baseball_steroid_use', 'Baseball Steorid Use',
                             '%s/datasets/preprocessed/baseball_steroid_use.json' % path2root)

            self.add_dataset('madoff', 'Madoff fraud',
                             '%s/datasets/preprocessed/madoff.json' % path2root)

            self.add_dataset('montreal_gangs', 'Montreal Street Gangs',
                             '%s/datasets/preprocessed/montreal_gangs.json' % path2root)

            self.add_dataset('noordintop', 'Noordin Top',
                             '%s/datasets/preprocessed/noordintop.json' % path2root)

            self.add_dataset('rhodes_bombing', 'Rhodes Bombing',
                             '%s/datasets/preprocessed/rhodes_bombing.json' % path2root)
    '''
    Initializes an instance of the BuiltinDatasetsManager class, likely used for managing built-in datasets within a larger application.

    Parameters:
    - self: Refers to the current instance of the class being initialized.
    - connector: An object presumably used for data access or communication.
    - params: A dictionary containing configuration parameters.
    - load_on_construcion: Boolean flag indicating whether to load datasets automatically during construction.

    Steps:
    - Initialize Base Class:
        - Calls the super constructor to initialize the inherited attributes and methods from the parent class.
    - Create Empty Dataset Dictionary:
        - Initializes an empty dictionary called self.datasets to store loaded datasets.
    - Conditional Dataset Loading:
        - If load_on_construcion is True:
            - Calls the add_dataset method (presumably defined within the same class) to add several built-in datasets to the self.datasets dictionary.
            - Each add_dataset call provides information about the dataset name, description, and file path.

    Enables management of multiple built-in datasets through a centralized class.
    Allows for conditional loading of datasets based on a configuration flag.
    Relies on a separate add_dataset method for actual dataset loading logic.
    '''

    def add_dataset(self, datset_id, name, path_2_data, settings=None, uploaded=False, from_file=True):
        """
        To add a dataset from file
        :param datset_id:
        :param name:
        :param settings: dict of dataset settings
        :param path_2_data: file containing the dataset, each line is a JSON object about either a node or an edge
            node object is in the following format:
            {
                "type": "node"
                "id": id of the node
                "properties": json object containing information about the node
            }

            edge object is in the following format:
            {
                "type": "edge"
                "source" id of source node,
                "target": id of target node,
                "properties": dictionaries containing properties of the edge, in the following format
                        {
                            "type": type of the edge, e.g., "work for", or "friend of",
                            "weight": optional, weight of the edge,
                            "confidence": optional, confidence/certainty of the edge,
                            ...
                        }
            }
        :return: a dictionary, in the following format
            {
                'success': 1 if the dataset is added successfully, 0 otherwise
                'message': a string
            }

        """
        if not settings:
            settings = {}
        try:
            if datset_id in self.datasets:
                return {'success': 0, 'message': 'dataset_id is already existed'}
            dataset = BuiltinDataset(path_2_data, uploaded, from_file)
            self.datasets[datset_id] = {
                'name': name,
                'data': dataset,
                'description': settings["description"] if "description" in settings else "",
                'version': settings["version"] if "version" in settings else 1.0,
                'directed': settings["directed"] if "directed" in settings else True,
                'multigraph': settings["multigraph"] if "multigraph" in settings else False
            }
            return {'success': 1, 'message': 'dataset is created successfully'}
        except Exception as e:
            print(e)
            return {'success': 0, 'message': 'there should be some error in IO'}
    '''
    Adds a new dataset to the self.datasets dictionary, making it accessible through the manager.
    Reads the dataset information from a provided file path.

    Parameters:
    - self: Refers to the current instance of the BuiltinDatasetsManager class.
    - datset_id: Unique identifier for the dataset.
    - name: Human-readable name for the dataset.
    - path_2_data: File path containing the dataset information in JSON format.
    - settings: Optional dictionary containing additional dataset settings (description, version, directedness, multigraph).
    - uploaded: Boolean flag indicating whether the dataset was uploaded by the user (not used in this implementation).
    - from_file: Boolean flag indicating whether the data is loaded from a file (always True in this implementation).

    Output:
    - Dictionary with keys:
        - success: Integer (1 for success, 0 for failure).
        - message: String describing the outcome.

    Steps:
    - Handle Missing Settings:
        - If settings is not provided, an empty dictionary is used.
    - Check for Existing ID:
        - If the datset_id already exists in self.datasets, returns an error message.
    - Create Dataset Object:
        - Creates a BuiltinDataset object (likely defined elsewhere) to handle loading and managing the dataset data.
    - Add Dataset to Dictionary:
        - Adds a new entry to the self.datasets dictionary with the provided datset_id.
        - The entry includes the dataset name, BuiltinDataset object, description (if provided in settings), version (if provided in settings), directedness (if provided in settings, defaults to True), and multigraph (if provided in settings, defaults to False).
    - Return Success Message:
        - If no errors occur, returns a success message (success=1) and a message indicating successful dataset creation.
    - Error Handling:
        - If any exceptions occur during the process:
            - Prints the error message for debugging purposes.
            - Returns an error message (success=0) indicating an I/O error.

    Validates the uniqueness of dataset IDs.
    Uses a separate BuiltinDataset class for data loading and management.
    Provides basic error handling for I/O issues.
    '''

    def create_network(self, network_id, name, nodes, edges, settings=None):
        """
        create a network from node and edge lists
        :param name: string
        :param network_id: string
        :param nodes: list of nodes, each is is a dictionary
                {
                'id': string, id of the node
                'properties': dictionary, properties of the node
                }
        :param edges: list of edges, each is is a dictionary
                {
                'source': string, id of the source node
                'target': string, id of the target node
                'properties': dictionary, properties of the edges
                }
        :return: a dictionary, in the following format
            {
                'success': 1 if the dataset is added successfully, 0 otherwise
                'message': a string
            }
        """
        if not settings:
            settings = {}
        if network_id in self.datasets:
            return {'success': 0, 'message': 'dataset_id is already existed'}
        g = BuiltinDataset(None, from_file=False)
        for node in nodes:
            g.nodes[node['id']] = node['properties']
            if 'type' in node['properties']:
                g.node_types.add(node['properties']['type'])

        for edge in edges:
            if edge['source'] in g.nodes and edge['target'] in g.nodes:
                g.edges.append(edge)
                e_index = len(g.edges) - 1
                source = edge['source']
                if source in g.adj_list:
                    g.adj_list[source].append(e_index)
                else:
                    g.adj_list[source] = [e_index]
                if 'type' in edge['properties']:
                    g.edge_types.add(edge['properties']['type'])
        self.datasets[network_id] = {
            'name': name,
            'data': g,
            'description': settings["description"] if "description" in settings else "",
            'version': settings["version"] if "version" in settings else 1.0,
            'directed': settings["directed"] if "directed" in settings else True,
            'multigraph': settings["multigraph"] if "multigraph" in settings else False
        }
        return {'success': 1, 'message': 'dataset is created successfully'}
    '''
    Creates a new network within the BuiltinDatasetsManager class, building it from provided lists of nodes and edges.

    Parameters:
    - self: Refers to the current instance of the class.
    - network_id: Unique identifier for the network.
    - name: Human-readable name for the network.
    - nodes: List of node dictionaries, each containing id and properties.
    - edges: List of edge dictionaries, each containing source, target, and properties.
    - settings: Optional dictionary with network settings (description, version, directedness, multigraph).

    Output:
    - Dictionary with keys:
        - success: Integer (1 for success, 0 for failure).
        - message: String describing the outcome.

    Steps:
    - Handle Missing Settings:
        - If settings is not provided, an empty dictionary is used.
    - Check for Existing ID:
        - If the network_id already exists, returns an error message.
    - Create Network Object:
        - Creates a BuiltinDataset object (likely defined elsewhere) to store network data.
    - Add Nodes:
        - Iterates through the nodes list:
            - Adds each node's properties to the g.nodes dictionary, using its ID as the key.
            - If a type property exists for the node, adds it to the g.node_types set.
    - Add Edges:
        - Iterates through the edges list:
            - Checks if both source and target nodes exist in the network.
                - If so, adds the edge to the g.edges list and its index to the source node's adj_list for adjacency information.
                - If a type property exists for the edge, adds it to the g.edge_types set.
    - Store Network:
        - Adds a new entry to the self.datasets dictionary with the provided network_id.
        - The entry includes network name, BuiltinDataset object, description (if provided in settings), version (if provided in settings), directedness (if provided in settings, defaults to True), and multigraph (if provided in settings, defaults to False).
    - Return Success Message:
        - If no errors occur, returns a success message (success=1) and a message indicating successful network creation.

    Uses BuiltinDataset to represent and manage network data.
    Stores network information in the self.datasets dictionary.
    Tracks node and edge types for potential analysis or visualization.
    '''

    def search_networks(self, networks=None, params=None):
        """

        :param networks:
        :param params:
        :return:
        """
        if networks is None:
            networks = list(self.datasets.keys())
        found = []
        not_found = []
        for g in networks:
            if g in self.datasets:
                n = self.datasets[g]
                properties = {'name': n['name'],
                              'edge_types': n['data'].edge_types,
                              'node_types': n['data'].node_types,
                              'num_nodes': len(n['data'].nodes),
                              'num_edges': len(n['data'].edges)
                              }
                found.append({'id': g, 'properties': properties})
            else:
                not_found.append(g)
        return {'found': found, 'not_found': not_found}
    '''
    Searches for specific networks or provides information about all available networks managed by the class.

    Parameters:
    - self: Refers to the current instance of the class.
    - networks: Optional list of network IDs to search for. If not provided, searches all networks.
    - params: Currently unused (set to None in the provided code).

    Output:
    - Dictionary with keys:
        - found: List of dictionaries containing information about found networks.
        - not_found: List of network IDs that were not found.

    Steps:
    - Handle Missing Network List:
        - If networks is not provided, uses all network IDs from self.datasets.
    - Initialize Results:
        - Creates empty lists for found and not_found networks.
    - Iterate through Networks:
        - Loops through each network ID (g) in the provided or default list:
            - If the ID exists in self.datasets:
                - Extracts network information like name, edge/node types, number of nodes, and number of edges.
                - Creates a dictionary with this information and the network ID.
                - Adds the dictionary to the found list.
            - Otherwise, adds the ID to the not_found list.
        - Return Search Results:
    - Returns a dictionary containing the found and not_found lists.

    Provides basic search functionality for network management.
    Returns basic network information for found networks.
    Handles cases where networks are not found.
    '''

    def get_network(self, network, node_ids=None, params=None):
        if network in self.datasets:
            return self.datasets[network]['data'].get_network(node_ids=node_ids, params=params)
        else:
            return {'edges': [], 'nodes': []}
    '''
    Retrieves a specific network or a subset of it from the BuiltinDatasetsManager class.

    Parameters:
    - self: Refers to the current instance of the class.
    - network: The ID of the network to retrieve.
    - node_ids: Optional list of node IDs to include in the retrieved network. If not provided, the entire network is returned.
    - params: Currently unused (set to None in the provided code).

    Output:
    - Dictionary representing the retrieved network, containing:
        - edges: List of edge dictionaries.
        - nodes: List of node dictionaries.

    Steps:
    - Check for Network Existence:
        - If the network ID exists in self.datasets:
            - Delegates the retrieval to the get_network method of the corresponding BuiltinDataset object.
                - This method likely handles filtering based on node_ids and any future params.
        - Otherwise, returns an empty network (no nodes or edges).

    Relies on the BuiltinDataset class for network data retrieval.
    Provides a way to retrieve specific portions of a network based on node IDs.
    Handles cases where networks are not found.
    '''

    def get_edges(self, node_ids, network, params=None):
        if network in self.datasets:
            return self.datasets[network]['data'].get_edges(node_ids=node_ids, params=params)
        else:
            return {'found': [], 'not_found': node_ids}
    '''
    Retrieves specific edges from a network within the BuiltinDatasetsManager class, based on provided node IDs.

    Parameters:
    - self: Refers to the current instance of the class.
    - node_ids: List of node IDs for which to retrieve connected edges.
    - network: The ID of the network to query.
    - params: Currently unused (set to None in the provided code).

    Output:
    - Dictionary with keys:
        - found: List of edge dictionaries found for the specified node IDs.
        - not_found: List of node IDs for which no edges were found.
    
    Steps:
    - Check for Network Existence:
        - If the network ID exists in self.datasets:
            - Delegates the edge retrieval to the get_edges method of the corresponding BuiltinDataset object.
                - This method likely handles filtering based on node_ids and any future params.
        - Otherwise, returns an empty found list and all node_ids in the not_found list.

    Relies on the BuiltinDataset class for edge retrieval logic.
    Provides a way to retrieve edges connected to specific nodes.
    Handles cases where networks are not found.
    Distinguishes between found and not-found edges.
    '''

    def get_neighbors(self, node_ids, network, params=None):
        if network in self.datasets:
            return self.datasets[network]['data'].get_neighbors(node_ids=node_ids, params=params)
        else:
            return {'found': [], 'not_found': node_ids}
    '''
    Retrieves the neighbors of specific nodes within a network managed by the class.

    Parameters:
    - self: Refers to the current instance of the class.
    - node_ids: List of node IDs for which to find neighbors.
    - network: The ID of the network to query.
    - params: Currently unused (set to None in the provided code).

    Output:
    - Dictionary with keys:
        - found: List of dictionaries containing information about found neighbors for each node ID.
        - not_found: List of node IDs for which no neighbors were found.

    Steps:
    - Check for Network Existence:
        - If the network ID exists in self.datasets:
            - Delegates the neighbor retrieval to the get_neighbors method of the corresponding BuiltinDataset object.
                - This method likely handles filtering based on node_ids and any future params.
        - Otherwise, returns an empty found list and all node_ids in the not_found list.

    Relies on the BuiltinDataset class for neighbor retrieval logic.
    Provides a way to find nodes directly connected to specific nodes.
    Handles cases where networks are not found.
    Distinguishes between found and not-found neighbors.
    '''

    def search_nodes(self, node_ids, network, params=None):
        if network in self.datasets:
            return self.datasets[network]['data'].search_nodes(node_ids=node_ids, params=params)
        else:
            return {'found': [], 'not_found': node_ids}
    '''
    Searches for specific nodes within a network managed by the BuiltinDatasetsManager class, potentially based on additional criteria.

    Parameters:
    - self: Refers to the current instance of the class.
    - node_ids: List of node IDs to search for.
    - network: The ID of the network to query.
    - params: Optional dictionary containing search criteria (currently unused in the provided code).

    Output:
    - Dictionary with keys:
        - found: List of dictionaries containing information about found nodes.
        - not_found: List of node IDs that were not found.

    Steps:
    - Check for Network Existence:
        - If the network ID exists in self.datasets:
            - Delegates the node search to the search_nodes method of the corresponding BuiltinDataset object.
                - This method likely handles filtering based on node_ids, params, and potentially node properties.
        - Otherwise, returns an empty found list and all node_ids in the not_found list.

    Relies on the BuiltinDataset class for node search logic.
    Provides a way to find specific nodes within a network.
    Handles cases where networks are not found.
    Distinguishes between found and not-found nodes.
    Allows for potential future extensions with search parameters.
    '''

    def save_nodes(self, nodes, network, params=None):
        if network in self.datasets:
            return self.datasets[network]['data'].save_nodes(nodes=nodes, params=params)
        else:
            return nodes
    '''
    Saves or updates a list of nodes within a network managed by the class.

    Parameters:
    - self: Refers to the current instance of the class.
    - nodes: List of dictionaries representing the nodes to be saved or updated. Each dictionary should include the node ID and potentially other properties.
    - network: The ID of the network where the nodes reside.
    - params: Optional dictionary containing additional parameters for saving (currently unused in the provided code).

    Output:
    - If successful: the original nodes list (possibly indicating successful saving).
    - If unsuccessful: the original nodes list (without changes).

    Steps:
    - Check for Network Existence:
        - If the network ID exists in self.datasets:
            - Delegates the node saving to the save_nodes method of the corresponding BuiltinDataset object.
                - This method likely handles updating existing nodes or creating new ones based on the provided information.
        - Otherwise, returns the original nodes list without any changes.

    Relies on the BuiltinDataset class for node saving logic.
    Enables updating existing nodes or creating new ones.
    Handles cases where the network is not found.
    Doesn't directly indicate success or failure in the current implementation.
    '''

    def save_edges(self, edges, network, params=None):
        if network in self.datasets:
            return self.datasets[network]['data'].save_edges(edges=edges, params=params)
        else:
            return edges
    '''
    Saves or updates a list of edges within a network managed by the BuiltinDatasetsManager class.

    Parameters:
    - self: Refers to the current instance of the class.
    - edges: List of dictionaries representing the edges to be saved or updated. Each dictionary should include the source and target node IDs, and potentially other properties.
    - network: The ID of the network where the edges reside.
    - params: Optional dictionary containing additional parameters for saving (currently unused in the provided code).

    Output:
    - If successful: the original edges list (possibly indicating successful saving).
    - If unsuccessful: the original edges list (without changes).

    Steps:
    - Check for Network Existence:
        - If the network ID exists in self.datasets:
            - Delegates the edge saving to the save_edges method of the corresponding BuiltinDataset object.
                - This method likely handles updating existing edges or creating new ones based on the provided information.
        - Otherwise, returns the original edges list without any changes.

    Relies on the BuiltinDataset class for edge saving logic.
    Enables updating existing edges or creating new ones.
    Handles cases where the network is not found.
    Doesn't directly indicate success or failure in the current implementation.
    '''

    def delete_node(self, node_ids, network):
        if network in self.datasets:
            return self.datasets[network]['data'].delete_node(node_ids=node_ids)
        else:
            return node_ids
    '''
    Deletes specified nodes from a network managed by the class.

    Parameters:
    - self: Refers to the current instance of the class.
    - node_ids: List of node IDs to be deleted.
    - network: The ID of the network where the nodes reside.

    Output:
    - If successful: the original node_ids list, possibly indicating successful deletion.
    - If unsuccessful: the original node_ids list, indicating that the deletion failed for some or all nodes.

    Steps:
    - Check for Network Existence:
        - If the network ID exists in self.datasets:
            - Delegates the node deletion to the delete_node method of the corresponding BuiltinDataset object.
                - This method likely handles removing the specified nodes and potentially associated edges.
        - Otherwise, returns the original node_ids list without any changes.
    '''

    def delete_edges(self, edges, network):
        if network in self.datasets:
            return self.datasets[network]['data'].delete_edges(deleted_edges=edges)
        else:
            return edges
    '''
    Deletes specified edges from a network managed by the BuiltinDatasetsManager class.

    Parameters:
    - self: Refers to the current instance of the class.
    - edges: List of edge dictionaries representing the edges to be deleted. Each dictionary should include the source and target node IDs.
    - network: The ID of the network where the edges reside.

    Output:
    - If successful: the original edges list, possibly indicating successful deletion.
    - If unsuccessful: the original edges list, indicating that the deletion failed for some or all edges.

    Steps:
    - Check for Network Existence:
        - If the network ID exists in self.datasets:
            - Delegates the edge deletion to the delete_edges method of the corresponding BuiltinDataset object.
                - This method handles removing the specified edges from the network's internal representation.
        - Otherwise, returns the original edges list without any changes.
    '''

    def dump_network(self, network, output_dir, params=None):
        if network in self.datasets:
            return self.datasets[network]['data'].dump_network(network=network, output_dir=output_dir,
                                                               params=params)
        else:
            return 0
    '''
    Parameters:
    - self: Refers to the current instance of the class.
    - network: ID of the network to export.
    - output_dir: Directory path where the network data will be saved.
    - params: Optional dictionary containing additional parameters for the export (currently unused in the provided code).

    Output:
    - Integer value (0 in this implementation), potentially indicating success or failure (interpretation depends on future enhancements).

    Steps:
    - Check Network Existence:
        - Verifies if the provided network ID exists within the self.datasets dictionary.
    - Delegate to BuiltinDataset:
        - If the network exists, retrieves the corresponding BuiltinDataset object from self.datasets[network].
        - Calls the dump_network method of the BuiltinDataset object, passing the network, output_dir, and params as arguments.
    - Return from BuiltinDataset:
        - The return value of the dump_network method within BuiltinDataset is directly returned by this function. In the provided code, BuiltinDataset.dump_network simply returns 0.
    '''

    def load_file(self, file_path):
        """
        Load a previously saved network from a file, adds its dataset to the data manager
        and initializes an ActiveNetwork
        :param file_path:
        :return:
        """
        pass
    '''
    Loads a previously saved network from a file.
    Adds the loaded network's dataset to the manager's internal data storage.
    Potentially initializes an "ActiveNetwork" object (implementation not provided).

    Parameters:
    - self: Refers to the current instance of the class.
    - file_path: Path to the file containing the network data.
    
    Output:
    - The function doesn't have an explicit return value in the provided code.
    '''

    def load_active_network(self, network_id=None, network_name=None, node_ids=None, initialize=True,
                            from_file=False, file_path=None, params={}):
        """
        Initialize an ActiveNetwork from a given internal dataset and (optionally) a list of entities.
        :param network_id:
        :param network_name:
        :param node_ids:
        :param initialize:
        :param from_file:
        :param file_path:
        :param params:
        :return:
        """
        if not from_file:
            if network_id not in self.datasets:
                return {'success': 0, 'message': 'dataset_id not found'}
            else:
                dataset = self.datasets[network_id]['data']
                # create a blank active network
                active_network = ActiveNetwork(path_2_data=None, from_file=False, uploaded=False, initialize=False)
                active_network.nodes = dataset.nodes
                active_network.edges = dataset.edges
                active_network.adj_list = dataset.adj_list
                active_network.node_types = dataset.node_types
                active_network.edge_types = dataset.edge_types
                if network_name is not None:
                    params['network_name'] = network_name
                if initialize:
                    active_network.initialize(selected_nodes=node_ids, params=params)
                return {'success': 1, 'message': 'active network created successfully',
                        'active_network': active_network}
        else:
            print('reading from file')
            active_network = ActiveNetwork(path_2_data=None, from_file=False, uploaded=False, initialize=False)
            active_network.load_from_file(file_path)
            if initialize:
                active_network.initialize(selected_nodes=node_ids, params=params)
            return {'success': 1, 'message': 'active network created successfully',
                    'active_network': active_network}
    '''
    Creates and initializes an "ActiveNetwork" object, which is a specialized representation of a network for potential further operations.
    Can load the network from an internal dataset or from a file.

    Parameters:
    - self: Refers to the current instance of the BuiltinDatasetsManager class.
    - network_id: ID of the internal dataset to load from (if not loading from a file).
    - network_name: Optional name to assign to the ActiveNetwork.
    - node_ids: Optional list of node IDs to selectively initialize the network with.
    - initialize: Boolean indicating whether to initialize the ActiveNetwork (meaning unclear without further context).
    - from_file: Boolean indicating whether to load the network from a file.
    - file_path: Path to the file containing the network data (if loading from a file).
    - params: Dictionary containing additional parameters for the ActiveNetwork initialization (specific usage unclear).
    
    Output:
    - Dictionary with keys:
        - success: 1 for successful loading, 0 for failure.
        - message: Status message indicating success or failure reason.
        - active_network: The created ActiveNetwork object (if successful).

    Steps:
    - Determine Source:
        - Checks from_file to decide whether to load from an internal dataset or a file.
    - Loading from Internal Dataset:
        - If from_file is False:
            - Retrieves the specified dataset from self.datasets.
            - Creates a new ActiveNetwork object.
            - Copies network data (nodes, edges, adjacency list, node types, edge types) from the dataset to the ActiveNetwork.
            - Optionally sets the network name and initializes the ActiveNetwork using selected_nodes and params.
    - Loading from File:
        - If from_file is True:
            - Creates a new ActiveNetwork object.
            - Calls active_network.load_from_file(file_path) to load the network data from the specified file (implementation not provided).
            - Optionally initializes the ActiveNetwork using selected_nodes and params.
    '''

    def save_data(self, save_path):
        """
        Save the dataset and the current state of the active_network to a file.
        :param save_path:
        :return:
        """
    '''
    Saves the current state of the BuiltinDatasetsManager data to a file at the specified save_path. This likely involves saving both the internal datasets managed by the class and the state of the currently active network (if one exists).

    Missing Implementation:
    - The actual logic for saving the data is missing. This would likely involve:
        - Serializing the internal datasets (potentially using JSON or another format).
        - Capturing the relevant state of the active network (implementation depends on the ActiveNetwork class).
        - Writing the serialized data to the specified file path.

    - Possible Enhancements:
        - Implement the data saving logic based on the chosen serialization format and ActiveNetwork representation.
        - Add error handling for invalid file paths, serialization issues, or potential write errors.
        - Consider options for saving only specific datasets or the active network independently.
        - Provide feedback or status messages about the save operation (success, failure, etc.).
        - Implement versioning or timestamps in the saved data for future compatibility or tracking changes.
    '''
