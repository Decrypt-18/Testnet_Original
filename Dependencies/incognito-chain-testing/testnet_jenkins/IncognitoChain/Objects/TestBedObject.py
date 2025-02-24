from typing import List

import IncognitoChain.Helpers.Logging as Log
from IncognitoChain.Objects.NodeObject import Node


def load_test_data(name):
    Log.INFO(f'Loading: test data {name}')
    try:
        return __import__(f'IncognitoChain.TestData.{name}', fromlist=['object'])
    except ModuleNotFoundError:
        raise Exception(f"!!! Test data not found: {name}")


def load_test_bed(name):
    Log.INFO(f'Loading test bed: {name}')
    try:
        return __import__(f'IncognitoChain.TestBeds.{name}', fromlist=['object'])
    except ModuleNotFoundError:
        raise Exception(f"!!! Test bed not found: {name}")


class TestBed:
    REQUEST_HANDLER: Node = Node()

    def __init__(self, test_bed=None):
        if test_bed is not None:
            tb = load_test_bed(test_bed)
            self.full_node: Node = tb.full_node
            self.beacons: Beacon = tb.beacon
            self.shards: List[Shard] = tb.shard_list
            TestBed.REQUEST_HANDLER = self.full_node
        else:
            self.full_node = Node()
            self.beacons = Beacon()
            self.shards: List[Shard] = []
            TestBed.REQUEST_HANDLER = self.full_node

    def __call__(self, *args, **kwargs):
        return TestBed.REQUEST_HANDLER

    def precondition_check(self):
        Log.INFO(f'Checking test bed')
        return self

    def get_committee_accounts(self, shard_id=None):
        acc_list = []
        shards_to_get = self.shards if shard_id is None else [self.shards[shard_id]]
        for shard in shards_to_get:
            shard_acc = [node.account for node in shard._node_list]
            acc_list += shard_acc

        return acc_list

    def get_beacon_accounts(self):
        acc_list = [node.account for node in self.beacons._node_list]
        return acc_list

    def is_default(self):
        return self.full_node.is_local_host()


class Shard:
    def __init__(self, node_list: list = None):
        self._node_list = node_list

    def add_node(self, node: Node):
        self._node_list.append(node)

    def get_node(self, index_or_name=0) -> Node:
        if type(index_or_name) is int:
            return self._node_list[index_or_name]
        if type(index_or_name) is str:
            return self._node_list[self.__find_index_with_name(index_or_name)]

    def get_representative_node(self) -> Node:
        for node in self._node_list:
            if node._address is not None:
                return node

    def __find_index_with_name(self, node_name_to_find):
        for node in self._node_list:
            if node._node_name == node_name_to_find:
                return self._node_list.index(node)
        return -1


class Beacon(Shard):
    pass
