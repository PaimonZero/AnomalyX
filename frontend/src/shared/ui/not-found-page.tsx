import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <section className="not-found">
      <p className="eyebrow">404</p>
      <h2>Screen not found</h2>
      <Link to="/alerts">Back to Alerts</Link>
    </section>
  );
}
