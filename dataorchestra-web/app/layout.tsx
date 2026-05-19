import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DataOrchestra AI | Diagnóstico comercial controlado para PyMEs",
  description:
    "Servicio supervisado de diagnóstico comercial para PyMEs basado en datos anonimizados de ventas, productos y stock, con privacidad, auditoría y revisión humana.",
  keywords: [
    "DataOrchestra AI",
    "análisis de datos para PyMEs",
    "diagnóstico comercial",
    "ventas",
    "stock",
    "margen",
    "datos anonimizados",
    "inteligencia comercial",
    "auditoría de datos"
  ],
  openGraph: {
    title: "DataOrchestra AI | Diagnóstico comercial controlado para PyMEs",
    description:
      "Diagnóstico comercial supervisado con datos anonimizados, trazabilidad y revisión humana antes de entregar resultados.",
    type: "website",
    locale: "es_AR"
  }
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
