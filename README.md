# LinkedIn Connection Automation Tool

This repository contains a Python script to automate sending connection requests on LinkedIn using Selenium. It supports logging in with cookies or credentials, selecting location filters, and sending personalized connection requests. The tool is configurable via an `ini` file and uses color-coded console outputs for better readability.

## Features

- Login using LinkedIn cookies or credentials
- Select location filters for connection requests
- Send personalized connection requests
- Configurable via `setup.ini` file
- Color-coded console outputs for better readability

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/ahmedmujtaba1/Linkedin-Auto-Connector.git
    cd Linkedin-Auto-Connector
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Configure your LinkedIn credentials and settings in the `setup.ini` file:
    ```ini
    [LinkedIn]
    li_at = YOUR_LI_AT_COOKIE_HERE
    email = YOUR_EMAIL_HERE
    password = YOUR_PASSWORD_HERE
    ```

## Usage

1. Run the script:
    ```bash
    python script.py
    ```

2. Follow the prompts to enter your search criteria and connection request details.

## How to Get `li_at` LinkedIn Cookies

1. Open Chrome and log in to your LinkedIn account.
2. Press `F12` or `Ctrl+Shift+I` to open Developer Tools.
3. Go to the `Application` tab.
4. In the left sidebar, under `Storage`, click on `Cookies` and then select `https://www.linkedin.com`.
5. Look for the `li_at` cookie in the list.
6. Copy the value of the `li_at` cookie and paste it into the `setup.ini` file under `[LinkedIn]`.

## Contributing

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a pull request.

## Contact

Ahmed Mujtaba - [Your LinkedIn Profile](https://www.linkedin.com/in/creative-programmer/)
