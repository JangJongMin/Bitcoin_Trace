# import networkx as nx
# import matplotlib.pyplot as plt
from log.bitcoin_tracing_logger import Bitcoin_logger
from streamlit_agraph import Node, Edge
import requests
import time
#from pyvis.network import Network
#import random
#address = bc1qvzquqqazwh0ctt67z0y8m7esuw6786vje2emfp5m3eypn85ad68q9tez3x
class transaction():
    """
    Transacation Data Struct

    result -> + -
    inputs : value, addr
    out : addr, value

    """
    def __init__(self, address=None, time=None, filtering=0.1, depth=0, maxdepth=0, proxy=False):
        self.btc = 0.00000001
        self.address = address
        self.transaction = None
        self.time = time
        self.proxy_setting = proxy
        #print(maxdepth)
        self.maxdepth = maxdepth
        self.point_to_point_list = list()
        self.filtering = filtering
        self.depth=depth
        self.nodes = list()
        self.edges = list()
        self.timestamp = dict()
        self.node_count = 0
    def default_setting(self, tracing_json_data):
        self.transaction = tracing_json_data
    def tranaction_extend(self, txs):
        self.transaction['txs'].extend(txs)
    def point_to_point_filter(self):
        i = 0
        #print("Transaction : ",len(self.transaction['txs']))
        while i < len(self.transaction['txs']):
            Flag = True
            check = True
            if self.transaction['txs'][i]['result'] < 0: #송금
                for transaction in self.transaction['txs'][i]['inputs']:        
                    if transaction['prev_out']['addr'] != self.address:
                        check = False
                for transaction in self.transaction['txs'][i]['out']:
                    _ = 0
                    __ = None
                    while not __:
                        try:
                            __ = self.transaction['txs'][i]['out'][_]['addr']
                        except IndexError:
                            break
                        except:
                            _+=1
                    if not __:
                        Bitcoin_logger.get_logger().debug('IndexError')
                        #print("FUCK")
                        break
                    if not transaction['spent']:
                        continue
                    if not check and __ != transaction['addr']:
                        Flag = False
                        break
            else: #입금
                list_ = []
                for transaction in self.transaction['txs'][i]['inputs']:
                    list_.append(transaction['prev_out']['addr'])
                if len(list_) != 1:
                    list_.append(self.address)
                    for transaction in self.transaction['txs'][i]['out']:
                        if not transaction['spent']:
                            continue
                        if check and transaction['addr'] not in list_:
                            Flag = False
                            break
            if Flag:
                self.point_to_point_list.append(self.transaction['txs'].pop(i))
                continue
            i+=1
        print("[Filtering]Transaction : ",len(self.transaction['txs']))
        print("[Filtering]Point List : ", len(self.point_to_point_list))
    def data_mining(self):
        result = dict()
        for point_to_point in self.point_to_point_list:
            if point_to_point['result'] < 0: #입금
                for point in point_to_point['inputs']:
                    if point['prev_out']['addr'] == self.address:
                        outaddress = point_to_point['out'][0]['addr']
                        result[outaddress] = result.get(outaddress, 0) + point['prev_out']['value']
                        #print("[Result] : ", result)
                        self.timestamp[outaddress] = point_to_point['time']
                #print()
        address = [self.address]+list(result.keys())
        value = list(result.values())
        return address, value
    def create_node(self):
        #nodes.append(Node(id=i, label=str(i), size=200))
        Bitcoin_logger.get_logger().info('Creating Noad Start!')
        address , value = self.data_mining()
        #edges.append(Edge(source=k, target=v, type="STRAIGHT"))
        # _ = ["#%06x" % random.randint(0, 0xFFFFFF) for i in address]
        # self.add_nodes(range(len(address)), label = address, color=_)
        # _ = list()
        # for i in range(len(value)):
        #     _.append((0, i+1, 1))
        # self.add_edges(_)
        # self.show_buttons(filter_=True)
        # self.show('test.html')
        #print("[Depth {}] Value Address ".format(self.depth), address, value)
        _ = self.node_count
        for add in address:
            self.nodes.append(
                Node(id=self.node_count, label=add)
            )
            self.node_count += 1
        # if self.depth == 0:
        #     print(len(self.nodes))
        for i in range(len(value)):
            print("[Depth {}]Node Append".format(self.depth))
            self.edges.append(
                Edge(source=_, target=_+i+1, label="{:.8f}BTC".format(value[i]*self.btc),type="STRAIGHT")
            )
        if self.depth < self.maxdepth:
            for index, add in enumerate(address[1:]):
                self.trace(add, value[index], self.filtering, self.timestamp[add], self.depth+1, self.node_count-1)
        # if self.depth == 0:
        #     print(len(self.nodes))
        #pos = nx.spring_layout(self)
        #nx.draw(self, pos = pos, with_labels = True)
        #labels = nx.get_edge_attributes(self,'weight')
        #nx.draw_networkx_edge_labels(self, pos, edge_labels = labels)
        #nx.draw(self, with_labels = True)
        '''self.add_nodes_from([1,2,3,4,1,2])
        self.add_edge(1,2)
        self.add_edge(1,3)
        self.add_edge(3,4)
        nx.draw(self, with_labels=True)
        plt.show()'''
    def trace(self, address, bitcoin, filtering, time, depth, node_count):
        print("[Trace Start] Depth : ", depth)
        trace_transaction(self.nodes, self.edges ,address, bitcoin, filtering, time, depth, node_count, self.maxdepth)
    def crawling(self):
        time.sleep(2)
        tracing_json_data = address_request(self.address, self.proxy_setting)
        self.default_setting(tracing_json_data)
        Bitcoin_logger.get_logger().info('Address : ' + self.address)
        Bitcoin_logger.get_logger().info('Transaction Count : ' + str(self.transaction['n_tx']))
        Bitcoin_logger.get_logger().info('Transaction UPDATE : ' + str(len(self.transaction['txs'])))
        count = tracing_json_data['n_tx']/5000 
        i = 1
        while count>1:
            tracing_json_data = address_request(self.address, self.proxy_setting, i)
            self.tranaction_extend(tracing_json_data['txs'])
            Bitcoin_logger.get_logger().info('Transaction UPDATE : ' + str(len(self.transaction['txs'])))
            count-=1
            i+=1
            time.sleep(2)
        self.point_to_point_filter()
        return self

