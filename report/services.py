from datetime import datetime

from report.parsers import ContributorParser, LanguageParser, OrganizationParser

from .constants import REPO_LANGUAGES_CACHE_KEY
from .exceptions import (
    ContributorServiceException,
    LanguageServiceException,
    OrganizationServiceException,
    RateLimitException,
)
from .mixins import CacheMixin


class BaseService:
    def __init__(self, github_obj, *args, **kwargs):
        self.github_obj = github_obj

    def _get_rate_limit_details(self):
        data = self.github_obj.get_rate_limit().core.raw_data
        data["reset"] = datetime.fromtimestamp(data["reset"]).strftime(
            "%m-%d-%Y %H:%M:%S"
        )
        return data

    def _is_limit_exceeded(self):
        data = self._get_rate_limit_details()
        if data["remaining"] > 0:
            print(f"Remaining: >>>>>>>>>>> {data['remaining']}")
            return False
        print(
            f"You exceed the rate limit: {data['limit']} of Github API, please try again after: {data['reset']}"
        )
        return True

    def _request(self):
        raise NotImplementedError

    def request(self):
        if self._is_limit_exceeded():
            raise RateLimitException(
                message="You exceed the rate limit Github API", status_code=403
            )
        try:
            return self._request()
        except Exception as e:
            raise self.EXCEPTION(message=e.data.get("message"), status_code=e.status)


class OrganizationService(BaseService):
    EXCEPTION = OrganizationServiceException

    def __init__(self, github_obj, organization, *args, **kwargs):
        super().__init__(github_obj, *args, **kwargs)
        self.organization = organization

    def _request(self):
        # Returns Organization object
        # https://pygithub.readthedocs.io/en/latest/github_objects/Organization.html#github.Organization.Organization
        return self.github_obj.get_organization(self.organization)


class ContributorService(BaseService):
    EXCEPTION = ContributorServiceException

    def __init__(self, github_obj, repo, *args, **kwargs):
        super().__init__(github_obj, *args, **kwargs)
        self.repo = repo

    def _request(self):
        # Return PaginatedList of NamedUser
        # https://pygithub.readthedocs.io/en/latest/utilities.html#github.PaginatedList.PaginatedList
        # https://pygithub.readthedocs.io/en/latest/github_objects/NamedUser.html#github.NamedUser.NamedUser
        return self.repo.get_contributors()


class LanguageService(BaseService, CacheMixin):
    EXCEPTION = LanguageServiceException

    def __init__(self, github_obj, repo, *args, **kwargs):
        super().__init__(github_obj, *args, **kwargs)
        self.repo = repo

    def _request(self):
        # Try to get the languages from the cache, if it's not found in the cache, then it will get
        # the results from Github and cache them
        cache_key = REPO_LANGUAGES_CACHE_KEY.format(id=self.repo.id)
        if self.get_from_cache(cache_key):
            return self.get_from_cache(cache_key)
        else:
            # Return a dict of languages and number of lines for each language.
            languages = self.repo.get_languages()
            if languages:
                # Some repositories didn't have languages!, so it will raise an error if you
                # try to set an empty value for the cache_key. So we will ignore adding this key.
                self.set_into_cache(cache_key, languages)
            return languages


class GithubService:
    def __init__(self, github_object, *args, **kwargs):
        self.github_object = github_object

    def get_organization(self, organization):
        """Call the OrganizationService and return OrganizationParser.

        Args:
            - organization(str): The name of the organization.

        Returns:
            OrganizationParser(dict): with the name of the organization and its repositories.
        """
        organization = OrganizationService(self.github_object, organization).request()
        return OrganizationParser(organization).parse()

    def get_languages(self, repo):
        """Call the LanguageService and return LanguageParser.

        Args:
            - repo(obj): Instance of Repository

        Returns:
            LanguageParser(list): List of all languages in the repo.
        """
        language_service = LanguageService(self.github_object, repo).request()
        return LanguageParser(language_service).parse()

    def get_contributors(self, repo):
        """Call the ContributorService and return ContributorParser.

        Args:
            - repo(obj): Instance of Repository

        Returns:
            ContributorParser(dict): with all contributor info.
        """
        contributor_service = ContributorService(self.github_object, repo).request()
        return ContributorParser(contributor_service).parse()
