"""
SAND messages as HTTP headers, part of SAND conformance server.

This module is part of implementation of a conformance server
for ISO/IEC 23009-5 SAND.
It parses SAND messages received as HTTP header from a SAND client,
and checks they follow the syntax and constraints of the specification.

Copyright (c) 2016-, ISO/IEC JTC1/SC29/WG11
All rights reserved.

See AUTHORS for a full list of authors.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
* Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.
* Neither the name of the ISO/IEC nor the
names of its contributors may be used to endorse or promote products
derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import unittest
import glob
import re
from lxml import etree
from lxml import isoschematron

import sys
sys.path.append("..")
import sand.header
from sand.xml_message import XMLValidator
import logging

logging.basicConfig(filename='report.log', level=logging.DEBUG, filemode='w')

class TestMpd(unittest.TestCase):
    def setUp(self):
        with open("../schemas/SAND-MPD.xsd") as f:
            sand_mpd_schema_doc = etree.parse(f)
            self.sand_mpd_schema = etree.XMLSchema(sand_mpd_schema_doc)
        with open("../schemas/SAND-MPD.sch") as f:
            sand_mpd_schmeatron_doc = etree.parse(f)
            self.sand_mpd_schematron = isoschematron.Schematron(sand_mpd_schmeatron_doc)

    def test_valid_mpds(self):
        for mpd_path in glob.glob("../mpd/*-OK-*.xml"):
            mpd = etree.parse(mpd_path)
            self.assertTrue(
                self.sand_mpd_schema.validate(mpd)
            and self.sand_mpd_schematron.validate(mpd))
            logging.info("Test succesful : %s", mpd_path)

    def test_invalid_mpds(self):
        for mpd_path in glob.glob("../mpd/*-KO-*.xml"):
            mpd = etree.parse(mpd_path)
            self.assertFalse(
                self.sand_mpd_schema.validate(mpd)
            and self.sand_mpd_schematron.validate(mpd))
            logging.info("Test succesful : %s", mpd_path)

class TestXmlPerMessages(unittest.TestCase):
    def setUp(self):
        self.validator = XMLValidator()

    def test_valid_messages(self):
        for message in glob.glob("../per/*-OK-*.xml"):
            logging.info("Test : %s ...", message)
            self.assertTrue(self.validator.from_file(message))
            logging.info("Test : %s OK", message)
  
    def test_invalid_messages(self):
        for message in glob.glob("../per/*-KO-*.xml"):
            logging.info("Test : %s ...", message)
            self.assertFalse(self.validator.from_file(message))
            logging.info("Test : %s OK", message)

class TestXmlMetricsMessages(unittest.TestCase):
    def setUp(self):
        self.validator = XMLValidator()

    def test_valid_messages(self):
        for message in glob.glob("../metrics/*-OK-*.xml"):
            logging.info("Test : %s ...", message)
            self.assertTrue(self.validator.from_file(message))
            logging.info("Test : %s OK", message)
  
    def test_invalid_messages(self):
        for message in glob.glob("../metrics/*-KO-*.xml"):
            logging.info("Test : %s ...", message)
            self.assertFalse(self.validator.from_file(message))
            logging.info("Test : %s OK", message)

def check_header(header):
    match = re.search("([^:]+):(.+)", header)
    name = match.group(1).strip()
    value = match.group(2).strip()
    checker = sand.header.header_name_to_checker.get(name.lower())
    if checker:
        checker.check_syntax(value)
        return checker.errors
    else:
        logging.warning(("Header %s not supported by this " 
                         "version of conformance server"),
                        name) 
        

class TestTxtStatussMessages(unittest.TestCase):
    def test_valid_messages(self):
        for message_file in glob.glob("../status/*-OK-*.txt"):
            with open(message_file) as message:
                for header in message.readlines():
                    logging.info("Test : %s ...", message_file)
                    self.assertFalse(check_header(header))
                    logging.info("Test : %s OK", message_file)
  
    def test_invalid_messages(self):
        for message_file in glob.glob("../status/*-KO-*.txt"):
            with open(message_file) as message:
                for header in message.readlines():
                    logging.info("Test : %s ...", message_file)
                    self.assertTrue(check_header(header))
                    logging.info("Test : %s OK", message_file)

class TestTxtPerMessages(unittest.TestCase):
    def test_valid_messages(self):
        for message_file in glob.glob("../per/*-OK-*.txt"):
            with open(message_file) as message:
                for header in message.readlines():
                    logging.info("Test : %s ...", message_file)
                    self.assertFalse(check_header(header))
                    logging.info("Test : %s OK", message_file)
  
    def test_invalid_messages(self):
        for message_file in glob.glob("../per/*-KO-*.txt"):
            with open(message_file) as message:
                for header in message.readlines():
                    logging.info("Test : %s ...", message_file)
                    self.assertTrue(check_header(header))
                    logging.info("Test : %s OK", message_file)

class TestTxtPedMessages(unittest.TestCase):
    def test_valid_messages(self):
        for message_file in glob.glob("../ped/*-OK-*.txt"):
            with open(message_file) as message:
                for header in message.readlines():
                    logging.info("Test : %s ...", message_file)
                    self.assertFalse(check_header(header))
                    logging.info("Test : %s OK", message_file)
  
    def test_invalid_messages(self):
        for message_file in glob.glob("../ped/*-KO-*.txt"):
            with open(message_file) as message:
                for header in message.readlines():
                    logging.info("Test : %s ...", message_file)
                    self.assertTrue(check_header(header))
                    logging.info("Test : %s OK", message_file)

if __name__ == '__main__':
    testsuite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))
    unittest.TextTestRunner(verbosity=2).run(testsuite)
