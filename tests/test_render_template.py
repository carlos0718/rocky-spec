from spec_charless.scripts.render_template import find_unresolved, render


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
