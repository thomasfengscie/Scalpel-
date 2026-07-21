from examples.example_project.hello import greet


def test_greet():
    assert greet("World") == "Hello, World!"
