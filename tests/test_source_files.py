import pytest

from rocky_spec.scripts import source_files


def test_no_extension_belongs_to_two_languages():
    owner = {}
    for language, extensions in source_files.LANGUAGES.items():
        for extension in extensions:
            assert extension not in owner, f".{extension} está en {owner[extension]} y en {language}"
            owner[extension] = language


def test_code_extensions_is_every_extension_of_every_language():
    expected = {ext for exts in source_files.LANGUAGES.values() for ext in exts}
    assert set(source_files.CODE_EXTENSIONS) == expected
    assert len(source_files.CODE_EXTENSIONS) == len(expected)


@pytest.mark.parametrize("check", sorted(source_files.CHECK_EXTENSIONS))
def test_every_check_scope_only_uses_known_extensions(check):
    known = set(source_files.CODE_EXTENSIONS) | {"html", "css"}
    assert set(source_files.extensions_for(check)) <= known


def test_extensions_for_unknown_check_fails_loudly():
    with pytest.raises(KeyError):
        source_files.extensions_for("no-existe")


@pytest.mark.parametrize("check", sorted(source_files.NOT_READ))
def test_every_language_is_either_read_or_explicitly_not_read_with_a_reason(check):
    # Un lenguaje nuevo en LANGUAGES no entra solo a un check con patrones propios:
    # este test falla hasta que alguien decida si ese check lo lee o lo excluye.
    read = source_files.languages_read(check)
    excluded = set(source_files.NOT_READ[check])
    assert read | excluded == set(source_files.LANGUAGES)
    assert read & excluded == set()
    assert all(reason.strip() for reason in source_files.NOT_READ[check].values())


def test_unread_language_counts_counts_files_per_language_the_check_does_not_read(tmp_path):
    (tmp_path / "a.cs").write_text("x")
    (tmp_path / "b.cs").write_text("x")
    (tmp_path / "c.java").write_text("x")
    (tmp_path / "d.py").write_text("x")  # observability sí lo lee: no cuenta

    assert source_files.unread_language_counts(tmp_path, "observability") == {"csharp": 2, "java": 1}


def test_unread_language_counts_is_empty_for_checks_that_read_everything(tmp_path):
    (tmp_path / "a.cs").write_text("x")
    assert source_files.unread_language_counts(tmp_path, "size") == {}


def test_iter_source_files_filters_by_extension_and_skips_ignored_dirs_inside_the_project(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x = 1")
    (tmp_path / "src" / "b.ts").write_text("x = 1")
    (tmp_path / "node_modules" / "lib").mkdir(parents=True)
    (tmp_path / "node_modules" / "lib" / "c.py").write_text("x = 1")

    found = {p.name for p in source_files.iter_source_files(tmp_path, ("py",))}

    assert found == {"a.py"}


def test_iter_source_files_keeps_project_that_lives_under_an_ignored_dir_name(tmp_path):
    project = tmp_path / "build" / "app"
    project.mkdir(parents=True)
    (project / "a.py").write_text("x = 1")

    assert [p.name for p in source_files.iter_source_files(project, ("py",))] == ["a.py"]


def test_iter_source_files_is_lazy(tmp_path):
    (tmp_path / "a.py").write_text("x = 1")
    assert iter(source_files.iter_source_files(tmp_path, ("py",))) is not None
    assert not isinstance(source_files.iter_source_files(tmp_path, ("py",)), list)
