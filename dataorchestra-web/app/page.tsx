import { AnalysisScopeSection } from "@/components/AnalysisScopeSection";
import { ContactSection } from "@/components/ContactSection";
import { DifferentiationSection } from "@/components/DifferentiationSection";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { Hero } from "@/components/Hero";
import { PilotSection } from "@/components/PilotSection";
import { PrivacySection } from "@/components/PrivacySection";
import { ProblemSection } from "@/components/ProblemSection";
import { ProcessSection } from "@/components/ProcessSection";
import { SolutionSection } from "@/components/SolutionSection";

export default function Home() {
  return (
    <main>
      <Header />
      <Hero />
      <ProblemSection />
      <SolutionSection />
      <ProcessSection />
      <AnalysisScopeSection />
      <PrivacySection />
      <DifferentiationSection />
      <PilotSection />
      <ContactSection />
      <Footer />
    </main>
  );
}
