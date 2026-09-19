from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).parents[1] / "app.py"


def test_demo_renders_and_filters():
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    assert not app.exception
    assert app.metric[0].value == "360"
    app.selectbox(key="group").set_value(1).run()
    assert not app.exception
    assert app.metric[0].value == "90"
    app.selectbox(key="label").set_value(0).run()
    assert not app.exception
    assert app.metric[0].value == "33"
    assert app.metric[1].value == "0.0%"


def test_upload_waits_for_both_files():
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    app.radio(key="source").set_value("Upload my data").run()
    assert not app.exception
    assert any("Add both" in message.value for message in app.info)


def test_chart_controls_and_thresholds_render():
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    assert not app.exception
    app.slider(key="chart_height").set_value(600).run()
    assert not app.exception
    app.slider(key="threshold").set_value(100).run()
    assert not app.exception
    app.button(key="expand_distribution").click().run()
    assert not app.exception
