<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron" xmlns:sand="urn:mpeg:dash:schema:sandmessage:2016" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" queryBinding='xslt' schemaVersion='ISO19757-3'>
  <ns prefix="sand" uri="urn:mpeg:dash:schema:sandmessage:2016"/>
  <ns prefix="xsi" uri="http://www.w3.org/2001/XMLSchema-instance"/>
  <pattern>
    <rule context="sand:QoSInformation">
      <assert test="@gbr or @mbr or @delay or @pl">
        At least one of the QoS metrics shall be present in the message.
      </assert>
    </rule>
  </pattern>
</schema>
