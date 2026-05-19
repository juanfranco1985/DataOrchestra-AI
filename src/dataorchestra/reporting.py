from __future__ import annotations

from html import escape


def render_markdown_report(analysis: dict) -> str:
    metrics = analysis["metrics"]
    sales = metrics["sales"]
    profitability = metrics["profitability"]
    stock = metrics["stock"]
    concentration = metrics["concentration"]
    alerts = analysis["alerts"]
    recommendations = analysis["recommendations"]

    lines = [
        "# DataOrchestra AI - Diagnostico borrador",
        "",
        "**Estado:** pending_human_review",
        "",
        "**Uso interno:** no entregar al cliente sin revision humana y aprobacion explicita.",
        "",
        "## Resumen ejecutivo",
        "",
        f"- Cliente: `{analysis['client_id']}`",
        f"- Periodo analizado: {_value(sales.get('periodo_inicio'))} a {_value(sales.get('periodo_fin'))}",
        f"- Ventas totales: {_money(sales['ventas_totales'])}",
        f"- Margen bruto: {_money(profitability['margen_bruto'])} ({_percent(profitability['margen_porcentaje'])})",
        f"- Unidades vendidas: {sales['unidades_vendidas']}",
        f"- Ticket promedio: {_money(sales['ticket_promedio'])}",
        f"- Valor estimado de stock: {_money(stock['valor_stock_total'])}",
        f"- Productos con stock bajo: {stock['productos_stock_bajo']}",
        f"- Productos con exceso de stock: {stock['productos_exceso']}",
        f"- Concentracion top {concentration['top_n']}: {_percent(concentration['ratio'])}",
        "",
        "## Alertas",
        "",
    ]

    if alerts:
        for alert in alerts:
            evidence = alert.get("evidence", {})
            lines.extend(
                [
                    f"- **{alert['priority']} | {alert['type']} | {alert['item']}**",
                    f"  - Hallazgo: {alert['description']}",
                    f"  - Accion sugerida: {alert['suggested_action']}",
                    f"  - Evidencia: {_format_evidence(evidence)}",
                ]
            )
    else:
        lines.append("- No se generaron alertas con los umbrales actuales.")

    lines.extend(["", "## Recomendaciones", ""])
    for recommendation in recommendations:
        evidence_ids = ", ".join(recommendation.get("evidence_alert_ids") or ["sin_alerta_especifica"])
        lines.extend(
            [
                f"- **{recommendation['priority']} | {recommendation['title']}**",
                f"  - {recommendation['detail']}",
                f"  - Evidencia asociada: {evidence_ids}",
            ]
        )

    lines.extend(
        [
            "",
            "## Evidencia y controles",
            "",
            f"- Preflight aprobado: `{analysis['evidence']['preflight_report']}`",
            "- Archivos raw usados:",
        ]
    )
    for item in analysis["evidence"]["raw_fingerprints"]:
        lines.append(f"  - `{item['name']}` | sha256 `{item['sha256']}` | {item['size_bytes']} bytes")

    lines.extend(
        [
            "",
            "## Limitaciones",
            "",
            "- Este borrador usa reglas deterministicas y datos provistos por el cliente.",
            "- Las recomendaciones son hipotesis operativas respaldadas por metricas, no promesas de resultado.",
            "- No ejecutar entrega si aparece informacion personal, dudas de calidad de datos o afirmaciones sin evidencia.",
            "- El informe requiere revision humana antes de cambiar a `approved_for_delivery`.",
            "",
        ]
    )
    return "\n".join(lines)


