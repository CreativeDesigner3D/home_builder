import os
from . import drop_ops_fixtures
LIBRARY_TYPE = 'FIXTURES'
FIXTURES_LIBRARY_PATH = os.path.join(os.path.dirname(__file__),'library',"Bathroom Fixtures")

FIXTURES = {"library_name": "Bathroom Fixtures",
            "library_type": "PRODUCTS",
            "library_path": FIXTURES_LIBRARY_PATH,
            "libary_drop_id": "hb_sample_fixtures.drop_fixture"}
            
LIBRARIES = [FIXTURES]

def register():
    drop_ops_fixtures.register()