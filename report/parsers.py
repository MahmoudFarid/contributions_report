from .constants import CONTRIBUTOR_CACHE_KEY
from .mixins import CacheMixin


class OrganizationParser:
    def __init__(self, organization):
        self.organization = organization

    def _get_repos(self):
        """Return a list of all possible repositories.

        Args:
            - repos(PaginatedList): PaginatedList

        Returns:
            list: list of all possible repositories.
        """
        return [repo for repo in self.organization.get_repos()]

    def parse(self):
        return {
            "name": self.organization.name,
            "repos": self._get_repos(),
        }


class ContributorParser(CacheMixin):
    def __init__(self, contributors):
        self.contributors = contributors

    def _get_contributor_info(self, contributor):
        """Try to get the contributors from the cache, if it's not found in the cache, then it will get
        the results from Github and cache them.

        Args:
            - contributor(NamedUser): NamedUser

        Returns:
            - dict: dict with all needed contributor's information.
        """
        cache_key = CONTRIBUTOR_CACHE_KEY.format(id=contributor.id)
        if self.get_from_cache(cache_key):
            return self.get_from_cache(cache_key)
        else:
            user_info = {
                "id": contributor.id,
                "login": contributor.login,
                "name": contributor.name or "",
                "email": contributor.email or "",
            }
            self.set_into_cache(cache_key, user_info)
            return user_info

    def parse(self):
        results = []
        for contributor in self.contributors:
            results.append(self._get_contributor_info(contributor))
        return results


class LanguageParser:
    def __init__(self, languages):
        self.languages = languages

    def parse(self):
        return [lang for lang in self.languages]
