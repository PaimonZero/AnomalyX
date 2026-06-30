import architectureImage from "../../assets/system-architecture.webp";
import type { Language } from "../../types";

export function ArchitectureDiagram(_: { language: Language; token: string }) {
  return (
    <figure className="arch-static" aria-label="AnomalyX component and data-flow architecture">
      <img src={architectureImage} alt="AnomalyX system architecture diagram from Report 2" />
    </figure>
  );
}
