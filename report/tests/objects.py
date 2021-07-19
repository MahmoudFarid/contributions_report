class Rate:
    @property
    def raw_data(self):
        return {"limit": 5000, "used": 0, "remaining": 5000, "reset": 1626708493}


class RateLimit:
    @property
    def core(self):
        return Rate()


class NamedUser:
    @property
    def id(self):
        return 123456789

    @property
    def login(self):
        return "testuser"

    @property
    def name(self):
        return "Test User"

    @property
    def email(self):
        return "test@test.com"


class Repository:
    def get_contributors(self):
        return [NamedUser()]

    def get_languages(self):
        return {
            "Python": 120697,
            "HTML": 19396,
            "Shell": 8786,
            "CSS": 1420,
            "Makefile": 1234,
            "Dockerfile": 832,
            "JavaScript": 817,
        }


class Organization:
    def __init__(self, name, *args, **kwargs):
        self.name = name

    def get_repos(self):
        return [Repository()]


class Github:
    def __init__(self, token, *args, **kwargs):
        self.token = token

    def get_rate_limit(self):
        return RateLimit()

    def get_organization(self, name):
        return Organization()
