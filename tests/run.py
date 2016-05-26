import unittest
import glob
import re
from lxml import etree

import sys
sys.path.append("..")
import sand.header
from sand.xml_message import XMLValidator

class TestXmlPerMessages(unittest.TestCase):
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

class TestXmlMetricsMessages(unittest.TestCase):
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

def check_header(header):
    match = re.search("([^:]+):(.+)", header)
    name = match.group(1).strip()
    value = match.group(2).strip()
    checker = sand.header.header_name_to_checker.get(name.lower())
    if checker:
        checker.check_syntax(value)
        return checker.errors
    else:
        print ("Header name not supported by this " 
               "version of conformance server|" + name) 
        

class TestTxtStatussMessages(unittest.TestCase):
    def test_valid_messages(self):
        for message_file in glob.glob("../status/*-OK-*.txt"):
            with open(message_file) as message:
                for header in message.readlines():
                    self.assertFalse(check_header(header))
                    print "Test succesful : " + message_file
  
    def test_invalid_messages(self):
        for message_file in glob.glob("../status/*-KO-*.txt"):
            with open(message_file) as message:
                for header in message.readlines():
                    self.assertTrue(check_header(header))
                    print "Test succesful : " + message_file

class TestTxtPerMessages(unittest.TestCase):
    def test_valid_messages(self):
        for message_file in glob.glob("../per/*-OK-*.txt"):
            with open(message_file) as message:
                for header in message.readlines():
                    self.assertFalse(check_header(header))
                    print "Test succesful : " + message_file
  
    def test_invalid_messages(self):
        for message_file in glob.glob("../per/*-KO-*.txt"):
            with open(message_file) as message:
                for header in message.readlines():
                    self.assertTrue(check_header(header))
                    print "Test succesful : " + message_file

class TestTxtPedMessages(unittest.TestCase):
    def test_valid_messages(self):
        for message_file in glob.glob("../ped/*-OK-*.txt"):
            with open(message_file) as message:
                for header in message.readlines():
                    self.assertFalse(check_header(header))
                    print "Test succesful : " + message_file
  
    def test_invalid_messages(self):
        for message_file in glob.glob("../ped/*-KO-*.txt"):
            with open(message_file) as message:
                for header in message.readlines():
                    self.assertTrue(check_header(header))
                    print "Test succesful : " + message_file

if __name__ == '__main__':
      unittest.main()
