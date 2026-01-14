# ruff: noqa: UP031
# pylint: disable=W8116

import argparse
import os
import pprint
import re
import sys

import odoorpc

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__) + "/..")
# print(SCRIPT_DIR)
# print(os.path.dirname(SCRIPT_DIR))
sys.path.append(os.path.dirname(SCRIPT_DIR) + "/..")

from oca_status import update_oca_to_odoo  # noqa: E402

# Define the mapping for the "state" column
status_mapping = {
    "Done (partial)": "todo",
    "Done": "migrated",
    "Nothing to do": "migrated",
    "": "todo",  # Default state if no status is provided
}


def determine_state(status, tag):
    """Determine the state of a module based on its status and tag."""
    if tag == "|new|":
        return ""
    elif tag == "|del|":
        return "removed"
    return status_mapping.get(status, "todo")


def load_table_rows_from_rst(file_path):
    """Load table rows from a .rst file."""
    table_rows = []
    with open(file_path, encoding="utf-8") as file:
        for line in file:
            # Only process lines that look like table rows
            if line.startswith("|"):
                table_rows.append(line.strip())
    return table_rows


def rst_to_dict(file_path):
    # Load the table rows from the specified .rst file
    table_rows = load_table_rows_from_rst(file_path)

    # Initialize the dictionary
    modules_status = {}

    # Process each row
    for row in table_rows:
        # Extract the tag, module name, status, and note using regex
        match = re.match(
            r"\|\s*(\|new\||\|del\|)?\s*([\w_]+)\s*\|\s*([\w\s\(\)]*)\s*\|\s*(.*)\|",
            row,
        )
        if match:
            tag = match.group(1) or ""
            module_name = match.group(2)
            status = match.group(3).strip()
            note = match.group(4).strip()
            # determine the state
            state = determine_state(status, tag)
            # keep status as note if no comment exists
            if note == "":
                note = status
            # add the module to the dictionary
            modules_status[module_name] = {"state": state, "note": note}

    return modules_status


def dict_to_odoo(data, version, host, port, db_name, user, password, github_token=None):
    """Convert the dictionary to Odoo format."""
    # prepare the connection to the server
    odoo = odoorpc.ODOO(host, port=port)
    # login
    odoo.login(db_name, user, password)
    # current user
    user = odoo.env.user
    print("Logged in as: %s (%s)" % (user.name, user.company_id.name))

    for module_name, m_data in data.items():
        module_id = odoo.env["ir.module.module"].search(
            [("name", "=", module_name)],
            limit=1,
        )
        if not module_id:
            print(f"[-] Module {module_name} not found in this Odoo database.")
        else:
            migration = False
            # m_data["note"] = "*" + m_data["note"]
            module = odoo.env["ir.module.module"].browse(module_id)
            for _migration in module.migration_ids:
                new_data = {
                    "state": m_data["state"],
                    "note": m_data["note"],
                }
                if _migration.version == version:
                    mig_data = _migration.read(["state", "note"])[0]
                    mig_data.pop("id", None)
                    # compare both dictionaries
                    if mig_data == new_data:
                        pass
                    else:
                        # Update the existing migration record
                        print(f"[*] Updating migration record for {module_name}...")
                        _migration.write(new_data)
                    migration = _migration
            if not migration:
                # Create a new migration record if it doesn't exist
                print(f"[+] Creating new migration record for {module_name}...")
                migration_id = odoo.env["ir.module.migration"].create(
                    {
                        "module_id": module.id,
                        "version": version,
                        "state": m_data["state"],
                        "note": m_data["note"],
                    }
                )
                migration = odoo.env["ir.module.migration"].browse(migration_id)
            if migration.state == "todo":
                repo_name = "OpenUpgrade"
                repo_url = f"https://github.com/OCA/{repo_name}/list/{version}.0"
                module_url = f"{repo_url}/openupgrade_scripts/scripts/{module.name}"
                # search if the module is referenced in the pull request cache.
                data = update_oca_to_odoo.get_module_migration_data_from_pr(
                    module.name, module_url, repo_name, version, github_token
                )
                if data:
                    migration.write(data)


if __name__ == "__main__":
    # Argument parser for the file path
    parser = argparse.ArgumentParser(
        description="Convert .rst table to Python dictionary."
    )

    parser.add_argument(
        "file",
        help="Path to the .rst file to be processed.",
    )
    parser.add_argument(
        "--host",
        help="Odoo Host Address",
    )
    parser.add_argument(
        "--port",
        type=int,
        help="Odoo Port Number",
    )
    parser.add_argument(
        "--database",
        help="Odoo Database",
    )
    parser.add_argument(
        "--user",
        help="Odoo Username",
    )
    parser.add_argument(
        "--github-token",
        help="Github Token for authentication (optional). "
        "https://github.com/settings/tokens",
    )

    args = parser.parse_args()
    # extract version number from the filename
    version = int(args.file.split(".")[0])
    # ensure all arguments are provided together or none at all
    odoo_args = [args.host, args.port, args.database, args.user]
    if any(odoo_args) and not all(odoo_args):
        parser.error(
            "All Odoo connection arguments (--host, --port, --database, --user) "
            "must be provided together."
        )

    data = rst_to_dict(args.file)
    if data:
        # Print the resulting dictionary
        pprint.pprint(data)
        if all(odoo_args):
            password = input("Password for '%s': " % args.user)
            dict_to_odoo(
                data,
                version,
                args.host,
                args.port,
                args.database,
                args.user,
                password,
                args.github_token,
            )
