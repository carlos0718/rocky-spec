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
