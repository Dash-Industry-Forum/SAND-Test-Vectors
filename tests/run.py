"""
SAND Test Vectors validation

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
    """
    Test the conformance of MPD test vectors.
    """
    def setUp(self):
        with open("../schemas/SAND-MPD.xsd") as schema:
            sand_mpd_schema_doc = etree.parse(schema)
            self.sand_mpd_schema = etree.XMLSchema(sand_mpd_schema_doc)
        with open("../schemas/SAND-MPD.sch") as schematron:
            sand_mpd_schmeatron_doc = etree.parse(schematron)
            self.sand_mpd_schematron = isoschematron.Schematron(
                sand_mpd_schmeatron_doc)

    def test_valid_mpds(self):
        """
        Test that valid MPD test vectors are indeed conformant.
        """
        for mpd_path in glob.glob("../mpd/*/*-OK-*.mpd"):
            try:
                mpd = etree.parse(mpd_path)
                self.assertTrue(
                    self.sand_mpd_schema.validate(mpd)
                    and self.sand_mpd_schematron.validate(mpd))
                logging.info("Test succesful : %s", mpd_path)
            except Exception as error:
                logging.error("Test : %s KO", mpd_path)
                raise type(error)(error.message + " %s" % mpd_path)

    def test_invalid_mpds(self):
        """
        Test that invalid MPD test vectors are indeed not conformant.
        """
        for mpd_path in glob.glob("../mpd/*/*-KO-*.mpd"):
            try:
                mpd = etree.parse(mpd_path)
                self.assertFalse(
                    self.sand_mpd_schema.validate(mpd)
                    and self.sand_mpd_schematron.validate(mpd))
                logging.info("Test succesful : %s", mpd_path)
            except Exception as error:
                logging.error("Test : %s KO", mpd_path)
                raise type(error)(error.message + " %s" % mpd_path)

class TestXmlPerMessages(unittest.TestCase):
    """
    Test the conformance of PER message test vectors.
    """
    def setUp(self):
        self.validator = XMLValidator()

    def test_valid_messages(self):
        """
        Test that valid PER message test vectors are indeed conformant.
        """
        for message in glob.glob("../per/*-OK-*.xml"):
            try:
                logging.info("Test : %s ...", message)
                self.assertTrue(self.validator.from_file(message))
                logging.info("Test : %s OK", message)
            except Exception as error:
                logging.error("Test : %s KO", message)
                raise type(error)(error.message + " %s" % message)

    def test_invalid_messages(self):
        """
        Test that invalid PER message test vectors are indeed not conformant.
        """
        for message in glob.glob("../per/*-KO-*.xml"):
            try:
                logging.info("Test : %s ...", message)
                self.assertFalse(self.validator.from_file(message))
                logging.info("Test : %s OK", message)
            except Exception as error:
                logging.error("Test : %s KO", message)
                raise type(error)(error.message + " %s" % message)

class TestXmlMetricsMessages(unittest.TestCase):
    """
    Test the conformance of PER text message test vectors.
    """
    def setUp(self):
        self.validator = XMLValidator()

    def test_valid_messages(self):
        """
        Test that valid Metrics message test vectors are indeed conformant.
        """
        for message in glob.glob("../metrics/*-OK-*.xml"):
            try:
                logging.info("Test : %s ...", message)
                self.assertTrue(self.validator.from_file(message))
                logging.info("Test : %s OK", message)
            except Exception as error:
                logging.error("Test : %s KO", message)
                raise type(error)(error.message + " %s" % message)

    def test_invalid_messages(self):
        """
        Test that invalid Metrics message test vectors are indeed not
        conformant.
        """
        for message in glob.glob("../metrics/*-KO-*.xml"):
            try:
                logging.info("Test : %s ...", message)
                self.assertFalse(self.validator.from_file(message))
                logging.info("Test : %s OK", message)
            except Exception as error:
                logging.error("Test : %s KO", message)
                raise type(error)(error.message + " %s" % message)

def is_header_valid(header):
    ret = False

    match = re.search("([^:]+):(.+)", header)
    name = match.group(1).strip()
    value = match.group(2).strip()
    checker = sand.header.header_name_to_checker.get(name.lower())
    if checker:
        checker.check_syntax(value)
        if not checker.errors:
            ret = True
        else:
            logging.error(checker.errors)
    else:
        logging.warning(("Header %s not supported by this "
                         "version of conformance server"),
                        name)
    return ret


class TestTxtStatussMessages(unittest.TestCase):
    """
    Test the conformance of Status message test vectors.
    """
    def test_valid_messages(self):
        """
        Test that valid Status message test vectors are indeed conformant.
        """
        for message_file in glob.glob("../status/*-OK-*.txt"):
            with open(message_file) as message:
                for header in message.readlines():
                    try:
                        logging.info("Test : %s ...", message_file)
                        self.assertTrue(is_header_valid(header))
                        logging.info("Test : %s OK", message_file)
                    except Exception as error:
                        logging.error("Test : %s KO", message_file)
                        raise type(error)(error.message + " %s" % message_file)

    def test_invalid_messages(self):
        """
        Test that invalid Status message test vectors are indeed not conformant.
        """
        for message_file in glob.glob("../status/*-KO-*.txt"):
            with open(message_file) as message:
                for header in message.readlines():
                    try:
                        logging.info("Test : %s ...", message_file)
                        self.assertFalse(is_header_valid(header))
                        logging.info("Test : %s OK", message_file)
                    except Exception as error:
                        logging.error("Test : %s KO", message_file)
                        raise type(error)(error.message + " %s" % message_file)

class TestTxtPerMessages(unittest.TestCase):
    """
    Test the conformance of PER text message test vectors.
    """
    def test_valid_messages(self):
        """
        Test that valid PER text message test vectors are indeed conformant.
        """
        for message_file in glob.glob("../per/*-OK-*.txt"):
            with open(message_file) as message:
                for header in message.readlines():
                    try:
                        logging.info("Test : %s ...", message_file)
                        self.assertTrue(is_header_valid(header))
                        logging.info("Test : %s OK", message_file)
                    except Exception as error:
                        logging.error("Test : %s KO", message_file)
                        raise type(error)(error.message + " %s" % message_file)

    def test_invalid_messages(self):
        """
        Test that invalid PER text message test vectors are indeed not
        conformant.
        """
        for message_file in glob.glob("../per/*-KO-*.txt"):
            with open(message_file) as message:
                for header in message.readlines():
                    try:
                        logging.info("Test : %s ...", message_file)
                        self.assertFalse(is_header_valid(header))
                        logging.info("Test : %s OK", message_file)
                    except Exception as error:
                        logging.error("Test : %s KO", message_file)
                        raise type(error)(error.message + " %s" % message_file)

if __name__ == '__main__':
    testsuite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))
    ret = not unittest.TextTestRunner(verbosity=2).run(testsuite).wasSuccessful()
    sys.exit(ret)
