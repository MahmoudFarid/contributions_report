class BaseException(Exception):
    def __init__(self, message="", status_code=""):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class OrganizationServiceException(BaseException):
    pass


class ContributorServiceException(BaseException):
    pass


class LanguageServiceException(BaseException):
    pass
