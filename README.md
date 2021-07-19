# Generate Contributions CSV Report for Github Organization.

How to Run
----------

In the beginning we need to create a virtual environment and install the requirements

    $ pip install -r equirements.txt

Then we need to call the entrypoint with some args:

    $ python report.py --organization (ORGANIZATION_NAME) --auth-key (GITHUB_ACCESS_TOKEN) --file-path (PATH_OF_THE_REPORT)

Args:
* --organization (REQUIRED)
* --auth-key (REQUIRED)
* --file-path (OPTIONAL: Default is /tmp/)

Unit tests
----------

I added unit tests for the most of the application (not fully covered), all tests in the folder tests and splits into multiple files.
All tests related with services will be in `test_services.py`
All tests related with parsers will be in `test_parsers.py`
All mocked objects that used in tests will be in `objects.py`

To run unit tests, just run:

    $ python -m unittest discover

