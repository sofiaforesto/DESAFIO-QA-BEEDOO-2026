import pytest
from playwright.sync_api import sync_playwright

BASE_URL = "https://creative-sherbet-a51eac.netlify.app"

@pytest.fixture(scope="module")
def playwright_module():
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="function")
def page(playwright_module):
    browser = playwright_module.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    # Limpa localStorage antes de cada teste
    page.goto(BASE_URL, wait_until="networkidle")
    page.evaluate("() => localStorage.clear()")
    yield page
    browser.close()

def fill_form(page, data: dict):
    """Preenche o formulário de cadastro usando eventos nativos (compatível com Vue/Quasar)"""
    import time

    def trigger_input(selector, value):
        page.evaluate(f"""() => {{
            const inputs = document.querySelectorAll('{selector}');
            const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value');
            inputs.forEach(el => {{
                if (setter) setter.set.call(el, `{value}`);
                else el.value = `{value}`;
                el.dispatchEvent(new Event('input', {{bubbles: true}}));
            }});
        }}""")

    if "name" in data:
        page.evaluate(f"""() => {{
            const el = document.querySelectorAll('input[type="text"]')[0];
            if (!el) return;
            const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value');
            if (setter) setter.set.call(el, `{data["name"]}`);
            el.dispatchEvent(new Event('input', {{bubbles: true}}));
        }}""")
    if "description" in data:
        page.evaluate(f"""() => {{
            const el = document.querySelector('textarea');
            if (!el) return;
            const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value');
            if (setter) setter.set.call(el, `{data["description"]}`);
            el.dispatchEvent(new Event('input', {{bubbles: true}}));
        }}""")
    if "instructor" in data:
        page.evaluate(f"""() => {{
            const el = document.querySelectorAll('input[type="text"]')[1];
            if (!el) return;
            const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value');
            if (setter) setter.set.call(el, `{data["instructor"]}`);
            el.dispatchEvent(new Event('input', {{bubbles: true}}));
        }}""")
    if "cover" in data:
        page.evaluate(f"""() => {{
            const el = document.querySelectorAll('input[type="text"]')[2];
            if (!el) return;
            const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value');
            if (setter) setter.set.call(el, `{data["cover"]}`);
            el.dispatchEvent(new Event('input', {{bubbles: true}}));
        }}""")
    if "start_date" in data:
        page.evaluate(f"""() => {{
            const el = document.querySelectorAll('input[type="date"]')[0];
            if (!el) return;
            const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value');
            if (setter) setter.set.call(el, '{data["start_date"]}');
            el.dispatchEvent(new Event('input', {{bubbles: true}}));
        }}""")
    if "end_date" in data:
        page.evaluate(f"""() => {{
            const el = document.querySelectorAll('input[type="date"]')[1];
            if (!el) return;
            const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value');
            if (setter) setter.set.call(el, '{data["end_date"]}');
            el.dispatchEvent(new Event('input', {{bubbles: true}}));
        }}""")
    if "vagas" in data:
        page.evaluate(f"""() => {{
            const el = document.querySelector('input[type="number"]');
            if (!el) return;
            const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value');
            if (setter) setter.set.call(el, '{data["vagas"]}');
            el.dispatchEvent(new Event('input', {{bubbles: true}}));
        }}""")
    if "tipo" in data:
        page.locator(".q-select").last.click()
        time.sleep(0.8)
        tipo = data["tipo"].lower()
        if tipo == "online":
            page.locator(".q-menu .q-item").nth(2).click()
        elif tipo == "presencial":
            page.locator(".q-menu .q-item").nth(1).click()
        time.sleep(0.3)
