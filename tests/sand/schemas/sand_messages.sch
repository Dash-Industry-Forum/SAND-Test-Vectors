<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron" xmlns:sand="urn:mpeg:dash:schema:sandmessage:2016" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" queryBinding='xslt' schemaVersion='ISO19757-3'>
  <ns prefix="sand" uri="urn:mpeg:dash:schema:sandmessage:2016"/>
  <ns prefix="xsi" uri="http://www.w3.org/2001/XMLSchema-instance"/>
  <pattern>
    <rule context="sand:SharedResourceAssignment">
      <assert test="@validityTime">
        5.B.1 - The validityTime attribute in the SAND message envelope shall be present for the SharedResourceAssignment message as it allows the DASH client to discover for how long the resource assignment is available.
      </assert>
    </rule>
    <rule context="sand:QoSInformation">
      <assert test="@gbr or @mbr or @delay or @pl">
        5.B.4 - At least one of the QoS metrics shall be present in the message.
      </assert>
    </rule>
    <rule context="sand:AvailabilityTimeOffset">
      <assert test="@repId or @baseUrl">
        5.B.5 - Either Representation ID or Base URL shall be used.
      </assert>
    </rule>
    <rule context="sand:Throughput">
      <assert test="@repId or @baseUrl">
        5.B.6 - Either Representation ID or Base URL shall be used.
      </assert>
    </rule>
  </pattern>
</schema>
