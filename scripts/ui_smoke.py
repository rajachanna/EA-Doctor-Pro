"""Optional visual+behavior smoke test. Requires: pip install playwright

Uses a local browser and synthetic sample data only.
"""
from pathlib import Path
from os import environ
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
html=(root/"web/index.html").as_uri()
assets=root/"docs/assets"
assets.mkdir(parents=True,exist_ok=True)

with sync_playwright() as p:
    launch={"headless": True, "args": ["--no-sandbox"]}
    if environ.get("CHROMIUM_EXECUTABLE"):
        launch["executable_path"]=environ["CHROMIUM_EXECUTABLE"]
    browser=p.chromium.launch(**launch)
    for name,width,height,output in (
        ("desktop",1440,1050,"ea-doctor-desktop.webp"),
        ("mobile",390,845,"ea-doctor-mobile.webp"),
    ):
        page=browser.new_page(viewport={"width":width,"height":height},device_scale_factor=1)
        errors=[]
        page.on("pageerror",lambda e:errors.append(str(e)))
        page.goto(html,wait_until="load")
        page.locator("#load-sample").click()
        page.locator("#run-scan").click()
        assert page.locator(".finding").count()==4,page.locator(".finding").all_text_contents()
        assert "MT10016" in page.locator("#finding-list").inner_text()
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth+1"),"horizontal overflow"
        if name=="desktop":
            page.locator('[data-mode="source"]').click()
            page.locator("#load-sample").click()
            page.locator("#run-scan").click()
            assert page.locator(".finding").count()>=3
            page.locator('[data-mode="trades"]').click()
            page.locator("#load-sample").click()
            page.locator("#run-scan").click()
            assert page.locator("#result-metrics .metric").count()==8
            assert "Small trade sample" in page.locator("#finding-list").inner_text()
            page.locator('[data-mode="journal"]').click()
            page.locator("#load-sample").click()
            page.locator("#run-scan").click()
        assert not errors,errors
        page.screenshot(path=str(assets/output),full_page=True,type="webp",quality=76)
        print(name,"PASS: journal, UI rendering, responsive width",output,flush=True)
        page.close()
    browser.close()
