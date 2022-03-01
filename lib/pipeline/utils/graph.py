# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""


class Graph(object):
    def __init__(self, nodes, flows):
        self.nodes = nodes
        self.flows = flows
        self.path = []
        self.last_visited_node = ""
        self.graph = {node: [] for node in self.nodes}
        for flow in self.flows:
            self.graph[flow[0]].append(flow[1])

    def has_cycle(self):
        self.path = []
        visited = {node: False for node in self.nodes}
        visit_stack = {node: False for node in self.nodes}

        for node in self.nodes:
            if self._has_cycle(node, visited, visit_stack):
                return True
        return False

    def _has_cycle(self, node, visited, visit_stack):
        self.last_visited_node = node
        self.path.append(node)
        visited[node] = True
        visit_stack[node] = True

        for neighbor in self.graph[node]:
            if not visited[neighbor]:
                if self._has_cycle(neighbor, visited, visit_stack):
                    return True
            elif visit_stack[neighbor]:
                self.path.append(neighbor)
                return True

        self.path.remove(node)
        visit_stack[node] = False
        return False

    def get_cycle(self):
        if self.has_cycle():
            cross_node = self.path[-1]
            if self.path.count(cross_node) > 1:
                return self.path[self.path.index(cross_node) :]
            else:
                return self.path
        return []


