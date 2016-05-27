<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron" xmlns:sand="urn:mpeg:dash:schema:sand:2016" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" queryBinding='xslt' schemaVersion='ISO19757-3'>
  <ns prefix="sand" uri="urn:mpeg:dash:schema:sand:2016"/>
  <ns prefix="xsi" uri="http://www.w3.org/2001/XMLSchema-instance"/>
  <pattern>
    <rule context="sand:Channel">
      <!--assert test="if (@schemeIdUri = 'urn:mpeg:dash:sand:channel:websocket:2016' and @endpoint = 'allo') then false() else true()"-->
      <assert test="./@schemeIdUri = 'urn:mpeg:dash:sand:channel:websocket:2016' and (starts-with(./@endpoint, 'ws://') or starts-with(./@endpoint, 'wss://'))">
        If the @schemeIdUri is "urn:mpeg:dash:sand:channel:websocket:2016", the @endpoint shall be a WebSocket URI according to RFC 6455.
      </assert>
    </rule>
  </pattern>
</schema>
