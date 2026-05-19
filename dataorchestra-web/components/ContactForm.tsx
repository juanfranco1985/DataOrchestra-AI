"use client";

import { useMemo, useState } from "react";
import type { ChangeEvent, FormEvent } from "react";
import { CheckCircle2, Clipboard, Mail, ShieldAlert } from "lucide-react";

type FormState = {
  name: string;
  company: string;
  email: string;
  industry: string;
  message: string;
  acceptedPrivacyScope: boolean;
  website: string;
};

const initialState: FormState = {
  name: "",
  company: "",
  email: "",
  industry: "",
  message: "",
  acceptedPrivacyScope: false,
  website: ""
};

const recipientEmail = process.env.NEXT_PUBLIC_CONTACT_EMAIL ?? "";
const maxMessageLength = 800;

const sensitiveMessagePatterns = [
  { label: "telefonos", pattern: /(?:\+?\d[\s().-]*){8,}/ },
  { label: "documentos o identificadores fiscales", pattern: /\b\d{2}-?\d{8}-?\d\b|\b\d{7,8}\b/ },
  { label: "tarjetas o cuentas", pattern: /\b(?:\d[ -]*?){13,18}\b/ },
  { label: "emails adicionales", pattern: /[^\s@]+@[^\s@]+\.[^\s@]+/ }
];

function normalize(value: string): string {
  return value.trim().replace(/\s+/g, " ");
}

function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function findSensitiveMessageMatch(message: string): string | null {
  const match = sensitiveMessagePatterns.find((item) => item.pattern.test(message));
  return match?.label ?? null;
}

function buildRequestBody(state: FormState): string {
  return [
    "Solicitud de evaluacion inicial - DataOrchestra AI",
    "",
    `Nombre: ${normalize(state.name)}`,
    `Empresa: ${normalize(state.company)}`,
    `Email: ${normalize(state.email)}`,
    `Rubro: ${normalize(state.industry)}`,
    "",
    "Mensaje:",
    state.message.trim(),
    "",
    "Confirmacion:",
    "El solicitante entiende que el piloto trabaja con datos anonimizados y revision humana.",
    "",
    "Importante:",
    "No se adjuntan archivos ni datos sensibles en esta solicitud inicial."
  ].join("\n");
}

