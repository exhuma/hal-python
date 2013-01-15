import logging
logging.basicConfig(level=logging.DEBUG)

from hal import Document

doc = Document.makeDocument(open('example.json'))
print doc.title
#print doc.author
print doc.tags
print 80 * "-"
for key in doc:
    print key, doc[key]

print 80 * "-"
doc.foo = 10
print doc.foo

tmpdoc = Document('/foo/bar')
tmpdoc.bar = 'baz'
doc.bar = tmpdoc
print doc.bar.asdict()
