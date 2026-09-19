"""End-to-end checks against a running app; optional real-data upload."""
import argparse
import json
import time
from urllib.request import urlopen
from urllib.error import URLError
from pathlib import Path

from playwright.sync_api import sync_playwright, expect

parser = argparse.ArgumentParser()
parser.add_argument("--url", default="http://localhost:8501")
parser.add_argument("--data-dir", type=Path)
parser.add_argument("--channel", default=None, help="Use msedge on Windows, or installed Chromium by default")
args = parser.parse_args()
for attempt in range(60):
    try:
        with urlopen(args.url + "/_stcore/health", timeout=2) as response:
            if response.status == 200:
                break
    except (URLError, TimeoutError):
        pass
    time.sleep(0.5)
else:
    raise RuntimeError("App did not become healthy within the startup window.")
out = Path("artifacts/e2e")
out.mkdir(parents=True, exist_ok=True)


def metric(page, label):
    return page.locator('[data-testid="stMetric"]').filter(has_text=label).locator('[data-testid="stMetricValue"]')


def check_visible_figures(page, name):
    """Catch marks that exist in the DOM but are hidden by zero-area SVG clips."""
    charts = page.locator('[data-testid="stVegaLiteChart"]:visible')
    assert charts.count() > 0, name
    for index in range(charts.count()):
        chart = charts.nth(index)
        chart.scroll_into_view_if_needed()
        expect(chart.locator('svg.marks')).to_be_visible()
        empty_clips = chart.locator('clipPath rect').evaluate_all(
            '(elements) => elements.filter(e => +e.getAttribute("width") <= 0 || +e.getAttribute("height") <= 0).map(e => e.outerHTML)'
        )
        assert not empty_clips, (name, index, empty_clips)
        marks = chart.locator('.role-mark path, .role-mark rect, .role-mark text')
        assert marks.evaluate_all('(elements) => elements.some(e => {const b=e.getBoundingClientRect(); return b.width > 1 && b.height > 1;})'), (name, index, "No rendered data marks")
        chart.screenshot(path=str(out / f"{name}-{index}.png"))


