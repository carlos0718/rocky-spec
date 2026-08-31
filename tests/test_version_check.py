import subprocess
from pathlib import Path

import pytest

from spec_charless.scripts import version_check


def _git(args: list[str], cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def _commit(cwd: Path, message: str, filename: str = "file.txt") -> None:
    path = cwd / filename
    existing = path.read_text() if path.exists() else ""
    path.write_text(existing + f"{message}\n")
    _git(["add", filename], cwd)
    _git(["commit", "-m", message], cwd)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _git(["init", "-q"], tmp_path)
    _git(["config", "user.email", "test@example.com"], tmp_path)
    _git(["config", "user.name", "Test"], tmp_path)
    _commit(tmp_path, "chore: initial commit")
    return tmp_path


def test_no_tags_uses_zero_baseline(repo: Path) -> None:
    _commit(repo, "feat: primera feature")

    report = version_check.check_version(repo)

    assert report.current_tag is None
    assert report.bump == "minor"
    assert report.suggested_version == "0.1.0"


def test_mixed_feat_and_fix_since_tag_bumps_minor_only(repo: Path) -> None:
    _git(["tag", "v0.2.0"], repo)
    _commit(repo, "feat: agregar X")
    _commit(repo, "fix: corregir Y")
    _commit(repo, "fix: corregir Z")

    report = version_check.check_version(repo)

    assert report.current_tag == "v0.2.0"
    assert report.bump == "minor"
    assert report.suggested_version == "0.3.0"
    assert len(report.classification.feat) == 1
    assert len(report.classification.fix) == 2


def test_only_fix_bumps_patch(repo: Path) -> None:
    _git(["tag", "v1.2.3"], repo)
    _commit(repo, "fix: corregir un bug")

    report = version_check.check_version(repo)

    assert report.bump == "patch"
    assert report.suggested_version == "1.2.4"


def test_docs_and_chore_do_not_bump(repo: Path) -> None:
    _git(["tag", "v0.5.0"], repo)
    _commit(repo, "docs: actualizar README")
    _commit(repo, "chore: limpieza")

    report = version_check.check_version(repo)

    assert report.bump == "none"
    assert report.suggested_version is None


def test_breaking_marker_in_subject_bumps_major_but_pre_1_0_suggests_minor(repo: Path) -> None:
    _git(["tag", "v0.4.0"], repo)
    _commit(repo, "feat!: cambia el formato de salida")

    report = version_check.check_version(repo)

    assert report.bump == "major"
    assert report.suggested_version == "0.5.0"
    assert report.pre_1_0_note is not None


def test_breaking_marker_bumps_major_when_past_1_0(repo: Path) -> None:
    _git(["tag", "v1.0.0"], repo)
    _commit(repo, "feat!: cambia el formato de salida")

    report = version_check.check_version(repo)

    assert report.bump == "major"
    assert report.suggested_version == "2.0.0"
    assert report.pre_1_0_note is None


def test_breaking_change_footer_in_body_bumps_major(repo: Path) -> None:
    _git(["tag", "v0.9.0"], repo)
    path = repo / "file.txt"
    path.write_text("cambio\n")
    _git(["add", "file.txt"], repo)
    _git(
        ["commit", "-m", "fix: ajuste chico\n\nBREAKING CHANGE: cambia el contrato de la API"],
        repo,
    )

    report = version_check.check_version(repo)

    assert report.bump == "major"


def test_breaking_change_mentioned_mid_bullet_is_not_a_real_footer(repo: Path) -> None:
    _git(["tag", "v0.6.0"], repo)
    path = repo / "file.txt"
    path.write_text("cambio\n")
    _git(["add", "file.txt"], repo)
    _git(
        [
            "commit",
            "-m",
            "feat: agregar deteccion de footer\n\n"
            "- BREAKING CHANGE: se detecta en el body, no en el subject",
        ],
        repo,
    )

    report = version_check.check_version(repo)

    assert report.bump == "minor"


def test_fix_budget_warning_escalates_on_feature_branch(repo: Path) -> None:
    _git(["checkout", "-b", "dev"], repo)
    _git(["checkout", "-b", "feature/algo"], repo)
    _commit(repo, "feat: la feature en si")
    for i in range(3):
        _commit(repo, f"fix: ajuste {i}")

    report = version_check.check_version(repo)

    assert report.fix_budget_warning is not None
    assert "🟡" in report.fix_budget_warning

    for i in range(3, 6):
        _commit(repo, f"fix: ajuste {i}")

    report = version_check.check_version(repo)

    assert "🔴" in report.fix_budget_warning


def test_no_fix_budget_warning_without_dev_branch(repo: Path) -> None:
    _git(["checkout", "-b", "feature/algo"], repo)
    for i in range(5):
        _commit(repo, f"fix: ajuste {i}")

    report = version_check.check_version(repo)

    assert report.fix_budget_warning is None


def test_no_fix_budget_warning_outside_feature_branch(repo: Path) -> None:
    _git(["checkout", "-b", "dev"], repo)
    for i in range(5):
        _commit(repo, f"fix: ajuste {i}")

    report = version_check.check_version(repo)

    assert report.fix_budget_warning is None
