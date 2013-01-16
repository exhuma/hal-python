import unittest

from hal import Document, Link


class SimpleTest(unittest.TestCase):

    def setUp(self):
        self.rawdoc = u'''{
  "_links": {
    "self": { "href": "/orders/523" },
    "warehouse": { "href": "/warehouse/56" },
    "invoice": { "href": "/invoices/873" }
  },
  "currency": "USD",
  "status": "shipped",
  "total": 10.20
}'''
        self.doc = Document.makeDocument(self.rawdoc)

    def testBasicType(self):
        self.assertTrue(isinstance(self.doc, Document))

    def testExistingAttributes(self):
        keys = set([_ for _ in self.doc])
        expected = set(['currency', 'status', 'total'])
        self.assertEquals(keys, expected)

    def testCurrency(self):
        self.assertEquals(self.doc.currency, 'USD')

    def testStatus(self):
        self.assertEquals(self.doc.status, 'shipped')

    def testTotal(self):
        self.assertEquals(self.doc.total, 10.20)

    def testKeyAccess(self):
        self.assertEquals(self.doc.total, self.doc['total'])


class EmbeddedTest(unittest.TestCase):

    def setUp(self):
        self.rawdoc = u'''{
  "_links": {
    "self": { "href": "/orders" },
    "next": { "href": "/orders?page=2" },
    "find": { "href": "/orders{?id}", "templated": true }
  },
  "_embedded": {
    "orders": [{
      "_links": {
        "self": { "href": "/orders/123" },
        "basket": { "href": "/baskets/98712" },
        "customer": { "href": "/customers/7809" }
      },
      "total": 30.00,
      "currency": "USD",
      "status": "shipped"
    },{
      "_links": {
        "self": { "href": "/orders/124" },
        "basket": { "href": "/baskets/97213" },
        "customer": { "href": "/customers/12369" }
      },
      "total": 20.00,
      "currency": "USD",
      "status": "processing"
    }]
  },
  "currentlyProcessing": 14,
  "shippedToday": 20
}'''
        self.doc = Document.makeDocument(self.rawdoc)

    def testContainerType(self):
        self.assertTrue(isinstance(self.doc.orders, list))

    def testEmbeddedType(self):
        "Test if the list elements are valid documents again"
        self.assertTrue(
            reduce(lambda a, b: a and b,
                   [isinstance(_, Document) for _ in self.doc.orders]))


class DocumentMutationTest(unittest.TestCase):
    pass
    # doc.foo = 10
    # print doc.foo
    #
    # tmpdoc = Document('/foo/bar')
    # tmpdoc.bar = 'baz'
    # doc.bar = tmpdoc
    # print doc.bar.asdict()

if __name__ == '__main__':
    unittest.main()
