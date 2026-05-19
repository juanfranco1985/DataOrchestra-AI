import type { Metadata } from "next";
import { CircleHelp, ClipboardCheck, Clock3, FileText, Mail, ShieldCheck, XCircle } from "lucide-react";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { SectionHeading } from "@/components/SectionHeading";

export const metadata: Metadata = {
  title: "Preguntas frecuentes | DataOrchestra AI",
  description:
    "Preguntas frecuentes sobre el diagnostico comercial controlado de DataOrchestra AI, datos anonimizados, alcance, privacidad y revision humana."
};

const groups = [
  {
    title: "Alcance del servicio",
    icon: ClipboardCheck,
    items: [
      {
        question: "¿DataOrchestra AI es un SaaS o una plataforma autoservicio?",
        answer:
          "No. En esta etapa es un servicio supervisado para ejecutar diagnosticos comerciales controlados. No hay acceso publico de clientes, panel autoservicio ni promesa de automatizacion total."
      },
      {
        question: "¿Que problema ayuda a resolver?",
        answer:
          "Ayuda a transformar archivos comerciales simples en hallazgos iniciales sobre ventas, margen, stock, concentracion e inconsistencias. El objetivo es aportar claridad para decidir proximos pasos, no reemplazar la gestion del negocio."
      },
      {
        question: "¿Que recibe el cliente?",
        answer:
          "Un informe ejecutivo revisado, con metricas, alertas, recomendaciones, evidencia y limitaciones. El informe no se entrega hasta pasar por revision humana."
      },
      {
        question: "¿Garantiza aumento de ventas, margen o ahorro?",
        answer:
          "No. El diagnostico puede detectar oportunidades y riesgos, pero no garantiza resultados comerciales. Las decisiones finales dependen del contexto del negocio y de la ejecucion posterior."
      }
    ]
  },
  {
    title: "Datos y privacidad",
    icon: ShieldCheck,
    items: [
      {
        question: "¿Que archivos se necesitan?",
        answer:
          "La base operativa es trabajar con ventas.csv, productos.csv y stock.csv. Los archivos deben estar anonimizados y con columnas suficientes para validar fechas, cantidades, importes, costos, precios y existencias."
      },
      {
        question: "¿Puedo enviar nombres, telefonos, emails, DNI o datos bancarios?",
        answer:
          "No. El proceso esta pensado para datos comerciales anonimizados. Si aparecen datos sensibles innecesarios, el preflight debe bloquear el flujo hasta corregirlos."
      },
      {
        question: "¿Que pasa si los archivos tienen errores?",
        answer:
          "Antes del analisis se ejecuta un preflight que revisa privacidad, columnas requeridas, fechas, valores numericos e integridad. Si hay problemas relevantes, se solicita correccion antes de continuar."
      },
      {
        question: "¿Como se mantiene trazabilidad?",
        answer:
          "Los archivos originales se registran con fingerprints SHA-256 y se generan eventos de auditoria. Esto permite saber que archivos fueron revisados y si cambiaron despues del preflight."
      }
    ]
  },
  {
    title: "Proceso y tiempos",
    icon: Clock3,
    items: [
      {
        question: "¿Cuanto demora un diagnostico piloto?",
        answer:
          "Depende de la calidad de los datos, el alcance acordado y la revision humana. Para un primer piloto, la prioridad es trabajar con un alcance limitado y evitar comprometer tiempos sin revisar los archivos."
      },
      {
        question: "¿El informe se genera automaticamente?",
        answer:
          "El sistema puede generar borradores, metricas y alertas, pero el informe queda en estado pending_human_review. Una persona debe revisar y aprobar antes de cualquier entrega."
      },
      {
        question: "¿Que ocurre despues del diagnostico?",
        answer:
          "Se revisa si los hallazgos fueron utiles, que decisiones podria tomar el cliente y si tiene sentido continuar con una segunda iteracion, seguimiento mensual o ajuste del alcance."
      },
      {
        question: "¿Se integra con mi sistema de facturacion o ERP?",
        answer:
          "No en esta etapa. El primer piloto trabaja con CSV exportados y anonimizados. Las integraciones pueden evaluarse mas adelante si el valor del diagnostico queda validado."
      }
    ]
  },
  {
    title: "Contacto inicial",
    icon: Mail,
    items: [
      {
        question: "¿Que debo enviar en el primer contacto?",
        answer:
          "Solo una descripcion breve del negocio, rubro y necesidad comercial. No se deben adjuntar archivos ni datos sensibles en el formulario o primer email."
      },
      {
        question: "¿Como se define si una PyME es apta para piloto?",
        answer:
          "Se revisa si el negocio tiene datos minimos, si puede anonimizarlos, si acepta el alcance controlado y si el caso es de bajo riesgo para una primera ejecucion real."
      }
    ]
  }
];

const notIncluded = [
  "Panel publico para clientes.",
  "Carga directa de archivos en la web.",
  "Automatizacion total sin revision humana.",
  "Garantias de resultado comercial.",
  "Asesoramiento legal, fiscal, contable o financiero."
];

export default function FaqPage() {
  return (
    <main>
      <Header />
      <section className="section-band py-20">
        <div className="site-shell">
          <SectionHeading
            eyebrow="Preguntas frecuentes"
            title="Respuestas claras antes de iniciar un piloto"
            description="Esta pagina aclara el alcance real de DataOrchestra AI, como se trabaja con datos anonimizados y que expectativas conviene tener antes de solicitar un diagnostico."
          />

          <div className="mt-10 grid gap-5 lg:grid-cols-[1fr_0.42fr] lg:items-start">
            <div className="grid gap-5">
              {groups.map((group) => {
                const Icon = group.icon;

                return (
                  <section key={group.title} className="rounded border border-white/10 bg-panel/75 p-5">
                    <div className="mb-5 flex items-center gap-3 border-b border-white/10 pb-4">
                      <div className="flex h-10 w-10 items-center justify-center rounded border border-cyan/30 bg-cyan/10">
                        <Icon className="h-5 w-5 text-cyan" aria-hidden="true" />
                      </div>
                      <h2 className="text-xl font-semibold text-white">{group.title}</h2>
                    </div>
                    <div className="grid gap-3">
                      {group.items.map((item) => (
                        <details key={item.question} className="group rounded border border-white/10 bg-ink/55 p-4">
                          <summary className="flex cursor-pointer list-none items-start justify-between gap-4 text-sm font-semibold leading-6 text-white">
                            {item.question}
                            <CircleHelp className="mt-0.5 h-5 w-5 shrink-0 text-mint transition group-open:rotate-45" aria-hidden="true" />
                          </summary>
                          <p className="mt-3 text-sm leading-6 text-slate-300">{item.answer}</p>
                        </details>
                      ))}
                    </div>
                  </section>
                );
              })}
            </div>

            <aside className="rounded border border-amber/20 bg-amber/8 p-5">
              <XCircle className="h-6 w-6 text-amber" aria-hidden="true" />
              <h2 className="mt-4 text-xl font-semibold text-white">Lo que no se ofrece en esta etapa</h2>
              <ul className="mt-5 grid gap-3">
                {notIncluded.map((item) => (
                  <li key={item} className="flex gap-3 text-sm leading-6 text-slate-200">
                    <FileText className="mt-0.5 h-5 w-5 shrink-0 text-amber" aria-hidden="true" />
                    {item}
                  </li>
                ))}
              </ul>
            </aside>
          </div>
        </div>
      </section>
      <Footer />
    </main>
  );
}
