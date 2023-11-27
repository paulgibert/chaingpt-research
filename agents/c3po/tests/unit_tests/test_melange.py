from c3po.melange import _build_step_to_prompt


def test__build_step_to_prompt__simple():
    yaml_str = """
    test_step:
        description: Sample description
        fields:
            field1:
                description: field1 description
            field2:
                description: field2 description
                required: false
            field3:
                description: field3 description
                required: true
    """

    prompt = _build_step_to_prompt(yaml_str)
    assert prompt == """

    """