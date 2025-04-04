from random import uniform
import re
import argparse
import pprint
from time import sleep
import odoorpc
import requests

OCA_URL = "https://github.com/OCA/"
REQUEST_TIMEOUT = 10


def get_repo_name(url):
    items = url.split("/")
    for item in items:
        if item == "OCA":
            return items[items.index(item) + 1]
    return None


# Pull Request Cache
pr_cache = {}


def update_pr_cache(repo_name, version, github_token=None):
    if repo_name in pr_cache:
        return
    base = "%d.0" % version
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    params = {
        "state": "open",
        "per_page": 100,
        "base": base,
    }
    response = requests.get(
        f"https://api.github.com/repos/OCA/{repo_name}/pulls",
        headers=headers,
        params=params,
        timeout=REQUEST_TIMEOUT,
    )
    if response.status_code == 200:
        pr_cache[repo_name] = response.json()
        wait_time = uniform(0.1, 0.2)
        print(
            "[*] PR cache updated for %s ... waiting for %.2f seconds"
            % (repo_name, wait_time)
        )
        sleep(wait_time)  # Rate limit handling
    else:
        print("[-] Error fetching PR for %s: %s" % (repo_name, response.status_code))
        # print headers to identify a rate limit error
        if response.status_code == 403:
            print("[-] Headers: %s" % response.headers)


def update_or_create_migration(odoo, module, version, new_data):
    migration_updated = False
    for migration in module.migration_ids:
        if migration.version == version:
            mig_data = migration.read(["state", "note"])[0]
            mig_data.pop("id", None)
            # compare both dictionaries
            if mig_data == new_data:
                pass
            # check if the migration edit is forbidden
            elif mig_data["note"] and mig_data["note"][0] == "✋" in mig_data["note"]:
                print(f"[-] Migration edit forbidden for {module.name} using emoji ✋")
            else:
                # Update the existing migration record
                print(f"[*] Updating migration record for {module.name}...")
                migration.write(new_data)
            migration_updated = True
    if not migration_updated:
        # Create a new migration record if it doesn't exist
        print(f"[+] Creating new migration record for {module.name}...")
        new_data.update(
            {
                "module_id": module.id,
                "version": version,
            }
        )
        migration = odoo.env["ir.module.migration"].create(new_data)


def get_module_migration_data_from_repo(module_name, module_url):
    response = requests.head(module_url, allow_redirects=True, timeout=REQUEST_TIMEOUT)
    if response.status_code == 200:
        print(f"[+] Module {module_name} is available at {module_url}.")
        data = {
            "state": "migrated",
            "note": "Migrated to OCA repository",
            "repo_address": module_url,
        }
        return data
    else:
        print(f"[-] Module {module_name} not available at {module_url}.")
        return None


def get_module_migration_data_from_pr(
    module_name, module_url, repo_name, version, github_token
):
    # caching the pull request data to avoid multiple requests
    update_pr_cache(repo_name, version, github_token)
    if repo_name not in pr_cache:
        print(f"[-] No PR cache for {repo_name}.")
        return None
    for pr in pr_cache[repo_name]:
        title = pr["title"]
        base = pr["base"]["ref"]
        if (
            "[MIG]" in title.upper() or "[OU-ADD]" in title.upper()
        ) and module_name in title.lower():
            # module is referenced in a pull request
            print(f"[+] Module {module_name} is referenced in a PR. {base}")
            data = {
                "state": "migrated",
                "note": "Review",
                "repo_address": module_url,
                "pr_address": pr["html_url"],
            }
            return data
    print(f"[-] Module {module_name} not referenced in any PR.")
    return None


def get_module_default_migration_data(module_name, module_url, repo_url, version):
    # module is not referenced in a pull request
    print(f"[-] Module {module_name} not referenced in any PR.")
    help_notes = [
        "- Check module status from issue named [Migration to version %d.0] at %s"
        % (version, repo_url + "/issues"),
        "- Check if migration exists with wrong name or closed status at %s"
        % (repo_url + "/pulls?q=is:pr"),
    ]
    data = {
        "state": "todo",
        "note": "\n".join(help_notes),
        "repo_address": module_url,
    }
    return data


def github_to_odoo(version, host, port, db_name, user, password, github_token=None):
    """Convert the dictionary to Odoo format."""
    # prepare the connection to the server
    odoo = odoorpc.ODOO(host, port=port)
    # login
    odoo.login(db_name, user, password)
    # current user
    user = odoo.env.user
    print("Logged in as: %s (%s)" % (user.name, user.company_id.name))

    module_ids = odoo.env["ir.module.module"].search(
        [
            ("website", "=ilike", OCA_URL + "%"),
            ("state", "in", ["installed", "to upgrade", "to remove"]),
        ],
        limit=0,
    )
    modules = odoo.env["ir.module.module"].browse(module_ids)
    print(module_ids)
    for module in modules:
        repo_name = get_repo_name(module.website)
        # execute an HEAD request to the module URL
        # to check if the module is available
        repo_url = f"https://github.com/OCA/{repo_name}/tree/{version}.0"
        module_url = f"{repo_url}/{module.name}"
        data = get_module_migration_data_from_repo(module.name, module_url)
        if data is None:
            # search if the module is referenced in the pull request cache
            data = get_module_migration_data_from_pr(
                module.name, module_url, repo_name, version, github_token
            )
            if data is None:
                # module is not referenced in a pull request
                data = get_module_default_migration_data(
                    module.name, module_url, repo_url, version
                )
        update_or_create_migration(odoo, module, version, data)


if __name__ == "__main__":
    # Argument parser for the file path
    parser = argparse.ArgumentParser(
        description="Update OCA modules migration status from Github"
    )

    parser.add_argument(
        "version",
        help="Version to check.",
    )
    parser.add_argument(
        "--host",
        required=True,
        help="Odoo Host Address",
    )
    parser.add_argument(
        "--port",
        required=True,
        type=int,
        help="Odoo Port Number",
    )
    parser.add_argument(
        "--database",
        required=True,
        help="Odoo Database",
    )
    parser.add_argument(
        "--user",
        required=True,
        help="Odoo Username",
    )
    parser.add_argument(
        "--github-token",
        help="Github Token for authentication (optional). "
        "https://github.com/settings/tokens",
    )
    args = parser.parse_args()

    # ensure all arguments are provided together or none at all
    odoo_args = [args.host, args.port, args.database, args.user]
    if any(odoo_args) and not all(odoo_args):
        parser.error(
            "All Odoo connection arguments (--host, --port, --database, --user) "
            "must be provided together."
        )

    password = input("Password for '%s': " % args.user)
    github_to_odoo(
        int(args.version),
        args.host,
        args.port,
        args.database,
        args.user,
        password,
        args.github_token,
    )
