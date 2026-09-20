import subprocess

import pytest

from rocky_spec.scripts import health_check


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


def _write_lines(path, n_lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(f"// line {i}" for i in range(n_lines)))


def _messages(report):
    return [f.message for f in report.findings]


def test_check_file_sizes_default_thresholds_are_250_and_400(tmp_path):
    _write_lines(tmp_path / "a.py", 249)
    _write_lines(tmp_path / "b.py", 250)
    _write_lines(tmp_path / "c.py", 400)
    by_file = {f.file.rsplit("\\", 1)[-1].rsplit("/", 1)[-1]: f.message for f in health_check.check_file_sizes(tmp_path).findings}
    assert "a.py" not in by_file
    assert "zona de revisar" in by_file["b.py"]
    assert "dividir sí o sí" in by_file["c.py"]


@pytest.mark.parametrize(
    "relative",
    [
        "tests/test_ok.py",
        "src/foo.test.ts",
        "src/foo.spec.ts",
        "pkg/foo_test.go",
        "src/__tests__/foo.ts",
        "MyApp.Tests/UserTests.cs",
        "Api/UserServiceTests.cs",  # test que además parece servicio: gana "tests"
    ],
)
def test_check_file_sizes_tests_get_500_lines_before_review(tmp_path, relative):
    _write_lines(tmp_path / relative, 300)
    assert health_check.check_file_sizes(tmp_path).findings == []


def test_check_file_sizes_tests_flagged_for_review_at_500_but_never_forced_to_split(tmp_path):
    # coding-principles.md no da un número de "dividir" para tests, solo "por describe/escenario".
    _write_lines(tmp_path / "tests" / "test_a.py", 500)
    _write_lines(tmp_path / "tests" / "test_b.py", 900)
    messages = _messages(health_check.check_file_sizes(tmp_path))
    assert len(messages) == 2
    assert all("zona de revisar" in m and "dividir sí o sí" not in m for m in messages)


def test_check_file_sizes_hard_ceiling_applies_to_tests_and_config_too(tmp_path):
    _write_lines(tmp_path / "tests" / "test_huge.py", 1000)
    _write_lines(tmp_path / "vite.config.ts", 1000)
    report = health_check.check_file_sizes(tmp_path)
    assert [f.severity for f in report.findings] == ["critical", "critical"]


def test_check_file_sizes_name_ending_in_test_is_not_a_test_file(tmp_path):
    _write_lines(tmp_path / "latest.py", 300)
    assert any("zona de revisar" in m for m in _messages(health_check.check_file_sizes(tmp_path)))


def test_check_file_sizes_classifies_by_path_inside_the_project_not_above_it(tmp_path):
    project = tmp_path / "tests" / "proj"
    _write_lines(project / "big.py", 300)
    assert any("zona de revisar" in m for m in _messages(health_check.check_file_sizes(project)))


@pytest.mark.parametrize(
    "relative", ["user_service.py", "UserService.ts", "src/useAuth.ts", "hooks/session.ts", "services/mail.py"]
)
def test_check_file_sizes_services_and_hooks_get_300_lines_before_review(tmp_path, relative):
    _write_lines(tmp_path / relative, 280)
    assert health_check.check_file_sizes(tmp_path).findings == []


def test_check_file_sizes_services_review_at_300_split_at_400(tmp_path):
    _write_lines(tmp_path / "user_service.py", 300)
    _write_lines(tmp_path / "mail_service.py", 400)
    by_file = {f.file.replace("\\", "/").rsplit("/", 1)[-1]: f.message for f in health_check.check_file_sizes(tmp_path).findings}
    assert "zona de revisar" in by_file["user_service.py"]
    assert "dividir sí o sí" in by_file["mail_service.py"]


@pytest.mark.parametrize("relative", ["user.types.ts", "index.d.ts", "types/user.ts", "types.ts"])
def test_check_file_sizes_types_get_300_lines_before_review_and_500_before_split(tmp_path, relative):
    _write_lines(tmp_path / relative, 299)
    assert health_check.check_file_sizes(tmp_path).findings == []
    _write_lines(tmp_path / relative, 450)
    (message,) = _messages(health_check.check_file_sizes(tmp_path))
    assert "zona de revisar" in message
    _write_lines(tmp_path / relative, 500)
    (message,) = _messages(health_check.check_file_sizes(tmp_path))
    assert "dividir sí o sí" in message


@pytest.mark.parametrize("relative", ["vite.config.ts", "tailwind.config.js", "constants.ts", "config.py"])
def test_check_file_sizes_config_and_constants_have_no_size_tier_below_the_ceiling(tmp_path, relative):
    _write_lines(tmp_path / relative, 900)
    assert health_check.check_file_sizes(tmp_path).findings == []


@pytest.mark.parametrize("extension", ["vue", "svelte", "java", "kt", "cs", "rb", "php"])
def test_check_file_sizes_scans_stacks_the_kit_supports(tmp_path, extension):
    _write_lines(tmp_path / "src" / f"Big.{extension}", 450)
    assert any("dividir sí o sí" in m for m in _messages(health_check.check_file_sizes(tmp_path)))


@pytest.mark.parametrize(
    "relative",
    ["obj/Debug/Gen.cs", "target/generated/Gen.java", "vendor/lib/x.php", ".next/chunk.js", "coverage/lcov/x.js", "venv/lib/x.py"],
)
def test_check_file_sizes_ignores_generated_and_third_party_dirs(tmp_path, relative):
    _write_lines(tmp_path / relative, 450)
    assert health_check.check_file_sizes(tmp_path).findings == []


def test_check_file_sizes_scans_project_that_lives_under_an_ignored_dir_name(tmp_path):
    # Ej. `WORKDIR /build` en Docker: la carpeta ancestro se llama como una
    # de IGNORED_DIRS, pero el proyecto en sí no está dentro de una carpeta ignorada.
    project = tmp_path / "build" / "proj"
    project.mkdir(parents=True)
    (project / "big.ts").write_text("\n".join(f"// line {i}" for i in range(450)))
    report = health_check.check_file_sizes(project)
    assert any("dividir sí o sí" in f.message for f in report.findings)


def test_check_file_sizes_still_ignores_ignored_dirs_inside_the_project(tmp_path):
    vendored = tmp_path / "node_modules" / "lib"
    vendored.mkdir(parents=True)
    (vendored / "big.ts").write_text("\n".join(f"// line {i}" for i in range(450)))
    report = health_check.check_file_sizes(tmp_path)
    assert report.findings == []


def test_check_security_scans_project_that_lives_under_an_ignored_dir_name(tmp_path):
    project = tmp_path / "dist" / "proj"
    project.mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    (project / "config.js").write_text("const API_KEY = 'sk-live-abc123def456ghi789jkl';\n")
    report = health_check.check_security(project)
    assert any("secret hardcodeado" in f.message for f in report.findings)


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
