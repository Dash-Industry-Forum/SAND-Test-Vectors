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

import re
from UserList import UserList

# URI regexps taken from
# http://blog.dieweltistgarnichtso.net/constructing-a-regular-expression-that-matches-uris
# regexp for the protocol part of an URI:
uri_proto = r'"[A-Za-z][A-Za-z0-9\+\.\-]*'
# regexp for the accepted characters in the rest of the URI
uri_allowed = r"[A-Za-z0-9\.\-_~:/\?#\[\]@!\$&'\(\)\*\+,;=]"
# regexp for URI encoded characters
uri_encoded = r'%[A-Fa-f0-9]{2}'

# A dictionary of regexps for checking all SAND value types
regular_expressions = {
    'QUOTEDSTRING': re.compile(r'"(\\"|[^"])*"'),
    'QUOTEDURI': re.compile(r'("%s:(%s|%s)+")|("(%s|%s)+")' % (uri_proto, uri_allowed, uri_encoded, uri_allowed, uri_encoded)),
    # TODO: we have no example of TOKEN in HTTP headers
    # the exact expression should be refined.
    'TOKEN': re.compile(r'[a-zA-Z0-9]+'),
    'INT': re.compile(r'\d+'),
    # TODO: do we accept empty start for 0 in a range?
    'BYTERANGE': re.compile(r'\d+-\d*'),
    'DATETIME': re.compile(r'\d\d\d\d\-\d\d\-\d\dT\d\d:\d\d:\d\d(\.\d{,6})?Z'),
    # Extension to DIS syntax, for ClientCapabilities
    # TODO: obtain the final specification
    'LIST': re.compile(r'\[(\d+(,\d+)*)?\]'),
}
# A regexp that allows to 'eat' characters that may belong to a DATETIME.
# This is used in case the DATETIME is wrongly written, e.g. one missing char
# example: 2016-0601T12:00:00Z has a missing dash, but this regexp allows to
# recognize all the string as 'wrong datetime', instead of stopping at 6th character
# and failing again because other characters will not match another expected attribute.
datetime_allowed_chars = re.compile(r'[\d\-T:\.Z]+')

class SandObject:
    """Representation of values in a sand-object element.
    The list attribute contains the sand-list if it exists, or is None.
    Other attributes are created for representing any found sand-attribute."""
    
    def __init__(self):
        self.list = None

class SandList(UserList):
    """Representation of a sand-list.
    It supports regular python list operations (provided by UserList).
    It provides access to the sand-objects described in the sand-list.
    If the parsing found no closing bracket, the attribute closed will be False.
    Note: UserList.data attribute is the list storing actual content."""
    
    def __init__(self, data=[]):
        """Constructor takes an optional data as required by UserList.
        Initially self.closed is False, and should be set to True
        by the parser when finding the closing bracket."""
        UserList.__init__(self, data)
        self.closed = False

class SandValue:
    """Representation of a sand-attribute.
    It just stores the value as a string, without modification of the input."""
    
    def __init__(self):
        self.data = ''

class ParsingStopped(Exception):
    """Our own exception to signal a parsing failure."""
    pass

# dict key used to mark mandatory attributes
# must be different from any possible attribute name
# using () is a good way
MANDATORY = ()

