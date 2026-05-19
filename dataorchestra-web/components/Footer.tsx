const footerLinks = [
  { label: "Privacidad", href: "#privacidad" },
  { label: "Piloto controlado", href: "#piloto" },
  { label: "Contacto", href: "#contacto" }
];

export function Footer() {
  return (
    <footer className="border-t border-white/10 bg-ink py-10">
      <div className="site-shell flex flex-col gap-6 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="text-lg font-semibold text-white">DataOrchestra AI</p>
          <p className="mt-2 text-sm text-slate-400">Diagnóstico comercial controlado para PyMEs</p>
          <p className="mt-4 max-w-xl text-xs leading-5 text-slate-500">
            Proyecto en etapa de piloto controlado. No constituye una plataforma SaaS pública ni autoservicio.
          </p>
        </div>
        <nav className="flex flex-wrap gap-4 text-sm text-slate-300" aria-label="Navegación de pie">
          {footerLinks.map((item) => (
            <a key={item.href} href={item.href} className="focus-ring rounded py-1 transition hover:text-white">
              {item.label}
            </a>
          ))}
        </nav>
      </div>
    </footer>
  );
}
