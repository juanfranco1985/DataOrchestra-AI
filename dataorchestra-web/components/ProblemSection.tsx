import { AlertTriangle, BarChart3, Boxes, DatabaseZap, SearchX, TrendingDown } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { SectionHeading } from "@/components/SectionHeading";

const problems: Array<{ title: string; description: string; icon: LucideIcon }> = [
  {
    title: "Margen poco visible",
    description: "Productos que venden mucho pueden estar dejando poco margen real.",
    icon: TrendingDown
  },
  {
    title: "Stock inmovilizado",
    description: "Capital detenido en productos con baja rotación o sobrecompra.",
    icon: Boxes
  },
  {
    title: "Facturación concentrada",
    description: "Dependencia excesiva de pocos productos, categorías o líneas comerciales.",
    icon: BarChart3
  },
  {
    title: "Oportunidades no detectadas",
    description: "Patrones comerciales que quedan ocultos en planillas o exportaciones.",
    icon: SearchX
  },
  {
    title: "Datos inconsistentes",
    description: "Columnas incompletas, fechas inválidas o valores que impiden analizar.",
    icon: DatabaseZap
  },
  {
    title: "Decisiones por intuición",
    description: "Acciones tomadas sin suficiente evidencia sobre ventas, margen y stock.",
    icon: AlertTriangle
  }
];

export function ProblemSection() {
  return (
    <section id="problema" className="section-band bg-graphite/35 py-20">
      <div className="site-shell">
        <SectionHeading
          eyebrow="El problema"
          title="Muchas PyMEs tienen datos, pero no siempre tienen claridad"
          description="Muchas empresas pequeñas y medianas registran ventas, productos y stock en planillas, sistemas de facturación o archivos exportados. Sin embargo, esos datos suelen quedar sin analizar o se revisan solo de forma superficial."
        />

        <div className="mt-10 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {problems.map((item) => {
            const Icon = item.icon;
            return (
              <article key={item.title} className="rounded border border-white/10 bg-panel/72 p-5">
                <Icon className="h-5 w-5 text-amber" aria-hidden="true" />
                <h3 className="mt-4 text-lg font-semibold text-white">{item.title}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-300">{item.description}</p>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
