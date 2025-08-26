import re


def to_snake_case(name: str) -> str:
    # replace space and hyphen with underscore
    name = re.sub(r"[\s\-]+", "_", name)

    # handle camelcase
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)

    # collapse multiple underscores
    name = re.sub(r"_+", "_", name)

    # lowercase everything
    name = name.lower()

    return name


def test_to_snake_case():
    # Test cases
    tests = [
        "HelloWorld",  # simple CamelCase
        "User Name",  # space
        "User    Name",  # multiple spaces
        "already_snake_case",  # already snake
        "HTTPRequest",  # acronym
        "User-Name-Test",  # hyphens
        "XMLHttpRequest",  # mixed acronym + word
    ]

    for t in tests:
        print(f"{t} -> {to_snake_case(t)}")
