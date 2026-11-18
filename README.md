# Sure for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/default)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1+-blue.svg)](https://www.home-assistant.io/)

A lightweight Home Assistant custom integration to expose account balances from your self-hosted [Sure](https://github.com/we-promise/sure) personal finance instance.

---

## Features

- **Account Sensors:** Automatically creates a sensor for each active account in Sure with its exact balance (from `balance_cents`).
- **Secure Credentials:** Setup through Home Assistant's UI Config Flow with masked API keys.
- **15-Minute Polling:** Polls Sure every 15 minutes (configurable in integration Options).
- **Auto-Discovery:** New accounts added in Sure are discovered automatically.

---

## Installation

### Method 1: HACS (Recommended)

1. Open **HACS** in Home Assistant.
2. Click the 3 dots in the top right corner and select **Custom repositories**.
3. Add this repository URL, choose **Integration** as the category, and click **Add**.
4. Download **Sure** and restart Home Assistant.

### Method 2: Manual Installation

1. Copy the `custom_components/sure` folder into your Home Assistant `<config>/custom_components/` directory:
   ```text
   <config>/
   └── custom_components/
       └── sure/
           ├── __init__.py
           ├── manifest.json
           ├── client.py
           ├── coordinator.py
           ├── config_flow.py
           ├── sensor.py
           ├── const.py
           └── strings.json
   ```
2. Restart Home Assistant.

---

## Configuration

1. In your **Sure** instance:
   - Go to **Settings** → **API Keys**
   - Create a key with `read` permissions.
2. In Home Assistant:
   - Go to **Settings** → **Devices & Services** → **Add Integration** → search for **Sure**
   - Enter your **Server URL** (e.g. `https://sure.example.com`) and **API Key**
   - Click **Submit**.

---

## Lovelace Card Example

```yaml
type: entities
title: Sure Accounts
entities:
  - entity: sensor.sure_checking
  - entity: sensor.sure_savings
```
