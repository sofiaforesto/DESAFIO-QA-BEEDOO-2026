"""
Testes automatizados — Desafio QA Beedoo 2026
Módulo: Cadastro e Listagem de Cursos
URL: https://creative-sherbet-a51eac.netlify.app/
Stack: Python + pytest + Playwright (Chromium headless)
"""

import json
import time
import pytest

BASE_URL = "https://creative-sherbet-a51eac.netlify.app"

# ─────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────

def go_to_form(page):
    page.goto(BASE_URL, wait_until="networkidle")
    page.click("a[href='/new-course']")
    time.sleep(1)

def fill_form(page, data: dict):
    from conftest import fill_form as _fill
    _fill(page, data)

def submit_form(page):
    page.locator("button.q-btn").filter(has_text="CADASTRAR").first.click()
    time.sleep(2)

def get_courses(page):
    raw = page.evaluate("() => localStorage.getItem('@beedoo-qa-tests/courses')")
    return json.loads(raw) if raw else []

VALID_DATA = {
    "name": "Curso Python Avancado",
    "description": "Aprenda Python do zero ao avancado com projetos praticos",
    "instructor": "Prof Joao Silva",
    "cover": "https://picsum.photos/300/200",
    "start_date": "2026-04-01",
    "end_date": "2026-06-30",
    "vagas": "50",
    "tipo": "online",
}

# ─────────────────────────────────────────────────────────
# CT01/CT02 — Cadastro Válido
# ─────────────────────────────────────────────────────────

class TestCadastroCurso:

    def test_cadastro_valido_online(self, page):
        """CT01 — Cadastrar curso válido tipo Online deve salvar e redirecionar para lista"""
        go_to_form(page)
        fill_form(page, VALID_DATA)
        submit_form(page)

        assert page.url == f"{BASE_URL}/", f"Não redirecionou para a lista. URL: {page.url}"
        courses = get_courses(page)
        assert len(courses) == 1, f"Esperado 1 curso, encontrado {len(courses)}"
        assert courses[0]["name"] == "Curso Python Avancado"
        assert courses[0]["type"]["value"] == "online"

    def test_cadastro_valido_presencial(self, page):
        """CT02 — Cadastrar curso válido tipo Presencial deve salvar corretamente"""
        go_to_form(page)
        data = {**VALID_DATA, "tipo": "presencial"}
        fill_form(page, data)
        submit_form(page)

        courses = get_courses(page)
        assert len(courses) == 1
        assert courses[0]["type"]["value"] == "presencial"

    def test_campos_condicionais_online(self, page):
        """CT04a — Tipo Online deve exibir campo 'Link de inscrição'"""
        go_to_form(page)
        fill_form(page, {"tipo": "online"})
        time.sleep(0.5)

        link_field = page.locator(".q-field__label:has-text('Link')").count()
        end_field = page.locator(".q-field__label:has-text('Endere')").count()

        assert link_field > 0, "Campo 'Link de inscrição' deveria aparecer para tipo Online"
        assert end_field == 0, "Campo 'Endereço' NÃO deveria aparecer para tipo Online"

    def test_campos_condicionais_presencial(self, page):
        """CT04b — Tipo Presencial deve exibir campo 'Endereço'"""
        go_to_form(page)
        fill_form(page, {"tipo": "presencial"})
        time.sleep(0.5)

        link_field = page.locator(".q-field__label:has-text('Link')").count()
        end_field = page.locator(".q-field__label:has-text('Endere')").count()

        assert end_field > 0, "Campo 'Endereço' deveria aparecer para tipo Presencial"
        assert link_field == 0, "Campo 'Link' NÃO deveria aparecer para tipo Presencial"

    # ── Testes Negativos (BUGs esperados) ──

    def test_validacao_campos_obrigatorios(self, page):
        """CT05 — BUG-01: Submeter formulário vazio NÃO deve salvar dados"""
        go_to_form(page)
        # Não preenche nenhum campo
        submit_form(page)

        courses = get_courses(page)
        assert len(courses) == 0, (
            f"BUG-01: Formulário vazio foi aceito e salvou {len(courses)} curso(s). "
            f"Esperado: 0 cursos. Dados salvos: {courses}"
        )

    def test_validacao_datas_invertidas(self, page):
        """CT06 — BUG-03: Data início posterior à data fim NÃO deve ser aceita"""
        go_to_form(page)
        data = {
            **VALID_DATA,
            "start_date": "2026-12-31",
            "end_date": "2026-01-01",
        }
        fill_form(page, data)
        submit_form(page)

        courses = get_courses(page)
        if courses:
            saved = courses[-1]
            assert saved["startDate"] <= saved["endDate"], (
                f"BUG-03: Datas invertidas foram aceitas. "
                f"startDate={saved['startDate']} > endDate={saved['endDate']}"
            )
        # Se não salvou nenhum curso, o teste passa (validação funcionou)

    def test_validacao_vagas_negativas(self, page):
        """CT07 — BUG-04: Número de vagas negativo NÃO deve ser aceito"""
        go_to_form(page)
        fill_form(page, {**VALID_DATA, "vagas": "-5"})
        submit_form(page)

        courses = get_courses(page)
        if courses:
            vagas = int(courses[-1].get("numberOfVagas", 0))
            assert vagas > 0, (
                f"BUG-04: Valor negativo de vagas foi aceito: numberOfVagas={vagas}"
            )

    def test_validacao_tipo_obrigatorio(self, page):
        """CT08 — BUG-06: Tipo 'Selecione...' (vazio) NÃO deve ser aceito"""
        go_to_form(page)
        data = {k: v for k, v in VALID_DATA.items() if k != "tipo"}
        fill_form(page, data)
        submit_form(page)

        courses = get_courses(page)
        if courses:
            tipo_value = courses[-1].get("type", {}).get("value", "MISSING")
            assert tipo_value not in ("", None), (
                f"BUG-06: Curso cadastrado sem tipo definido. type.value='{tipo_value}'"
            )


