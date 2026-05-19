import type { Metadata } from "next";
import { Database, Fingerprint, FolderLock, ShieldAlert, UserCheck } from "lucide-react";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { SectionHeading } from "@/components/SectionHeading";

export const metadata: Metadata = {
  title: "Privacidad | DataOrchestra AI",
  description: "Criterios de privacidad, datos anonimizados, trazabilidad y revisión humana en DataOrchestra AI."
};

const principles = [
  {
    title: "Datos anonimizados",
    text: "El piloto trabaja con ventas, productos y stock sin datos personales innecesarios.",
    icon: Database
  },
  {
    title: "Bloqueo preventivo",
    text: "Si el preflight detecta señales de datos sensibles, el proceso se detiene.",
    icon: ShieldAlert
  },
  {
    title: "Fingerprints SHA-256",
    text: "Los archivos originales quedan registrados para controlar cambios posteriores.",
    icon: Fingerprint
  },
  {
    title: "Separación por cliente",
    text: "Cada cliente opera en una carpeta separada para evitar mezcla de archivos.",
    icon: FolderLock
  },
  {
    title: "Revisión humana",
    text: "Ningún informe se entrega automáticamente; primero debe aprobarse.",
    icon: UserCheck
  }
];

export default function PrivacidadPage() {
  return (
    <main>
      <Header />
      <section className="section-band py-20">
        <div className="site-shell">
          <SectionHeading
            eyebrow="Privacidad"
            title="Privacidad, trazabilidad y revisión antes de la entrega"
            description="DataOrchestra AI está diseñado para minimizar riesgos durante el primer piloto controlado. La prioridad es trabajar con datos anonimizados, bloquear hallazgos sensibles y mantener evidencia de cada paso relevante."
          />

          <div className="mt-10 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {principles.map((item) => {
              const Icon = item.icon;
              return (
                <article key={item.title} className="rounded border border-white/10 bg-panel/75 p-5">
                  <Icon className="h-6 w-6 text-cyan" aria-hidden="true" />
                  <h2 className="mt-4 text-lg font-semibold text-white">{item.title}</h2>
                  <p className="mt-2 text-sm leading-6 text-slate-300">{item.text}</p>
                </article>
              );
            })}
          </div>

          <section className="mt-10 rounded border border-amber/20 bg-amber/8 p-5">
            <h2 className="text-xl font-semibold text-white">Qué no se debe enviar</h2>
            <p className="mt-3 text-sm leading-6 text-slate-200">
              No se deben enviar nombres de personas, teléfonos, emails, direcciones, DNI, datos bancarios, información
              médica, laboral, legal, fiscal personal o cualquier dato sensible que no sea necesario para el diagnóstico
              comercial.
            </p>
          </section>
        </div>
      </section>
      <Footer />
    </main>
  );
}
