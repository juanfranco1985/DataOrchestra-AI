import { BadgeCheck, ClipboardCheck, Database, FileCheck2, Fingerprint, UserCheck } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { SectionHeading } from "@/components/SectionHeading";

const steps: Array<{ step: string; title: string; description: string; icon: LucideIcon }> = [
  {
    step: "Paso 1",
    title: "Preparación del cliente",
    description: "Se crea una carpeta separada para cada cliente y se trabaja con datos anonimizados.",
    icon: Database
  },
  {
    step: "Paso 2",
    title: "Preflight de seguridad",
    description: "Se validan privacidad, columnas requeridas, fechas, valores numéricos e integridad de archivos.",
    icon: ClipboardCheck
  },
  {
    step: "Paso 3",
    title: "Fingerprints SHA-256",
    description: "Los archivos originales se registran mediante fingerprints para mantener trazabilidad.",
    icon: Fingerprint
  },
  {
    step: "Paso 4",
    title: "Análisis comercial",
    description: "El motor analítico procesa ventas, margen, stock, concentración y oportunidades.",
    icon: BadgeCheck
  },
  {
    step: "Paso 5",
    title: "Revisión humana",
    description: "El borrador queda en estado pending_human_review hasta que una persona valida los hallazgos.",
    icon: UserCheck
  },
  {
    step: "Paso 6",
    title: "Entrega final",
    description: "Se genera un informe ejecutivo con alertas, recomendaciones y próximos pasos.",
    icon: FileCheck2
  }
];

export function ProcessSection() {
  return (
    <section id="proceso" className="section-band bg-graphite/35 py-20">
      <div className="site-shell">
        <SectionHeading
          eyebrow="Cómo funciona"
          title="Proceso diseñado para reducir riesgos y aumentar confianza"
          description="El flujo está pensado para separar clientes, validar datos antes del análisis y evitar entregas automáticas sin revisión."
          align="center"
        />

        <div className="mt-12 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {steps.map((item) => {
            const Icon = item.icon;
            return (
              <article key={item.title} className="rounded border border-white/10 bg-panel/78 p-5">
                <div className="flex items-center justify-between gap-3">
                  <span className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">{item.step}</span>
                  <Icon className="h-5 w-5 text-mint" aria-hidden="true" />
                </div>
                <h3 className="mt-5 text-lg font-semibold text-white">{item.title}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-300">{item.description}</p>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
