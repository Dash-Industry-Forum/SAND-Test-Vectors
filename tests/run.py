import unittest
import glob
import re
from lxml import etree

import sys
sys.path.append("..")
import sand.header
from sand.xml_message import XMLValidator

class TestPerMessages(unittest.TestCase):
    def setUp(self):
        self.validator = XMLValidator()

    def test_valid_messages(self):
        for message in glob.glob("../per/*-OK-*.xml"):
            self.assertTrue(self.validator.from_file(message))
            print "Test succesful : " + message
  
    def test_invalid_messages(self):
        for message in glob.glob("../per/*-KO-*.xml"):
            self.assertFalse(self.validator.from_file(message))
            print "Test succesful : " + message

class TestMetricsMessages(unittest.TestCase):
    def setUp(self):
        self.validator = XMLValidator()

    def test_valid_messages(self):
        for message in glob.glob("../metrics/*-OK-*.xml"):
            self.assertTrue(self.validator.from_file(message))
            print "Test succesful : " + message
  
    def test_invalid_messages(self):
        for message in glob.glob("../metrics/*-KO-*.xml"):
            self.assertFalse(self.validator.from_file(message))
            print "Test succesful : " + message

class TestStatussMessages(unittest.TestCase):
    def test_valid_messages(self):
        for message_file in glob.glob("../status/*-OK-*.txt"):
            with open(message_file) as message:
                for header in message.readlines():
                    match = re.search("([^:]+):(.+)", header.replace(" ", ""))
                    name = match.group(1)
                    value = match.group(2)
                    checker = sand.header.header_name_to_checker.get(name.lower())
                    if checker:
                        checker.check_syntax(value)
                    else:
                        print ("Header name not supported by this " 
                               "version of conformance server.") 
        
                    self.assertFalse(checker.errors)
                    print "Test succesful : " + message_file
  
    def test_invalid_messages(self):
        for message_file in glob.glob("../status/*-KO-*.txt"):
            with open(message_file) as message:
                for header in message.readlines():
                    match = re.search("([^:]+):(.+)", header.replace(" ", ""))
                    name = match.group(1)
                    value = match.group(2)
                    checker = sand.header.header_name_to_checker.get(name.lower())
                    if checker:
                        checker.check_syntax(value)
                    else:
                        print ("Header name not supported by this "
                               "version of conformance server.")
        
                    self.assertTrue(checker.errors)
                    print "Test succesful : " + message_file

if __name__ == '__main__':
      unittest.main()
