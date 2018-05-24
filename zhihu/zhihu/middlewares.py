
import logging

logger=logging.getLogger()

class monitor(object):
    def process_request(self, request, spider):
        logger.info('monitor process_request:',request.url)

    def process_response(request, response, spider):
        logger.info('monitor process_response:', response.url)
        return response

    def process_exception(request, exception, spider):
        logger.info('monitor process_exception:', exception)