class HeaderSyntaxChecker:
    """Base class for syntax checking of a SAND HTTP header.
    Attributes are:
    - syntax: a dictionary describing expected structure and types
    - errors: a list of error messages found during parsing"""

    def __init__(self, syntax):
        """Constructor. Just store the syntax descriptor."""
        self.syntax = syntax
        self.errors = []

    def add_error(self, msg):
        """Adds the msg to the list of errors."""
        self.errors.append(msg)

    def clear_errors(self):
        """Clears the list of errors (call me before starting to parse)."""
        self.errors = []

    def check_syntax(self, input):
        """Checks the input string conforms to the message syntax.
        This is the entry point for parsing a message in a header.
        If parsing went to the end correctly or with non fatal errors,
        returns the SandObject describing the found content."""
        self.clear_errors()
        try:
            result = self.check_object(self.syntax, input, first_level=True)
        except ParsingStopped:
            result = None
        return result
    
    def check_object(self, syntax, input, first_level=False, item_number=None):
        """Performs the syntax check when a sand-object is expected.
        syntax: description of the syntax expected for this object.
        input: string to parse (starts with the object, but may contain more at the end)
        first_level: is True if the object is a top-level one in the message.
        item_number: if provided, it is the position of the object in the enclosing sand-list
        Returns the corresponding SandObject or raises ParsingStopped.
        The returned SandObject has its attribute char_count indicating how many
        characters where used from input."""
        result = SandObject()
        result.char_count = 0
        if item_number is not None:
            number_text = ' for object at position %d' % item_number
        else:
            number_text = ''
        # Eat input until end or some closing delimiter
        while input:
            item_length = 0 # number of chars for one item (sublist or attribute)
            if input[0] == '[':
                # Apparently the start of a sublist
                # First is it allowed?
                if result.list is not None:
                    self.add_error('Only one list is allowed%s.' % number_text)
                    # we will parse it anyway, it may have the right syntax
                elif 'list' not in syntax:
                    self.add_error("Unexpected sand-list found %s. Stopping parsing." % number_text)
                    raise ParsingStopped
                # Second, parse the sublist
                result.list = self.check_list(syntax['list'], input)
                item_length += result.list.char_count
                if not result.list.closed:
                    if 'list' in syntax:
                        self.add_error("Unmatched '[' to close sand-list%s." % number_text)
                    else:
                        self.add_error("Unexpected '[' found (and no closing ']')%s." % number_text)
            else:
                # We have to parse a sand-attribute
                # First decompose name=something
                try:
                    attr_name, right = input.split('=', 1)
                    item_length += 1 # aknowledge for '='
                except ValueError:
                    attr_name = input
                    right = None
                    self.add_error("Expecting '=' for sand-attribute%s." % number_text)
                # Check attribute name is well formed
                if not attr_name.isalpha():
                    # TODO: make a special case for white space
                    self.add_error("sand-attribute name should be alphabetic%s." % number_text)
                item_length += len(attr_name)
                # Check we have something to parse for the value
                if right is not None and not right:
                    self.add_error("Empty value for sand-attribute after '='%s." % number_text)
                # Check it is an expected attribute
                if attr_name not in syntax:
                    self.add_error("Unexpected sand-attribute name '%s'%s. Stopping parsing." % (attr_name, number_text))
                    raise ParsingStopped
                # Parse the value
                value = self.check_value(syntax[attr_name], input[item_length:])
                item_length += value.char_count
                # Attributes must be unique
                if hasattr(result, attr_name):
                    self.add_error("sand-attribute %s should occur only once%s." % (attr_name, number_text))
                setattr(result, attr_name, value.data)
            # Now that on item has been parsed, prepare for the next
            # move to remaining input:
            input = input[item_length:]
            result.char_count += item_length
            if input:
                # Still some chars, check for delimiters
                if input[0] == ',':
                    result.char_count += 1
                    input = input[1:]
                elif first_level:
                    self.add_error("Expecting ',', found '%s'%s. Stopping parsing." % (input[0], number_text))
                    raise ParsingStopped
                else:
                    # 2 cases:
                    # input[0] in (';', ']') is normal end of current sand-object
                    # otherwise its a syntax error, but we assume it will be caught by further analysis
                    break
        # Once the object is completely parse, check we got all mandatory attributes
        for attr_name in syntax[MANDATORY]:
            if attr_name == 'list':
                if result.list is None:
                    self.add_error("Mandatory sand-list is missing%s." % number_text)
            else:
                if not hasattr(result, attr_name):
                    self.add_error("Mandatory sand-attribute '%s' is missing%s." % (attr_name, number_text))
        return result
    
    def check_list(self, syntax, input):
        """Performs the syntax check when a sand-list is expected.
        syntax: description of the syntax expected for items in this list.
        input: string to parse (starts with the list, but may contain more at the end)
        Returns the corresponding SandList or raises ParsingStopped.
        The returned SandList has its attribute char_count indicating how many
        characters where used from input."""
        # Skip the opening bracket
        assert(input[0] == '[') # ensured by caller
        result = SandList()
        result.char_count = 1
        input = input[1:]
        item_number = 0
        # Eat input until end or closing backet
        while input and input[0] != ']':
            item_number += 1
            # items of the list should be sand-object:
            next = self.check_object(syntax, input, item_number=item_number)
            result.char_count += next.char_count
            # store the found item
            result.append(next)
            # move to remaining input:
            input = input[next.char_count:]
            # check we found either the list separator or terminator
            if input:
                if input[0] == ';':
                    # OK, go to next item
                    result.char_count += 1
                    input = input[1:]
                    if input and input[0] == ']':
                        self.add_error('Empty element at end of sand-list.')
                elif input[0] != ']':
                    self.add_error("Expecting ';' or ']', found '%s'. Stopping parsing." % input[0])
                    raise ParsingStopped
        # If we leave the loop normally, we aknowledge for the closing bracket:
        if input:
            assert(input[0] == ']')
            result.closed = True
            result.char_count += 1
        return result
    
    def check_value(self, expected_type, input):
        """Performs the syntax check when a sand-value is expected.
        expected_type: the name of the type expected for the value.
        input: string to parse (starts with the value, but may contain more at the end)
        Returns the corresponding SandValue or raises ParsingStopped.
        The returned SandValue has its attribute char_count indicating how many
        characters where used from input."""
        # We require the caller to pass some input
        assert(input)
        result = SandValue()
        # Most work is done thanks to the regexp associted to this type:
        match = regular_expressions[expected_type].match(input)
        if match:
            # Correct value
            result.data = match.group(0)
        else:
            # Wrong value
            if expected_type == 'DATETIME':
                # try to consider allowed DATETIME characters
                # so that an error in the middle of it does not stop
                # processing the reminder
                match = datetime_allowed_chars.match(input)
                if match:
                    result.data = match.group(0)
            self.add_error("Wrong or missing %s specification." % expected_type)
        result.char_count = len(result.data)
        return result
    
    def optional_attributes(self, obj, syntax):
        """Extracts a tuple of the optional attributes included in a SandObject.
        This is a utility method for subclasses.
        obj is the considered SandObject after parsing.
        syntax is the syntax for this object.
        Retuns the set of the optional attribute names present on the object."""
        result = set()
        for attr_name in syntax:
            if attr_name is not MANDATORY and attr_name not in syntax[MANDATORY] and hasattr(obj, attr_name):
                result.add(attr_name)
        return result

