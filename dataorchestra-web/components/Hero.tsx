import { ArrowRight, CheckCircle2, FileText, Fingerprint, ShieldCheck } from "lucide-react";
import { siteHref } from "@/components/routes";

const controls = [
  { label: "Privacidad", icon: ShieldCheck },
  { label: "Integridad", icon: Fingerprint },
  { label: "Auditoría", icon: CheckCircle2 }
];

export function Hero() {
  return (
    <section id="inicio" className="relative isolate overflow-hidden">
      <div className="hero-grid absolute inset-0 -z-10" aria-hidden="true" />
      <img
        src={siteHref("/images/diagnostic-signal.svg")}
        alt=""
        className="pointer-events-none absolute right-0 top-12 -z-10 hidden w-[54rem] max-w-none opacity-45 lg:block"
        aria-hidden="true"
      />

      <div className="site-shell grid min-h-[calc(100vh-65px)] items-center gap-10 py-16 lg:grid-cols-[1.05fr_0.95fr] lg:py-20">
        <div className="max-w-3xl">
          <p className="mb-5 inline-flex rounded border border-mint/30 bg-mint/10 px-3 py-1 text-sm font-medium text-mint">
            v2.1 - Version Integradora
          </p>
          <h1 className="max-w-4xl text-4xl font-semibold leading-tight tracking-normal text-white sm:text-5xl lg:text-6xl">
            Transformamos datos simples de tu PyME en decisiones comerciales claras
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-300">
            DataOrchestra AI analiza ventas, productos y stock para detectar oportunidades, alertas y problemas de
            margen, con privacidad, trazabilidad y revisión humana antes de entregar resultados.
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <a
              href="#contacto"
              className="focus-ring inline-flex items-center justify-center gap-2 rounded bg-cyan px-5 py-3 text-sm font-bold text-ink transition hover:bg-white"
            >
              Solicitar diagnóstico piloto
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </a>
            <a
              href="#proceso"
              className="focus-ring inline-flex items-center justify-center rounded border border-white/16 px-5 py-3 text-sm font-semibold text-white transition hover:border-white/35 hover:bg-white/6"
            >
              Ver cómo funciona
            </a>
          </div>
        </div>

        <div className="relative">
          <div className="rounded border border-white/12 bg-panel/86 p-5 shadow-soft backdrop-blur">
            <div className="flex items-center justify-between border-b border-white/10 pb-4">
              <div>
                <p className="text-sm text-slate-400">Diagnóstico comercial</p>
                <p className="mt-1 text-lg font-semibold text-white">flujo_controlado.run</p>
              </div>
              <span className="rounded bg-amber/12 px-3 py-1 text-xs font-semibold text-amber">pending_human_review</span>
            </div>

            <div className="mt-5 grid gap-3">
              <div className="rounded border border-white/10 bg-ink/60 p-4">
                <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-white">
                  <FileText className="h-4 w-4 text-cyan" aria-hidden="true" />
                  Archivos recibidos
                </div>
                <div className="grid gap-2 text-sm text-slate-300 sm:grid-cols-3">
                  <span className="rounded bg-white/6 px-3 py-2">ventas.csv</span>
                  <span className="rounded bg-white/6 px-3 py-2">productos.csv</span>
                  <span className="rounded bg-white/6 px-3 py-2">stock.csv</span>
                </div>
              </div>

              <div className="grid gap-3 sm:grid-cols-3">
                {controls.map((item) => {
                  const Icon = item.icon;
                  return (
                    <div key={item.label} className="rounded border border-white/10 bg-ink/52 p-4">
                      <Icon className="mb-3 h-5 w-5 text-mint" aria-hidden="true" />
                      <p className="text-sm font-medium text-white">{item.label}</p>
                    </div>
                  );
                })}
              </div>

              <div className="rounded border border-mint/20 bg-mint/8 p-4">
                <p className="text-sm text-slate-300">Resultado esperado</p>
                <p className="mt-1 text-lg font-semibold text-white">Informe ejecutivo revisado</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
