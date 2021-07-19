import csv
import multiprocessing as mp
import os
from datetime import datetime

from github import Github
from report.services import GithubService


class GithubContributorsReport:
    def __init__(
        self, auth_key: str, organization: str, report_path: str, *args, **kwargs
    ) -> None:
        self.github_object = Github(auth_key)
        self.organization = organization
        self.report_path = report_path
        self.service = GithubService(self.github_object)

    def _get_repo_contributors_and_languages(self, repo) -> dict:
        """Get the contributors and languages for the repo

        Args:
            - repo (Repository[obj]): Github Repository object

        Returns:
            dict: with all contributors and languages
        """
        print(f"start getting contributors and languages for {repo.name}")
        languages = self.service.get_languages(repo)
        contributors = self.service.get_contributors(repo)
        return {
            "users": contributors,
            "repo": repo.name,
            "languages": languages,
        }

    def _aggregate_repositories_to_user(self, data: dict) -> dict:
        """Group the repositories to the user, so each user will has a list of repositories.

        Args:
            - data (dict): Dict contains repositories with its contributors and languages.

        Returns:
            dict: for contributors with its repositories and languages
        """
        results = dict()
        for result in data:
            for user in result["users"]:
                if user["id"] in results:
                    results[user["id"]]["repos"].append(result["repo"])
                else:
                    results[user["id"]] = {
                        "user": user,
                        "repos": [result["repo"]],
                        "languages": result["languages"],
                    }
        return results

    def _run(self):
        """Call all Github services in multiprocessing pool of requests.
        Will initialize the Pool processes with the maximum number of CPUs.

        Return:
            dict: for contributors with its repositories and languages
        """
        organization_parser = self.service.get_organization(self.organization)
        pool = mp.Pool(processes=mp.cpu_count())
        results = pool.map(
            self._get_repo_contributors_and_languages, organization_parser["repos"]
        )
        return self._aggregate_repositories_to_user(results)

    @property
    def filename(self):
        """Generate the report filename in the directory.
        The directory will be created if it's not exists.

        Return:
            str: The filename
        """
        # create the folder if it doesn't exist'
        if not os.path.exists(self.report_path):
            os.makedirs(self.report_path)
        time_now = datetime.now().strftime("%m_%d_%Y_%H_%M")
        filename = f"{self.report_path}/report_{time_now}.csv"
        return os.path.join(self.report_path, filename)

    def _write_csv(self, results: dict) -> None:
        """Write the results into a CSV file.

        Args:
            results (dict): dict for contributors with its repositories and languages
        """
        with open(self.filename, mode="w+") as report_file:
            employee_writer = csv.writer(report_file)
            employee_writer.writerow(
                ["Login", "Name", "Email", "Repositories", "Languages"]
            )
            for data in results.values():
                user_dict = data["user"]
                employee_writer.writerow(
                    [
                        user_dict["login"],
                        user_dict["name"],
                        user_dict["email"],
                        ", ".join(data["repos"]),
                        ", ".join(data["languages"]),
                    ]
                )
            print(f"Created CSV file successfully: {self.filename}")

    def generate_report(self) -> None:
        """Start point for this class, will call all services and write
        the results into a CSV.
        """
        csv_data = self._run()
        self._write_csv(csv_data)
