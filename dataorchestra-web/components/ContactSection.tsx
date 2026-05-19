import { Mail, ShieldAlert } from "lucide-react";
import { SectionHeading } from "@/components/SectionHeading";

export function ContactSection() {
  return (
    <section id="contacto" className="section-band py-20">
      <div className="site-shell grid gap-10 lg:grid-cols-[0.9fr_1.1fr]">
        <div>
          <SectionHeading
            eyebrow="Contacto"
            title="¿Querés evaluar si tus datos sirven para un diagnóstico piloto?"
            description="Podemos revisar si tus archivos de ventas, productos y stock son aptos para un primer diagnóstico comercial controlado."
          />
          <div className="mt-8 rounded border border-amber/25 bg-amber/8 p-4">
            <div className="flex gap-3">
              <ShieldAlert className="mt-0.5 h-5 w-5 shrink-0 text-amber" aria-hidden="true" />
              <p className="text-sm leading-6 text-slate-200">
                No compartas datos sensibles en este formulario. El intercambio de archivos debe realizarse únicamente
                mediante un proceso acordado y con datos anonimizados.
              </p>
            </div>
          </div>
        </div>

        <form className="rounded border border-white/10 bg-panel/78 p-5" aria-label="Formulario preparado para integración futura">
          <div className="mb-5 flex items-center gap-3 border-b border-white/10 pb-5">
            <div className="flex h-10 w-10 items-center justify-center rounded border border-cyan/30 bg-cyan/10">
              <Mail className="h-5 w-5 text-cyan" aria-hidden="true" />
            </div>
            <div>
              <p className="font-semibold text-white">Solicitud de evaluación inicial</p>
              <p className="text-sm text-slate-400">Formulario visual preparado para backend futuro.</p>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <label className="grid gap-2 text-sm font-medium text-slate-200">
              Nombre
              <input className="focus-ring rounded border border-white/12 bg-ink px-3 py-3 text-white" name="name" />
            </label>
            <label className="grid gap-2 text-sm font-medium text-slate-200">
              Empresa
              <input className="focus-ring rounded border border-white/12 bg-ink px-3 py-3 text-white" name="company" />
            </label>
            <label className="grid gap-2 text-sm font-medium text-slate-200">
              Email
              <input className="focus-ring rounded border border-white/12 bg-ink px-3 py-3 text-white" name="email" type="email" />
            </label>
            <label className="grid gap-2 text-sm font-medium text-slate-200">
              Rubro
              <input className="focus-ring rounded border border-white/12 bg-ink px-3 py-3 text-white" name="industry" />
            </label>
          </div>

          <label className="mt-4 grid gap-2 text-sm font-medium text-slate-200">
            Mensaje
            <textarea className="focus-ring min-h-32 rounded border border-white/12 bg-ink px-3 py-3 text-white" name="message" />
          </label>

          <label className="mt-4 flex items-start gap-3 text-sm leading-6 text-slate-300">
            <input type="checkbox" className="mt-1 h-4 w-4 rounded border-white/20 bg-ink" />
            Confirmo que entiendo que el piloto trabaja con datos anonimizados y revisión humana.
          </label>

          <button
            type="button"
            className="focus-ring mt-6 w-full rounded bg-cyan px-5 py-3 text-sm font-bold text-ink transition hover:bg-white"
          >
            Solicitar evaluación inicial
          </button>
          <p className="mt-3 text-center text-xs text-slate-500">En v0.1 este formulario no envía información.</p>
        </form>
      </div>
    </section>
  );
}
