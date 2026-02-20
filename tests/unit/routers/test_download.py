from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
from starlette.responses import Response
from src.frontend import app

client = TestClient(app)


@patch("routers.download.FileResponse")
@patch("routers.download.Path.is_file", return_value=True)
@patch("routers.download.Path.exists", return_value=True)
class TestDownloadFile:
    def setup_method(self, method):
        self.mock_response = Response(content=b"", status_code=200)

    def test_returns_200(self, mock_exists, mock_is_file, mock_fr):
        mock_fr.return_value = self.mock_response
        assert client.get("/download/test.zip").status_code == 200

    def test_calls_file_response(self, mock_exists, mock_is_file, mock_fr):
        mock_fr.return_value = self.mock_response
        client.get("/download/test.zip")
        assert mock_fr.called

    def test_passes_correct_filename(self, mock_exists, mock_is_file, mock_fr):
        mock_fr.return_value = self.mock_response
        client.get("/download/test.zip")
        assert mock_fr.call_args[1]["filename"] == "test.zip"


@patch("src.routers.download.Path.is_file", return_value=False)
@patch("src.routers.download.Path.exists", return_value=False)
class TestDownloadFileNotFound:
    def test_not_found(self, mock_exists, mock_is_file):
        assert client.get("/download/nonexistent.zip").status_code == 404

    def test_file_exists_but_not_file(self, mock_exists, mock_is_file):
        mock_exists.return_value = True
        mock_is_file.return_value = False
        assert client.get("/download/notafile").status_code == 404