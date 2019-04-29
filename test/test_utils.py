import pytest
import shutil
from pyggi.utils import get_file_extension

class TestUtils(object):

    def test_get_file_extension(self):
        python_file = "./example.py"
        java_file = "../example.java"
        c_file = "../../example.c"

        assert get_file_extension(python_file) == '.py'
        assert get_file_extension(java_file) == '.java'
        assert get_file_extension(c_file) == '.c'

@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    def remove_test_dir():
        shutil.rmtree('.pyggi')
    request.addfinalizer(remove_test_dir)