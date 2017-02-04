#!/usr/bin/env python
"""
Read test details from nosetests.xml output file
"""

from lxml import etree as ET
from lxml.builder import E

from nosepicker.log import Logger

class NosePicker(dict):
    def __init__(self,path='noseresults.xml',short_classnames=False):
        self.log = Logger('nosepicker').default_stream
        self.path = path

        self.parser = None
        self.loaded = False
        self.__next = None
        self.short_classnames = short_classnames

    def __del__(self):
        """
        Close our XML parser before deleting
        """
        self.__close_parser__()

    def __len__(self):
        if not self.parser and not self.loaded:
            self.load()
        return len(self.keys())

    def __getitem__(self,item):
        if not self.parser and not self.loaded:
            self.load()
        try:
            item = int(item)
            return self[self.indexed[item]]
        except ValueError:
            # not integer, lookup by path
            pass
        except IndexError:
            raise DataSourceError('Invalid library index:' % item)
        return NoseResults.__getitem__(self,normalized(item))

    def __open_parser__(self):
        """
        Open XML parser instance
        """
        if self.parser is not None:
            raise DataSourceError('XML file already open: %s' % self.path)
        self.parser = ET.iterparse(self.path, events=('start','end',))
        self.parent = None

    def __close_parser__(self):
        """
        Close XML parser instance, interrupting iterator
        """
        if not hasattr(self, 'parser') or self.parser is None:
            return
        self.parent = None
        if self.parser is not None:
            del self.parser
            self.parser = None

    def __iter__(self):
        return self

    def load(self):
        return

    def next(self):
        """
        First time iterate over XML file on the fly
        After this, return elements loaded by first round
        """

        if not self.loaded:
            if self.parser is None:
                self.__open_parser__()
        elif self.__next is None:
            self.__next = 0

        try:
            if self.loaded:
                # Return elements loaded in first iteration
                try:
                    entry = self[self.indexed[self.__next]]
                    self.__next += 1
                    return entry
                except IndexError:
                    raise StopIteration
            else:
                # Load and return elements from XML dynamically
                return self.__next_xml_element__()
        except StopIteration:
            self.__close_parser__()
            self.loaded = True
            self.__next = None
            self.indexed = self.keys()
            raise StopIteration

    __next__ = next

    def __next_xml_element__(self):
        """
        Placeholder for function to parse and insert elements to our
        dictionary and playlists.

        Must be implemented in child classes.
        """
        while True:
            (event, element) = next(self.parser)

            if event not in ['start', 'end']:
                raise ValueError('Unknown XML parser event: %s' % event)

            if event=='end' and element.tag == 'testsuite':
                self.parent = None

            if event=='start':
                if element.tag == 'testsuite':
                    self.parent = NoseTestSuite(self,element)
                    continue

            if event=='end':
                if element.tag == 'testcase':
                    if not self.parent:
                        raise ValueError('Test case outside suite')
                    testcase = NoseTestCase(self.parent,element)
                    return testcase

    def keys(self):
        """
        Return keys (data sources paths) sorted
        """
        return sorted(dict.keys(self))

    def items(self):
        """
        Return data sources items sorted by self.keys() with self.__getitem__
        """
        return [(k,self[k]) for k in self.keys()]

    def values(self):
        """
        Return data sources items sorted by self.keys() with self.__getitem__
        """
        return [self[k] for k in self.keys()]

class NoseTestSuite(object):
    def __init__(self,parent,node):
        self.log = Logger('nosepicker').default_stream
        self.parent = parent
        self.node = node

    @property
    def short_classnames(self):
        return self.parent.short_classnames

class NoseTestCase(object):
    def __init__(self,suite,node):
        self.log = Logger('nosepicker').default_stream
        self.suite = suite
        self.node = node

        self.skipped = [node for node in self.node.xpath('skipped')]
        self.errors = [NoseTestError(self,node) for node in self.node.xpath('error')]
        self.failures = [NoseTestError(self,node) for node in self.node.xpath('failure')]

        for node in self.node:
            if node.tag not in ('error','failure','skipped','system-err'):
                self.log.debug('UNEXPECTED: %s' % ET.tostring(node))
                raise ValueError('Unexpected testcase child element: %s' % node.tag)

    def __hash__(self):
        return '%s %s' % (self.classname,self.name)

    def __repr__(self):
        self.log.debug('%8s %s: %d errors %d failures %d skipped' % (
            self.status,self.name,len(self.errors),len(self.failures),len(self.errors)
        ))
        if not self.short_classnames:
            return '%-7s %-40s %s' % (self.status,self.classname,self.name)
        else:
            return '%-7s %-40s %s' % (self.status,self.testclass,self.name)

    @property
    def short_classnames(self):
        return self.suite.short_classnames

    @property
    def status(self):
        if len(self.failures):
            return 'FAILURE'
        elif len(self.errors):
            return 'ERROR'
        elif len(self.skipped):
            return 'SKIP'
        else:
            return 'OK'

    @property
    def time(self):
        return float(self.node.get('time'))

    @property
    def testclass(self):
        return self.node.get('classname').split('.')[0]

    @property
    def classname(self):
        return self.node.get('classname')

    @property
    def name(self):
        return self.node.get('name')

class NoseTestError(object):
    def __init__(self,testcase,node):
        self.log = Logger('nosepicker').default_stream
        self.testcase = testcase
        self.node = node

    def __repr__(self):
        return ET.tostring(self.node)

    @property
    def type(self):
        return self.node.get('type')

    @property
    def consolelog(self):
        return self.node.get('message')

    @property
    def errors(self):
        msg = self.node.text.split('\n')
        lines = []
        for l in msg:
            if l=='-------------------- >> begin captured stdout << ---------------------':
                break
            lines.append(l)
        return '\n'.join(lines)
