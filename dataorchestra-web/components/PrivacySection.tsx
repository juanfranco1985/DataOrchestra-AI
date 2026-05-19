import { CheckCircle2, Fingerprint, FolderLock, History, LockKeyhole, ScrollText, ShieldCheck, UserCheck } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { SectionHeading } from "@/components/SectionHeading";

const safeguards: Array<{ title: string; icon: LucideIcon }> = [
  { title: "Validación de privacidad", icon: ShieldCheck },
  { title: "Bloqueo de datos sensibles", icon: LockKeyhole },
  { title: "Fingerprints SHA-256", icon: Fingerprint },
  { title: "Auditoría de eventos", icon: ScrollText },
  { title: "Historial de corridas por cliente", icon: History },
  { title: "Separación de carpetas por cliente", icon: FolderLock },
  { title: "Revisión humana obligatoria", icon: UserCheck },
  { title: "Informe final aprobado antes de entrega", icon: CheckCircle2 }
];

export function PrivacySection() {
  return (
    <section id="privacidad" className="section-band bg-graphite/35 py-20">
      <div className="site-shell grid gap-10 lg:grid-cols-[0.95fr_1.05fr] lg:items-center">
        <SectionHeading
          eyebrow="Privacidad y trazabilidad"
          title="Privacidad y auditoría desde el inicio"
          description="El servicio está diseñado para trabajar con datos anonimizados y controles previos. Antes de analizar, DataOrchestra AI valida que los archivos no contengan información sensible innecesaria y registra eventos relevantes del proceso."
        />

        <div className="rounded border border-mint/20 bg-panel/75 p-5">
          <div className="grid gap-3 sm:grid-cols-2">
            {safeguards.map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.title} className="flex items-start gap-3 rounded border border-white/10 bg-ink/55 p-4">
                  <Icon className="mt-0.5 h-5 w-5 shrink-0 text-mint" aria-hidden="true" />
                  <p className="text-sm font-medium leading-6 text-white">{item.title}</p>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
