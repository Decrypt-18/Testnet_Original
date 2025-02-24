from pexpect import pxssh

import IncognitoChain.Helpers.Logging as Log
from IncognitoChain.APIs.Bridge import BridgeRpc
from IncognitoChain.APIs.DEX import DexRpc
from IncognitoChain.APIs.Explore import ExploreRpc
from IncognitoChain.APIs.Portal import PortalRpc
from IncognitoChain.APIs.Subscription import SubscriptionWs
from IncognitoChain.APIs.System import SystemRpc
from IncognitoChain.APIs.Transaction import TransactionRpc
from IncognitoChain.Configs.Constants import ChainConfig, PRV_ID
from IncognitoChain.Drivers.Connections import WebSocket, RpcConnection
from IncognitoChain.Helpers import TestHelper
from IncognitoChain.Helpers.Logging import INFO, DEBUG, WARNING
from IncognitoChain.Helpers.TestHelper import l6, ChainHelper
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.BeaconObject import BeaconBestStateDetailInfo, BeaconBlock, BeaconBestStateInfo
from IncognitoChain.Objects.BlockChainObjects import BlockChainCore
from IncognitoChain.Objects.PdeObjects import PDEStateInfo
from IncognitoChain.Objects.PortalObjects import PortalStateInfo
from IncognitoChain.Objects.ShardBlock import ShardBlock
from IncognitoChain.Objects.ShardState import ShardBestStateDetailInfo, ShardBestStateInfo


