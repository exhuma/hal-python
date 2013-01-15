import logging
logging.basicConfig(level=logging.DEBUG)

from hal import Document

doc = Document(open('example.json'))
print doc.title
#print doc.author
print doc.tags.items
