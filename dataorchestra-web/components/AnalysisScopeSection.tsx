import { Activity, AlertCircle, Archive, BarChart2, LineChart, PackageCheck, RefreshCcw, Scale } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { SectionHeading } from "@/components/SectionHeading";

const scope: Array<{ title: string; icon: LucideIcon }> = [
  { title: "Productos de alto volumen y bajo margen", icon: Scale },
  { title: "Productos de margen alto pero baja rotación", icon: LineChart },
  { title: "Stock inmovilizado", icon: Archive },
  { title: "Concentración de facturación", icon: BarChart2 },
  { title: "Categorías con bajo rendimiento", icon: Activity },
  { title: "Oportunidades de reposición", icon: PackageCheck },
  { title: "Inconsistencias en datos", icon: RefreshCcw },
  { title: "Alertas comerciales prioritarias", icon: AlertCircle }
];

export function AnalysisScopeSection() {
  return (
    <section id="alcance" className="section-band py-20">
      <div className="site-shell">
        <SectionHeading
          eyebrow="Qué analizamos"
          title="Qué puede detectar el diagnóstico"
          description="El análisis se concentra en señales comerciales concretas que una PyME puede revisar y convertir en decisiones operativas."
        />

        <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {scope.map((item) => {
            const Icon = item.icon;
            return (
              <article key={item.title} className="rounded border border-white/10 bg-panel/72 p-5">
                <Icon className="h-5 w-5 text-cyan" aria-hidden="true" />
                <h3 className="mt-4 text-base font-semibold leading-6 text-white">{item.title}</h3>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
