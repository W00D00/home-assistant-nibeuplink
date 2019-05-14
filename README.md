---
layout: page
title: "NIBEUplink"
description: "Instructions on how to integrate NIBE systems into Home Assistant."
date: 2019-05-14 10:00
sidebar: true
comments: false
sharing: true
footer: true
logo: nibe.png
ha_category:
  - Sensor
ha_iot_class: Cloud Polling
ha_release: 0.92.2
redirect_from:
  - /components/sensor.nibeuplink/
---

The `nibeuplink` component is the main component to integrate all [NIBE](https://nibe.com) related platforms.

There is currently support for the following device types within Home Assistant:

- Sensor

## {% linkable_title Configuration %}

To enable this component, add the following lines to your `configuration.yaml`:

```yaml
# Example configuration.yaml entry
nibeuplink:
  client_id: NIBEUPLINK_CLIENT_ID
  client_secret: NIBEUPLINK_CLIENT_SECRET
  redirect_url: NIBEUPLINK_REDIRECT_URL
  scope: NIBEUPLINK_SCOPE
  api_auth_url: NIBEUPLINK_API_AUTH_URL
  api_functions_url: NIBEUPLINK_API_FUNCTIONS_URL

sensor:
    - platform: nibeuplink
      sensors:
          sukorooutdoortempbt1:
              name: YOURSENSORNAME
              system_name: YOURSYSTEMNAME
              system_id: SYSTMEID
              system_parameter: PARAMATERID
```

{% configuration %}
client_id:
  description: NIBE Uplink client ID.
  required: true
  type: string
client_secret:
  description: NIBE Uplink client secret.
  required: true
  type: string
redirect_url:
  description: NIBE Uplink API redirect url.
  required: true
  type: string
scope:
  description: NIBE Uplink client access type.
  required: false
  type: string
api_auth_url:
  description: NIBE Uplink API base url.
  required: false
  type: string
api_functions_url:
  description: NIBE Uplink token url.
  required: false
  type: string

sensors:
  description: List of sensors.
  required:  true
  type: map
  keys:
    name:
      description: Name. The name of the given sensor.
      required: true
      type: string    
    system_name:
      description: System Name. The name of the system. Found in the My Systems settings page.
      required: true
      type: string
    system_id:
      description: Device ID. Found in the given system path.
      required: true
      type: string
    system_parameter:
      description: Parameter number.
      required: true
      type: string

{% endconfiguration %}

## {% linkable_title Sensor %}

The `nibeuplink` sensor platform allows you to control your NIBE Uplink systems.
