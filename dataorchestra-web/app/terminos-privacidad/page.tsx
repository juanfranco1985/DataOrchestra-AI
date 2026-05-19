import type { Metadata } from "next";
import { AlertTriangle, ClipboardCheck, Database, FileCheck2, LockKeyhole, Scale, ShieldCheck } from "lucide-react";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { SectionHeading } from "@/components/SectionHeading";

export const metadata: Metadata = {
  title: "Terminos y privacidad | DataOrchestra AI",
  description:
    "Terminos de uso, alcance del piloto, privacidad, datos anonimizados, limitaciones y revision humana de DataOrchestra AI."
};

const principles = [
  {
    title: "Servicio supervisado",
    text: "DataOrchestra AI opera como diagnostico comercial controlado para PyMEs. No es una plataforma publica, autoservicio ni SaaS abierto.",
    icon: ClipboardCheck
  },
  {
    title: "Datos anonimizados",
    text: "El proceso esta diseñado para trabajar con archivos comerciales sin datos personales o sensibles innecesarios.",
    icon: Database
  },
  {
    title: "Revision humana",
    text: "Los informes no se entregan automaticamente. Todo resultado queda sujeto a revision y aprobacion antes de compartirse.",
    icon: FileCheck2
  },
  {
    title: "Limitaciones claras",
    text: "El diagnostico no garantiza resultados comerciales ni reemplaza asesoramiento legal, contable, fiscal o financiero.",
    icon: Scale
  }
];

const termsSections = [
  {
    title: "1. Estado del servicio",
    body:
      "DataOrchestra AI se encuentra en etapa de Primer Piloto Real Controlado. El servicio se ofrece con alcance limitado, supervision humana y foco en clientes de bajo riesgo. La web institucional no representa una plataforma final escalable ni un producto autoservicio."
  },
  {
    title: "2. Alcance del diagnostico",
    body:
      "El diagnostico puede revisar datos anonimizados de ventas, productos y stock para detectar metricas, alertas, recomendaciones, concentracion, margen, rotacion e inconsistencias. El alcance concreto de cada piloto debe acordarse antes de recibir archivos."
  },
  {
    title: "3. Datos aceptados",
    body:
      "Los archivos esperados son ventas.csv, productos.csv y stock.csv. Pueden incluir fechas, cantidades, importes, costos, precios, categorias, codigos internos de producto y existencias, siempre que no identifiquen personas ni incluyan informacion sensible innecesaria."
  },
  {
    title: "4. Datos no aceptados",
    body:
      "No deben enviarse nombres de personas, telefonos, emails, direcciones, DNI, CUIT/CUIL personales, datos bancarios, datos medicos, informacion laboral personal, informacion legal sensible ni datos fiscales personales. Si se detectan datos sensibles, el proceso puede bloquearse hasta su correccion."
  },
  {
    title: "5. Formulario de contacto",
    body:
      "El formulario de la web solo prepara una solicitud inicial por correo o copia de texto. No debe usarse para enviar archivos, datos sensibles ni informacion confidencial. El intercambio de archivos debe realizarse unicamente mediante un proceso acordado."
  },
  {
    title: "6. Trazabilidad y auditoria",
    body:
      "Durante el flujo operativo pueden registrarse fingerprints SHA-256, eventos de auditoria, reportes de preflight, estados de corrida y aprobaciones humanas. Estos registros ayudan a mantener evidencia sobre archivos revisados, cambios y decisiones operativas."
  },
  {
    title: "7. Retencion y borrado",
    body:
      "La retencion de datos debe definirse por piloto. Como criterio inicial, los archivos raw se conservan solo mientras dure la revision operativa, los informes aprobados segun el acuerdo comercial y los logs/fingerprints mientras exista necesidad de trazabilidad. El cierre del piloto debe incluir revision de retencion o borrado."
  },
  {
    title: "8. Responsabilidad del cliente",
    body:
      "El cliente es responsable de entregar datos anonimizados, contar con autorizacion para compartirlos, validar que no incluyan informacion sensible innecesaria y revisar el informe antes de tomar decisiones comerciales."
  },
  {
    title: "9. Limitacion de resultados",
    body:
      "DataOrchestra AI puede aportar hallazgos y recomendaciones basadas en los datos disponibles, pero no garantiza aumento de ventas, mejora de margen, ahorro, continuidad comercial ni resultados economicos especificos."
  },
  {
    title: "10. Cambios en estos terminos",
    body:
      "Estos terminos pueden actualizarse a medida que el proyecto evolucione. Para pilotos reales, las condiciones especificas deben quedar confirmadas por escrito antes de iniciar el intercambio de archivos."
  }
];

const privacyControls = [
  "Validacion previa de privacidad y estructura.",
  "Bloqueo ante datos sensibles innecesarios.",
  "Separacion operativa por cliente.",
  "Fingerprints SHA-256 para integridad.",
  "Revision humana antes de la entrega.",
  "Cierre operativo con revision de retencion o borrado."
];

export default function TerminosPrivacidadPage() {
  return (
    <main>
      <Header />
      <section className="section-band py-20">
        <div className="site-shell">
          <SectionHeading
            eyebrow="Terminos y privacidad"
            title="Condiciones claras para un piloto comercial controlado"
            description="Esta pagina resume el alcance del servicio, el uso de datos anonimizados, los limites actuales y los criterios de privacidad de DataOrchestra AI."
          />

          <div className="mt-6 rounded border border-amber/25 bg-amber/8 p-4">
            <div className="flex gap-3">
              <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber" aria-hidden="true" />
              <p className="text-sm leading-6 text-slate-200">
                Este texto es una base institucional y operativa. No reemplaza una revision legal formal ni constituye
                por si solo un contrato definitivo para clientes reales.
              </p>
            </div>
          </div>

          <div className="mt-10 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
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

          <div className="mt-10 grid gap-5 lg:grid-cols-[1fr_0.42fr] lg:items-start">
            <div className="grid gap-4">
              {termsSections.map((section) => (
                <article key={section.title} className="rounded border border-white/10 bg-panel/75 p-5">
                  <h2 className="text-xl font-semibold text-white">{section.title}</h2>
                  <p className="mt-3 text-sm leading-6 text-slate-300">{section.body}</p>
                </article>
              ))}
            </div>

            <aside className="grid gap-5">
              <section className="rounded border border-mint/20 bg-mint/8 p-5">
                <ShieldCheck className="h-6 w-6 text-mint" aria-hidden="true" />
                <h2 className="mt-4 text-xl font-semibold text-white">Controles de privacidad</h2>
                <ul className="mt-5 grid gap-3">
                  {privacyControls.map((item) => (
                    <li key={item} className="flex gap-3 text-sm leading-6 text-slate-200">
                      <LockKeyhole className="mt-0.5 h-5 w-5 shrink-0 text-mint" aria-hidden="true" />
                      {item}
                    </li>
                  ))}
                </ul>
              </section>

              <section className="rounded border border-white/10 bg-panel/75 p-5">
                <h2 className="text-xl font-semibold text-white">Ultima actualizacion</h2>
                <p className="mt-3 text-sm leading-6 text-slate-300">19 de mayo de 2026.</p>
              </section>
            </aside>
          </div>
        </div>
      </section>
      <Footer />
    </main>
  );
}
