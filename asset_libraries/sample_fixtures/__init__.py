import os

LIBRARY_TYPE = 'FIXTURES'
FIXTURES_LIBRARY_PATH = os.path.join(os.path.dirname(__file__),'library',"Sample Fixtures")

FIXTURES = {"library_name": "Sample Fixtures",
            "library_type": "FIXTURES",
            "library_path": FIXTURES_LIBRARY_PATH}
            
LIBRARIES = [FIXTURES]

def register():
    pass