import { SectionHeading } from "@/components/SectionHeading";

const traditional = [
  "Consultoría amplia y costosa.",
  "Dashboards sin interpretación.",
  "Herramientas difíciles de adoptar.",
  "Automatización sin contexto.",
  "Datos sensibles sin proceso claro."
];

const dataorchestra = [
  "Diagnóstico inicial controlado.",
  "Hallazgos y recomendaciones.",
  "Flujo simple con CSV anonimizados.",
  "IA y análisis con revisión humana.",
  "Privacidad, trazabilidad y auditoría."
];

export function DifferentiationSection() {
  return (
    <section id="diferenciacion" className="section-band py-20">
      <div className="site-shell">
        <SectionHeading
          eyebrow="Diferenciación"
          title="No vendemos humo. No prometemos magia. Diagnosticamos con método."
          description="DataOrchestra AI se ubica entre la planilla aislada y la consultoría analítica compleja. Está pensado para PyMEs que necesitan entender mejor su negocio sin iniciar todavía un proyecto tecnológico grande."
          align="center"
        />

        <div className="mt-12 grid gap-5 lg:grid-cols-2">
          <div className="rounded border border-white/10 bg-panel/70 p-5">
            <h3 className="text-lg font-semibold text-white">Enfoque tradicional</h3>
            <ul className="mt-5 grid gap-3">
              {traditional.map((item) => (
                <li key={item} className="rounded border border-white/8 bg-ink/50 px-4 py-3 text-sm text-slate-300">
                  {item}
                </li>
              ))}
            </ul>
          </div>

          <div className="rounded border border-cyan/25 bg-cyan/8 p-5">
            <h3 className="text-lg font-semibold text-white">DataOrchestra AI</h3>
            <ul className="mt-5 grid gap-3">
              {dataorchestra.map((item) => (
                <li key={item} className="rounded border border-cyan/16 bg-ink/50 px-4 py-3 text-sm font-medium text-white">
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
