<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron" xmlns:dash="urn:mpeg:dash:schema:mpd:2011" xmlns:sand="urn:mpeg:dash:schema:sand:2016" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" queryBinding='xslt' schemaVersion='ISO19757-3'>
  <ns prefix="dash" uri="urn:mpeg:dash:schema:mpd:2011"/>
  <ns prefix="sand" uri="urn:mpeg:dash:schema:sand:2016"/>
  <ns prefix="xsi" uri="http://www.w3.org/2001/XMLSchema-instance"/>
  <pattern>
    <rule context="sand:Channel">
      <assert test="(@schemeIdUri = 'urn:mpeg:dash:sand:channel:websocket:2016' and (starts-with(@endpoint, 'ws://') or starts-with(@endpoint, 'wss://'))) or @schemeIdUri != 'urn:mpeg:dash:sand:channel:websocket:2016'">
        If the @schemeIdUri is "urn:mpeg:dash:sand:channel:websocket:2016", the @endpoint shall be a WebSocket URI according to RFC 6455.
      </assert>
      <assert test="(@schemeIdUri = 'urn:mpeg:dash:sand:channel:http:2016' and (starts-with(@endpoint, 'http://') or starts-with(@endpoint, 'https://'))) or @schemeIdUri != 'urn:mpeg:dash:sand:channel:http:2016'">
        If the @schemeIdUri is "urn:mpeg:dash:sand:channel:http:2016", the @endpoint shall be a valid HTTP-URL according to RFC 3986.
      </assert>
      <assert test="(@schemeIdUri = 'urn:mpeg:dash:sand:channel:header:2016' and count(@endpoint) = 0) or @schemeIdUri != 'urn:mpeg:dash:sand:channel:header:2016'">
        If the @schemeIdUri is "urn:mpeg:dash:sand:channel:http:2016", the @endpoint shall not present.
      </assert>
    </rule>
    <rule context="dash:Reporting">
        <assert test="(@schemeIdUri != 'urn:mpeg:dash:sand:channel:2016') or (@schemeIdUri = 'urn:mpeg:dash:sand:channel:2016' and @value = //sand:Channel/@id) ">
        5.H.3 - If SAND Channle is used for reporting, then @value shall contain
        the value of @id of a SAND Channel present in the MPD.
      </assert>
    </rule>
  </pattern>
</schema>