class AnticipatedRequestsChecker(HeaderSyntaxChecker):
    """Class to check a SAND-AnticipatedRequests header message."""
    
    def __init__(self):
        """Build the syntax description for this message"""
        HeaderSyntaxChecker.__init__(
            self, 
            { MANDATORY: ('list',),
              'list': { MANDATORY: ('sourceURL', 'targetTime'),
                        'sourceURL': 'QUOTEDURI',
                        'range': 'BYTERANGE',
                        'targetTime': 'DATETIME' } })

    def check_syntax(self, input):
        """Checks the input string conforms to SAND- syntax."""
        # Generic checking:
        o = HeaderSyntaxChecker.check_syntax(self, input)
        # Additional checks
        if o:
            if not o.list:
                self.add_error("At least one request must be specified.")

class SharedResourceAllocationChecker(HeaderSyntaxChecker):
    """Class to check a SAND-ResourceAllocation header message."""

    def __init__(self):
        """Build the syntax description for this message"""
        HeaderSyntaxChecker.__init__(
            self,
            { MANDATORY: ('list',),
              'list': { MANDATORY: ('bandwidth',),
                        'bandwidth': 'INT',
                        'quality': 'INT',
                        'minBufferTime': 'INT' },
              'weight': 'INT',
              'allocationStrategy': 'QUOTEDURI',
              'mpdURL': 'QUOTEDURI' })

    def check_syntax(self, input):
        """Checks the input string conforms to SAND-ResourceAllocation syntax."""
        # Generic checking:
        o = HeaderSyntaxChecker.check_syntax(self, input)
        # Additional checks
        if o:
            if not o.list:
                self.add_error("At least one operation point must be specified.")
            try:
                strategy = o.allocationStrategy
                if strategy in ('"urn:mpeg:dash:sand:allocation:premium-privileged:2016"',
                                '"urn:mpeg:dash:sand:allocation:everybody-served:2016"',
                                '"urn:mpeg:dash:sand:allocation:weighted:2016"'):
                    if not hasattr(o, 'weight'):
                        self.add_error("Attribute weight is mandatory for strategy %s." % strategy)
            except AttributeError:
                # no allocation strategy specified
                pass
            if o.list and False: # TODO: if approved check (noted in specification) then remove the False to activate check
                # Check that provided attributes are consistent through the list:
                syntax = self.syntax['list']
                attributes = self.optional_attributes(o.list[0], syntax)
                for obj in o.list[1:]:
                    if self.optional_attributes(obj, syntax) != attributes:
                        self.add_error("Optional attributes are not consistent through the list of operationPoints")
                        break

