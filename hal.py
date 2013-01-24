import logging

try:
    import json
except ImportError:
    import simplejson as json  # NOQA


LOG = logging.getLogger(__name__)


class Link(object):
    """
    Object to encapsulate HAL links.

    If an attribute of the link is accessed and the document had not been
    fetched before, a GET request is sent to the ``href`` of this Link.

    :param rel: The relation name.
    :type rel: basestring
    :param obj: A dictionary representing the link, following the HAL spec for
                links.
    :type obj: dict
    """

    def __init__(self, rel, obj):
        self._data = obj
        self._document = None
        self.rel = rel

    def __repr__(self):
        return "Link(%r, %r)" % (self.rel, self._data)

    def __getattribute__(self, attr):
        if attr in ('_document', '_fetch_document', '_data', 'rel'):
            return object.__getattribute__(self, attr)
        if not self._document:
            self._fetch_document()
        LOG.warning('Links are not yet fully implemented')
        return getattr(self._document, attr)

    def _fetch_document(self):
        """
        Send a GET request to the href of this link and stores the result
        in a local variable.
        """
        LOG.warning('Links are not yet fully implemented')
        print 'fetching document (dummy)'
        self._document = Document(u'/author/10')
        self._document.name = u'John Doe'

    def asdict(self):
        """
        Returns a HAL style dict.
        """
        return self._data


class Document(object):
    """
    A HAL Document representation.

    :param selfurl: The URL pointing to self.
    :type selfurl: basestring
    """

    @staticmethod
    def makeDocument(obj):
        """
        Factory method to construct Document instances from different sources.

        The source (``obj``) can be any of the following:

        * A ``dict`` -- This assumes that the dict follows the HAL spec and
          implements all required keys.
        * A file-like object (any object with a ``read`` method). This should
          contain a JSON representation of the HAL document.
        * A string. Again, this should be a valid JSON representation
          following the HAL spec.
        * A list. This assumes, that each item is a valid HAL Document
          representation. The items are instantiated using
          ``Document.makeDocument``, so they can be of any of the above types.
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
            return Link(attr, data['_links'][attr])
        raise AttributeError('%r has no attribute %r' % (self, attr))

    def __repr__(self):
        data = object.__getattribute__(self, '_data')
        return "<Document %s>" % (data['_links']['self']['href'])

    def __str__(self):
        data = object.__getattribute__(self, '_data')
        return json.dumps(data)

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
            elif isinstance(value, Link):
                data['_links'][name] = value.asdict()
            else:
                data[name] = value

    def asdict(self):
        """
        Returns a dictionary following the HAL spec.
        """
        data = object.__getattribute__(self, '_data')
        return data
