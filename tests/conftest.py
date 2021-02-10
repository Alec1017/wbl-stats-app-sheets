import pytest

from app import create_app
from config import Test


@pytest.fixture
def test_app(scope='module'):
    """
    Creates a test application instance
    """
    return create_app(Test)