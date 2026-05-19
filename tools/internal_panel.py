from __future__ import annotations

from pathlib import Path
import os
import sys

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dataorchestra.cli import (
    run_analysis,
    run_approval,
    run_close_pilot,
    run_export_pdf,
    run_full_run,
    run_init_client,
    run_prepare_runtime,
    run_preflight,
    run_status,
)
from dataorchestra.panel_support import client_label, list_client_dirs, raw_file_table, read_text_preview


st.set_page_config(page_title="DataOrchestra AI - Panel interno", layout="wide")


def main() -> None:
    st.title("DataOrchestra AI - Panel interno local")
    st.caption("Herramienta privada para operar pilotos controlados. No es portal de clientes ni SaaS.")

    clients_root = runtime_sidebar()
    selected_client = sidebar(clients_root)

    if selected_client is None:
        st.info("Crea o selecciona un cliente para comenzar.")
        return

    status = run_status(selected_client)
    render_status_header(status)

    tabs = st.tabs(["Estado", "Archivos raw", "Operacion", "Entregables", "Auditoria"])
    with tabs[0]:
        render_status(status)
    with tabs[1]:
        render_raw_files(selected_client)
    with tabs[2]:
        render_operations(selected_client)
    with tabs[3]:
        render_outputs(selected_client)
    with tabs[4]:
        render_audit(selected_client)


def runtime_sidebar() -> Path:
    st.sidebar.header("Runtime")
    default_root = os.environ.get("DATAORCHESTRA_CLIENTS_ROOT") or str(ROOT / "clients")
    clients_root = Path(st.sidebar.text_input("Raiz de clientes", value=default_root))
    with st.sidebar.expander("Preparar runtime seguro", expanded=False):
        runtime_dir = st.text_input("Runtime dir", value=str(Path.home() / "DataOrchestra_Runtime"))
        if st.button("Crear estructura runtime", use_container_width=True):
            result = run_prepare_runtime(runtime_dir)
            st.json(result)
            st.info(f"Raiz recomendada de clientes: {result['recommended_clients_root']}")
    return clients_root


def sidebar(clients_root: Path) -> Path | None:
    st.sidebar.header("Clientes")
    with st.sidebar.expander("Crear cliente", expanded=False):
        client_id = st.text_input("ID del cliente", placeholder="cliente_002")
        display_name = st.text_input("Nombre visible", placeholder="Cliente piloto 002")
        business_type = st.text_input("Rubro", value="Pendiente")
        currency = st.text_input("Moneda", value="ARS")
        if st.button("Crear cliente", use_container_width=True):
            try:
                result = run_init_client(
                    clients_root,
                    client_id=client_id,
                    display_name=display_name or None,
                    business_type=business_type,
                    currency=currency,
                )
                st.sidebar.json(result)
                if result.get("can_continue"):
                    st.rerun()
            except ValueError as exc:
                st.sidebar.error(str(exc))

    clients = list_client_dirs(clients_root)
    if not clients:
        return None

    selected = st.sidebar.selectbox("Cliente", clients, format_func=client_label)
    st.sidebar.caption(str(selected))
    return selected


def render_status_header(status: dict) -> None:
    c1, c2, c3 = st.columns(3)
    c1.metric("Cliente", status["client_id"])
    c2.metric("Etapa", status["current_stage"])
    c3.metric("Raw listos", "si" if status["raw_files"]["ready"] else "no")
    st.info(status["next_action"])


def render_status(status: dict) -> None:
    st.subheader("Estado operativo")
    st.json(status)


def render_raw_files(client_dir: Path) -> None:
    st.subheader("Archivos raw")
    st.dataframe(raw_file_table(client_dir), use_container_width=True, hide_index=True)
    st.warning("No reemplaces archivos raw despues de un preflight aprobado. Si cambian, ejecuta preflight nuevamente.")

    uploads = st.file_uploader(
        "Cargar CSV anonimizados",
        type="csv",
        accept_multiple_files=True,
        help="Usar exactamente ventas.csv, productos.csv y stock.csv.",
    )
    confirm = st.checkbox("Confirmo que estos archivos estan anonimizados y pertenecen al cliente seleccionado.")
    if st.button("Guardar en raw/", disabled=not uploads or not confirm):
        raw_dir = client_dir / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        saved = []
        for upload in uploads:
            if upload.name not in {"ventas.csv", "productos.csv", "stock.csv"}:
                st.error(f"Nombre no permitido: {upload.name}")
                continue
            target = raw_dir / upload.name
            target.write_bytes(upload.getbuffer())
            saved.append(upload.name)
        if saved:
            st.success(f"Archivos guardados: {', '.join(saved)}")
            st.rerun()


def render_operations(client_dir: Path) -> None:
    st.subheader("Operacion controlada")
    c1, c2, c3 = st.columns(3)
    if c1.button("Ejecutar preflight", use_container_width=True):
        st.json(run_preflight(client_dir))
    if c2.button("Ejecutar analisis", use_container_width=True):
        st.json(run_analysis(client_dir))
    if c3.button("Full-run", use_container_width=True):
        st.json(run_full_run(client_dir))

    st.divider()
    st.subheader("Aprobacion humana")
    reviewer = st.text_input("Revisor")
    notes = st.text_area("Notas de revision")
    confirm = st.checkbox("Confirmo que revise el borrador, privacidad, metricas y recomendaciones.")
    if st.button("Aprobar entrega", disabled=not reviewer.strip() or not notes.strip() or not confirm):
        st.json(run_approval(client_dir, reviewer=reviewer, notes=notes, confirm_human_review=confirm))

    st.divider()
    st.subheader("PDF")
    if st.button("Exportar informe aprobado a PDF"):
        st.json(run_export_pdf(client_dir))

    st.divider()
    st.subheader("Cierre de piloto")
    close_reviewer = st.text_input("Responsable de cierre")
    close_notes = st.text_area("Notas de cierre")
    outcome = st.selectbox("Resultado", ["completed", "needs_follow_up", "converted_to_service", "not_viable"])
    confirm_close = st.checkbox("Confirmo cierre operativo y revision de retencion/borrado de datos.")
    if st.button("Cerrar piloto", disabled=not close_reviewer.strip() or not close_notes.strip() or not confirm_close):
        st.json(
            run_close_pilot(
                client_dir,
                reviewer=close_reviewer,
                notes=close_notes,
                outcome=outcome,
                confirm_close=confirm_close,
            )
        )


def render_outputs(client_dir: Path) -> None:
    st.subheader("Entregables")
    reports = client_dir / "reports"
    files = [
        reports / "diagnostico_borrador.md",
        reports / "diagnostico_borrador.html",
        reports / "diagnostico_aprobado.md",
        reports / "diagnostico_aprobado.html",
        reports / "diagnostico_aprobado.pdf",
    ]
    for path in files:
        if path.exists():
            st.write(f"**{path.name}** - {path.stat().st_size} bytes")
            if path.suffix == ".md":
                st.text_area(path.name, read_text_preview(path), height=220)
        else:
            st.caption(f"No existe: {path.name}")


def render_audit(client_dir: Path) -> None:
    st.subheader("Auditoria")
    audit_path = client_dir / "logs" / "audit.jsonl"
    if not audit_path.exists():
        st.info("Todavia no hay audit log.")
        return
    st.code(read_text_preview(audit_path, max_chars=12000), language="json")


if __name__ == "__main__":
    main()
