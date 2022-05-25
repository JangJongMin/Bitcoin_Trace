from Module.crawling import get_address_to_trancation
from log.bitcoin_tracing_logger import Bitcoin_logger

class Bitcoin(object):
    def __init__(self):
        pass

def main():
    token_16 = "bc1qsfxssclfwp3rykwjdl9ghz99j7zmw9yhvdnr2f"
    token_5000 = "3D2oetdNuZUqQHPJmcMDDHYoqkyNVsFk9r"
    transaction_class = get_address_to_trancation(token_5000)
    transaction_class.create_node()


if __name__ == '__main__':
    Bitcoin_logger.get_logger().debug('main start')
    main()