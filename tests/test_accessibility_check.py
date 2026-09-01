from spec_charless.scripts import accessibility_check as a11y


def _write(tmp_path, name, content):
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


# --- img sin alt ---


def test_img_without_alt_is_flagged(tmp_path):
    _write(tmp_path, "page.html", '<img src="x.png">')
    findings = a11y.check_img_alt(tmp_path)
    assert len(findings) == 1
    assert "alt" in findings[0].message


def test_img_with_alt_is_not_flagged(tmp_path):
    _write(tmp_path, "page.html", '<img src="x.png" alt="descripción">')
    assert a11y.check_img_alt(tmp_path) == []


def test_img_with_spread_props_is_not_flagged(tmp_path):
    # {...imgProps} puede traer alt inyectado -- no se ve en el texto, no se flaggea
    _write(tmp_path, "Page.tsx", '<img {...imgProps} src="x.png" />')
    assert a11y.check_img_alt(tmp_path) == []


# --- html sin lang ---


def test_html_without_lang_is_flagged(tmp_path):
    _write(tmp_path, "index.html", "<html><head></head></html>")
    findings = a11y.check_html_lang(tmp_path)
    assert len(findings) == 1
    assert findings[0].severity == "critical"


def test_html_with_lang_is_not_flagged(tmp_path):
    _write(tmp_path, "index.html", '<html lang="es"><head></head></html>')
    assert a11y.check_html_lang(tmp_path) == []


# --- div onClick sin role/tabIndex ---


def test_div_onclick_without_role_is_flagged(tmp_path):
    _write(tmp_path, "Page.tsx", "<div onClick={handleClick}>Click acá</div>")
    findings = a11y.check_clickable_div_role(tmp_path)
    assert len(findings) == 1


def test_div_onclick_with_role_and_tabindex_is_not_flagged(tmp_path):
    _write(
        tmp_path,
        "Page.tsx",
        '<div onClick={handleClick} role="button" tabIndex={0}>Click acá</div>',
    )
    assert a11y.check_clickable_div_role(tmp_path) == []


def test_div_onclick_attribute_order_does_not_matter(tmp_path):
    _write(
        tmp_path,
        "Page.tsx",
        '<div tabIndex={0} onClick={handleClick}>Click acá</div>',
    )
    assert a11y.check_clickable_div_role(tmp_path) == []


# --- button solo-ícono sin aria-label ---


def test_icon_only_button_without_aria_label_is_flagged(tmp_path):
    _write(tmp_path, "Page.tsx", "<button onClick={f}><svg/></button>")
    findings = a11y.check_icon_only_button(tmp_path)
    assert len(findings) == 1


def test_icon_only_button_with_aria_label_is_not_flagged(tmp_path):
    _write(tmp_path, "Page.tsx", '<button aria-label="Cerrar"><svg/></button>')
    assert a11y.check_icon_only_button(tmp_path) == []


def test_button_with_text_is_not_flagged(tmp_path):
    assert a11y.check_icon_only_button(_write(tmp_path, "Page.tsx", "<button>Cerrar</button>").parent) == []


def test_icon_plus_visible_text_button_is_not_flagged(tmp_path):
    _write(tmp_path, "Page.tsx", "<button><svg/> Cerrar</button>")
    assert a11y.check_icon_only_button(tmp_path) == []


def test_icon_button_with_sr_only_text_is_correctly_not_flagged(tmp_path):
    # sr-only da nombre accesible real (screen reader lo lee, solo se oculta
    # visualmente) -- correcto que el heurístico no lo marque.
    _write(
        tmp_path,
        "Page.tsx",
        '<button><svg/><span className="sr-only">Cerrar</span></button>',
    )
    assert a11y.check_icon_only_button(tmp_path) == []


