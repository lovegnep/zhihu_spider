
import logging
import codecs
import datetime

logger=logging.getLogger()

class monitor(object):
    def process_request(self, request, spider):
        logger.info('monitor process_request:%s', request.url)

    def process_response(self, request, response, spider):
        if response.status >= 400:
            reason = response.status
            self._faillog(request, u'HTTPERROR', reason, spider)
        return response

    def process_exception(self, request, exception, spider):
        self._faillog(request, u'EXCEPTION', exception, spider)
        return request

    def _faillog(self, request, errorType, reason, spider):
        with codecs.open('log/faillog.log', 'a', encoding='utf-8') as file:
            file.write("%(now)s [%(error)s] %(url)s reason: %(reason)s \r\n" %
                       {'now': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'error': errorType,
                        'url': request.url,
                        'reason': reason})