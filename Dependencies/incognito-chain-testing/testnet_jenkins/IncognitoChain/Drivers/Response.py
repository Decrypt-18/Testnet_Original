import json
import re

import IncognitoChain.Helpers.Logging as Log
from IncognitoChain.Helpers.Logging import INFO
from IncognitoChain.Objects.TransactionObjects import TransactionDetail


class Response:
    def __init__(self, response, more_info=None):
        self.response = response
        self.more_info = more_info
        if more_info is not None:
            Log.DEBUG(more_info)
        Log.DEBUG(self.__str__())

    def __str__(self):
        return f'\n{json.dumps(self.data(), indent=3)}'

    def expect_no_error(self, additional_msg_if_fail=''):
        """
        @param additional_msg_if_fail: the name says it all
        @return:
        """
        assert self.get_error_msg() is None, f'{self.get_error_trace().get_message()}\n{additional_msg_if_fail}'
        return self

    def expect_error(self, expecting_error='any error'):
        if expecting_error == 'any error':
            INFO(self.get_error_trace().get_message())
            assert self.get_error_msg() is not None, \
                f'Found no error while expecting {expecting_error}'
        else:
            trace_msg = self.get_error_trace().get_message()
            INFO(trace_msg)
            assert (expecting_error in self.get_error_msg() or expecting_error in trace_msg), \
                f'Found no error while expecting {expecting_error}'
        return self

    def data(self):
        if type(self.response) is str:
            return json.loads(self.response)  # response from WebSocket
        return json.loads(self.response.text)  # response from rpc

    def params(self):
        return Response.Params(self.data()["Params"])

    def size(self):
        if self.response is str:  # response from WebSocket
            return len(self.response)
        return len(self.response.content)  # response from rpc

    def response_time(self):
        if self.response is str:  # response from WebSocket
            return None
        return self.response.elapsed.total_seconds()  # response from rpc

    def get_error_trace(self):
        if self.data()['Error'] is None:
            return ''
        return Response.StackTrace(self.data()['Error']['StackTrace'][0:512])

    def get_error_msg(self):
        if self.data()['Error'] is None:
            return None
        return self.data()['Error']['Message']

    def find_in_result(self, string):
        for k, v in self.data()["Result"].items():
            if k == str(string):
                return True
        return False

    def get_result(self, string=None):
        try:
            if string is None:
                return self.data()['Result']
            return self.data()['Result'][string]
        except(KeyError, TypeError):
            return None

    def get_tx_id(self):
        return self.get_result("TxID")

    def get_beacon_height(self):
        return self.get_result("BeaconHeight")

    def get_token_id_1_str(self):
        return self.get_result("TokenID1Str")

    def get_token_id_2_str(self):
        return self.get_result("TokenID2Str")

    def get_token_id(self):
        return self.get_result("TokenID")

    def get_returned_1_amount(self):
        return self.get_result("Returned1Amount")

    def get_returned_2_amount(self):
        return self.get_result("Returned2Amount")

    def get_contributed_1_amount(self):
        return self.get_result("Contributed1Amount")

    def get_contributed_2_amount(self):
        return self.get_result("Contributed2Amount")

    def get_fee(self):
        try:
            return self.get_result('Result')['Fee']
        except (KeyError, TypeError):
            return self.get_result('Fee')

    def get_tx_size(self):
        try:
            return self.get_result()['TxSize']
        except (KeyError, TypeError):
            return self.get_result('Result')['TxSize']

    def get_custom_token_privacy(self):
        return self.get_result("PrivacyCustomTokenIsPrivacy")

    def get_block_height(self):
        return self.get_result("BlockHeight")

    def get_tx_hashes(self):
        # for retrieveblockbyheight database v1
        ret = self.get_result("TxHashes")
        if ret is None:
            # for retrieveblockbyheight database v2
            ret = self.get_result()[0]["TxHashes"]
        return ret

    def get_list_txs(self):
        return self.get_result("ListTxs")

    def get_block_hash(self):
        return self.get_result("BlockHash")

    def get_shard_id(self):
        return self.get_result('ShardID')

    # !!!!!!!! Next actions base on response
    def subscribe_transaction(self, tx_id=None):
        """
        Subscribe transaction by txid

        :param tx_id: if not specified, use tx id from self
        :return: TransactionDetail Object
        """
        if tx_id is None:
            tx_id = self.get_tx_id()
        INFO(f'Subscribe to transaction tx_id = {tx_id}')
        from IncognitoChain.Objects.IncognitoTestCase import SUT
        from IncognitoChain.Objects.TransactionObjects import TransactionDetail
        tx = SUT().subscription().subscribe_pending_transaction(tx_id)
        return TransactionDetail(tx.get_result('Result'))

    def is_transaction_v2_error_appears(self):
        try:
            stack_trace_msg = self.get_error_trace().get_message()
        except AttributeError:
            return False
        if 'error calling MarshalJSON for type *transaction.TxTokenVersion2' in stack_trace_msg:
            INFO('Transaction v2 no longer support paying fee with token')
            return True

    def get_transaction_by_hash(self):
        return TransactionDetail().get_transaction_by_hash(self.get_tx_id())

    def get_mem_pool_transactions_id_list(self) -> list:
        hashes = self.get_list_txs()
        if hashes is None:
            return []
        tx_id_list = list()
        for entry in hashes:
            tx_id_list.append(entry['TxID'])
        return tx_id_list

    def get_created_proof(self):
        """
        get proof created by RPC "createtransaction"
        @return:
        """
        return self.get_result("Base58CheckData")

    class StackTrace:
        def __init__(self, stack_string):
            self.stack_string = stack_string

        def __str__(self):
            return self.stack_string

        def get_error_codes(self):
            code_list = re.findall("(-[0-9]\\w+: )", self.stack_string)
            return ''.join([str(elem) for elem in code_list])

        def get_message(self):
            try:
                i_start = len(self.get_error_codes())
                i_end = str.index(self.stack_string, 'github.com')
                return str(self.stack_string[i_start:i_end])
            except ValueError:
                return str(self.stack_string)

        def get_estimated_fee(self):
            return re.search("fee=(.*)", self.stack_string).group(1)

    class Params:
        def __init__(self, data):
            self.data = data

        def get_beacon_height(self):
            return int(self.data[0]["BeaconHeight"])

        def get_portal_redeem_req_id(self):
            return self.data[4]["UniqueRedeemID"]

        def get_portal_register_id(self):
            return self.data[4]['UniqueRegisterId']

        def get_portal_porting_fee(self):
            return int(self.data[4]['PortingFee'])

        def get_portal_register_amount(self):
            return int(self.data[4]['RegisterAmount'])

        def get_portal_redeem_amount(self):
            return int(self.data[4]['TokenAmount'])

        def get_portal_redeem_fee(self):
            return int(self.data[4]['RedeemFee'])
