#!/usr/bin/python

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

from os.path import dirname, join
from lxml import etree
from lxml import isoschematron

class XMLValidator:

    sand_message_xsd = "./schemas/sand_messages.xsd"
    sand_message_sch = "./schemas/sand_messages.sch"

    def __init__(self):
        xsd_path = join(dirname(__file__), self.sand_message_xsd)
        with open(xsd_path) as f:
            sand_schema_doc = etree.parse(f)
            self.sand_xml_schema = etree.XMLSchema(sand_schema_doc)
        
        sch_path = join(dirname(__file__), self.sand_message_sch)
        with open(sch_path) as f:
            sand_schematron_doc = etree.parse(f)
            self.sand_schematron = isoschematron.Schematron(sand_schematron_doc)

    def from_file(self, file_path):
        is_valid = False
        try:
            message_doc = etree.parse(file_path)
            is_valid = (self.sand_xml_schema.validate(message_doc)
                    and self.sand_schematron.validate(message_doc))
        except etree.XMLSyntaxError as e:
            print e

        return is_valid

    def from_string(self, message_string):
        is_valid = False
        try:
            parser = etree.XMLParser(schema = self.sand_xml_schema)
            etree.fromstring(message_string, parser)
            # If execution passes, XML schema validation succeeded
            message_doc = etree.parse(message_string)
            is_valid = self.sand_schematron.validate(message_doc)
        except etree.XMLSyntaxError as e:
            print e

        return is_valid
