from unittest import TestCase
from unittest.mock import patch

from report.services import OrganizationService, ContributorService, LanguageService
from report import exceptions

from github import GithubException

from .objects import Github, Organization, Repository


class TestOrganizationService(TestCase):
    def setUp(self):
        self.github_object = Github("AUTH_KEY")

    @patch("report.services.OrganizationService._request")
    def test_organization_service(self, org_service_mock):
        org = Organization("test")
        org_service_mock.return_value = org
        org_service = OrganizationService(self.github_object, "test").request()
        self.assertEqual(org_service_mock.call_count, 1)
        self.assertEqual(org_service.name, org.name)
        self.assertEqual(len(org_service.get_repos()), len(org.get_repos()))

    @patch("report.services.OrganizationService._is_limit_exceeded", return_value=True)
    @patch("report.services.OrganizationService._request")
    def test_organization_service_with_limit_exceeded(self, org_service_mock, _):
        with self.assertRaises(exceptions.RateLimitException) as error:
            OrganizationService(self.github_object, "test").request()
            self.assertEqual(
                error.exception.message, "You exceed the rate limit Github API"
            )
        self.assertEqual(org_service_mock.call_count, 0)

    @patch("report.services.OrganizationService._request")
    def test_organization_service_with_unknown_exception(self, org_service_mock):
        org_service_mock.side_effect = GithubException(
            status=404, data={"message": "Not Found"}, headers={""}
        )
        with self.assertRaises(exceptions.OrganizationServiceException) as error:
            OrganizationService(self.github_object, "test").request()
            self.assertEqual(error.exception.message, "Not Found")
            self.assertEqual(error.exception.status_code, 404)


class TestContributorService(TestCase):
    def setUp(self):
        self.github_object = Github("AUTH_KEY")

    @patch("report.services.ContributorService._request")
    def test_contributors_service(self, contributor_service_mock):
        repo = Repository()
        contributor_service_mock.return_value = repo
        contributor_service = ContributorService(self.github_object, repo).request()
        self.assertEqual(contributor_service_mock.call_count, 1)
        self.assertEqual(
            len(contributor_service.get_contributors()), len(repo.get_contributors())
        )

    @patch("report.services.ContributorService._is_limit_exceeded", return_value=True)
    @patch("report.services.ContributorService._request")
    def test_contributors_service_with_limit_exceeded(
        self, contributor_service_mock, _
    ):
        repo = Repository()
        with self.assertRaises(exceptions.RateLimitException) as error:
            ContributorService(self.github_object, repo).request()
            self.assertEqual(
                error.exception.message, "You exceed the rate limit Github API"
            )

        self.assertEqual(contributor_service_mock.call_count, 0)

    @patch("report.services.ContributorService._request")
    def test_contributors_service_with_limit_exceeded_with_unknown_exception(
        self, contributor_service_mock
    ):
        repo = Repository()
        contributor_service_mock.side_effect = GithubException(
            status=404, data={"message": "Not Found"}, headers={""}
        )
        with self.assertRaises(exceptions.ContributorServiceException) as error:
            ContributorService(self.github_object, repo).request()
            self.assertEqual(error.exception.message, "Not Found")
            self.assertEqual(error.exception.status_code, 404)


class TestLanguageService(TestCase):
    def setUp(self):
        self.github_object = Github("AUTH_KEY")

    @patch("report.services.LanguageService._request")
    def test_languages_service(self, language_service_mock):
        repo = Repository()
        language_service_mock.return_value = repo
        contributor_service = LanguageService(self.github_object, repo).request()
        self.assertEqual(language_service_mock.call_count, 1)
        self.assertEqual(
            len(contributor_service.get_languages()), len(repo.get_languages())
        )

    @patch("report.services.LanguageService._is_limit_exceeded", return_value=True)
    @patch("report.services.LanguageService._request")
    def test_languages_service_with_limit_exceeded(self, language_service_mock, _):
        repo = Repository()
        with self.assertRaises(exceptions.RateLimitException) as error:
            LanguageService(self.github_object, repo).request()
            self.assertEqual(
                error.exception.message, "You exceed the rate limit Github API"
            )

        self.assertEqual(language_service_mock.call_count, 0)

    @patch("report.services.LanguageService._request")
    def test_languages_service_with_limit_exceeded_with_unknown_exception(
        self, language_service_mock
    ):
        repo = Repository()
        language_service_mock.side_effect = GithubException(
            status=404, data={"message": "Not Found"}, headers={""}
        )
        with self.assertRaises(exceptions.LanguageServiceException) as error:
            LanguageService(self.github_object, repo).request()
            self.assertEqual(error.exception.message, "Not Found")
            self.assertEqual(error.exception.status_code, 404)