class trace_transaction(transaction):
    def __init__(self, nodes, edges, address, bitcoin, filtering, time, depth, node_count, maxdepth):
        super().__init__()
        self.address = address
        self.nodes = nodes
        self.bitcoin = bitcoin
        self.filtering = filtering
        self.maxdepth = maxdepth
        self.node_count = node_count
        self.depth = depth
        self.time = time
        self.edges = edges
        Bitcoin_logger.get_logger().info('[Retranscation] ' + self.address)
        self.crawling()
        self.create_node()
    def data_mining(self):
        result = dict()
        for point_to_point in self.point_to_point_list:
            if point_to_point['result'] < 0: #입금
                for point in point_to_point['inputs']:
                    if point['prev_out']['addr'] == self.address:
                        outaddress = point_to_point['out'][0]['addr']
                        result[outaddress] = result.get(outaddress, 0) + point['prev_out']['value']
                        self.timestamp[outaddress] = point_to_point['time']
        address = [self.address]+list(result.keys())
        value = list(result.values())
        return address, value
    def crawling(self):
        time.sleep(2)
        tracing_json_data = address_request(self.address, self.proxy_setting, 0, 5000)
        self.default_setting(tracing_json_data)
        Bitcoin_logger.get_logger().info('Address : ' + self.address)
        Bitcoin_logger.get_logger().info('Transaction Count : ' + str(self.transaction['n_tx']))
        Bitcoin_logger.get_logger().info('Transaction UPDATE : ' + str(len(self.transaction['txs'])))
        count = tracing_json_data['n_tx']/5000
        i = 1
        while count>1 or self.last_time():
            tracing_json_data = address_request(self.address, self.proxy_setting, i, 5000)
            self.tranaction_extend(tracing_json_data['txs'])
            Bitcoin_logger.get_logger().info('Transaction UPDATE : ' + str(len(self.transaction['txs'])))
            count-=1
            i+=1
            time.sleep(2)
        self.point_to_point_filter()
    def last_time(self):
        return self.transaction['txs'][-1]['time'] > self.time

url = 'https://blockchain.info/rawaddr/{}?limit={}&offset={}'

def get_address_to_trancation(address):
    transaction_class = transaction(address)
    tracing_json_data = address_request(address, self.proxy_setting)
    transaction_class.default_setting(tracing_json_data)
    Bitcoin_logger.get_logger().info('Address : ' + transaction_class.address)
    Bitcoin_logger.get_logger().info('Transaction Count : ' + str(transaction_class.transaction['n_tx']))
    Bitcoin_logger.get_logger().info('Transaction UPDATE : ' + str(len(transaction_class.transaction['txs'])))
    count = tracing_json_data['n_tx']/5000 
    i = 1
    while count>1:
        tracing_json_data = address_request(address, self.proxy_setting, i)
        transaction_class.tranaction_extend(tracing_json_data['txs'])
        Bitcoin_logger.get_logger().info('Transaction UPDATE : ' + str(len(transaction_class.transaction['txs'])))
        count-=1
        i+=1
    transaction_class.point_to_point_filter()
    return transaction_class
    #Data split && Get Informaction

def address_request(address, proxy_setting, offset=0, limit=5000):
    url = create_url(address, limit, offset)
    Bitcoin_logger.get_logger().info('[Request]Address: {}, limit: {} , offest: {}'.format(address, limit, offset))
    if proxy_setting:
        return proxy_get_address_to_json(url)
    else:
        return get_address_to_json(url)

def proxy_get_address_to_json(url):
    Bitcoin_logger.get_logger().info('[Proxy]Request URL : ' + url)
    session = requests.session()
    session.proxies = {}
    session.proxies['http'] = 'socks5://localhost:9050'
    session.proxies['https'] = 'socks5://localhost:9050'
    request_headers = { 
        "accept-language":	"ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "accept-encoding":	"gzip, deflate, br",
        "sec-fetch-dest":	"document",
        "sec-fetch-user":   "1",
        "sec-fetch-mode":	"navigate",
        "sec-fetch-site":	"none",
        "accept":	"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent":	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
        "upgrade-insecure-requests":	"1",
        "sec-ch-ua-platform":	"macOS",
        "sec-ch-ua-mobile": "0",
        "sec-ch-ua":	'Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96'
    }
    try:
        return session.get(url, headers=request_headers).json()
    except:
        raise Exception("Rate Limit Wait Request")

def get_address_to_json(url):
    Bitcoin_logger.get_logger().info('Request URL : ' + url)
    try:
        return requests.get(url).json()
    except:
        raise "Rate Limit Wait Request"

def create_url(address, limit, offset):
    return url.format(address, limit, offset*limit)
