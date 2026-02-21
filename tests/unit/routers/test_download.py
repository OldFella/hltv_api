from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
from starlette.responses import Response
from src.frontend import app

client = TestClient(app)


import tempfile
import os

class TestDownloadFile:
    def setup_method(self, method):
        os.makedirs("static/downloads", exist_ok=True)
        with open("static/downloads/test.zip", "wb") as f:
            f.write(b"test content")

    def teardown_method(self, method):
        os.remove("static/downloads/test.zip")

    def test_returns_200(self):
        assert client.get("/download/test.zip").status_code == 200

    def test_passes_correct_filename(self):
        response = client.get("/download/test.zip")
        assert "test.zip" in response.headers["content-disposition"]


@patch("src.routers.download.Path.is_file", return_value=False)
@patch("src.routers.download.Path.exists", return_value=False)
class TestDownloadFileNotFound:
    def test_not_found(self, mock_exists, mock_is_file):
        assert client.get("/download/nonexistent.zip").status_code == 404

    def test_file_exists_but_not_file(self, mock_exists, mock_is_file):
        mock_exists.return_value = True
        mock_is_file.return_value = False
        assert client.get("/download/notafile").status_code == 404