# ─────────────────────────────────────────────────────────
# Listagem
# ─────────────────────────────────────────────────────────

class TestListagem:

    def test_lista_vazia_sem_cursos(self, page):
        """Lista deve estar vazia quando não há cursos cadastrados"""
        page.goto(BASE_URL, wait_until="networkidle")
        time.sleep(1)

        cards = page.locator(".my-card").count()
        assert cards == 0, f"Lista deveria estar vazia, mas encontrou {cards} card(s)"

    def test_curso_aparece_na_lista_apos_cadastro(self, page):
        """Curso cadastrado deve aparecer na lista"""
        go_to_form(page)
        fill_form(page, VALID_DATA)
        submit_form(page)

        assert page.url == f"{BASE_URL}/"
        cards = page.locator(".my-card").count()
        assert cards >= 1, "Nenhum card exibido após cadastro"

    def test_excluir_curso(self, page):
        """CT09 — BUG-02: Excluir curso deve removê-lo da lista e do localStorage"""
        # Cadastra primeiro
        go_to_form(page)
        fill_form(page, VALID_DATA)
        submit_form(page)

        page.goto(BASE_URL, wait_until="networkidle")
        time.sleep(2)

        before = get_courses(page)
        assert len(before) >= 1, "Pré-condição: deve haver ao menos 1 curso para deletar"

        del_btn = page.locator("button.q-btn").filter(has_text="Excluir curso").first
        assert del_btn.count() > 0, "Botão 'Excluir curso' não encontrado"
        del_btn.click()
        time.sleep(2)

        after = get_courses(page)
        assert len(after) < len(before), (
            f"BUG-02: Botão 'Excluir curso' não removeu o curso. "
            f"Antes: {len(before)} curso(s), Depois: {len(after)} curso(s)"
        )


# ─────────────────────────────────────────────────────────
# Navegação
# ─────────────────────────────────────────────────────────

class TestNavegacao:

    def test_url_direta_new_course(self, page):
        """CT10 — BUG-05: Acesso direto a /new-course não deve retornar 404"""
        page.goto(f"{BASE_URL}/new-course", wait_until="domcontentloaded")
        time.sleep(1)

        title = page.title()
        body = page.locator("body").inner_text()

        assert "Page not found" not in body, (
            f"BUG-05: Acesso direto à /new-course retornou 404. Title: '{title}'"
        )
        assert "404" not in title.lower(), f"Título indica 404: '{title}'"

    def test_titulo_sem_typo(self, page):
        """CT11 — BUG-08: Título da aplicação deve ser 'Beedoo QA Challenge' (sem typo)"""
        page.goto(BASE_URL, wait_until="networkidle")
        title = page.locator(".q-toolbar__title").inner_text()

        assert "Challenge" in title, (
            f"BUG-08: Typo no título. Encontrado: '{title}'. "
            f"Esperado: título contendo 'Challenge' (não 'Chalenge')"
        )

    def test_navegacao_menu_listar_cursos(self, page):
        """Menu 'Listar cursos' deve navegar para a home"""
        page.goto(f"{BASE_URL}/new-course", wait_until="networkidle")
        page.wait_for_timeout(500)
        page.click("a:has-text('Listar cursos')")
        time.sleep(1)
        assert page.url == f"{BASE_URL}/", f"URL inesperada: {page.url}"

    def test_navegacao_menu_cadastrar_curso(self, page):
        """Menu 'Cadastrar curso' deve navegar para /new-course via SPA"""
        page.goto(BASE_URL, wait_until="networkidle")
        page.click("a:has-text('Cadastrar curso')")
        time.sleep(1)
        assert "/new-course" in page.url, f"URL inesperada: {page.url}"
        assert "Page not found" not in page.locator("body").inner_text()
