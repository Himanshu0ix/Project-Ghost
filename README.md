# Project Ghost: System-Wide IP Rotator

**Project Ghost** is a sophisticated anonymity framework for Windows, designed for ethical hacking, penetration testing, and security research. It transforms your machine into a digital ghost by routing all system-wide internet traffic through a constantly changing series of public proxies, making your digital footprint nearly impossible to trace.

This tool is not a simple browser extension; it directly manipulates the Windows Registry and API to enforce system-level anonymization for all applications.

---

## Features

-   **Automated Proxy Harvesting:** Deploys a stealthy Firefox browser instance to scrape hundreds of live SSL proxies from public sources, bypassing anti-bot measures.
-   **Intelligent Validation:** Performs a multi-stage validation process, including an initial bulk scan and a real-time, pre-engagement "heartbeat check" to ensure only live proxies are used.
-   **System-Wide Anonymization:** Modifies the Windows Registry and uses low-level API calls to force the entire operating system, including all browsers and applications, to use the selected proxy.
-   **Dynamic Rotation:** Automatically rotates to a new, validated proxy at a user-defined interval, ensuring your egress point is constantly in flux.
-   **Self-Healing:** Actively detects and discards dead proxies from its live pool, maintaining a stable and reliable connection.

---

## How It Works

1.  **Ammunition Run:** The script launches a headless Firefox browser to scrape a list of potential proxies from `sslproxies.org`.
2.  **Boot Camp:** It performs an initial, intensive validation of all harvested proxies to create a pool of known-live candidates.
3.  **The Loop:** The main rotation cycle begins.
    a. A random proxy is selected from the live pool.
    b. A real-time "heartbeat check" is performed to ensure it's still alive.
    c. If dead, the proxy is discarded, and a new one is selected.
    d. If alive, the script uses `ctypes` and `winreg` to set it as the system-wide proxy.
    e. It then forces a system-wide settings refresh via `wininet.dll` to ensure all applications (including lazy browsers) adopt the new identity.
    f. It waits for the user-defined interval and repeats the process.

---

## Prerequisites

-   Windows Operating System
-   Python 3.x
-   Mozilla Firefox browser installed

---

## Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Himanshu0ix/Project-Ghost
    cd Project-Ghost
    ```

2.  **Install required Python libraries:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Download GeckoDriver:**
    -   Go to the [GeckoDriver releases page](https://github.com/mozilla/geckodriver/releases).
    -   Download the latest `win64.zip` version.
    -   Unzip the file and place **`geckodriver.exe`** in the root of the `Project-Ghost` directory.

---

### A Note on WebDrivers: The Key to the Ignition

This tool relies on a technology called **Selenium** to automate a web browser for the initial proxy harvesting. To do this, Selenium requires a specific middleman called a **WebDriver**.

Think of it like this:
-   **Your Python Script (`ghost.py`)** is the driver.
-   **The Web Browser (Firefox, Chrome, etc.)** is the car.
-   **The WebDriver (`geckodriver.exe`, `chromedriver.exe`)** is the specific key, steering wheel, and pedal assembly for that *exact model* of car.

You cannot use a Ford key to start a Honda. Likewise, you cannot use `chromedriver` to control Firefox. The WebDriver is the essential translator that allows your script to give commands to the browser.

#### Why Firefox and GeckoDriver?

This project is configured to use **Mozilla Firefox** and its corresponding **GeckoDriver**. The primary reason for this choice is **stability**. GeckoDriver is generally more forgiving with browser version mismatches. As Firefox updates, an older GeckoDriver will often continue to function perfectly, leading to fewer maintenance headaches.

#### Adapting for Other Browsers

While configured for Firefox, the core logic of this tool can be adapted to use other browsers. Here are the requirements for the most common alternatives:

**1. Google Chrome**
*   **Driver:** `chromedriver.exe`
*   **Challenge:** Chrome is notoriously strict. The `chromedriver` version **must exactly match** the installed Chrome browser version down to the minor revision number. As Chrome auto-updates frequently, this can cause the script to break often, requiring you to download a new driver.
*   **To Adapt:**
    1.  Download the correct `chromedriver.exe` from the [Chrome for Testing Dashboard](https://googlechromelabs.github.io/chrome-for-testing/).
    2.  Modify the `setup_browser` function in the script to import and use `webdriver.Chrome` instead of `webdriver.Firefox`.

**2. Microsoft Edge**
*   **Driver:** `msedgedriver.exe`
*   **Challenge:** Since Edge is built on the same Chromium engine as Chrome, it suffers from the same strict version-matching requirements. You must sync the `msedgedriver` version with your Edge browser version.
*   **To Adapt:**
    1.  Download the correct `msedgedriver.exe` from the [Microsoft Edge WebDriver page](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/).
    2.  Modify the `setup_browser` function to import and use `webdriver.Edge`.

Ultimately, Firefox was chosen to provide the most stable, "set it and forget it" experience for the end-user.

---

## Usage

You **MUST** run this script with administrator privileges to allow it to modify the system registry.

1.  Right-click on PowerShell or Command Prompt and select "Run as administrator".
2.  Navigate to the `Project-Ghost` directory.
3.  Execute the script:
    ```bash
    python ghost.py
    ```
4.  The script will harvest and validate proxies (this may take a few minutes).
5.  When prompted, enter the rotation interval in seconds (e.g., `60` for one minute).
6.  To stop the script and automatically disable the proxy, press `Ctrl+C`.

---

## ⚠️ Disclaimer

This tool is intended for educational and ethical purposes only. Using public proxies is inherently slow and unreliable. This tool does **NOT** encrypt your traffic and is not a replacement for a full VPN. The user assumes all responsibility for their actions.
