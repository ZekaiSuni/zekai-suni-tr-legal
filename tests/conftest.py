"""Testler GERÇEK data/zekai.db yerine izole veritabanı kullanır (P0-1).
app.db import edilmeden ÖNCE env ayarlanmalı — bu yüzden conftest en üstte."""
import os

os.environ["ZEKAI_DB"] = os.path.join(os.path.dirname(__file__), "test-zekai.db")
