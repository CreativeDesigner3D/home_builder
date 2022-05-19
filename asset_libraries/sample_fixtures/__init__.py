import os
from . import drop_ops_fixtures
LIBRARY_TYPE = 'FIXTURES'
FIXTURES_LIBRARY_PATH = os.path.join(os.path.dirname(__file__),'library',"Sample Fixtures")

FIXTURES = {"library_name": "Sample Fixtures",
            "library_type": "FIXTURES",
            "library_path": FIXTURES_LIBRARY_PATH,
            "libary_drop_id": "hb_sample_fixtures.drop_fixture"}
            
LIBRARIES = [FIXTURES]

def register():
    drop_ops_fixtures.register()