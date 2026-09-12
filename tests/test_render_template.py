from rocky_spec.scripts.render_template import extract_headers, find_unresolved, render


def test_render_replaces_provided_values():
    out = render("Hola {{NAME}}", {"NAME": "Charly"})
    assert out == "Hola Charly"


def test_render_falls_back_to_inline_default():
    out = render("Hasheo: {{PASSWORD_HASHING, default: bcrypt}}", {})
    assert out == "Hasheo: bcrypt"


def test_render_provided_value_wins_over_default():
    out = render("{{X, default: uno}}", {"X": "dos"})
    assert out == "dos"


def test_render_leaves_unresolved_placeholder_intact():
    out = render("Auth: {{AUTH_PATTERN}}", {})
    assert out == "Auth: {{AUTH_PATTERN}}"


def test_find_unresolved_after_partial_render():
    template = "{{A}} y {{B, default: b}} y {{C}}"
    rendered = render(template, {"A": "a"})
    assert find_unresolved(rendered) == ["C"]


def test_find_unresolved_empty_when_all_resolved():
    template = "{{A, default: a}} y {{B, default: b}}"
    rendered = render(template, {})
    assert find_unresolved(rendered) == []


# --- extract_headers (compartido entre drift_check.py y build.py, RF-22/RF-23) ---


def test_extract_headers_returns_h2_and_h3_in_order():
    text = "# Título\n\n## Uno\ntexto\n\n### Uno punto uno\n\n## Dos\n"
    assert extract_headers(text) == ["## Uno", "### Uno punto uno", "## Dos"]


def test_extract_headers_ignores_headers_with_unresolved_placeholder():
    text = "## [Unreleased]\n\n## [0.1.0] - {{DATE}}\n"
    assert extract_headers(text) == ["## [Unreleased]"]


def test_extract_headers_empty_for_text_without_headers():
    assert extract_headers("solo texto plano, sin encabezados\n") == []
