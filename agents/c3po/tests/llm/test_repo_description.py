from c3po.llm.repo_description import repo_description_from_llm


def test__repo_description_from_llm__enough_info():
    """
    Checks that a sufficiently long description is returned
    for a known repository with detailed provided content.
    """
    content = """
    A vulnerability scanner for container images and filesystems. Easily install the binary to try it out. Works with Syft, the powerful SBOM (software bill of materials) tool for container images and filesystems.
    Join our community meetings!

    Calendar: https://calendar.google.com/calendar/u/0/r?cid=Y182OTM4dGt0MjRtajI0NnNzOThiaGtnM29qNEBncm91cC5jYWxlbmRhci5nb29nbGUuY29t
    Agenda: https://docs.google.com/document/d/1ZtSAa6fj2a6KRWviTn3WoJm09edvrNUp4Iz_dOjjyY8/edit?usp=sharing (join this group for write access)
    All are welcome!
    """
    response = repo_description_from_llm("grype", "0.72.0", content)
    assert response.output is not None
    assert len(response.output) > 16 # Ensure that the output is long.


def test__repo_description_from_llm__not_enough_info_on_known_project():
    """
    Checks that a sufficiently long description is returned
    for a known repository even if the content does not contain
    enough relevant details about the project.
    """
    content = """
    In the heart of a bustling city, a small, unassuming coffee shop sat tucked between
    towering skyscrapers. Its walls, adorned with vintage posters and local artwork,
    radiated a warm, welcoming glow. Inside, a symphony of aromas — rich espresso,
    cinnamon, and freshly baked pastries — filled the air, enticing passersby. 
    """
    response = repo_description_from_llm("grype", "0.72.0", content)
    assert response.output is not None
    assert len(response.output) > 16 # Ensure that the output is long.


def test__repo_description_from_llm__not_enough_info_on_unknown_project():
    """
    Checks that not description is returned for an unknown project
    with no relevant details provided.
    """
    content = """
    In the heart of a bustling city, a small, unassuming coffee shop sat tucked between
    towering skyscrapers. Its walls, adorned with vintage posters and local artwork,
    radiated a warm, welcoming glow. Inside, a symphony of aromas — rich espresso,
    cinnamon, and freshly baked pastries — filled the air, enticing passersby. 
    """
    response = repo_description_from_llm("yogoboga", "0.1.2", content)
    assert response.output is None
