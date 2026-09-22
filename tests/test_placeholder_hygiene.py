"""Higiene de placeholders: que ningún ``{{...}}`` del kit sea un falso positivo
de `rocky check qa` ni un valor congelado en lo que se genera.

Nace de tres casos reales. La fila del historial de SPEC.md nombraba
placeholders con llaves y `rocky check qa .` los marcaba como sin rellenar.
``CONSTITUTION.md.template`` repetía ``{{CONSTITUTION_VERSION}}`` en prosa, así
que el número quedaba congelado en el valor inicial. Y varios templates tenían
marcadores en minúscula (``{{fecha}}``, ``{{feature-slug-1}}``) o con puntos
(``{{...}}``) que `find_unresolved` no reconoce: si nadie los rellena,
sobreviven sin que ningún chequeo avise.

Los tests miran la *salida* (lo que se renderiza / lo que ve el chequeo), no
solo el string de entrada.

Un cuarto caso, distinto de los tres anteriores (no es sobre la sintaxis de
un placeholder, es sobre qué archivos mira `rocky check qa`): el título de
`commands/p7.5-qa-review.md`, su propio grep de fallback y
`qa_review.py` tenían tres listas de archivos distintas entre sí, y ninguna
incluía `AGENTS.md`/`CLAUDE.md`/`CHANGELOG.md`/`README.md` pese a ser
archivos base que `rocky build` genera siempre. `qa_review.tracked_file_candidates()`
pasa a derivarse de `build.BASE_FILES` para que sea imposible que ambas
listas vuelvan a divergir.
"""
import re
from importlib import resources
from pathlib import Path

import pytest

from rocky_spec.scripts import build, qa_review, render_template

PACKAGE = Path(str(resources.files("rocky_spec")))
TEMPLATES = sorted((PACKAGE / "templates").glob("*.template"))
REPO_ROOT = Path(__file__).resolve().parent.parent

BRACE_PAIR = re.compile(r"\{\{[^{}]*\}\}")


def test_templates_were_found():
    # Sin esto, un cambio de ruta dejaría vacía la parametrización de abajo y
    # los tests "pasarían" sin haber mirado ningún template.
    assert len(TEMPLATES) >= 15


@pytest.mark.parametrize("template", TEMPLATES, ids=lambda p: p.name)
def test_every_brace_pair_in_template_is_a_valid_placeholder(template):
    # `find_unresolved` solo reconoce MAYUSCULAS_Y_GUIONES_BAJOS. Un marcador
    # como `{{fecha}}` o `{{...}}` sobrevive al render sin que nada lo detecte.
    # Las llaves de sintaxis JSX (`style={{...}}`) no son marcadores: se
    # descartan por ir pegadas a un `=`.
    invalid = []
    for lineno, line in enumerate(template.read_text(encoding="utf-8").splitlines(), 1):
        for match in BRACE_PAIR.finditer(line):
            if line[: match.start()].endswith("="):
                continue
            if not render_template.find_unresolved(match.group(0)):
                invalid.append(f"L{lineno}: {match.group(0)}")
    assert invalid == []


def test_constitution_version_is_not_frozen_into_the_amendment_rule():
    # El valor se define una sola vez (campo "Versión de esta Constitution").
    # Si la regla de enmienda lo repite como placeholder, se renderiza con el
    # valor inicial y "subir 1.0.0" queda escrito aunque la Constitution ya
    # vaya por la 1.5.0.
    template = (PACKAGE / "templates" / "CONSTITUTION.md.template").read_text(encoding="utf-8")
    rendered = render_template.render(template, {"CONSTITUTION_VERSION": "9.9.9"})
    assert rendered.count("9.9.9") == 1


@pytest.mark.skipif(
    not (REPO_ROOT / "SPEC.md").exists(),
    reason="solo corre en el checkout del repo, no en una instalación del paquete",
)
def test_repo_root_docs_have_no_unresolved_placeholders():
    # Es lo que corre `rocky check qa .` sobre este mismo repo. Un placeholder
    # nombrado con llaves como texto (en vez de un valor olvidado) dispara el
    # mismo aviso, y el ruido hace que se ignoren los avisos reales.
    report = qa_review.full_report(REPO_ROOT)
    assert report.unresolved_placeholders == {}


# --- qa_review.tracked_file_candidates() -- el "hueco de los huecos" ---


def test_tracked_candidates_cover_every_base_file():
    # Anti-drift: qa_review deriva su lista de BASE_FILES en vez de repetirla a
    # mano -- este test protege esa relación aunque alguien vuelva a hardcodear
    # una lista propia en qa_review.py más adelante (la regresión real).
    base_file_outputs = {output for _, output in build.BASE_FILES}
    assert base_file_outputs <= set(qa_review.tracked_file_candidates())


@pytest.mark.parametrize(
    "relative_path",
    [
        "AGENTS.md",
        "CLAUDE.md",
        "CHANGELOG.md",
        "README.md",
        "SYSTEM_PROMPT.md",
        "BRIEF.md",
        "STORYBOARD.md",
    ],
)
def test_full_report_flags_unresolved_placeholder_in_previously_untracked_file(tmp_path, relative_path):
    # Regresión: antes de tracked_file_candidates(), `rocky check qa` nunca
    # miraba estos archivos -- un {{PLACEHOLDER}} olvidado en, por ejemplo,
    # AGENTS.md (el template con más placeholders derivados a mano, 39) podía
    # quedar en el proyecto generado sin que ningún chequeo lo detectara.
    (tmp_path / "SPEC.md").write_text("RF-1 Login\nUS-1 (implementa RF-1): login\n")
    (tmp_path / "TODO.md").write_text("- [ ] Endpoint de login (US-1)\n")
    target = tmp_path / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("Placeholder sin rellenar: {{ALGO_PENDIENTE}}\n")

    report = qa_review.full_report(tmp_path)

    assert not report.is_clean
    assert list(report.unresolved_placeholders.values()) == [["ALGO_PENDIENTE"]]