with sync_playwright() as p:
    browser = p.chromium.launch(channel=args.channel)
    page = browser.new_page(viewport={"width": 1440, "height": 1100})
    page.set_default_timeout(60000)
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(args.url)
    expand = page.get_by_role("button", name="Expand chart", exact=True).first
    expand.wait_for()
    expect(metric(page, "OBSERVATIONS")).to_have_text("360")
    expect(page.get_by_text("Start here · a two-minute tour", exact=True)).to_be_visible()
    check_visible_figures(page, "overview")
    expand.click()
    dialog = page.get_by_role("dialog")
    expect(dialog).to_be_visible()
    expect(dialog.get_by_text("Next-day return distribution", exact=True)).to_be_visible()
    assert dialog.locator('[data-testid="stVegaLiteChart"]').bounding_box()["height"] >= 550
    page.keyboard.press("Escape")
    expect(dialog).not_to_be_visible()
    page.wait_for_timeout(600)
    chart = page.locator('[data-testid="stVegaLiteChart"]').first
    chart.hover()
    page.get_by_role("button", name="Fullscreen", exact=True).first.click()
    page.wait_for_timeout(500)
    fullscreen = page.locator('[data-testid="stVegaLiteChart"]').first.bounding_box()
    assert fullscreen["width"] > 1100 and fullscreen["height"] > 700, fullscreen
    page.screenshot(path=str(out / "fullscreen.png"))
    # Fullscreen control toggles without changing the selected cohort.
    page.get_by_role("button", name="Close fullscreen", exact=True).click()
    expect(chart).to_be_visible()
    print("Dialog and native fullscreen dimensions passed.", flush=True)
    slider = page.locator('input[type="range"][aria-label="Chart height"]')
    slider.focus()
    slider.press("End")
    page.wait_for_timeout(900)
    assert chart.bounding_box()["height"] >= 680
    # Scroll zoom, pan and reset should not crash or invalidate the figure.
    chart.hover()
    page.mouse.wheel(0, -200)
    page.mouse.down()
    page.mouse.move(750, 650, steps=5)
    page.mouse.up()
    chart.dblclick()
    with page.expect_download() as downloaded:
        page.get_by_role("button", name="Export figure · JSON", exact=True).first.click()
    target = out / "figure.json"
    downloaded.value.save_as(target)
    assert "$schema" in json.loads(target.read_text())
    chart.hover()
    with page.expect_download() as downloaded:
        page.get_by_role("button", name="Download as PNG", exact=True).first.click()
    target = out / "figure.png"
    downloaded.value.save_as(target)
    assert target.read_bytes().startswith(b"\x89PNG")
    print("Expansion, native fullscreen, resizing, zoom and figure exports passed.", flush=True)

    page.get_by_role("tab", name="Model Lab", exact=True).click()
    expect(page.get_by_text("Evidence, before confidence.", exact=True)).to_be_visible()
    check_visible_figures(page, "validation")
    page.get_by_role("tab", name="Threshold lab", exact=True).click()
    threshold = page.locator('input[type="range"][aria-label="Positive-return probability threshold"]')
    threshold.focus()
    threshold.press("End")
    expect(metric(page, "PREDICTED POSITIVE")).to_have_text("0.0%")
    threshold.focus()
    threshold.press("Home")
    expect(metric(page, "PREDICTED POSITIVE")).to_have_text("100.0%")
    check_visible_figures(page, "threshold")
    page.screenshot(path=str(out / "threshold.png"))
    page.get_by_role("tab", name="Feature importance", exact=True).click()
    check_visible_figures(page, "importance")
    with page.expect_download() as downloaded:
        page.get_by_role("button", name="Download feature importance", exact=True).click()
    downloaded.value.save_as(out / "importance.csv")
    page.get_by_role("tab", name="Model card", exact=True).click()
    expect(page.get_by_text("Evaluation contract", exact=True)).to_be_visible()
    print("Model comparison, thresholds, importance download and model card passed.", flush=True)
    page.get_by_role("tab", name="Historical signals", exact=True).click()
    check_visible_figures(page, "demo-history")
    page.get_by_role("tab", name="Data explorer", exact=True).click()
    with page.expect_download() as downloaded:
        page.get_by_role("button", name="Download this preview · CSV", exact=True).click()
    downloaded.value.save_as(out / "preview.csv")
    assert len((out / "preview.csv").read_text().splitlines()) == 361

    if args.data_dir:
        page.get_by_text("Upload my data", exact=True).click()
        page.locator('input[type="file"]').nth(0).set_input_files(str(args.data_dir / "X_train_9xQjqvZ.csv"), timeout=120000)
        page.locator('input[type="file"]').nth(1).set_input_files(str(args.data_dir / "y_train_Ppwhaz8.csv"), timeout=120000)
        expect(metric(page, "OBSERVATIONS")).to_have_text("527,073", timeout=120000)
        page.get_by_role("tab", name="Overview", exact=True).click()
        check_visible_figures(page, "uploaded-overview")
        page.get_by_role("tab", name="Historical signals", exact=True).click()
        expect(page.get_by_text("One observation. Twenty days of context.", exact=True)).to_be_visible()
        observation = page.get_by_role("spinbutton")
        observation.fill("2")
        observation.press("Enter")
        with page.expect_download() as downloaded:
            page.get_by_role("button", name="Download this observation's features", exact=True).click()
        downloaded.value.save_as(out / "features.csv")
        assert "ewma_ret" in (out / "features.csv").read_text()
        check_visible_figures(page, "uploaded-history")
        page.screenshot(path=str(out / "feature-explorer.png"), full_page=True)
        print("Full upload and observation feature workflow passed.", flush=True)

    for width in [375, 768, 1024]:
        page.set_viewport_size({"width": width, "height": 1000})
        page.wait_for_timeout(300)
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    assert not errors, errors
    assert page.locator('[data-testid="stException"]').count() == 0
    browser.close()
    print("Browser checks complete.", flush=True)
