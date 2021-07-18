import argparse

from report.github import GithubContributorReport


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a report of the organization's repositories contributions"
    )
    parser.add_argument(
        "--organization", type=str, required=True, help="The name of the organization"
    )
    parser.add_argument(
        "--auth-key", type=str, required=True, help="Access Token of Github account"
    )
    parser.add_argument(
        "--file-path", type=str, nargs="?", help="Path of the report", default="/tmp/"
    )

    args = parser.parse_args()

    GithubContributorReport(
        args.auth_key, args.organization, args.file_path
    ).generate_report()
