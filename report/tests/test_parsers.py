from unittest import TestCase
from unittest.mock import patch

from report.parsers import ContributorParser, LanguageParser, OrganizationParser
from report.services import ContributorService, LanguageService, OrganizationService

from .objects import Github, Organization, Repository, NamedUser


class TestOrganizationParser(TestCase):
    def setUp(self):
        self.github_object = Github("AUTH_KEY")

    @patch("report.services.OrganizationService._request")
    def test_organization_parser(self, service_mock):
        org = Organization("test")
        service_mock.return_value = org
        service = OrganizationService(self.github_object, "test").request()
        parser = OrganizationParser(service).parse()
        self.assertEqual(parser["name"], org.name)
        self.assertEqual(len(parser["repos"]), len(org.get_repos()))


class TestContributorParser(TestCase):
    def setUp(self):
        self.github_object = Github("AUTH_KEY")

    @patch("report.services.ContributorParser.set_into_cache")
    @patch("report.services.ContributorParser.get_from_cache", return_value={})
    @patch("report.services.ContributorService._request")
    def test_organization_parser_with_disable_cache(
        self, service_mock, parser_from_cache, parser_set_cache
    ):
        user = NamedUser()
        service_mock.return_value = [user]
        service = ContributorService(self.github_object, "test").request()
        parser = ContributorParser(service).parse()
        self.assertEqual(parser[0]["id"], user.id)
        self.assertEqual(parser[0]["login"], user.login)
        self.assertEqual(parser[0]["name"], user.name)
        self.assertEqual(parser[0]["email"], user.email)
        self.assertEqual(parser_from_cache.call_count, 1)
        self.assertEqual(parser_set_cache.call_count, 1)

    @patch("report.services.ContributorParser.set_into_cache")
    @patch(
        "report.services.ContributorParser.get_from_cache",
        return_value={"id": 123, "login": "test", "name": "Test", "email": ""},
    )
    @patch("report.services.ContributorService._request")
    def test_organization_parser_with_enable_cache(
        self, service_mock, parser_from_cache, parser_set_cache
    ):
        user = NamedUser()
        service_mock.return_value = [user]
        service = ContributorService(self.github_object, Repository()).request()
        parser = ContributorParser(service).parse()
        # Get these results from the parser_from_cache
        self.assertEqual(parser[0]["id"], 123)
        self.assertEqual(parser[0]["login"], "test")
        self.assertEqual(parser[0]["name"], "Test")
        self.assertEqual(parser[0]["email"], "")
        self.assertEqual(parser_from_cache.call_count, 2)
        self.assertEqual(parser_set_cache.call_count, 0)


class TestLanguageParser(TestCase):
    def setUp(self):
        self.github_object = Github("AUTH_KEY")

    @patch("report.services.LanguageService._request")
    def test_Language_parser(self, service_mock):
        service_mock.return_value = {"Python": 1234, "Go": 567, "JavaScript": 100}
        service = LanguageService(self.github_object, Repository()).request()
        parser = LanguageParser(service).parse()
        self.assertEqual(parser, ["Python", "Go", "JavaScript"])
