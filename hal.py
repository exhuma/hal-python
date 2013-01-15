import logging

try:
    import json
except ImportError:
    import simplejson as json  # NOQA


LOG = logging.getLogger(__name__)


class Document(object):

    @staticmethod
    def makeDocument(obj):
        """
        Constructs a HAL document from an object.
        """
        instance = Document()
        if isinstance(obj, dict):
            instance._data = obj
        elif hasattr(obj, 'read'):
            instance._data = json.load(obj)
        elif isinstance(obj, basestring):
            instance._data = json.loads(obj)
        elif isinstance(obj, list):
            instance = [Document.makeDocument(_) for _ in obj]
        else:
            raise NotImplementedError('Unable to instantiate a HAL Document '
                    'from %r' % obj)
        return instance

    def __init__(self, selfurl=u''):
        self._data = {'_links': {'self': {'href': selfurl}}}

    def __getattribute__(self, attr):
        LOG.debug('Retrieving %r from %r' % (attr, self))
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            pass

        data = object.__getattribute__(self, '_data')
        if attr in data:
            return data[attr]
        elif "_embedded" in data and attr in data['_embedded']:
            return Document.makeDocument(data['_embedded'][attr])
        elif "_links" in data and attr in data['_links']:
            raise NotImplementedError('Dynamically retrieving attributes '
                    'from "_links" is not yet supported!')
        raise AttributeError('%r has no attribute %r' % (self, attr))

    def __repr__(self):
        data = object.__getattribute__(self, '_data')
        return "<Document %s>" % (data['_links']['self']['href'])

    def __iter__(self):
        data = object.__getattribute__(self, '_data')
        for key in data:
            if key == '_embedded':
                for embedded_key in data[key]:
                    yield embedded_key
            elif key == '_links':
                # we'll ignore links when iterating over the keys. For now.
                pass
            else:
                yield key

    def __getitem__(self, key):
        return getattr(self, key)

    def __setattr__(self, name, value):
        if name == '_data':
            object.__setattr__(self, name, value)
        else:
            data = object.__getattribute__(self, '_data')
            if isinstance(value, Document) or (
                    isinstance(value, list) and all([isinstance(_, Document) for _ in value])):
                data['_embedded'][name] = value.asdict()
            else:
                data[name] = value

    def asdict(self):
        data = object.__getattribute__(self, '_data')
        return data
