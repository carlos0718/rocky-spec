"""
rocky update — actualización no destructiva del kit instalado en un proyecto.

Cubre el caso de un proyecto que corrió `rocky init` con una versión vieja del
paquete: refresca `commands/`, `reference/` y `templates/` (el conocimiento
compartido) archivo por archivo, preservando los que el usuario editó a mano
(única forma de customizar el kit, ver SPEC.md "Fuera del alcance") vía el
hash guardado en `shared-manifest.json` por `scaffold.ensure_shared_knowledge`.

También re-genera los archivos 100% del kit de cada integración ya instalada
(`SKILL.md`, `.cursor/commands/rocky-*.md`) llamando de nuevo a `install()` —
son contenido generado, nunca editado a mano, así que pisarlos es seguro.
`CLAUDE.md`/`rocky.mdc` ya vienen protegidos por su propia reparación de
ancla dentro de `install()`, no hace falta tocar nada acá.

No instala agentes nuevos — eso sigue siendo `rocky init --agent <x>`.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path

from .. import scaffold
from ..integrations import INTEGRATION_REGISTRY, SHARED_DIR_NAME
from ..integrations.base import sha256_of

INSTALL_MANIFEST_NAME = "install-manifest.json"
VERSION_FILE_NAME = "VERSION"


@dataclass
class UpdateReport:
    installed_version: str | None
    target_version: str
    already_up_to_date: bool = False
    updated: list[str] = field(default_factory=list)
    added: list[str] = field(default_factory=list)
    preserved_edited: list[str] = field(default_factory=list)
    preserved_no_baseline: list[str] = field(default_factory=list)
    removed_from_kit: list[str] = field(default_factory=list)
    agents_refreshed: list[str] = field(default_factory=list)


def _package_dir(name: str) -> Path:
    return Path(str(resources.files("rocky_spec"))) / name


def _files_under(root: Path) -> dict[str, Path]:
    if not root.exists():
        return {}
    return {p.relative_to(root).as_posix(): p for p in root.rglob("*") if p.is_file()}


def check_update(project_root: Path) -> UpdateReport:
    """Simula `rocky update` sin escribir nada — mismo cálculo, ``apply=False``."""
    return _run(project_root, apply=False)


def apply_update(project_root: Path) -> UpdateReport:
    """Corre `rocky update` de verdad: escribe los archivos y el manifest."""
    return _run(project_root, apply=True)


def _run(project_root: Path, apply: bool) -> UpdateReport:
    shared_root = project_root / SHARED_DIR_NAME
    version_file = shared_root / VERSION_FILE_NAME
    installed_version = version_file.read_text(encoding="utf-8").strip() if version_file.exists() else None
    target_version = scaffold.ROCKY_SPEC_VERSION

    report = UpdateReport(installed_version=installed_version, target_version=target_version)
    if installed_version == target_version:
        report.already_up_to_date = True
        return report

    manifest_path = shared_root / scaffold.SHARED_MANIFEST_NAME
    manifest: dict[str, str] = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    new_manifest = dict(manifest)

    tracked_keys: set[str] = set()
    package_keys: set[str] = set()

    for sub in scaffold.SHARED_KNOWLEDGE_SUBDIRS:
        source_files = _files_under(_package_dir(sub))
        target_dir = shared_root / sub
        dest_files = _files_under(target_dir)

        for relative, source_file in source_files.items():
            key = f"{sub}/{relative}"
            package_keys.add(key)
            new_content = source_file.read_text(encoding="utf-8")
            new_hash = sha256_of(new_content)
            dest_file = dest_files.get(relative)

            if dest_file is None:
                report.added.append(key)
                if apply:
                    write_target = target_dir / relative
                    write_target.parent.mkdir(parents=True, exist_ok=True)
                    write_target.write_text(new_content, encoding="utf-8")
                new_manifest[key] = new_hash
                continue

            current_hash = sha256_of(dest_file.read_text(encoding="utf-8"))
            recorded_hash = manifest.get(key)

            if recorded_hash is None:
                # Instalado antes de que existiera este manifest -- no hay
                # forma de saber si el usuario lo editó. Si ya coincide con
                # la versión nueva no hay nada que hacer; si no, se preserva
                # y se avisa en vez de asumir.
                if current_hash == new_hash:
                    new_manifest[key] = new_hash
                else:
                    report.preserved_no_baseline.append(key)
                continue

            if current_hash != recorded_hash:
                report.preserved_edited.append(key)
                continue

            if current_hash != new_hash:
                report.updated.append(key)
                if apply:
                    dest_file.write_text(new_content, encoding="utf-8")
                new_manifest[key] = new_hash

        for relative in dest_files:
            tracked_keys.add(f"{sub}/{relative}")

    report.removed_from_kit = sorted(tracked_keys - package_keys)

    if apply:
        manifest_path.write_text(
            json.dumps(new_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    install_manifest_path = shared_root / INSTALL_MANIFEST_NAME
    if install_manifest_path.exists():
        installed_agents: dict[str, list[dict]] = json.loads(
            install_manifest_path.read_text(encoding="utf-8")
        )
        commands = scaffold.all_commands()
        for agent_key in installed_agents:
            integration = INTEGRATION_REGISTRY.get(agent_key)
            if integration is None:
                continue
            report.agents_refreshed.append(agent_key)
            if apply:
                entries = integration.install(project_root, commands)
                installed_agents[agent_key] = [
                    {"path": e.path, "sha256": e.sha256} for e in entries
                ]
        if apply:
            install_manifest_path.write_text(
                json.dumps(installed_agents, indent=2), encoding="utf-8"
            )

    if apply:
        version_file.write_text(target_version + "\n", encoding="utf-8")

    return report
