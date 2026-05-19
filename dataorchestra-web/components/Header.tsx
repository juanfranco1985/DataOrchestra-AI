const navItems = [
  { label: "Inicio", href: "/#inicio" },
  { label: "Servicio", href: "/servicio" },
  { label: "Cómo funciona", href: "/#proceso" },
  { label: "Privacidad", href: "/privacidad" },
  { label: "Demo", href: "/demo" },
  { label: "Contacto", href: "/#contacto" }
];

export function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-ink/88 backdrop-blur-xl">
      <div className="site-shell flex min-h-16 items-center justify-between gap-4 py-3">
        <a href="/#inicio" className="focus-ring flex items-center gap-3 rounded px-1 py-1">
          <span className="flex h-9 w-9 items-center justify-center rounded border border-cyan/40 bg-cyan/10 text-sm font-bold text-cyan">
            DO
          </span>
          <span className="text-base font-semibold text-white">DataOrchestra AI</span>
        </a>

        <nav className="hidden items-center gap-6 text-sm text-slate-300 lg:flex" aria-label="Navegación principal">
          {navItems.map((item) => (
            <a key={item.href} href={item.href} className="focus-ring rounded py-2 transition hover:text-white">
              {item.label}
            </a>
          ))}
        </nav>

        <a
          href="/#contacto"
          className="focus-ring rounded border border-cyan/40 bg-cyan/12 px-4 py-2 text-sm font-semibold text-cyan transition hover:border-cyan hover:bg-cyan/18"
        >
          Solicitar diagnóstico piloto
        </a>
      </div>
    </header>
  );
}