class AcceptedAlternativesChecker(HeaderSyntaxChecker):
    """Class to check a SAND-AcceptedAlternatives header message."""
    
    def __init__(self):
        """Build the syntax description for this message"""
        HeaderSyntaxChecker.__init__(
            self, 
            { MANDATORY: ('list',),
              'list': { MANDATORY: ('sourceURL',),
                        'sourceURL': 'QUOTEDURI',
                        'range': 'BYTERANGE',
                        'bandwidth': 'INT',
                        'deliveryScope': 'INT' } })

    def check_syntax(self, input):
        """Checks the input string conforms to SAND-AcceptedAlternatives syntax."""
        # Generic checking:
        o = HeaderSyntaxChecker.check_syntax(self, input)
        # Additional checks
        if o:
            if not o.list:
                self.add_error("At least one alternative must be specified.")

class AbsoluteDeadlineChecker(HeaderSyntaxChecker):
    """Class to check a SAND- header message."""
    
    def __init__(self):
        """Build the syntax description for this message"""
        HeaderSyntaxChecker.__init__(
            self,
            { MANDATORY: ('deadline',),
              'deadline': 'DATETIME' })

    def check_syntax(self, input):
        """Checks the input string conforms to SAND-AbsoluteDeadline syntax."""
        # Generic checking:
        o = HeaderSyntaxChecker.check_syntax(self, input)
        # No additional checks

class MaxRTTChecker(HeaderSyntaxChecker):
    """Class to check a SAND-MaxRTT header message."""
    
    def __init__(self):
        """Build the syntax description for this message"""
        HeaderSyntaxChecker.__init__(
            self,
            { MANDATORY: ('maxRTT',),
              'maxRTT': 'INT' })

    def check_syntax(self, input):
        """Checks the input string conforms to SAND-MaxRTT syntax."""
        # Generic checking:
        o = HeaderSyntaxChecker.check_syntax(self, input)
        # No additional checks

class NextAlternativesChecker(HeaderSyntaxChecker):
    """Class to check a SAND-NextAlternatives header message."""
    
    def __init__(self):
        """Build the syntax description for this message"""
        HeaderSyntaxChecker.__init__(
            self,
            { MANDATORY: ('list',),
              'list': { MANDATORY: ('sourceURL',),
                        'sourceURL': 'QUOTEDURI',
                        'range': 'BYTERANGE',
                        'bandwidth': 'INT',
                        'deliveryScope': 'INT' } })

    def check_syntax(self, input):
        """Checks the input string conforms to SAND-NextAlternatives syntax."""
        # Generic checking:
        o = HeaderSyntaxChecker.check_syntax(self, input)
        # Additional checks
        if o:
            if not o.list:
                self.add_error("At least one alternative must be specified.")

