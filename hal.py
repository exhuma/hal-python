import logging

try:
    import json
except ImportError:
    import simplejson as json  # NOQA


LOG = logging.getLogger(__name__)


class Document(object):

    def __init__(self, document_source):
        if isinstance(document_source, dict):
            self.data = document_source
        elif hasattr(document_source, 'read'):
            self.data = json.load(document_source)
        else:
            self.data = json.loads(document_source)

    def __getattribute__(self, attr):
        LOG.debug('Retrieving %r from %r' % (attr, self))
        data = object.__getattribute__(self, 'data')
        if attr in data:
            return data[attr]
        elif "_embedded" in data and attr in data['_embedded']:
            return Document(data['_embedded'][attr])
        elif "_links" in data and attr in data['_links']:
            raise NotImplementedError('Dynamically retrieving attributes '
                    'from "_links" is not yet supported!')
        raise AttributeError('%r has no attribute %r' % (self, attr))
