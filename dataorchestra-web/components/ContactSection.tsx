import { ShieldAlert } from "lucide-react";
import { ContactForm } from "@/components/ContactForm";
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

        <ContactForm />
      </div>
    </section>
  );
}
