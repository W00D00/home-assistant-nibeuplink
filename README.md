---
layout: page
title: "NIBEUplink"
description: "Instructions on how to integrate NIBE systems into Home Assistant."
date: 2019-04-07 10:00
sidebar: true
comments: false
sharing: true
footer: true
logo: nibe.png
ha_category:
  - Sensor
ha_iot_class: Cloud Polling
ha_release: 0.91.1
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
  api_base_url: NIBEUPLINK_API_BASE_URL
  token_url: NIBEUPLINK_TOKEN_URL
  systems:
    - system_name: SYSTEM_NAME_1
      system_id: SYSTEM_ID_1
    - system_name: SYSTEM_NAME_2
      system_id: SYSTEM_ID_2
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
api_base_url:
  description: NIBE Uplink API base url.
  required: false
  type: string
token_url:
  description: NIBE Uplink token url.
  required: false
  type: string
systems:
  description: List of systems.
  required:  true
  type: map
  keys:
    system_name:
      description: System Name. The name of the system. Found in the My Systems settings page.
      required: true
      type: string
    system_id:
      description: Device ID. Found in the given system path.
      required: true
      type: string
{% endconfiguration %}

## {% linkable_title Sensor %}

The `nibeuplink` sensor platform allows you to control your NIBE Uplink systems.
