# ruff: noqa: UP031
# pylint: disable=W8116

import requests

OPENUPGRADE_ROOT = "https://raw.githubusercontent.com/OCA/OpenUpgrade/refs/heads"
urls = {
    14: OPENUPGRADE_ROOT + "/14.0/docsource/modules130-140.rst",
    15: OPENUPGRADE_ROOT + "/15.0/docsource/modules140-150.rst",
    16: OPENUPGRADE_ROOT + "/16.0/docsource/modules150-160.rst",
    17: OPENUPGRADE_ROOT + "/17.0/docsource/modules160-170.rst",
    18: OPENUPGRADE_ROOT + "/18.0/docsource/modules170-180.rst",
}

for version, url in urls.items():
    try:
        # Download the file
        response = requests.get(url, timeout=2)
        response.raise_for_status()  # Raise an error for bad responses

        # Save the file locally
        filename = f"{version}.rst"
        with open(filename, "wb") as file:
            file.write(response.content)
        print(f"Downloaded {url} to {filename}")
    except requests.RequestException as e:
        print(f"Failed to download {url}: {e}")
