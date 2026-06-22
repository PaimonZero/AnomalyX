import { Clipboard, TerminalSquare } from "lucide-react";

import { buildIntegrationSample } from "@/features/api-testing/utils/integration-sample";
import { Button } from "@/shared/ui/button";
import { Modal } from "@/shared/ui/modal";

interface IntegrationSampleModalProps {
  apiBaseUrl: string;
  body: string;
  description?: string;
  endpointPath: string;
  open: boolean;
  title?: string;
  token: string;
  onClose: () => void;
  onCopied: (message: string) => void;
}

export function IntegrationSampleModal(props: IntegrationSampleModalProps) {
  const sample = buildIntegrationSample({
    apiBaseUrl: props.apiBaseUrl,
    body: props.body,
    endpointPath: props.endpointPath,
    token: props.token,
  });

  const copy = async (value: string, message: string) => {
    await navigator.clipboard.writeText(value);
    props.onCopied(message);
  };

  return (
    <Modal
      open={props.open}
      onClose={props.onClose}
      size="lg"
      title={props.title ?? "Integration request sample"}
      description={props.description ?? "Copy this request into another service to call the API."}
    >
      <div className="integration-sample">
        <section className="integration-code-card">
          <header>
            <div><TerminalSquare size={15} /><span>cURL request</span></div>
            <Button variant="secondary" size="sm" onClick={() => void copy(sample.curl, "cURL copied.")}>
              <Clipboard size={13} /> Copy cURL
            </Button>
          </header>
          <pre>{sample.curl}</pre>
        </section>
      </div>
    </Modal>
  );
}
