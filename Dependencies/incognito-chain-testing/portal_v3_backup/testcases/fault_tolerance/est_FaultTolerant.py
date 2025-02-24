"""
Created Oct 11 2019
@Author: Khanh Le
"""
# pylint: disable = too-many-public-methods
import unittest

# from Automation.pages.sign_up.base_sign_up import BaseSignUp
# from Automation.util.utils import Utils
# from Automation.util.mail_checking import MailChecking
# from Automation.pages.menu.main_menu import MainMenu
# from Automation.pages.login.base_login import BaseLogin
# from Automation.pages.user_profile.base_user_profile import BaseUserProfile
# from Automation.workflow.sign_up import SignUp
import pytest

import topology.NodeList as NodeList
from libs.NodeHandler import SSH2PC
from libs.Transaction import Transaction
from libs.WebSocket import WebSocket
# from ddt import ddt, data
from libs.AutoLog import STEP


class test_sendPRV(unittest.TestCase):
    """
    Test case: Send PRV
    """

    test_data = {
        'address1_privatekey':
            "112t8rnX5E2Mkqywuid4r4Nb2XTeLu3NJda43cuUM1ck2brpHrufi4Vi42EGybFhzfmouNbej81YJVoWewJqbR4rPhq2H945BXCLS2aDLBTA",
        'address1_payment':
            "12RxERBySmquLtM1R1Dk2s7J4LyPxqHxcZ956kupQX3FPhVo2KtoUYJWKet2nWqWqSh3asWmgGTYsvz3jX73HqD8Jr2LwhjhJfpG756",
        'address2_payment':
            "12RyJTSL2G8KvjN7SUFuiS9Ek4pvFFze3EMMic31fmXVw8McwYzpKPpxeW6TLsNo1UoPhCHKV3GDRLQwdLF41PED3LQNCLsGNKzmCE5",
        'address2_privatekey':
            "112t8rnXVMJJZzfF1naXvfE9nkTKwUwFWFeh8cfEyViG1vpA8A9khJk3mhyB1hDuJ4RbreDTsZpgJK4YcSxdEpXJKMEd8Vmp5UqKWwBcYzxv",
        'address3_payment':
            "12RtmpqwyzghGQJHXGRhXnNqs7SDhx1wXemgAZNC2xePj9DNpxcTZfpwCeNoBvvyxNU8n2ChVijPhSsNhGCDmFmiwXSjQEMSef4cMFG",
        'address3_privatekey':
            "112t8rnXJgKz6wxuvo6s8aFHFN16j9fvh7y3ZLdrQpN1zRZcubmekm7WHc8KjQS3EWeGBCq8L7qQTuVm3QtnEX66WFHP5e7v6fQunJRJZx2c",
        'prv_amount': 1 * 1000000000

    }


    shard03 = Transaction(NodeList.shard0[3]['ip'], NodeList.shard0[3]['rpc'])
    shard03ws = WebSocket(NodeList.shard0[3]['ip'], NodeList.shard0[3]['ws'])
    

    def stopNode(self, ip, username, stakename):
        staking = SSH2PC(ip, username, "na")
        print(staking.stopDocker(stakename))
        # print(staking.startDocker(stakename))
        staking.logout()

    def startNode(self, ip, username, stakename):
        staking = SSH2PC(ip, username, "na")
        # print(staking.stopDocker(stakename))
        print(staking.startDocker(stakename))
        staking.logout()

    def delDbNode(self, ip, username, stakename):
        staking = SSH2PC(ip, username, "na")
        # print(staking.stopDocker(stakename))
        print(staking.deleteDatabase(stakename))
        staking.logout()

    @pytest.mark.run
    def est_1stopnode_shard0(self):
        """
        Verify 
        """
        self.stopNode("51.79.78.184", "root", "staking15")
        self.stopNode("35.196.237.28", "david", "staking56")
        self.stopNode("157.230.150.190", "root", "staking10")
        self.stopNode("51.91.247.206", "root", "staking23")
        self.stopNode("35.227.101.26", "david", "staking51")
        self.stopNode("35.227.83.106", "david", "staking57")

        self.stopNode("51.79.78.184", "root", "staking16")
        self.stopNode("35.196.237.28", "david", "staking53")

    @pytest.mark.run
    def est_1startnode_shard0(self):
        """
        Verify 
        """
        self.startNode("51.79.78.184", "root", "staking15")
        self.startNode("35.196.237.28", "david", "staking56")
        self.startNode("157.230.150.190", "root", "staking10")
        self.startNode("51.91.247.206", "root", "staking23")
        self.startNode("35.227.101.26", "david", "staking51")
        self.startNode("35.227.83.106", "david", "staking57")

        self.startNode("51.79.78.184", "root", "staking16")
        self.startNode("35.196.237.28", "david", "staking53")

    @pytest.mark.run
    def est_1stopnode_shard4(self):
        """
        Verify 
        """
        # self.stopNode("35.245.162.129","david","staking41")
        # self.stopNode("34.74.120.99","david","staking78")
        # self.stopNode("35.227.101.26","david","staking49")
        # self.stopNode("34.73.39.182","david","staking70")
        self.stopNode("35.196.237.28", "david", "staking55")

        self.stopNode("35.196.115.97", "david", "staking61")

    @pytest.mark.run
    def est_1startnode_shard4(self):
        """
        Verify 
        """
        self.startNode("35.245.162.129", "david", "staking41")
        self.startNode("34.74.120.99", "david", "staking78")
        self.startNode("35.227.101.26", "david", "staking49")
        self.startNode("34.73.39.182", "david", "staking70")
        self.startNode("35.196.237.28", "david", "staking55")

        self.startNode("35.196.115.97", "david", "staking61")

    @pytest.mark.run
    def est_1deldbnode_shard4(self):
        """
        Verify 
        """
        self.delDbNode("35.245.162.129", "david", "staking41")
        self.delDbNode("34.74.120.99", "david", "staking78")
        # self.delDbNode("35.227.101.26","david","staking49")
        # self.delDbNode("34.73.39.182","david","staking70")
        # self.delDbNode("35.196.237.28","david","staking55")

        # self.delDbNode("35.196.115.97","david","staking61")

    @pytest.mark.run
    def test_2sendPRV_privacy_1shard(self):
        """
        Verify send PRV to another address
        """
        print("\n")
        STEP("1. get address1 balance")
        # shard0_15.sendTransaction(self.test_data['address1_privatekey'], self.test_data['address3_payment'], 100)
        step1_result = self.shard0_15.getBalance(self.test_data["address1_privatekey"])
        # step1_result = self.get_balance(self.test_data["shard0"], self.test_data["address1_privatekey"])
        print("addr1_balance: " + str(step1_result))
        assert step1_result != "Invalid parameters"

        STEP("2. get address2 balance")
        # step2_result = self.get_balance(self.test_data["shard0"], self.test_data["address2_privatekey"])
        step2_result = self.shard0_15.getBalance(self.test_data["address2_privatekey"])
        print("addr2_balance: " + str(step2_result))
        assert step2_result != "Invalid parameters"

        STEP("3. from address1 send prv to address2")
        step3_result = self.shard0_15.sendTransaction(self.test_data["address1_privatekey"],
                                     self.test_data["address2_payment"], self.test_data["prv_amount"])
        print("transaction id: " + step3_result)
        assert step3_result != 'Can not create tx'

        STEP("3.1 subcribe transaction")
        # step31 = WebSocket(self.test_data["ws0"])
        self.shard0_15ws.createConnection()
        step31_result = self.shard0_15ws.subcribePendingTransaction(step3_result)
        # step31.closeConnection()
        # print (step31_result)
        # assert step3_result != 'Can not create tx'

        # print("sleep 3")
        # time.sleep(3)

        STEP("4. check address1 balance")
        step4_result = self.shard0_15.getBalance(self.test_data["address1_privatekey"])
        print("addr1_balance: " + str(step4_result))
        assert step4_result == step1_result - self.test_data["prv_amount"]

        STEP("5. check address2 balance")
        step5_result = self.shard0_15.getBalance(self.test_data["shard0"], self.test_data["address2_privatekey"])
        print("addr2_balance: " + str(step5_result))
        assert step5_result == step2_result + self.test_data["prv_amount"]

    @pytest.mark.run
    def est_3sendPRV_privacy_Xshard(self):
        """
        Verify send PRV to another address
        """
        print("\n")
        STEP("1. get address1 balance")
        step1_result = self.get_balance(self.test_data["shard0"], self.test_data["address1_privatekey"])
        print("addr1_balance: " + str(step1_result))
        assert step1_result != "Invalid parameters"

        STEP("2. get address3 balance")
        step2_result = self.get_balance(self.test_data["shard4"], self.test_data["address3_privatekey"])
        print("addr3_balance: " + str(step2_result))
        assert step2_result != "Invalid parameters"

        STEP("3. from address1 send prv to address3")
        step3_result = self.send_trx(self.test_data["shard0"], self.test_data["address1_privatekey"],
                                     self.test_data["address3_payment"], self.test_data["prv_amount"])
        print("transaction id: " + step3_result)
        assert step3_result != 'Can not create tx'

        STEP("3.1 subcribe transaction")
        step31 = WebSocket(self.test_data["ws0"])
        step31.createConnection()
        step31_result = step31.subcribePendingTransaction(step3_result)
        step31.closeConnection()

        STEP("3.2 subcribe cross transaction")
        step32 = WebSocket(self.test_data["ws4"])
        step32.createConnection()
        step32_result = step32.subcribeCrossOutputCoinByPrivatekey(self.test_data["address3_privatekey"])
        step32.closeConnection()

        STEP("4. check address1 balance")
        step4_result = self.get_balance(self.test_data["shard0"], self.test_data["address1_privatekey"])
        print("addr1_balance: " + str(step4_result))
        assert step4_result == step1_result - self.test_data["prv_amount"]

        STEP("5. check address3 balance")
        step5_result = self.get_balance(self.test_data["shard4"], self.test_data["address3_privatekey"])
        print("addr3_balance: " + str(step5_result))
        assert step5_result == step2_result + self.test_data["prv_amount"]

    @pytest.mark.run
    def est_4offBlockProposer(self):
        """
        Verify send PRV to another address
        """
        STEP("1. subcribe cross transaction")
        step1 = WebSocket(self.test_data["ws4"])
        step1.createConnection()
        step1_result = step1.subcribeCrossOutputCoinByPrivatekey(self.test_data["address3_privatekey"])
        step1.closeConnection()

    @pytest.mark.run
    def test_cleanup(self):
        """
        CLEAN UP
        """
        self.shard0_15ws.closeConnection()
