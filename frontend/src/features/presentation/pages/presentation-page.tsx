import { Slideshow } from "../components/slideshow";
import { slides } from "../data/slides";

export function PresentationPage() {
  return (
    <div className="presentation-page">
      <Slideshow slides={slides} />
    </div>
  );
}
