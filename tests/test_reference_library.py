"""RF-26: biblioteca de referencias, fichas de arquitectura y paso P5.9.

Son casi todos archivos Markdown, así que lo que se puede verificar de forma
determinista es la *forma*: que se instalen, que compartan la plantilla que
promete el SPEC, y que ningún archivo del kit apunte a otro que no existe.
"""
import re
from importlib import resources
from pathlib import Path

from rocky_spec import scaffold
from rocky_spec.integrations import INTEGRATION_REGISTRY, SHARED_DIR_NAME
from rocky_spec.scripts import render_template

PACKAGE = Path(str(resources.files("rocky_spec")))
REFERENCE = PACKAGE / "reference"

INSTALLED_BY_RF_26 = [
    "reference/solid.md",
    "reference/general-principles.md",
    "reference/design-patterns.md",
    "reference/design-patterns/creational.md",
    "reference/design-patterns/structural.md",
    "reference/design-patterns/behavioral.md",
    "reference/best-practices-frontend.md",
    "reference/best-practices-backend.md",
    "reference/architecture-styles/monolith.md",
    "reference/architecture-styles/layered.md",
    "reference/architecture-styles/onion.md",
    "reference/architecture-styles/hexagonal.md",
    "reference/architecture-styles/microservices.md",
    "reference/architecture-styles/event-driven.md",
    "commands/p5.9-practices.md",
    "templates/PRACTICES.md.template",
]

ARCHITECTURE_SECTIONS = (
    "## Qué es",
    "## Diagrama",
    "## Estructura de carpetas de ejemplo",
    "## Cuándo sí",
    "## Cuándo no",
    "## Señales de alarma",
    "## Qué ganás y qué sacrificás",
    "## Cómo se combina con otros estilos",
    "## Cómo la usa la skill",
)

PATTERN_FIELDS = (
    "**Frecuencia:**",
    "**Qué es**",
    "**Cuándo sí**",
    "**Cuándo no**",
    "**Señal en el código**",
    "**Cómo lo aplica la skill**",
)


def _headings(text: str, prefix: str) -> list[str]:
    return [line for line in text.splitlines() if line.startswith(prefix)]


def test_init_installs_the_reference_library_and_the_practices_step(tmp_path):
    scaffold.ensure_shared_knowledge(tmp_path)
    shared = tmp_path / SHARED_DIR_NAME

    missing = [rel for rel in INSTALLED_BY_RF_26 if not (shared / rel).is_file()]

    assert not missing, f"no se instaló: {missing}"


def test_practices_step_sits_between_accessibility_and_build():
    keys = [key for key, _title, _source in scaffold.COMMAND_CATALOG]

    assert keys.index("accessibility") < keys.index("practices") < keys.index("build")


def test_every_catalog_step_points_to_an_existing_command_file():
    for key, _title, source in scaffold.COMMAND_CATALOG:
        assert (PACKAGE / "commands" / source).is_file(), f"'{key}' apunta a {source}, que no existe"


def test_cursor_gets_a_command_for_the_practices_step(tmp_path):
    scaffold.ensure_shared_knowledge(tmp_path)
    INTEGRATION_REGISTRY["cursor"].install(tmp_path, scaffold.all_commands())

    assert (tmp_path / ".cursor" / "commands" / "rocky-practices.md").is_file()


def test_claude_skill_index_lists_the_practices_step(tmp_path):
    scaffold.ensure_shared_knowledge(tmp_path)
    INTEGRATION_REGISTRY["claude"].install(tmp_path, scaffold.all_commands())

    index = (tmp_path / ".claude" / "skills" / "rocky-spec" / "SKILL.md").read_text(encoding="utf-8")

    assert "P5.9" in index
    assert "p5.9-practices.md" in index


def test_practices_template_renders_with_no_unresolved_placeholders():
    template = (PACKAGE / "templates" / "PRACTICES.md.template").read_text(encoding="utf-8")
    values = {
        "PROJECT_NAME": "demo",
        "FRONTEND": "React",
        "BACKEND": "No aplica",
        "ARCHITECTURE_NAME": "Feature-based",
        "PRACTICES_SCALE": "Producto real",
        "PRACTICES_PRINCIPLES": "| KISS | funciones planas |",
        "ACTIVE_PATTERNS": "Adapter",
        "PRACTICES_TOOLS": "| Linter | ESLint | recomendada |",
        "DATE": "2026-09-20",
        "INITIAL_COMMIT": "(pendiente)",
    }

    rendered = render_template.render(template, values)

    assert render_template.find_unresolved(rendered) == []
    assert "## Patrones descartados a propósito" in rendered