if __name__ == "__main__":
    graph1 = Graph([1, 2, 3, 4], [[1, 2], [2, 3], [3, 4]])
    assert not graph1.has_cycle()
    assert graph1.get_cycle() == []
    graph2 = Graph([1, 2, 3, 4], [[1, 2], [2, 3], [3, 4], [4, 1]])
    assert graph2.has_cycle()
    assert graph2.get_cycle() == [1, 2, 3, 4, 1]
    graph3 = Graph([1, 2, 3, 4], [[1, 2], [2, 3], [3, 4], [4, 2]])
    assert graph3.has_cycle()
    assert graph3.get_cycle() == [2, 3, 4, 2]
    graph4 = Graph(
        [
            "n20c4a0601193f268bfa168f1192eacd",
            "nef42d10350b3961b53df7af67e16d9b",
            "n0ada7b4abe63771a43052eaf188dc4b",
            "n0cd3b95c714388bacdf1a486ab432fc",
            "n1430047af8537f88710c4bbf3cbfb0f",
            "n383748fe27434d582f0ca17af9d968a",
            "n51426abd4be3a4691c80a73c3f93b3c",
            "n854753a77933562ae72ec87c365f23d",
            "n89f083892a731d7b9d7edb0f372006d",
            "n8d4568db0ad364692b0387e86a2f1e0",
            "n8daedbb02273a0fbc94cc118c90649f",
            "n90b7ef55fe839b181879e036b4f8ffe",
            "n99817348b4a36a6931854c93eed8c5f",
            "na02956eba6f3a36ab9b0af2f2350213",
            "nc3d0d49adf530bbaffe53630c184c0a",
            "nca50848d1aa340f8c2b4776ce81868d",
            "ncab9a48e79d357195dcee68dad3a31f",
            "ncb4e013a6a8348bab087cc8500a3876",
            "ne1f86f902a23e7fa4a67192e8b38a05",
            "ne26def77df1385caa206c64e7e3ea53",
            "nf3ebee137c53da28091ad7d140ce00c",
            "nfc1dcdd7476393b9a81a988c113e1cf",
            "n0197f8f210b3a1b8a7fc2f90e94744e",
            "n01fb40259ad3cf285bb11a8bbbe59f2",
            "n03f39191e8a32629145ba6a677ed040",
            "n03ffc3b9e12316d8be63261cb9dec71",
            "n07982b8985139249bca3a046f3a4379",
            "n0b9e36e6b633ddb906d2044f658f110",
            "n136c4fedebe3eb0ba932495aff6a945",
            "n17cdc62c5d43976a413bda8f35634eb",
            "n1d48483d8023439ad98d61d156c85fb",
            "n26725bdcc0931fab0bc73e7244545ca",
            "n2890db24f6c3cd1bbcd6b7d8cf2c045",
            "n2ad9caac5b737bd897d4c8844c85f12",
            "n2c88d1c1d8b35aebf883cbf259fb6bc",
            "n302d25dfc9c369ab13104d5208e7119",
            "n31688b7ab44338e9e6cb8dcaf259eef",
            "n374443fbdc1313d98ebbe19d535fec2",
            "n38c3dd0344a3f86bc7511c454bcdf4c",
            "n3934eef90463940a6a9cf4ba2e63b1c",
            "n40d5f0ca4bc3dd99c0b264cb186f00f",
            "n476ddcb6dd33e2abac43596b08c2bc1",
            "n4790f8aa48e335aa712e2af757e180b",
            "n48bbfdc912334fc89c4f48c05e8969e",
            "n5bef4f4532a382eaf79a0af70b2396b",
            "n5ced56bcc863060ac4977755f35a5f5",
            "n66a0562670e37648a3e05c243335bff",
            "n6dc118cd3f7341d9ef8c97c63e2e9d9",
            "n6e9d52e1ea53958a93e5b34022e7037",
            "n786694b5ed33295a885b5bcd8c7c1ce",
            "n7dccd56c80233469a4609f684ebe457",
            "n8492d92ab6a3da48c2b49d6fcb8a479",
            "n86a8b1a56f9399f90c4c227594a9d03",
            "n8a805c0cd02307bad9f7828880b53dc",
            "n8c7e35b0457300d9d6a96a6b1d18329",
            "n91fdaed36403d06a07f4afe85e2892c",
            "n9335d0718a937f9a39ec5b36d5637fe",
            "n9372fb07ad936cba31f3d4e440f395a",
            "n9ab96f926d83a93a5d3ebe2888fd343",
            "na2a8a54e68033d0a276eb88dbff91c3",
            "na493a7b5d5b3cc29f4070a6c4589cb7",
            "nadfa68cb2503a39aac6626d6c72484a",
            "nae1218ddd2e3448b562bc79dc084401",
            "nc012287be793377b975b0230b35d713",
            "ncb2e01f0c5336fe82b0e0e496f2612b",
            "ncb5843900903b4c8a0a8302474d8c51",
            "ncbf4db2c48f3348b2c7081f9e3b363a",
            "nd4ee6c3248935ce9239e4bb20a81ab8",
            "ndb1cf7af0e2319c9868530d0df8fd93",
            "ne36a6858a733430bffa4fec053dc1ab",
            "ne7af4a7c3613b3d81fe9e6046425a36",
            "ne8035dd8de732758c1cc623f80f2fc8",
            "ned91fdb914c35f3a21f320f62d72ffd",
            "nf5448b3c66430f4a299d08208d313a6",
            "nfaa0756a06f300495fb2e2e45e05ed3",
        ],
        [
            ["n8d4568db0ad364692b0387e86a2f1e0", "n5bef4f4532a382eaf79a0af70b2396b"],
            ["n8daedbb02273a0fbc94cc118c90649f", "nf5448b3c66430f4a299d08208d313a6"],
            ["n01fb40259ad3cf285bb11a8bbbe59f2", "ne1f86f902a23e7fa4a67192e8b38a05"],
            ["ncab9a48e79d357195dcee68dad3a31f", "n0197f8f210b3a1b8a7fc2f90e94744e"],
            ["na493a7b5d5b3cc29f4070a6c4589cb7", "ne1f86f902a23e7fa4a67192e8b38a05"],
            ["n89f083892a731d7b9d7edb0f372006d", "n136c4fedebe3eb0ba932495aff6a945"],
            ["n51426abd4be3a4691c80a73c3f93b3c", "n9ab96f926d83a93a5d3ebe2888fd343"],
            ["n89f083892a731d7b9d7edb0f372006d", "n8492d92ab6a3da48c2b49d6fcb8a479"],
            ["n17cdc62c5d43976a413bda8f35634eb", "n6e9d52e1ea53958a93e5b34022e7037"],
            ["n476ddcb6dd33e2abac43596b08c2bc1", "ne1f86f902a23e7fa4a67192e8b38a05"],
            ["n6dc118cd3f7341d9ef8c97c63e2e9d9", "nfc1dcdd7476393b9a81a988c113e1cf"],
            ["n91fdaed36403d06a07f4afe85e2892c", "ncb4e013a6a8348bab087cc8500a3876"],
            ["n8a805c0cd02307bad9f7828880b53dc", "n3934eef90463940a6a9cf4ba2e63b1c"],
            ["n2890db24f6c3cd1bbcd6b7d8cf2c045", "n0ada7b4abe63771a43052eaf188dc4b"],
            ["ned91fdb914c35f3a21f320f62d72ffd", "n383748fe27434d582f0ca17af9d968a"],
            ["n89f083892a731d7b9d7edb0f372006d", "n0b9e36e6b633ddb906d2044f658f110"],
            ["nc3d0d49adf530bbaffe53630c184c0a", "na493a7b5d5b3cc29f4070a6c4589cb7"],
            ["ncb2e01f0c5336fe82b0e0e496f2612b", "nc012287be793377b975b0230b35d713"],
            ["n86a8b1a56f9399f90c4c227594a9d03", "nf3ebee137c53da28091ad7d140ce00c"],
            ["nc3d0d49adf530bbaffe53630c184c0a", "nadfa68cb2503a39aac6626d6c72484a"],
            ["na02956eba6f3a36ab9b0af2f2350213", "na2a8a54e68033d0a276eb88dbff91c3"],
            ["n8daedbb02273a0fbc94cc118c90649f", "n07982b8985139249bca3a046f3a4379"],
            ["n136c4fedebe3eb0ba932495aff6a945", "nfc1dcdd7476393b9a81a988c113e1cf"],
            ["n9372fb07ad936cba31f3d4e440f395a", "n1430047af8537f88710c4bbf3cbfb0f"],
            ["n8d4568db0ad364692b0387e86a2f1e0", "n91fdaed36403d06a07f4afe85e2892c"],
            ["n854753a77933562ae72ec87c365f23d", "n40d5f0ca4bc3dd99c0b264cb186f00f"],
            ["n854753a77933562ae72ec87c365f23d", "n1d48483d8023439ad98d61d156c85fb"],
            ["n9ab96f926d83a93a5d3ebe2888fd343", "n383748fe27434d582f0ca17af9d968a"],
            ["ne36a6858a733430bffa4fec053dc1ab", "n0cd3b95c714388bacdf1a486ab432fc"],
            ["n03ffc3b9e12316d8be63261cb9dec71", "nca50848d1aa340f8c2b4776ce81868d"],
            ["ne8035dd8de732758c1cc623f80f2fc8", "n0ada7b4abe63771a43052eaf188dc4b"],
            ["n51426abd4be3a4691c80a73c3f93b3c", "ned91fdb914c35f3a21f320f62d72ffd"],
            ["nd4ee6c3248935ce9239e4bb20a81ab8", "nfaa0756a06f300495fb2e2e45e05ed3"],
            ["n5bef4f4532a382eaf79a0af70b2396b", "ncb4e013a6a8348bab087cc8500a3876"],
            ["ne26def77df1385caa206c64e7e3ea53", "n786694b5ed33295a885b5bcd8c7c1ce"],
            ["n854753a77933562ae72ec87c365f23d", "ne8035dd8de732758c1cc623f80f2fc8"],
            ["n374443fbdc1313d98ebbe19d535fec2", "ndb1cf7af0e2319c9868530d0df8fd93"],
            ["nfaa0756a06f300495fb2e2e45e05ed3", "n8c7e35b0457300d9d6a96a6b1d18329"],
            ["n90b7ef55fe839b181879e036b4f8ffe", "n26725bdcc0931fab0bc73e7244545ca"],
            ["n8d4568db0ad364692b0387e86a2f1e0", "ncb2e01f0c5336fe82b0e0e496f2612b"],
            ["ncb5843900903b4c8a0a8302474d8c51", "ncb4e013a6a8348bab087cc8500a3876"],
            ["nf5448b3c66430f4a299d08208d313a6", "nf3ebee137c53da28091ad7d140ce00c"],
            ["n20c4a0601193f268bfa168f1192eacd", "nd4ee6c3248935ce9239e4bb20a81ab8"],
            ["nca50848d1aa340f8c2b4776ce81868d", "nc3d0d49adf530bbaffe53630c184c0a"],
            ["na02956eba6f3a36ab9b0af2f2350213", "n03ffc3b9e12316d8be63261cb9dec71"],
            ["n7dccd56c80233469a4609f684ebe457", "n8daedbb02273a0fbc94cc118c90649f"],
            ["n0ada7b4abe63771a43052eaf188dc4b", "na02956eba6f3a36ab9b0af2f2350213"],
            ["n9335d0718a937f9a39ec5b36d5637fe", "n99817348b4a36a6931854c93eed8c5f"],
            ["n90b7ef55fe839b181879e036b4f8ffe", "n5ced56bcc863060ac4977755f35a5f5"],
            ["ncb4e013a6a8348bab087cc8500a3876", "ne26def77df1385caa206c64e7e3ea53"],
            ["na02956eba6f3a36ab9b0af2f2350213", "n4790f8aa48e335aa712e2af757e180b"],
            ["nc012287be793377b975b0230b35d713", "ncb4e013a6a8348bab087cc8500a3876"],
            ["n8d4568db0ad364692b0387e86a2f1e0", "ncb5843900903b4c8a0a8302474d8c51"],
            ["n40d5f0ca4bc3dd99c0b264cb186f00f", "n0ada7b4abe63771a43052eaf188dc4b"],
            ["n38c3dd0344a3f86bc7511c454bcdf4c", "n17cdc62c5d43976a413bda8f35634eb"],
            ["n6e9d52e1ea53958a93e5b34022e7037", "n90b7ef55fe839b181879e036b4f8ffe"],
            ["nf3ebee137c53da28091ad7d140ce00c", "n51426abd4be3a4691c80a73c3f93b3c"],
            ["n99817348b4a36a6931854c93eed8c5f", "n89f083892a731d7b9d7edb0f372006d"],
            ["n89f083892a731d7b9d7edb0f372006d", "n6dc118cd3f7341d9ef8c97c63e2e9d9"],
            ["n8daedbb02273a0fbc94cc118c90649f", "n66a0562670e37648a3e05c243335bff"],
            ["nadfa68cb2503a39aac6626d6c72484a", "ne1f86f902a23e7fa4a67192e8b38a05"],
            ["n383748fe27434d582f0ca17af9d968a", "nef42d10350b3961b53df7af67e16d9b"],
            ["na02956eba6f3a36ab9b0af2f2350213", "n03f39191e8a32629145ba6a677ed040"],
            ["nae1218ddd2e3448b562bc79dc084401", "n383748fe27434d582f0ca17af9d968a"],
            ["n26725bdcc0931fab0bc73e7244545ca", "n1430047af8537f88710c4bbf3cbfb0f"],
            ["n48bbfdc912334fc89c4f48c05e8969e", "n8a805c0cd02307bad9f7828880b53dc"],
            ["ne7af4a7c3613b3d81fe9e6046425a36", "ncb4e013a6a8348bab087cc8500a3876"],
            ["nfc1dcdd7476393b9a81a988c113e1cf", "n8d4568db0ad364692b0387e86a2f1e0"],
            ["n0197f8f210b3a1b8a7fc2f90e94744e", "n99817348b4a36a6931854c93eed8c5f"],
            ["n90b7ef55fe839b181879e036b4f8ffe", "n302d25dfc9c369ab13104d5208e7119"],
            ["n1d48483d8023439ad98d61d156c85fb", "n0ada7b4abe63771a43052eaf188dc4b"],
            ["na2a8a54e68033d0a276eb88dbff91c3", "nca50848d1aa340f8c2b4776ce81868d"],
            ["n90b7ef55fe839b181879e036b4f8ffe", "n9372fb07ad936cba31f3d4e440f395a"],
            ["ndb1cf7af0e2319c9868530d0df8fd93", "n2ad9caac5b737bd897d4c8844c85f12"],
            ["n8492d92ab6a3da48c2b49d6fcb8a479", "nfc1dcdd7476393b9a81a988c113e1cf"],
            ["n8d4568db0ad364692b0387e86a2f1e0", "ne7af4a7c3613b3d81fe9e6046425a36"],
            ["n302d25dfc9c369ab13104d5208e7119", "n1430047af8537f88710c4bbf3cbfb0f"],
            ["n51426abd4be3a4691c80a73c3f93b3c", "n2c88d1c1d8b35aebf883cbf259fb6bc"],
            ["n786694b5ed33295a885b5bcd8c7c1ce", "n0cd3b95c714388bacdf1a486ab432fc"],
            ["n854753a77933562ae72ec87c365f23d", "n2890db24f6c3cd1bbcd6b7d8cf2c045"],
            ["nc3d0d49adf530bbaffe53630c184c0a", "n476ddcb6dd33e2abac43596b08c2bc1"],
            ["n2c88d1c1d8b35aebf883cbf259fb6bc", "n383748fe27434d582f0ca17af9d968a"],
            ["n0cd3b95c714388bacdf1a486ab432fc", "n854753a77933562ae72ec87c365f23d"],
            ["n51426abd4be3a4691c80a73c3f93b3c", "nae1218ddd2e3448b562bc79dc084401"],
            ["nc3d0d49adf530bbaffe53630c184c0a", "n01fb40259ad3cf285bb11a8bbbe59f2"],
            ["ne1f86f902a23e7fa4a67192e8b38a05", "n374443fbdc1313d98ebbe19d535fec2"],
            ["n0b9e36e6b633ddb906d2044f658f110", "nfc1dcdd7476393b9a81a988c113e1cf"],
            ["ncab9a48e79d357195dcee68dad3a31f", "ncbf4db2c48f3348b2c7081f9e3b363a"],
            ["n8daedbb02273a0fbc94cc118c90649f", "n86a8b1a56f9399f90c4c227594a9d03"],
            ["ncbf4db2c48f3348b2c7081f9e3b363a", "n99817348b4a36a6931854c93eed8c5f"],
            ["n1430047af8537f88710c4bbf3cbfb0f", "ncab9a48e79d357195dcee68dad3a31f"],
            ["n4790f8aa48e335aa712e2af757e180b", "nca50848d1aa340f8c2b4776ce81868d"],
            ["ne26def77df1385caa206c64e7e3ea53", "ne36a6858a733430bffa4fec053dc1ab"],
            ["ncab9a48e79d357195dcee68dad3a31f", "n31688b7ab44338e9e6cb8dcaf259eef"],
            ["n07982b8985139249bca3a046f3a4379", "nf3ebee137c53da28091ad7d140ce00c"],
            ["n66a0562670e37648a3e05c243335bff", "nf3ebee137c53da28091ad7d140ce00c"],
            ["n03f39191e8a32629145ba6a677ed040", "nca50848d1aa340f8c2b4776ce81868d"],
            ["n8c7e35b0457300d9d6a96a6b1d18329", "n38c3dd0344a3f86bc7511c454bcdf4c"],
            ["n5ced56bcc863060ac4977755f35a5f5", "n1430047af8537f88710c4bbf3cbfb0f"],
            ["n2ad9caac5b737bd897d4c8844c85f12", "n48bbfdc912334fc89c4f48c05e8969e"],
            ["n31688b7ab44338e9e6cb8dcaf259eef", "n99817348b4a36a6931854c93eed8c5f"],
            ["n3934eef90463940a6a9cf4ba2e63b1c", "n7dccd56c80233469a4609f684ebe457"],
            ["ncab9a48e79d357195dcee68dad3a31f", "n9335d0718a937f9a39ec5b36d5637fe"],
        ],
    )
    assert not graph4.has_cycle()
    assert graph4.get_cycle() == []
    graph5 = Graph([1, 2, 3, 4, 5], [[1, 2], [2, 3], [2, 4], [4, 5], [5, 2]])
    assert graph5.has_cycle()
    assert graph5.get_cycle() == [2, 4, 5, 2]