def test_icon_button_with_display_none_text_is_a_known_false_negative(tmp_path):
    # Limitación documentada: display:none oculta el texto de TODOS
    # (screen reader incluido) -- no da nombre accesible real, pero el
    # heurístico no distingue esto de sr-only y no lo flaggea igual.
    _write(
        tmp_path,
        "Page.tsx",
        '<button><svg/><span style="display:none">Cerrar</span></button>',
    )
    assert a11y.check_icon_only_button(tmp_path) == []  # falso negativo esperado, documentado


# --- contraste WCAG ---


def test_low_contrast_css_pair_is_flagged(tmp_path):
    _write(tmp_path, "styles.css", ".card { color: #ffffff; background: #f0f0f0; }")
    findings = a11y.check_color_contrast(tmp_path)
    assert len(findings) == 1
    assert "contraste" in findings[0].message


def test_high_contrast_css_pair_is_not_flagged(tmp_path):
    _write(tmp_path, "styles.css", ".card { color: #000000; background: #ffffff; }")
    assert a11y.check_color_contrast(tmp_path) == []


def test_inline_style_low_contrast_is_flagged(tmp_path):
    _write(tmp_path, "Page.tsx", '<div style="color: #ffd700; background: #ffffff;">x</div>')
    assert len(a11y.check_color_contrast(tmp_path)) == 1


def test_css_custom_property_is_not_flagged(tmp_path):
    # var(--x) no se resuelve -- limitación documentada, no falso negativo silencioso
    _write(tmp_path, "styles.css", ".card { color: var(--text); background: #ffffff; }")
    assert a11y.check_color_contrast(tmp_path) == []


def test_tailwind_utility_classes_are_not_flagged(tmp_path):
    # sin CSS/inline-style literal, no hay nada que parsear -- correcto, no un bug
    _write(tmp_path, "Page.tsx", '<div className="text-white bg-gray-100">x</div>')
    assert a11y.check_color_contrast(tmp_path) == []


# --- funciones puras de contraste ---


def test_parse_color_hex_short_and_long():
    assert a11y.parse_color("#fff") == (255, 255, 255)
    assert a11y.parse_color("#ffffff") == (255, 255, 255)


def test_parse_color_rgb():
    assert a11y.parse_color("rgb(0, 0, 0)") == (0, 0, 0)
    assert a11y.parse_color("rgba(10, 20, 30, 0.5)") == (10, 20, 30)


def test_parse_color_returns_none_for_var_and_keywords():
    assert a11y.parse_color("var(--x)") is None
    assert a11y.parse_color("white") is None


def test_relative_luminance_extremes():
    assert a11y.relative_luminance((255, 255, 255)) == 1.0
    assert a11y.relative_luminance((0, 0, 0)) == 0.0


def test_contrast_ratio_black_on_white_is_max():
    ratio = a11y.contrast_ratio((255, 255, 255), (0, 0, 0))
    assert round(ratio, 1) == 21.0


def test_contrast_ratio_known_wcag_pass_and_fail_examples():
    # #767676 sobre blanco es el ejemplo canónico de WCAG que SÍ pasa AA (~4.5:1)
    passing = a11y.contrast_ratio((0x76, 0x76, 0x76), (255, 255, 255))
    assert passing >= a11y.WCAG_AA_NORMAL_TEXT_RATIO

    # #A0A0A0 sobre blanco (mencionado en ui-design-guidelines.md) falla AA
    failing = a11y.contrast_ratio((0xA0, 0xA0, 0xA0), (255, 255, 255))
    assert failing < a11y.WCAG_AA_NORMAL_TEXT_RATIO


# --- agregador ---


def test_check_accessibility_aggregates_all_heuristics(tmp_path):
    _write(
        tmp_path,
        "index.html",
        '<html><body><img src="x.png"><div onClick={f}>x</div></body></html>',
    )
    report = a11y.check_accessibility(tmp_path)
    assert report.category == "accessibility"
    assert len(report.findings) >= 2


def test_check_accessibility_clean_project_has_no_findings(tmp_path):
    _write(
        tmp_path,
        "index.html",
        '<html lang="es"><body><img src="x.png" alt="foto"></body></html>',
    )
    report = a11y.check_accessibility(tmp_path)
    assert report.findings == []