def test_practices_template_only_leaves_the_mandatory_placeholders_open():
    # Los opcionales (patrones, descartados, capas, versión) traen su default
    # en el propio template: es lo que hace posible la versión mínima sin
    # pasarle valores vacíos. Los obligatorios tienen que pedirse.
    template = (PACKAGE / "templates" / "PRACTICES.md.template").read_text(encoding="utf-8")

    unresolved = set(render_template.find_unresolved(render_template.render(template, {})))

    assert unresolved == {
        "PROJECT_NAME", "FRONTEND", "BACKEND", "ARCHITECTURE_NAME", "PRACTICES_SCALE",
        "PRACTICES_PRINCIPLES", "ACTIVE_PATTERNS", "PRACTICES_TOOLS", "DATE", "INITIAL_COMMIT",
    }


def test_every_architecture_style_has_the_common_sheet_template():
    sheets = sorted((REFERENCE / "architecture-styles").glob("*.md"))
    assert len(sheets) == 6

    for sheet in sheets:
        headings = _headings(sheet.read_text(encoding="utf-8"), "## ")
        for section in ARCHITECTURE_SECTIONS:
            assert any(h.startswith(section) for h in headings), f"{sheet.name}: falta '{section}'"


def test_gof_patterns_are_all_there_and_share_the_common_template():
    gof = []
    for kind in ("creational", "structural", "behavioral"):
        text = (REFERENCE / "design-patterns" / f"{kind}.md").read_text(encoding="utf-8")
        blocks = re.split(r"^### ", text, flags=re.MULTILINE)[1:]
        for block in blocks:
            name = block.splitlines()[0].strip()
            gof.append(name)
            for field in PATTERN_FIELDS:
                assert field in block, f"{kind}.md · {name}: falta {field}"

    assert len(gof) == 23, f"GoF tiene 23 patrones, hay {len(gof)}: {gof}"
    assert len(set(gof)) == 23


def test_non_gof_patterns_share_the_same_template():
    text = (REFERENCE / "design-patterns.md").read_text(encoding="utf-8")
    section = text.split("## Patrones frecuentes que no son GoF")[1].split("## MVC y MVVM")[0]
    blocks = re.split(r"^### ", section, flags=re.MULTILINE)[1:]

    assert [b.splitlines()[0].strip() for b in blocks] == ["Repository", "Dependency Injection", "Registry / Plugin"]
    for block in blocks:
        for field in PATTERN_FIELDS:
            assert field in block, f"{block.splitlines()[0]}: falta {field}"


_REFERENCE_LINK = re.compile(
    r"`((?:\.rocky-spec/(?:reference|commands|templates)/|(?:architecture-styles|design-patterns|architectures)/)"
    r"[\w./-]+\.(?:md|template))`"
)


def test_shared_knowledge_has_no_dead_references_to_its_own_files():
    # RF-26/US-36: mover contenido entre archivos (SOLID, patrones, estilos)
    # no puede dejar un `.rocky-spec/...` apuntando a algo que ya no existe.
    dead = []
    for sub in scaffold.SHARED_KNOWLEDGE_SUBDIRS:
        for path in (PACKAGE / sub).rglob("*"):
            if not path.is_file():
                continue
            for match in _REFERENCE_LINK.finditer(path.read_text(encoding="utf-8")):
                ref = match.group(1)
                if ref.startswith(".rocky-spec/"):
                    target = PACKAGE / ref[len(".rocky-spec/"):]
                else:
                    target = REFERENCE / ref
                if not target.is_file():
                    dead.append(f"{path.relative_to(PACKAGE).as_posix()} -> {ref}")

    assert not dead, "referencias rotas:\n" + "\n".join(sorted(set(dead)))


def test_coding_principles_keeps_only_what_can_be_measured():
    # US-36: SOLID/principios/patrones se migraron; coding-principles.md
    # conserva smells, tamaños, estilo y reglas base, y vuelve a tener margen
    # bajo su propio techo de 500 líneas para archivos Markdown.
    text = (REFERENCE / "coding-principles.md").read_text(encoding="utf-8")
    headings = _headings(text, "## ")

    assert len(text.splitlines()) < 400
    assert not any(h.startswith("## Patrones de diseño") for h in headings)
    assert not any(h.startswith("## Principios generales") for h in headings)
    for kept in ("## Code smells", "## Tamaño de archivo", "## Reglas de estilo de código"):
        assert any(h.startswith(kept) for h in headings), f"se perdió '{kept}'"
