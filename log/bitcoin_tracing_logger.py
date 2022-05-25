import logging

class Bitcoin_logger(logging.Logger):

    # -- Init
    logging.basicConfig(format='[%(asctime)s][%(levelname)s][Bitcoin][%(module)s][%(funcName)s:%(lineno)d] ' +
                               '%(message)s')
    _logger = logging.getLogger('DagdaLogger')
    _logger.setLevel('INFO')

    # -- Static methods
    @staticmethod
    def get_logger():
        return Bitcoin_logger._logger
    @staticmethod
    def set_level(level):
        Bitcoin_logger._logger.setLevel(level)
