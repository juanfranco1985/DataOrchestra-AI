import type { Metadata } from "next";
import { AlertCircle, BarChart3, FileCheck2, PackageSearch, TrendingDown } from "lucide-react";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { SectionHeading } from "@/components/SectionHeading";

export const metadata: Metadata = {
  title: "Demo ficticia | DataOrchestra AI",
  description: "Caso demo ficticio para mostrar el flujo de diagnóstico comercial controlado sin datos reales."
};

const findings = [
  {
    title: "Concentración de facturación",
    text: "Los principales productos concentran una parte alta de la facturación del periodo.",
    icon: BarChart3
  },
  {
    title: "Productos de bajo margen",
    text: "Algunos productos venden volumen, pero dejan margen porcentual bajo.",
    icon: TrendingDown
  },
  {
    title: "Stock bajo en producto crítico",
    text: "Un producto con rotación relevante aparece por debajo del stock mínimo.",
    icon: AlertCircle
  },
  {
    title: "Capital inmovilizado",
    text: "Un producto presenta exceso de stock frente a ventas recientes.",
    icon: PackageSearch
  }
];

export default function DemoPage() {
  return (
    <main>
      <Header />
      <section className="section-band py-20">
        <div className="site-shell">
          <SectionHeading
            eyebrow="Caso demo"
            title="Retail Santa Clara: ejemplo ficticio de diagnóstico"
            description="Este caso usa datos simulados para mostrar cómo se ve un diagnóstico comercial controlado. No representa resultados reales de ningún cliente."
          />

          <div className="mt-10 rounded border border-cyan/20 bg-panel/80 p-5">
            <div className="grid gap-4 md:grid-cols-4">
              <div>
                <p className="text-xs uppercase tracking-[0.16em] text-slate-400">Estado</p>
                <p className="mt-2 font-semibold text-mint">approved_for_delivery</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.16em] text-slate-400">Datos</p>
                <p className="mt-2 font-semibold text-white">CSV ficticios</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.16em] text-slate-400">Controles</p>
                <p className="mt-2 font-semibold text-white">Privacidad + SHA-256</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.16em] text-slate-400">Entrega</p>
                <p className="mt-2 font-semibold text-white">Informe HTML/PDF</p>
              </div>
            </div>
          </div>

          <div className="mt-10 grid gap-4 md:grid-cols-2">
            {findings.map((item) => {
              const Icon = item.icon;
              return (
                <article key={item.title} className="rounded border border-white/10 bg-panel/75 p-5">
                  <Icon className="h-6 w-6 text-amber" aria-hidden="true" />
                  <h2 className="mt-4 text-lg font-semibold text-white">{item.title}</h2>
                  <p className="mt-2 text-sm leading-6 text-slate-300">{item.text}</p>
                </article>
              );
            })}
          </div>

          <section className="mt-10 rounded border border-mint/20 bg-mint/8 p-5">
            <div className="flex gap-3">
              <FileCheck2 className="mt-1 h-6 w-6 shrink-0 text-mint" aria-hidden="true" />
              <div>
                <h2 className="text-xl font-semibold text-white">Uso del caso demo</h2>
                <p className="mt-3 text-sm leading-6 text-slate-200">
                  Sirve para explicar el proceso, entrenar la operación interna y mostrar el tipo de informe que puede
                  generarse. No debe usarse como promesa de resultados ni como evidencia de desempeño comercial real.
                </p>
              </div>
            </div>
          </section>
        </div>
      </section>
      <Footer />
    </main>
  );
}
