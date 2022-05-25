import requests
from Struct.prototype import transaction
from log.bitcoin_tracing_logger import Bitcoin_logger
import time

url = 'https://blockchain.info/rawaddr/{}?limit={}&offset={}'
def checkaddress(address, proxy):
    time.sleep(1)
    if ' ' in address:
        return False
    tracing_json_data = address_request(address, proxy, 0, 1)
    return 'error' not in tracing_json_data


def get_address_to_trancation(address):
    transaction_class = transaction(address)
    tracing_json_data = address_request(address)
    transaction_class.default_setting(tracing_json_data)
    Bitcoin_logger.get_logger().info('Address : ' + transaction_class.address)
    Bitcoin_logger.get_logger().info('Transaction Count : ' + str(transaction_class.transaction['n_tx']))
    Bitcoin_logger.get_logger().info('Transaction UPDATE : ' + str(len(transaction_class.transaction['txs'])))
    count = tracing_json_data['n_tx']/5000 
    i = 1
    while count>1:
        tracing_json_data = address_request(address, i)
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
    #Bitcoin_logger.get_logger().info('Request URL : ' + url)
    try:
        return requests.get(url).json()
    except:
        raise Exception("Rate Limit Wait Request")

def create_url(address, limit, offset):
    return url.format(address, limit, offset*limit)

if __name__ == '__main__':
    address = 'bc1qsfxssclfwp3rykwjdl9ghz99j7zmw9yhvdnr2f'
    print("ADDRESS : {}".format(address))
    print(get_address_to_trancation(address))