def render_html_report(analysis: dict, approval: dict | None = None) -> str:
    metrics = analysis["metrics"]
    sales = metrics["sales"]
    profitability = metrics["profitability"]
    stock = metrics["stock"]
    concentration = metrics["concentration"]
    alerts = analysis["alerts"]
    recommendations = analysis["recommendations"]
    status = analysis.get("report_status", "pending_human_review")
    approved = status == "approved_for_delivery"
    title = "Diagnostico ejecutivo aprobado" if approved else "Diagnostico ejecutivo borrador"
    status_label = "approved_for_delivery" if approved else "pending_human_review"

    summary_cards = [
        ("Ventas totales", _money(sales["ventas_totales"])),
        ("Margen bruto", f"{_money(profitability['margen_bruto'])} / {_percent(profitability['margen_porcentaje'])}"),
        ("Ticket promedio", _money(sales["ticket_promedio"])),
        ("Valor stock", _money(stock["valor_stock_total"])),
        ("Stock bajo", str(stock["productos_stock_bajo"])),
        ("Exceso stock", str(stock["productos_exceso"])),
        (f"Concentracion top {concentration['top_n']}", _percent(concentration["ratio"])),
        ("Unidades vendidas", str(sales["unidades_vendidas"])),
    ]

    approval_block = ""
    if approval:
        approval_block = f"""
        <section class="approval">
          <h2>Aprobacion humana</h2>
          <div class="approval-grid">
            <p><strong>Revisor</strong><span>{_html(approval.get("reviewer"))}</span></p>
            <p><strong>Fecha UTC</strong><span>{_html(approval.get("approved_at"))}</span></p>
            <p class="wide"><strong>Notas</strong><span>{_html(approval.get("notes"))}</span></p>
          </div>
        </section>
        """

    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>DataOrchestra AI - {_html(title)}</title>
  <style>
    :root {{
      --ink: #111827;
      --muted: #536172;
      --line: #d9e2ec;
      --panel: #f7fafc;
      --cyan: #0369a1;
      --mint: #047857;
      --amber: #92400e;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      background: #eef3f8;
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.55;
    }}
    main {{
      width: min(980px, calc(100% - 32px));
      margin: 32px auto;
      background: white;
      border: 1px solid var(--line);
      box-shadow: 0 20px 70px rgba(15, 23, 42, 0.12);
    }}
    header {{
      padding: 36px 40px;
      color: white;
      background: linear-gradient(135deg, #0b1b31, #123a56);
    }}
    .eyebrow {{
      margin: 0 0 10px;
      color: #8ee6f5;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.12em;
      text-transform: uppercase;
    }}
    h1, h2, h3, p {{ margin-top: 0; }}
    h1 {{ margin-bottom: 14px; font-size: 34px; line-height: 1.12; }}
    h2 {{ margin-bottom: 16px; font-size: 22px; }}
    h3 {{ margin-bottom: 8px; font-size: 15px; }}
    .subtitle {{ max-width: 760px; margin: 0; color: #dbeafe; }}
    .meta {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
      margin-top: 28px;
    }}
    .meta div, .card, .alert, .recommendation, .control, .approval-grid p {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
    }}
    .meta div {{ padding: 12px; color: var(--ink); background: #f8fbff; }}
    .meta strong, .card strong, .approval-grid strong {{ display: block; font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em; }}
    .meta span, .card span, .approval-grid span {{ display: block; margin-top: 6px; font-weight: 700; }}
    section {{ padding: 30px 40px; border-top: 1px solid var(--line); }}
    .status {{
      display: inline-block;
      padding: 6px 10px;
      border-radius: 999px;
      background: {_status_bg(status_label)};
      color: {_status_color(status_label)};
      font-size: 12px;
      font-weight: 700;
    }}
    .cards {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }}
    .card {{ padding: 14px; }}
    .alert, .recommendation {{ padding: 16px; margin-top: 12px; }}
    .priority {{ color: var(--cyan); font-weight: 700; }}
    .evidence {{ color: var(--muted); font-size: 12px; }}
    .controls {{ display: grid; gap: 10px; }}
    .control {{ padding: 12px; font-family: Consolas, monospace; font-size: 12px; word-break: break-word; }}
    .approval {{ background: #f0fdf4; }}
    .approval-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }}
    .approval-grid p {{ padding: 14px; margin: 0; background: white; }}
    .approval-grid .wide {{ grid-column: 1 / -1; }}
    .note {{ color: var(--muted); font-size: 13px; }}
    footer {{ padding: 22px 40px; color: var(--muted); border-top: 1px solid var(--line); font-size: 12px; }}
    @media (max-width: 760px) {{
      main {{ width: 100%; margin: 0; border: 0; }}
      header, section, footer {{ padding-left: 20px; padding-right: 20px; }}
      h1 {{ font-size: 28px; }}
      .meta, .cards, .approval-grid {{ grid-template-columns: 1fr; }}
    }}
    @media print {{
      body {{ background: white; }}
      main {{ width: 100%; margin: 0; border: 0; box-shadow: none; }}
      section {{ break-inside: avoid; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <p class="eyebrow">DataOrchestra AI</p>
      <h1>{_html(title)}</h1>
      <p class="subtitle">Diagnostico comercial controlado a partir de datos anonimizados de ventas, productos y stock. El resultado se entrega solo despues de revision humana.</p>
      <div class="meta">
        <div><strong>Cliente</strong><span>{_html(analysis["client_id"])}</span></div>
        <div><strong>Periodo</strong><span>{_html(_value(sales.get("periodo_inicio")))} a {_html(_value(sales.get("periodo_fin")))}</span></div>
        <div><strong>Estado</strong><span class="status">{_html(status_label)}</span></div>
      </div>
    </header>
    {approval_block}
    <section>
      <h2>Resumen ejecutivo</h2>
      <div class="cards">
        {"".join(_summary_card(label, value) for label, value in summary_cards)}
      </div>
    </section>
    <section>
      <h2>Alertas prioritarias</h2>
      {_render_html_alerts(alerts)}
    </section>
    <section>
      <h2>Recomendaciones</h2>
      {_render_html_recommendations(recommendations)}
    </section>
    <section>
      <h2>Evidencia y controles</h2>
      <p class="note">Preflight aprobado: {_html(analysis["evidence"]["preflight_report"])}</p>
      <div class="controls">
        {"".join(_fingerprint_control(item) for item in analysis["evidence"]["raw_fingerprints"])}
      </div>
    </section>
    <section>
      <h2>Limitaciones</h2>
      <p>Este diagnostico usa reglas deterministicas y datos provistos por el cliente. Las recomendaciones son hipotesis operativas respaldadas por metricas; no constituyen promesas de resultado.</p>
      <p class="note">Si aparece informacion personal, dudas de calidad de datos o afirmaciones sin evidencia, la entrega debe detenerse.</p>
    </section>
    <footer>
      DataOrchestra AI - Servicio supervisado para diagnostico comercial controlado. No constituye una plataforma SaaS publica ni autoservicio.
    </footer>
  </main>
</body>
</html>"""


def _money(value: float) -> str:
    return f"{float(value):,.2f}"


def _percent(value: float) -> str:
    return f"{float(value):.1%}"


def _value(value: object) -> str:
    return str(value) if value not in {None, ""} else "sin_dato"


def _format_evidence(evidence: dict) -> str:
    parts = []
    for key in ("source", "metric", "value", "threshold"):
        if key in evidence:
            parts.append(f"{key}={evidence[key]}")
    return "; ".join(parts) if parts else "sin_evidencia_registrada"


def _html(value: object) -> str:
    return escape(_value(value))


def _summary_card(label: str, value: str) -> str:
    return f'<div class="card"><strong>{_html(label)}</strong><span>{_html(value)}</span></div>'


def _render_html_alerts(alerts: list[dict]) -> str:
    if not alerts:
        return '<p class="note">No se generaron alertas con los umbrales actuales.</p>'
    output = []
    for alert in alerts:
        evidence = _format_evidence(alert.get("evidence", {}))
        output.append(
            f"""
            <article class="alert">
              <h3><span class="priority">{_html(alert["priority"])}</span> | {_html(alert["type"])} | {_html(alert["item"])}</h3>
              <p>{_html(alert["description"])}</p>
              <p><strong>Accion sugerida:</strong> {_html(alert["suggested_action"])}</p>
              <p class="evidence">Evidencia: {_html(evidence)}</p>
            </article>
            """
        )
    return "".join(output)


def _render_html_recommendations(recommendations: list[dict]) -> str:
    output = []
    for recommendation in recommendations:
        evidence_ids = ", ".join(recommendation.get("evidence_alert_ids") or ["sin_alerta_especifica"])
        output.append(
            f"""
            <article class="recommendation">
              <h3><span class="priority">{_html(recommendation["priority"])}</span> | {_html(recommendation["title"])}</h3>
              <p>{_html(recommendation["detail"])}</p>
              <p class="evidence">Evidencia asociada: {_html(evidence_ids)}</p>
            </article>
            """
        )
    return "".join(output)


def _fingerprint_control(item: dict) -> str:
    return f'<div class="control">{_html(item["name"])} | sha256 {_html(item["sha256"])} | {_html(item["size_bytes"])} bytes</div>'


def _status_bg(status: str) -> str:
    return "#ecfdf5" if status == "approved_for_delivery" else "#fffbeb"


def _status_color(status: str) -> str:
    return "#047857" if status == "approved_for_delivery" else "#92400e"