export function ContactForm() {
  const [formState, setFormState] = useState<FormState>(initialState);
  const [errors, setErrors] = useState<string[]>([]);
  const [status, setStatus] = useState<string>("");
  const requestBody = useMemo(() => buildRequestBody(formState), [formState]);
  const hasConfiguredRecipient = Boolean(recipientEmail);

  function updateField(event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) {
    const target = event.target;

    if (target instanceof HTMLInputElement && target.type === "checkbox") {
      setFormState((current) => ({
        ...current,
        acceptedPrivacyScope: target.checked
      }));
      setStatus("");
      return;
    }

    const fieldName = target.name as Exclude<keyof FormState, "acceptedPrivacyScope">;

    setFormState((current) => ({
      ...current,
      [fieldName]: target.value
    }));
    setStatus("");
  }

  function validateForm(): string[] {
    const nextErrors: string[] = [];
    const sensitiveMatch = findSensitiveMessageMatch(formState.message);

    if (formState.website.trim()) {
      return ["No se pudo validar la solicitud."];
    }

    if (!normalize(formState.name)) nextErrors.push("Ingresá tu nombre.");
    if (!normalize(formState.company)) nextErrors.push("Ingresá el nombre de la empresa.");
    if (!validateEmail(normalize(formState.email))) nextErrors.push("Ingresá un email válido.");
    if (!normalize(formState.industry)) nextErrors.push("Indicá el rubro.");
    if (!formState.message.trim()) nextErrors.push("Agregá un mensaje breve sobre la necesidad comercial.");
    if (formState.message.length > maxMessageLength) {
      nextErrors.push(`El mensaje debe tener menos de ${maxMessageLength} caracteres.`);
    }
    if (sensitiveMatch) {
      nextErrors.push(`El mensaje parece incluir ${sensitiveMatch}. Quitá ese dato antes de continuar.`);
    }
    if (!formState.acceptedPrivacyScope) {
      nextErrors.push("Confirmá que entendés el uso de datos anonimizados y revisión humana.");
    }

    return nextErrors;
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const validationErrors = validateForm();
    setErrors(validationErrors);

    if (validationErrors.length > 0) {
      setStatus("");
      return;
    }

    const subject = encodeURIComponent("Solicitud de diagnostico piloto - DataOrchestra AI");
    const body = encodeURIComponent(requestBody);
    window.location.href = `mailto:${recipientEmail}?subject=${subject}&body=${body}`;
    setStatus(
      hasConfiguredRecipient
        ? "Se preparó un correo estructurado. Revisalo antes de enviarlo."
        : "Se preparó un correo sin destinatario configurado. Agregá el email operativo antes de enviarlo."
    );
  }

  async function copyRequest() {
    const validationErrors = validateForm();
    setErrors(validationErrors);

    if (validationErrors.length > 0) {
      setStatus("");
      return;
    }

    try {
      await navigator.clipboard.writeText(requestBody);
      setStatus("Solicitud copiada. Podés pegarla en tu email o CRM.");
    } catch {
      setStatus("No se pudo copiar automáticamente. Usá la opción de preparar correo.");
    }
  }

  return (
    <form className="rounded border border-white/10 bg-panel/78 p-5" aria-label="Formulario de contacto controlado" onSubmit={handleSubmit} noValidate>
      <div className="mb-5 flex items-center gap-3 border-b border-white/10 pb-5">
        <div className="flex h-10 w-10 items-center justify-center rounded border border-cyan/30 bg-cyan/10">
          <Mail className="h-5 w-5 text-cyan" aria-hidden="true" />
        </div>
        <div>
          <p className="font-semibold text-white">Solicitud de evaluación inicial</p>
          <p className="text-sm text-slate-400">Prepara un correo seguro. No sube archivos ni guarda datos.</p>
        </div>
      </div>

      <input className="hidden" name="website" tabIndex={-1} autoComplete="off" value={formState.website} onChange={updateField} aria-hidden="true" />

      <div className="grid gap-4 sm:grid-cols-2">
        <label className="grid gap-2 text-sm font-medium text-slate-200">
          Nombre
          <input className="focus-ring rounded border border-white/12 bg-ink px-3 py-3 text-white" name="name" value={formState.name} onChange={updateField} autoComplete="name" />
        </label>
        <label className="grid gap-2 text-sm font-medium text-slate-200">
          Empresa
          <input className="focus-ring rounded border border-white/12 bg-ink px-3 py-3 text-white" name="company" value={formState.company} onChange={updateField} autoComplete="organization" />
        </label>
        <label className="grid gap-2 text-sm font-medium text-slate-200">
          Email
          <input className="focus-ring rounded border border-white/12 bg-ink px-3 py-3 text-white" name="email" type="email" value={formState.email} onChange={updateField} autoComplete="email" />
        </label>
        <label className="grid gap-2 text-sm font-medium text-slate-200">
          Rubro
          <input className="focus-ring rounded border border-white/12 bg-ink px-3 py-3 text-white" name="industry" value={formState.industry} onChange={updateField} />
        </label>
      </div>

      <label className="mt-4 grid gap-2 text-sm font-medium text-slate-200">
        Mensaje
        <textarea
          className="focus-ring min-h-32 rounded border border-white/12 bg-ink px-3 py-3 text-white"
          name="message"
          value={formState.message}
          onChange={updateField}
          maxLength={maxMessageLength + 80}
        />
      </label>
      <p className="mt-2 text-xs text-slate-500">{formState.message.length}/{maxMessageLength} caracteres recomendados.</p>

      <label className="mt-4 flex items-start gap-3 text-sm leading-6 text-slate-300">
        <input
          type="checkbox"
          name="acceptedPrivacyScope"
          checked={formState.acceptedPrivacyScope}
          onChange={updateField}
          className="mt-1 h-4 w-4 rounded border-white/20 bg-ink"
        />
        Confirmo que entiendo que el piloto trabaja con datos anonimizados y revisión humana.
      </label>

      {errors.length > 0 ? (
        <div className="mt-5 rounded border border-amber/25 bg-amber/8 p-4" role="alert">
          <div className="flex gap-3">
            <ShieldAlert className="mt-0.5 h-5 w-5 shrink-0 text-amber" aria-hidden="true" />
            <ul className="grid gap-1 text-sm leading-6 text-slate-200">
              {errors.map((error) => (
                <li key={error}>{error}</li>
              ))}
            </ul>
          </div>
        </div>
      ) : null}

      {status ? (
        <div className="mt-5 flex gap-3 rounded border border-mint/20 bg-mint/8 p-4 text-sm leading-6 text-slate-200" role="status">
          <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-mint" aria-hidden="true" />
          <p>{status}</p>
        </div>
      ) : null}

      <div className="mt-6 grid gap-3 sm:grid-cols-[1fr_auto]">
        <button type="submit" className="focus-ring rounded bg-cyan px-5 py-3 text-sm font-bold text-ink transition hover:bg-white">
          Preparar correo de evaluación
        </button>
        <button
          type="button"
          onClick={copyRequest}
          className="focus-ring inline-flex items-center justify-center gap-2 rounded border border-white/16 px-5 py-3 text-sm font-semibold text-white transition hover:border-white/35 hover:bg-white/6"
        >
          <Clipboard className="h-4 w-4" aria-hidden="true" />
          Copiar
        </button>
      </div>

      <p className="mt-3 text-center text-xs text-slate-500">
        El envío final ocurre desde tu cliente de correo. No adjuntes archivos ni datos sensibles en esta solicitud.
      </p>
    </form>
  );
}
