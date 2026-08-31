import subprocess

import pytest

from spec_charless.scripts import health_check


@pytest.fixture
def git_repo(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    return tmp_path


def test_check_file_sizes_flags_over_400_lines(tmp_path):
    big_file = tmp_path / "big.ts"
    big_file.write_text("\n".join(f"// line {i}" for i in range(450)))
    report = health_check.check_file_sizes(tmp_path)
    assert any("dividir sí o sí" in f.message for f in report.findings)


def test_check_file_sizes_hard_ceiling_at_1000(tmp_path):
    huge_file = tmp_path / "huge.ts"
    huge_file.write_text("\n".join(f"// line {i}" for i in range(1200)))
    report = health_check.check_file_sizes(tmp_path)
    assert any(f.severity == "critical" for f in report.findings)


def test_check_file_sizes_ignores_small_files(tmp_path):
    small_file = tmp_path / "small.ts"
    small_file.write_text("const x = 1;\n")
    report = health_check.check_file_sizes(tmp_path)
    assert report.findings == []


def test_check_security_detects_missing_env_in_gitignore(git_repo):
    (git_repo / ".gitignore").write_text("node_modules\n")
    report = health_check.check_security(git_repo)
    assert any(".env no está en .gitignore" in f.message for f in report.findings)


def test_check_security_detects_hardcoded_secret_without_leaking_value(git_repo):
    secret_value = "sk-live-abc123def456ghi789jkl"
    (git_repo / "config.js").write_text(f"const API_KEY = '{secret_value}';\n")
    report = health_check.check_security(git_repo)
    critical = [f for f in report.findings if f.severity == "critical"]
    assert any("secret hardcodeado" in f.message for f in critical)
    # Nunca debe filtrarse el valor real del secret en el mensaje.
    assert all(secret_value not in f.message for f in report.findings)


def test_check_security_ignores_placeholder_values(git_repo):
    (git_repo / "config.js").write_text("const API_KEY = 'your-key-here-0000000000';\n")
    report = health_check.check_security(git_repo)
    assert not any("secret hardcodeado" in f.message for f in report.findings)


def test_check_observability_flags_missing_error_tracking_and_health_endpoint(tmp_path):
    (tmp_path / "app.ts").write_text("console.log('hola');\n")
    report = health_check.check_observability(tmp_path)
    messages = [f.message for f in report.findings]
    assert any("error tracking" in m for m in messages)
    assert any("health check" in m for m in messages)


def test_check_observability_recognizes_sentry_and_health_endpoint(tmp_path):
    (tmp_path / "app.ts").write_text(
        "Sentry.init({dsn: process.env.SENTRY_DSN});\n"
        "app.get('/health', () => {});\n"
    )
    report = health_check.check_observability(tmp_path)
    messages = [f.message for f in report.findings]
    assert not any("error tracking" in m for m in messages)
    assert not any("health check" in m for m in messages)