class Node:
    default_user = "root"
    default_password = 'xxx'
    default_address = "localhost"
    default_rpc_port = 9334
    default_ws_port = 19334

    def __init__(self, address=default_address, username=default_user, password=default_password,
                 rpc_port=default_rpc_port, ws_port=default_ws_port, account=None, sshkey=None,
                 node_name=None):
        self._address = address
        self._username = username
        self._password = password
        self._sshkey = sshkey
        self._rpc_port = rpc_port
        self._ws_port = ws_port
        self._node_name = node_name
        self._spawn = pxssh.pxssh()
        self._web_socket = None
        self._rpc_connection = RpcConnection(self._get_rpc_url())
        self.account = account

    def parse_url(self, url):
        import re
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if re.match(regex, "http://www.example.com") is None:
            raise SyntaxError('Url is not in correct format')

        self._address = url.split(':')[1].lstrip('//')
        self._rpc_port = int(url.split(':')[2])
        return self

    def set_web_socket_port(self, port):
        self._ws_port = port
        return self

    def ssh_connect(self):
        if self._password is not None:
            Log.INFO(f'SSH logging in with password. User: {self._username}')
            self._spawn.login(self._address, self._username, password=self._password)
            return self
        if self._sshkey is not None:
            Log.INFO(f'SSH logging in with ssh key. User: {self._username}')
            self._spawn.login(self._username, ssh_key=self._sshkey)
            return self

    def logout(self):
        self._spawn.logout()
        Log.INFO(f'SSH logout of: {self._address}')

    def send_cmd(self, command):
        if not self._spawn.isalive():
            self.ssh_connect()

        self._spawn.sendline(command)
        self._spawn.prompt()

    def _get_rpc_url(self):
        return f'http://{self._address}:{self._rpc_port}'

    def _get_ws_url(self):
        return f'ws://{self._address}:{self._ws_port}'

    def rpc_connection(self) -> RpcConnection:
        """
        get RPC connection to send custom command
        :return: RpcConnection object
        """
        return self._rpc_connection

    def web_socket_connection(self) -> WebSocket:
        """
        get web socket to send your custom command
        :return: WebSocket object
        """
        return self._web_socket

    def transaction(self) -> TransactionRpc:
        """
        Transaction APIs by RPC
        :return: TransactionRpc object
        """
        return TransactionRpc(self._get_rpc_url())

    def system_rpc(self) -> SystemRpc:
        return SystemRpc(self._get_rpc_url())

    def dex(self) -> DexRpc:
        """
        Decentralize Exchange APIs by RPC
        :return: DexRpc Object
        """
        return DexRpc(self._get_rpc_url())

    def bridge(self) -> BridgeRpc:
        """
        Bridge APIs by RPC
        :return: BridgeRpc object
        """
        return BridgeRpc(self._get_rpc_url())

    def portal(self) -> PortalRpc:
        return PortalRpc(self._get_rpc_url())

    def subscription(self) -> SubscriptionWs:
        """
        Subscription APIs on web socket
        :return: SubscriptionWs object
        """
        if self._web_socket is None:
            self._web_socket = WebSocket(self._get_ws_url())
        return SubscriptionWs(self._web_socket)

    def explore_rpc(self) -> ExploreRpc:
        return ExploreRpc(self._get_rpc_url())

    def get_latest_beacon_block(self, beacon_height=None):
        if beacon_height is None:
            beacon_height = self.help_get_beacon_height()
        INFO(f'Get beacon block at height {beacon_height}')
        response = self.system_rpc().retrieve_beacon_block_by_height(beacon_height)
        return BeaconBlock(response.get_result()[0])

    def get_first_beacon_block_of_epoch(self, epoch=None):
        """

        @param epoch: epoch number
        @return: BeaconBlock obj of the first epoch of epoch.
        If epoch is specify, get first beacon block of that epoch
        If epoch is None,  get first beacon block of current epoch.
        If epoch = -1 then wait for the next epoch and get first beacon block of epoch
        """
        if epoch == -1:
            current_height = self.get_block_chain_info().get_beacon_block().get_height()
            current_epoch = ChainHelper.cal_epoch_from_height(current_height)
            if not ChainConfig.is_first_height_of_epoch(current_height):
                next_first_height = ChainHelper.cal_first_height_of_epoch(current_epoch + 1)
                wait_height = next_first_height + 1 - current_height
                time_till_next_epoch_first_block = ChainConfig.BLOCK_TIME * wait_height
                INFO(f'Current epoch {current_epoch} Current height {current_height}, '
                     f'wait for {wait_height} height till height {current_height + wait_height}')
                # +1 just to make sure that the first block of epoch is already confirmed
                WAIT(time_till_next_epoch_first_block)
            else:
                INFO(f'Current epoch {current_epoch} Current height {current_height}, no need to wait')
            epoch = current_epoch + 1
        elif epoch is None:
            epoch = self.help_get_current_epoch()
        else:
            pass

        beacon_height = TestHelper.ChainHelper.cal_first_height_of_epoch(epoch)
        return self.get_latest_beacon_block(beacon_height)

    def get_beacon_best_state_detail_info(self):
        beacon_detail_raw = self.system_rpc().get_beacon_best_state_detail().get_result()
        beacon_state_obj = BeaconBestStateDetailInfo(beacon_detail_raw)
        return beacon_state_obj

    def get_latest_pde_state_info(self, beacon_height=None):
        if beacon_height is None:
            beacon_height = self.help_get_beacon_height()
            INFO(f'Get LATEST PDE state at beacon height: {beacon_height}')
        else:
            INFO(f'Get PDE state at beacon height: {beacon_height}')

        pde_state = self.dex().get_pde_state(beacon_height)
        return PDEStateInfo(pde_state.get_result())

    def get_block_chain_info(self):
        return BlockChainCore(self.system_rpc().get_block_chain_info().get_result())

    def help_get_beacon_height(self):
        chain_info = self.get_block_chain_info()
        return chain_info.get_beacon_block().get_height()

    def help_get_beacon_height_in_best_state_detail(self, refresh_cache=True):
        beacon_height = self.system_rpc().get_beacon_best_state_detail(refresh_cache).get_beacon_height()
        INFO(f"Current beacon height = {beacon_height}")
        return beacon_height

    def help_clear_mem_pool(self):
        list_tx = self.system_rpc().get_mem_pool().get_result('ListTxs')
        for tx in list_tx:
            self.system_rpc().remove_tx_in_mem_pool(tx['TxID'])

    def help_count_shard_committee(self, refresh_cache=False):
        best = self.system_rpc().get_beacon_best_state_detail(refresh_cache)
        shard_committee_list = best.get_result()['ShardCommittee']
        return len(shard_committee_list)

    def help_count_committee_in_shard(self, shard_id, refresh_cache=False):
        best = self.system_rpc().get_beacon_best_state_detail(refresh_cache)
        shard_committee_list = best.get_result()['ShardCommittee']
        shard_committee = shard_committee_list[f'{shard_id}']
        return len(shard_committee)

    def help_get_current_epoch(self, refresh_cache=True):
        """
        DEPRECATED, please don't use this method anymore
        :param refresh_cache:
        :return:
        """
        DEBUG(f'Get current epoch number')
        beacon_best_state = self.system_rpc().get_beacon_best_state_detail(refresh_cache)
        epoch = beacon_best_state.get_result('Epoch')
        DEBUG(f"Current epoch = {epoch}")
        return epoch

    def get_latest_portal_state_info(self, beacon_height=None):
        if beacon_height is None:
            beacon_height = self.help_get_beacon_height()
            INFO(f'Get LATEST portal state at beacon height: {beacon_height}')
        else:
            INFO(f'Get portal state at beacon height: {beacon_height}')

        portal_state_raw = self.portal().get_portal_state(beacon_height)
        return PortalStateInfo(portal_state_raw.get_result())

    def cal_transaction_reward_from_beacon_block_info(self, epoch=None, token=None, shard_txs_fee_list=None):
        """
        Calculate reward of an epoch
        :param shard_txs_fee_list:
        :param token:
        :param epoch: if None, get latest epoch -1
        :return: dict { "DAO" : DAO_reward_amount
                        "beacon" : total_beacon_reward_amount
                        "0" : shard0_reward_amount
                        "1" : shard1_reward_amount
                        .....
                        }
        """

        num_of_active_shard = self.get_block_chain_info().get_num_of_shard()
        shard_txs_fee_list = [0] * num_of_active_shard if shard_txs_fee_list is None else shard_txs_fee_list
        shard_range = range(0, num_of_active_shard)
        RESULT = {}

        if epoch is None:
            latest_beacon_block = self.get_latest_beacon_block()
            epoch = latest_beacon_block.get_epoch() - 1
            # can not calculate reward on latest epoch, because the instruction for splitting reward is only exist on
            # the first beacon block of next future epoch

        token = PRV_ID if token is None else token
        # todo: not yet handle custom token

        INFO(f'GET reward info, epoch {epoch}, token {l6(token)}')

        first_height_of_epoch = TestHelper.ChainHelper.cal_first_height_of_epoch(epoch)
        first_BB_of_epoch = self.get_latest_beacon_block(first_height_of_epoch)
        second_BB_of_epoch = self.get_latest_beacon_block(first_height_of_epoch + 1)

        last_height_of_epoch = TestHelper.ChainHelper.cal_last_height_of_epoch(epoch)
        last_BB_of_epoch = self.get_latest_beacon_block(last_height_of_epoch)
        pre_last_BB_of_epoch = self.get_latest_beacon_block(last_height_of_epoch - 1)

        list_num_of_shard_block = []
        # calculate number of shard block in each shard of this epoch
        for shard_id in shard_range:
            try:
                DEBUG(f"Try finding shard {shard_id} state in 1st beacon block of epoch")
                shard_first_block = first_BB_of_epoch.get_shard_states(shard_id).get_smallest_block_height()
            except AttributeError:  # case shard state in beacon block is not exist, get it in next beacon block
                try:
                    WARNING(f'Could not find shard {shard_id} state in 1st beacon block of epoch. '
                            f'Try again with 2nd block')
                    shard_first_block = second_BB_of_epoch.get_shard_states(shard_id).get_smallest_block_height()
                except AttributeError:  # if could not find it in the second block then probably it just doesn't exist
                    WARNING(f'Could not find shard {shard_id} state in 1st and 2nd beacon block, '
                            f'assume that this shard create 0 block in this epoch')
                    shard_first_block = 0

            try:
                DEBUG(f"Try finding shard {shard_id} state in last beacon block of epoch")
                shard_last_block = last_BB_of_epoch.get_shard_states(shard_id).get_biggest_block_height()
            except AttributeError:  # case shard state in beacon block is not exist, get it in previous beacon block
                try:
                    WARNING(f'Could not find shard {shard_id} state in last beacon block of epoch. '
                            f'Try again with 2nd last block')
                    shard_last_block = pre_last_BB_of_epoch.get_shard_states(shard_id).get_biggest_block_height()
                except AttributeError:  # if could not find it in the previous block then probably it just doesn't exist
                    WARNING(f'Could not find shard {shard_id} state in last and 2nd last beacon block, '
                            f'assume that this shard create 0 block in this epoch')
                    shard_last_block = -1

            list_num_of_shard_block.append(shard_last_block - shard_first_block + 1)
        # now calculate each shard reward
        list_beacon_reward_from_shard = []
        list_DAO_reward_from_shard = []
        for shard_id in shard_range:
            DAO_share = ChainConfig.DAO_REWARD_PERCENT
            basic_reward = ChainConfig.BASIC_REWARD_PER_BLOCK
            num_of_shard_block = list_num_of_shard_block[shard_id]
            shard_fee_total = shard_txs_fee_list[shard_id]

            total_reward_from_shard = num_of_shard_block * basic_reward + shard_fee_total
            DAO_reward_from_shard = DAO_share * total_reward_from_shard
            beacon_reward_from_shard = \
                (1 - DAO_share) * 2 * total_reward_from_shard / (num_of_active_shard + 2)
            shard_reward = (1 - DAO_share) * total_reward_from_shard - beacon_reward_from_shard

            shard_reward_to_split = max(0, int(shard_reward))
            if shard_reward_to_split > 0:
                RESULT[str(shard_id)] = shard_reward_to_split
            list_beacon_reward_from_shard.append(max(0, beacon_reward_from_shard))
            list_DAO_reward_from_shard.append(max(0, DAO_reward_from_shard))

        # now calculate total beacon reward
        total_beacon_reward = max(0, sum(list_beacon_reward_from_shard))
        if total_beacon_reward > 0:
            RESULT['beacon'] = int(total_beacon_reward)
        # now calculate DAO reward
        total_DAO_reward = max(0, sum(list_DAO_reward_from_shard))
        if total_DAO_reward > 0:
            RESULT['DAO'] = int(total_DAO_reward)

        return RESULT

    def help_get_shard_height(self, shard_num=None):
        """
        Function to get shard height
        :param shard_num:
        :return:
        """
        if shard_num is None:
            dict_shard_height = {}
            num_shards_info = self.get_block_chain_info().get_num_of_shard()
            for shard_id in range(0, num_shards_info):
                shard_height = self.get_block_chain_info().get_shard_block(shard_id).get_height()
                dict_shard_height.update({str(shard_id): shard_height})
            return dict_shard_height
        else:
            return self.get_block_chain_info().get_shard_block(shard_num).get_height()

    def get_shard_best_state_detail_info(self, shard_num):
        shard_state_detail_raw = self.system_rpc().get_shard_best_state_detail(shard_num).get_result()
        shard_state_detail_obj = ShardBestStateDetailInfo(shard_state_detail_raw)
        return shard_state_detail_obj

    def get_beacon_best_state_info(self):
        beacon_best_state_raw = self.system_rpc().get_beacon_best_state().get_result()
        beacon_best_state_obj = BeaconBestStateInfo(beacon_best_state_raw)
        return beacon_best_state_obj

    def get_shard_best_state_info(self, shard_num=None):
        shard_state_raw = self.system_rpc().get_shard_best_state(shard_num).get_result()
        shard_state_obj = ShardBestStateInfo(shard_state_raw)
        return shard_state_obj

    def is_local_host(self):
        return self._address == Node.default_address

    def send_proof(self, proof):
        INFO('Sending proof')
        return self.transaction().send_tx(proof)

    def get_mem_pool_txs(self):
        response = self.system_rpc().get_mem_pool()
        return response.get_mem_pool_transactions_id_list()

    def get_shard_block_by_height(self, shard_id, height):
        response = self.system_rpc().retrieve_block_by_height(height, shard_id)
        return ShardBlock(response.get_result())
