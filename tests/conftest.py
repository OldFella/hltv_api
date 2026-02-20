import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, '/root/hltv_api')

mock_engine = MagicMock()
mock_conn = MagicMock()
mock_conn.execute.return_value.mappings.return_value.all.return_value = []
mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)

with patch('sqlalchemy.create_engine', return_value=mock_engine):
    with patch('sqlalchemy.schema.MetaData.create_all', return_value=None):
        from src.main import app

from fastapi.testclient import TestClient


@pytest.fixture
def client():
    return TestClient(app)