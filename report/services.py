from report.parsers import ContributorParser, LanguageParser, OrganizationParser

from .conf import redis_conn
from .constants import REPO_LANGUAGES_CACHE_KEY
from .exceptions import (
    ContributorServiceException,
    LanguageServiceException,
    OrganizationServiceException,
)


class BaseService:
    def _request(self):
        raise NotImplementedError

    def request(self):
        try:
            return self._request()
        except Exception as e:
            raise self.EXCEPTION(message=e.data.get("message"), status_code=e.status)


class OrganizationService(BaseService):
    EXCEPTION = OrganizationServiceException

    def __init__(self, github_obj, organization, *args, **kwargs):
        self.github_obj = github_obj
        self.organization = organization

    def _request(self):
        # Returns Organization object
        # https://pygithub.readthedocs.io/en/latest/github_objects/Organization.html#github.Organization.Organization
        return self.github_obj.get_organization(self.organization)


class ContributorService(BaseService):
    EXCEPTION = ContributorServiceException

    def __init__(self, repo, *args, **kwargs):
        self.repo = repo

    def _request(self):
        # Return PaginatedList of NamedUser
        # https://pygithub.readthedocs.io/en/latest/utilities.html#github.PaginatedList.PaginatedList
        # https://pygithub.readthedocs.io/en/latest/github_objects/NamedUser.html#github.NamedUser.NamedUser
        return self.repo.get_contributors()


class LanguageService(BaseService):
    EXCEPTION = LanguageServiceException

    def __init__(self, repo, *args, **kwargs):
        self.repo = repo

    def _request(self):
        # Try to get the languages from the cache, if it's not found in the cache, then it will get
        # the results from Github and cache them
        cache_key = REPO_LANGUAGES_CACHE_KEY.format(id=self.repo.id)
        if redis_conn.hgetall(cache_key):
            print(f"Get {self.repo.id} languages from the cache")
            return redis_conn.hgetall(cache_key)
        else:
            # Return a dict of languages and number of lines for each language.
            languages = self.repo.get_languages()
            try:
                redis_conn.hmset(cache_key, languages)
            except Exception:
                # Some repositories didn't have languages!, so it will raise an error if you
                # try to set an empty value for the cache_key. So we will ignore adding this key.
                pass
            return languages


class GithubService:
    @staticmethod
    def get_organization(github_object, organization):
        """Call the OrganizationService and return OrganizationParser.

        Args:
            - github_object(obj): Instance of Github
            - organization(str): The name of the organization.

        Returns:
            OrganizationParser(dict): with the name of the organization and its repositories.
        """
        organization = OrganizationService(github_object, organization).request()
        return OrganizationParser(organization).parse()

    @staticmethod
    def get_languages(repo):
        """Call the LanguageService and return LanguageParser.

        Args:
            - repo(obj): Instance of Repository

        Returns:
            LanguageParser(list): List of all languages in the repo.
        """
        language_service = LanguageService(repo).request()
        return LanguageParser(language_service).parse()

    @staticmethod
    def get_contributors(repo):
        """Call the ContributorService and return ContributorParser.

        Args:
            - repo(obj): Instance of Repository

        Returns:
            ContributorParser(dict): with all contributor info.
        """
        contributor_service = ContributorService(repo).request()
        return ContributorParser(contributor_service).parse()
