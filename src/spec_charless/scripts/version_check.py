"""
charless check version — sugerencia determinista del próximo bump de SemVer.

Reemplaza el "recordatorio" en prosa del Workflow de Git (`AGENTS.md`) por un
cálculo real sobre los commits: cuenta lo que se mergeó desde el último tag,
lo clasifica por Conventional Commits, aplica la regla "el más alto gana"
(MAJOR > MINOR > PATCH, nunca se apilan varios bumps), y devuelve el próximo
`X.Y.Z` exacto.

Se dispara al mergear `feature/*`/`fix/*` -> `dev` (o `fix/*` -> `master` en
un hotfix) — NO al mergear `dev` -> `master` para un release, donde `master`
simplemente hereda la versión que `dev` ya trae acumulada.
"""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

CONVENTIONAL_TYPE_PATTERN = re.compile(r"^(?P<type>\w+)(\([^)]*\))?(?P<breaking>!)?:\s")
# El footer BREAKING CHANGE: es, por convención, su propia línea/párrafo al
# final del commit -- anclado a inicio de línea para no confundir una mención
# suelta dentro de una viñeta o una oración con el footer real.
BREAKING_FOOTER_PATTERN = re.compile(r"^BREAKING[ -]CHANGE:", re.MULTILINE)

FIX_BUDGET_WARN = 3  # 3-5 fixes acumulados en una feature -> aviso suave (🟡)
FIX_BUDGET_STRONG = 6  # 6+ -> aviso fuerte (🔴), mismo patrón que el TODO Size Check


@dataclass
class CommitClassification:
    breaking: list[str] = field(default_factory=list)
    feat: list[str] = field(default_factory=list)
    fix: list[str] = field(default_factory=list)
    other: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.breaking) + len(self.feat) + len(self.fix) + len(self.other)


@dataclass
class VersionReport:
    current_tag: str | None  # None si el repo todavía no tiene tags
    branch: str
    classification: CommitClassification
    bump: str  # "major" | "minor" | "patch" | "none"
    suggested_version: str | None
    pre_1_0_note: str | None = None
    fix_budget_warning: str | None = None


def _run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, timeout=15
    )


def _last_tag(cwd: Path) -> str | None:
    result = _run_git(["describe", "--tags", "--abbrev=0"], cwd)
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def _current_branch(cwd: Path) -> str:
    return _run_git(["branch", "--show-current"], cwd).stdout.strip()


def _branch_exists(cwd: Path, name: str) -> bool:
    return _run_git(["rev-parse", "--verify", "--quiet", name], cwd).returncode == 0


def _commit_subjects(cwd: Path, rev_range: str) -> list[str]:
    result = _run_git(["log", rev_range, "--pretty=format:%s"], cwd)
    return [line for line in result.stdout.splitlines() if line.strip()]


def _commit_bodies(cwd: Path, rev_range: str) -> list[str]:
    result = _run_git(["log", rev_range, "--pretty=format:%B%x1e"], cwd)
    return [body for body in result.stdout.split("\x1e") if body.strip()]


def _classify(subjects: list[str], bodies: list[str]) -> CommitClassification:
    classification = CommitClassification()

    for subject in subjects:
        match = CONVENTIONAL_TYPE_PATTERN.match(subject)
        if not match:
            classification.other.append(subject)
            continue
        if match.group("breaking"):
            classification.breaking.append(subject)
        elif match.group("type") == "feat":
            classification.feat.append(subject)
        elif match.group("type") == "fix":
            classification.fix.append(subject)
        else:
            classification.other.append(subject)

    # BREAKING CHANGE: va en el body (footer), no en el subject -- si aparece
    # ahí, escala el bump a MAJOR sin importar de qué tipo era el commit.
    if not classification.breaking and any(
        BREAKING_FOOTER_PATTERN.search(body) for body in bodies
    ):
        classification.breaking.append("(detectado por 'BREAKING CHANGE:' en el body)")

    return classification


def _bump_for(classification: CommitClassification) -> str:
    if classification.breaking:
        return "major"
    if classification.feat:
        return "minor"
    if classification.fix:
        return "patch"
    return "none"


def _parse_semver(tag: str) -> tuple[int, int, int]:
    match = re.match(r"v?(\d+)\.(\d+)\.(\d+)", tag)
    if not match:
        return (0, 0, 0)
    major, minor, patch = (int(part) for part in match.groups())
    return (major, minor, patch)


def _next_version(current: tuple[int, int, int], bump: str) -> tuple[tuple[int, int, int], str | None]:
    major, minor, patch = current
    if bump == "major":
        if major == 0:
            # Pre-1.0: SemVer permite seguir bumpeando MINOR en vez de saltar
            # a 1.0.0 automáticamente -- pasar a 1.0.0 es decisión explícita
            # del usuario, nunca automática (ver reference/versioning.md).
            note = (
                "Hay un cambio breaking, pero el proyecto todavía está en 0.x.y — "
                "se sugiere MINOR en vez de saltar a 1.0.0 automáticamente. "
                "Pasar a 1.0.0 es una decisión explícita, no de este chequeo."
            )
            return (major, minor + 1, 0), note
        return (major + 1, 0, 0), None
    if bump == "minor":
        return (major, minor + 1, 0), None
    if bump == "patch":
        return (major, minor, patch + 1), None
    return current, None


def _fix_budget_warning(cwd: Path, branch: str) -> str | None:
    if not branch.startswith("feature/"):
        return None
    if not _branch_exists(cwd, "dev"):
        return None

    subjects = _commit_subjects(cwd, "dev..HEAD")
    fix_count = sum(
        1
        for subject in subjects
        if (match := CONVENTIONAL_TYPE_PATTERN.match(subject)) and match.group("type") == "fix"
    )

    if fix_count >= FIX_BUDGET_STRONG:
        return (
            f"🔴 La rama '{branch}' acumuló {fix_count} fix además del feature — "
            "señal de que conviene partir esta feature en dos, o replantear el diseño. "
            "No es solo iterar."
        )
    if fix_count >= FIX_BUDGET_WARN:
        return (
            f"🟡 La rama '{branch}' acumuló {fix_count} fix además del feature — "
            "¿la spec (RF-N/US-N) subestimó la complejidad? Vale la pena revisar antes de mergear."
        )
    return None


def check_version(root: Path) -> VersionReport:
    tag = _last_tag(root)
    rev_range = f"{tag}..HEAD" if tag else "HEAD"
    branch = _current_branch(root)

    subjects = _commit_subjects(root, rev_range)
    bodies = _commit_bodies(root, rev_range)
    classification = _classify(subjects, bodies)
    bump = _bump_for(classification)

    current = _parse_semver(tag) if tag else (0, 0, 0)
    suggested_version: str | None = None
    pre_1_0_note: str | None = None
    if bump != "none":
        next_version, pre_1_0_note = _next_version(current, bump)
        suggested_version = ".".join(str(part) for part in next_version)

    return VersionReport(
        current_tag=tag,
        branch=branch,
        classification=classification,
        bump=bump,
        suggested_version=suggested_version,
        pre_1_0_note=pre_1_0_note,
        fix_budget_warning=_fix_budget_warning(root, branch),
    )
