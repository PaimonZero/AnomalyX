import { ArrowRight, type LucideIcon } from "lucide-react";

interface FeaturePlaceholderProps {
  icon: LucideIcon;
  label: string;
  title: string;
  description: string;
  endpoint: string;
  nextStep: string;
}

export function FeaturePlaceholder({
  icon: Icon,
  label,
  title,
  description,
  endpoint,
  nextStep,
}: FeaturePlaceholderProps) {
  return (
    <section className="feature-stage">
      <div className="feature-marker" aria-hidden="true">
        <Icon size={22} />
      </div>
      <p className="eyebrow">{label}</p>
      <h2>{title}</h2>
      <p className="feature-description">{description}</p>
      <div className="feature-meta">
        <div>
          <span>Backend contract</span>
          <code>{endpoint}</code>
        </div>
        <div>
          <span>Next implementation unit</span>
          <p>{nextStep}</p>
        </div>
      </div>
      <div className="scaffold-note">
        <ArrowRight size={16} />
        <span>This feature already has a route, boundary, and dedicated place for the next implementation step.</span>
      </div>
    </section>
  );
}
