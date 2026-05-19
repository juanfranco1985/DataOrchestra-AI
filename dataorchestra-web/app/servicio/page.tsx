import type { Metadata } from "next";
import { CheckCircle2, FileText, ShieldCheck, XCircle } from "lucide-react";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { SectionHeading } from "@/components/SectionHeading";

export const metadata: Metadata = {
  title: "Servicio | DataOrchestra AI",
  description: "Alcance del diagnóstico comercial controlado para PyMEs con datos anonimizados y revisión humana."
};

const includes = [
  "Validación inicial de datos y privacidad.",
  "Diagnóstico sobre ventas, margen, stock y concentración.",
  "Alertas priorizadas y recomendaciones respaldadas por evidencia.",
  "Informe ejecutivo aprobado para entrega controlada."
];

const excludes = [
  "Integraciones con sistemas del cliente en esta etapa.",
  "Panel autoservicio o acceso público de clientes.",
  "Garantías de aumento de ventas, margen o ahorro.",
  "Asesoramiento legal, fiscal, contable o financiero."
];

export default function ServicioPage() {
  return (
    <main>
      <Header />
      <section className="section-band py-20">
        <div className="site-shell">
          <SectionHeading
            eyebrow="Servicio"
            title="Diagnóstico comercial controlado para PyMEs"
            description="Un servicio supervisado para revisar datos anonimizados de ventas, productos y stock, detectar señales comerciales y entregar un informe revisado por una persona antes de compartirlo con el cliente."
          />

          <div className="mt-10 grid gap-5 lg:grid-cols-3">
            <article className="rounded border border-white/10 bg-panel/75 p-5">
              <ShieldCheck className="h-6 w-6 text-mint" aria-hidden="true" />
              <h2 className="mt-4 text-xl font-semibold text-white">Requisitos</h2>
              <p className="mt-3 text-sm leading-6 text-slate-300">
                El cliente debe entregar `ventas.csv`, `productos.csv` y `stock.csv` anonimizados, aceptar el alcance
                limitado y entender que el diagnóstico no promete resultados garantizados.
              </p>
            </article>
            <article className="rounded border border-white/10 bg-panel/75 p-5">
              <FileText className="h-6 w-6 text-cyan" aria-hidden="true" />
              <h2 className="mt-4 text-xl font-semibold text-white">Entregable</h2>
              <p className="mt-3 text-sm leading-6 text-slate-300">
                El resultado es un informe ejecutivo aprobado, con métricas, alertas, recomendaciones, evidencia y
                limitaciones del análisis.
              </p>
            </article>
            <article className="rounded border border-white/10 bg-panel/75 p-5">
              <CheckCircle2 className="h-6 w-6 text-amber" aria-hidden="true" />
              <h2 className="mt-4 text-xl font-semibold text-white">Uso ideal</h2>
              <p className="mt-3 text-sm leading-6 text-slate-300">
                Primer diagnóstico de bajo riesgo para entender si los datos comerciales de una PyME pueden generar
                hallazgos útiles antes de invertir en una solución mayor.
              </p>
            </article>
          </div>

          <div className="mt-10 grid gap-5 lg:grid-cols-2">
            <section className="rounded border border-mint/20 bg-mint/8 p-5">
              <h2 className="text-xl font-semibold text-white">Incluye</h2>
              <ul className="mt-5 grid gap-3">
                {includes.map((item) => (
                  <li key={item} className="flex gap-3 text-sm leading-6 text-slate-200">
                    <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-mint" aria-hidden="true" />
                    {item}
                  </li>
                ))}
              </ul>
            </section>
            <section className="rounded border border-amber/20 bg-amber/8 p-5">
              <h2 className="text-xl font-semibold text-white">No incluye</h2>
              <ul className="mt-5 grid gap-3">
                {excludes.map((item) => (
                  <li key={item} className="flex gap-3 text-sm leading-6 text-slate-200">
                    <XCircle className="mt-0.5 h-5 w-5 shrink-0 text-amber" aria-hidden="true" />
                    {item}
                  </li>
                ))}
              </ul>
            </section>
          </div>
        </div>
      </section>
      <Footer />
    </main>
  );
}