class ClientCapabilitiesChecker(HeaderSyntaxChecker):
    """Class to check a SAND-ClientCapabilities header message."""
    
    def __init__(self):
        """Build the syntax description for this message"""
        HeaderSyntaxChecker.__init__(
            self,
            { MANDATORY: (),
              'supportedMessage': 'LIST',
              'messageSetUri': 'QUOTEDURI' })

    def check_syntax(self, input):
        """Checks the input string conforms to SAND-ClientCapabilities syntax."""
        # Generic checking:
        o = HeaderSyntaxChecker.check_syntax(self, input)
        # Additional checks
        if o:
            if hasattr(o, 'supportedMessage') and hasattr(o, 'messageSetUri'):
                self.add_error("Only one of supportedMessage or messageSetUri should be specified.")
            if hasattr(o, 'supportedMessage'):
                found = False
                codes = o.supportedMessage[1:-1].split(',')
                if '0' in codes:
                    self.add_error("supportedMessage should not include reserved code 0")
                if '12' not in codes:
                    self.add_error("supportedMessage must include code 12 (ClientCapabilities)")

class DeliveredAlternativeChecker(HeaderSyntaxChecker):
    """Class to check a SAND-DeliveredAlternative header message."""
    
    def __init__(self):
        """Build the syntax description for this message"""
        HeaderSyntaxChecker.__init__(
            self,
            { MANDATORY: ('initialURL', 'contentLocation'),
              'initialURL': 'QUOTEDURI',
              'contentLocation': 'QUOTEDURI' })

class BwInformationChecker(HeaderSyntaxChecker):
    """Class to check a SAND-BwInformation header message."""
    
    def __init__(self):
        """Build the syntax description for this message"""
        HeaderSyntaxChecker.__init__(
            self,
            { MANDATORY: (),
              'minBandwidth': 'INT',
              'maxBandwidth': 'INT' })

    def check_syntax(self, input):
        """Checks the input string conforms to SAND-BwInformation syntax."""
        # Generic checking:
        o = HeaderSyntaxChecker.check_syntax(self, input)
        # Additional checks
        if o:
            if not hasattr(o, 'minBandwidth') and not hasattr(o, 'maxBandwidth'):
                self.add_error("At least one of minBandwidth or maxBandwidth should be specified.")
            if hasattr(o, 'minBandwidth') and hasattr(o, 'maxBandwidth'):
                minBW = int(o.minBandwidth)
                maxBW = int(o.maxBandwidth)
                if maxBW < minBW:
                    self.add_error("The value of maxBandwidth should be greater or equal than minBandwidth.")

# This dictionary maps header names to the class to use for checking the value.
# We use lower cased values of header names, since HTTP headers are case-insensitive
# and so comparison can be made on lowered names.
header_name_to_checker = {
  'sand-anticipatedrequests': AnticipatedRequestsChecker(),
  'sand-sharedresourceallocation': SharedResourceAllocationChecker(),
  'sand-acceptedalternatives': AcceptedAlternativesChecker(),
  'sand-absolutedeadline': AbsoluteDeadlineChecker(),
  'sand-maxrtt': MaxRTTChecker(),
  'sand-nextalternatives': NextAlternativesChecker(),
  'sand-clientcapabilities': ClientCapabilitiesChecker(),
  'sand-deliveredalternative': DeliveredAlternativeChecker(),
  'sand-bwinformation': BwInformationChecker(),
}

if __name__ == '__main__':
    # Call this script from the test-vectors directory,
    # This will test the parsing against test vectors.
    from glob import glob
    import os
    for expected_result in ('OK', 'KO'):
        print
        if expected_result == 'OK':
            print '=== TESTS THAT SHOULD PASS ==='
        else:
            print '=== TESTS THAT SHOULD FAIL ==='
        print
        
        match = '*-%s-*.txt' % expected_result
        status_tests = glob(os.path.join('status', match))
        per_tests = glob(os.path.join('per', 'DeliveredAlternative-%s-*.txt' % expected_result))
        ped_tests = glob(os.path.join('ped', match))
        for file_name in status_tests + per_tests + ped_tests:
            with open(file_name) as f:
                name, input = f.readline().split(':', 1)
                c = header_name_to_checker[name.lower()]
                c.check_syntax(input.strip())
            if c.errors:
                print 'FAILED', file_name
                for msg in c.errors:
                    print '      ', msg
            else:
                print 'PASSED', file_name
