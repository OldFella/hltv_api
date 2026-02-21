from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.frontend import app
from starlette.responses import HTMLResponse

client = TestClient(app)

MOCK_FANTASY_MAP = {1: "Fantasy 2024", 2: "Fantasy 2023"}
MOCK_FOLDER_IDS = [2, 1]
MOCK_SHEETS = {
    "Sheet1": {
        "columns": ["player", "score"],
        "rows": [["s1mple", 100]]
    }
}


# ---------------------------------------------------------------------------
# GET /spreadsheet/
# ---------------------------------------------------------------------------

@patch("src.routers.spreadsheets.templates.TemplateResponse")
@patch("src.routers.spreadsheets._get_fantasy_map", return_value=MOCK_FANTASY_MAP)
@patch("src.routers.spreadsheets._get_sorted_fantasy_ids", return_value=MOCK_FOLDER_IDS)
class TestShowFolders:
    def setup_method(self, method):
        self.html_response = HTMLResponse(content="<html></html>", status_code=200)

    def test_returns_200(self, mock_ids, mock_map, mock_template):
        mock_template.return_value = self.html_response
        assert client.get("/spreadsheet/").status_code == 200

    def test_calls_fantasy_map(self, mock_ids, mock_map, mock_template):
        mock_template.return_value = self.html_response
        client.get("/spreadsheet/")
        assert mock_map.called

    def test_calls_sorted_ids(self, mock_ids, mock_map, mock_template):
        mock_template.return_value = self.html_response
        client.get("/spreadsheet/")
        assert mock_ids.called

    def test_renders_correct_template(self, mock_ids, mock_map, mock_template):
        mock_template.return_value = self.html_response
        client.get("/spreadsheet/")
        assert mock_template.call_args[0][0] == "fantasies.html"

    def test_passes_folders_to_template(self, mock_ids, mock_map, mock_template):
        mock_template.return_value = self.html_response
        client.get("/spreadsheet/")
        context = mock_template.call_args[0][1]
        assert "folders" in context


# ---------------------------------------------------------------------------
# GET /spreadsheet/{fantasyid}
# ---------------------------------------------------------------------------

@patch("src.routers.spreadsheets.templates.TemplateResponse")
@patch("src.routers.spreadsheets._parse_ods", return_value=(MOCK_SHEETS, []))
@patch("src.routers.spreadsheets._get_fantasy_map", return_value=MOCK_FANTASY_MAP)
@patch("src.routers.spreadsheets._get_sorted_fantasy_ids", return_value=MOCK_FOLDER_IDS)
@patch("src.routers.spreadsheets.Path.exists", return_value=True)
class TestDisplaySpreadsheet:
    def test_returns_200(self, mock_exists, mock_ids, mock_map, mock_ods, mock_template):
        mock_template.return_value = HTMLResponse(content="<html></html>", status_code=200)
        assert client.get("/spreadsheet/1").status_code == 200

    def test_renders_correct_template(self, mock_exists, mock_ids, mock_map, mock_ods, mock_template):
        mock_template.return_value = HTMLResponse(content="<html></html>", status_code=200)
        client.get("/spreadsheet/1")
        assert mock_template.call_args[0][0] == "table.html"

    def test_passes_correct_context(self, mock_exists, mock_ids, mock_map, mock_ods, mock_template):
        mock_template.return_value = HTMLResponse(content="<html></html>", status_code=200)
        client.get("/spreadsheet/1")
        context = mock_template.call_args[0][1]
        assert all(k in context for k in ["fantasyid", "fantasy_name", "fantasies", "sheets"])

    def test_calls_parse_ods(self, mock_exists, mock_ids, mock_map, mock_ods, mock_template):
        mock_template.return_value = HTMLResponse(content="<html></html>", status_code=200)
        client.get("/spreadsheet/1")
        assert mock_ods.called


@patch("routers.spreadsheets.Path.exists", return_value=False)
class TestDisplaySpreadsheetNotFound:
    def test_not_found(self, mock_exists):
        assert client.get("/spreadsheet/999999").status_code == 404