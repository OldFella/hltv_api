from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from sqlalchemy import select
import pytest

from src.repositories.base import execute_query, add_fuzzy_filter


# ---------------------------------------------------------------------------
# execute_query
# ---------------------------------------------------------------------------

class TestExecuteQuery:
    def test_returns_rows_when_many_true(self):
        mock_rows = [{"id": 1, "name": "s1mple"}]
        with patch("src.repositories.base.engine") as mock_engine:
            mock_conn = MagicMock()
            mock_conn.execute.return_value.mappings.return_value.all.return_value = mock_rows
            mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
            mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)

            result = execute_query(MagicMock())
            assert result == mock_rows

    def test_returns_first_row_when_many_false(self):
        mock_rows = [{"id": 1, "name": "s1mple"}]
        with patch("src.repositories.base.engine") as mock_engine:
            mock_conn = MagicMock()
            mock_conn.execute.return_value.mappings.return_value.all.return_value = mock_rows
            mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
            mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)

            result = execute_query(MagicMock(), many=False)
            assert result == mock_rows[0]

    def test_raises_404_when_empty(self):
        with patch("src.repositories.base.engine") as mock_engine:
            mock_conn = MagicMock()
            mock_conn.execute.return_value.mappings.return_value.all.return_value = []
            mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
            mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)

            with pytest.raises(HTTPException) as exc:
                execute_query(MagicMock())
            assert exc.value.status_code == 404

    def test_raises_404_when_empty_many_false(self):
        with patch("src.repositories.base.engine") as mock_engine:
            mock_conn = MagicMock()
            mock_conn.execute.return_value.mappings.return_value.all.return_value = []
            mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
            mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)

            with pytest.raises(HTTPException) as exc:
                execute_query(MagicMock(), many=False)
            assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# add_fuzzy_filter
# ---------------------------------------------------------------------------

class TestAddFuzzyFilter:
    def test_does_nothing_when_value_is_none(self):
        filters, order_bys = [], []
        add_fuzzy_filter(MagicMock(), None, filters, order_bys)
        assert filters == []
        assert order_bys == []

    def test_does_nothing_when_value_is_empty_string(self):
        filters, order_bys = [], []
        add_fuzzy_filter(MagicMock(), "", filters, order_bys)
        assert filters == []
        assert order_bys == []

    def test_appends_filter_when_value_provided(self):
        filters, order_bys = [], []
        add_fuzzy_filter(MagicMock(), "s1mple", filters, order_bys)
        assert len(filters) == 1

    def test_appends_order_by_when_value_provided(self):
        filters, order_bys = [], []
        add_fuzzy_filter(MagicMock(), "s1mple", filters, order_bys)
        assert len(order_bys) == 1

    def test_appends_both_filter_and_order_by(self):
        filters, order_bys = [], []
        add_fuzzy_filter(MagicMock(), "s1mple", filters, order_bys)
        assert len(filters) == 1 and len(order_bys) == 1