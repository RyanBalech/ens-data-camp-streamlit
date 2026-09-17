from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).parents[1] / "app.py"


def test_demo_renders_and_filters():
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    assert not app.exception
    assert app.metric[0].value == "6"
    app.selectbox(key="group").set_value(1).run()
    assert not app.exception
    assert app.metric[0].value == "3"
    app.selectbox(key="label").set_value(0).run()
    assert not app.exception
    assert app.metric[0].value == "1"
    assert app.metric[1].value == "0.0%"


def test_upload_waits_for_both_files():
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    app.radio(key="source").set_value("Upload my data").run()
    assert not app.exception
    assert "Add both" in app.info[0].value
