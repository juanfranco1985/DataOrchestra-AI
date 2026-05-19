import { FlaskConical, FileText, Lock, Target, UserRoundCheck, Workflow } from "lucide-react";
import { SectionHeading } from "@/components/SectionHeading";

const pilotItems = [
  { label: "Alcance limitado", icon: Target },
  { label: "Datos anonimizados", icon: Lock },
  { label: "Cliente real de bajo riesgo", icon: UserRoundCheck },
  { label: "Diagnóstico revisado manualmente", icon: Workflow },
  { label: "Informe ejecutivo", icon: FileText },
  { label: "Aprendizaje operativo", icon: FlaskConical }
];

export function PilotSection() {
  return (
    <section id="piloto" className="section-band bg-graphite/35 py-20">
      <div className="site-shell grid gap-10 lg:grid-cols-[1fr_0.9fr] lg:items-center">
        <SectionHeading
          eyebrow="Estado actual"
          title="Actualmente en etapa de Primer Piloto Real Controlado"
          description="DataOrchestra AI se encuentra en una etapa inicial controlada. El servicio se ofrece con alcance limitado, revisión personalizada y foco en clientes de bajo riesgo. No es una plataforma pública autoservicio ni un SaaS abierto."
        />

        <div className="rounded border border-amber/22 bg-panel/80 p-5">
          <div className="grid gap-3 sm:grid-cols-2">
            {pilotItems.map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.label} className="flex items-center gap-3 rounded border border-white/10 bg-ink/55 p-4">
                  <Icon className="h-5 w-5 text-amber" aria-hidden="true" />
                  <span className="text-sm font-medium text-white">{item.label}</span>
                </div>
              );
            })}
          </div>
          <p className="mt-5 rounded border border-mint/20 bg-mint/8 p-4 text-sm leading-6 text-slate-200">
            Esta etapa permite validar el valor real del diagnóstico antes de avanzar hacia una operación más escalable.
          </p>
        </div>
      </div>
    </section>
  );
}
