from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKUP_PATH = ROOT / "respaldo_jobsmatch_2026-02-10.sql"


def _extract_values_block(sql: str, table: str) -> str:
    marker = f"INSERT INTO `{table}` VALUES"
    start = sql.find(marker)
    if start == -1:
        raise AssertionError(f"No INSERT block found for {table}")
    end = sql.find(";", start)
    if end == -1:
        raise AssertionError(f"INSERT block for {table} missing ';'")
    return sql[start:end]


def _extract_empresa_ids(block: str) -> list[int]:
    # perfiles_empresas values: (usuario_id,'nombre_comercial',...)
    return [int(match) for match in re.findall(r"\((\d+),'", block)]


def _extract_vacantes_empresa_ids(block: str) -> list[int]:
    # vacantes values: (id,empresa_id,'titulo',...)
    return [int(match) for match in re.findall(r"\(\d+,(\d+),", block)]


def main() -> None:
    sql = BACKUP_PATH.read_text(encoding="latin-1")

    empresas_block = _extract_values_block(sql, "perfiles_empresas")
    vacantes_block = _extract_values_block(sql, "vacantes")

    empresa_ids = _extract_empresa_ids(empresas_block)
    if not empresa_ids:
        raise AssertionError("No perfiles_empresas rows found")

    vacantes_empresa_ids = _extract_vacantes_empresa_ids(vacantes_block)
    if not vacantes_empresa_ids:
        raise AssertionError("No vacantes rows found")

    counts: dict[int, int] = {}
    for empresa_id in vacantes_empresa_ids:
        counts[empresa_id] = counts.get(empresa_id, 0) + 1

    missing = [eid for eid in empresa_ids if counts.get(eid, 0) != 5]
    if missing:
        raise AssertionError(f"Expected 5 vacantes per empresa. Offenders: {sorted(missing)}")

    total_expected = len(empresa_ids) * 5
    if len(vacantes_empresa_ids) != total_expected:
        raise AssertionError(
            f"Total vacantes mismatch. Expected {total_expected}, got {len(vacantes_empresa_ids)}"
        )

    print("backup_check: OK (5 vacantes por empresa)")


if __name__ == "__main__":
    main()
