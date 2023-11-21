import pytest
from c3po.llm.repo_license import repo_license_from_llm


def test__repo_license_from_llm__enough_info():
    """
    Checks that the correct license is returned
    for a known repository provided detailed content.
    """
    content = "Grype uses the Apache2.0 license."
    response = repo_license_from_llm("grype", "0.72.0", content)
    assert response.output == "apache2.0"


@pytest.mark.repeat(3)
def test__repo_license_from_llm__not_enough_info_on_known_project():
    """
    Checks that the correct license is returned
    for a known repository even when not provided enough content.

    Repeat 3 times. The LLM's response is a little stochastic.
    """
    # TODO: Add this feature
    pass
    # content = """
    # In the heart of a bustling city, a small, unassuming coffee shop sat tucked between
    # towering skyscrapers. Its walls, adorned with vintage posters and local artwork,
    # radiated a warm, welcoming glow. Inside, a symphony of aromas — rich espresso,
    # cinnamon, and freshly baked pastries — filled the air, enticing passersby. 
    # """
    # response = repo_license_from_llm("grype", "0.72.0", content)
    # assert response.output == "apache-2.0"


def test__repo_license_from_llm__not_enough_info_on_unknown_project():
    """
    Checks that no license is returned
    for a unknown repository when not provided enough content.
    """
    content = """
    In the heart of a bustling city, a small, unassuming coffee shop sat tucked between
    towering skyscrapers. Its walls, adorned with vintage posters and local artwork,
    radiated a warm, welcoming glow. Inside, a symphony of aromas — rich espresso,
    cinnamon, and freshly baked pastries — filled the air, enticing passersby. 
    """
    response = repo_license_from_llm("yogoboga", "0.1.2", content)
    assert response.output is None
