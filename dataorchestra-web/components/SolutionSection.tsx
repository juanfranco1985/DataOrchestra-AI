import { FileSpreadsheet } from "lucide-react";
import { SectionHeading } from "@/components/SectionHeading";

const files = [
  {
    name: "ventas.csv",
    description: "Registro de operaciones, fechas, cantidades, importes y comportamiento comercial."
  },
  {
    name: "productos.csv",
    description: "Catálogo de productos, categorías, costos, precios y atributos comerciales."
  },
  {
    name: "stock.csv",
    description: "Existencias, movimientos o saldos disponibles para detectar inmovilización y oportunidades."
  }
];

export function SolutionSection() {
  return (
    <section id="solucion" className="section-band py-20">
      <div className="site-shell grid gap-10 lg:grid-cols-[0.9fr_1.1fr] lg:items-start">
        <SectionHeading
          eyebrow="La solución"
          title="Un diagnóstico comercial controlado, no una plataforma automática sin supervisión"
          description="DataOrchestra AI trabaja con datos comerciales anonimizados para generar un diagnóstico inicial sobre ventas, margen, stock y oportunidades. El sistema produce métricas, alertas y recomendaciones, pero el informe no se entrega automáticamente: queda bloqueado hasta pasar por revisión humana."
        />

        <div className="grid gap-4">
          {files.map((file) => (
            <article key={file.name} className="rounded border border-white/10 bg-panel/75 p-5">
              <div className="flex items-start gap-4">
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded border border-cyan/30 bg-cyan/10">
                  <FileSpreadsheet className="h-5 w-5 text-cyan" aria-hidden="true" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">{file.name}</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-300">{file.description}</p>
                </div>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
