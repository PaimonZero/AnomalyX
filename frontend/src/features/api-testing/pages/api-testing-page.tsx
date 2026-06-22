import { CheckCircle2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { useHeaderAction } from "@/app/providers/header-action-context";
import { useAuthToken } from "@/app/providers/auth-token-context";
import { sendApiTestRequest } from "@/features/api-testing/api/api-testing-api";
import { IntegrationSampleModal } from "@/features/api-testing/components/integration-sample-modal";
import { RequestBuilder } from "@/features/api-testing/components/request-builder";
import { ResponseViewer } from "@/features/api-testing/components/response-viewer";
import { blankPredictionBody, predictEndpoint, samplePredictionBody } from "@/features/api-testing/data/endpoints";
import type { ApiTestResponse } from "@/features/api-testing/types";
import { env } from "@/shared/config/env";

export function ApiTestingPage() {
  const { token } = useAuthToken();
  const { setHeaderAction } = useHeaderAction();
  const [body, setBody] = useState(samplePredictionBody);
  const [response, setResponse] = useState<ApiTestResponse | null>(null);
  const [sending, setSending] = useState(false);
  const [integrationOpen, setIntegrationOpen] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const jsonValid = useMemo(() => {
    if (!body.trim()) return false;
    try {
      JSON.parse(body);
      return true;
    } catch {
      return false;
    }
  }, [body]);

  useEffect(() => {
    if (!toast) return;
    const timeout = window.setTimeout(() => setToast(null), 2600);
    return () => window.clearTimeout(timeout);
  }, [toast]);

  useEffect(() => {
    setHeaderAction(
      <span className="header-integration-hint">
        Want to integrate with another system?
        <button
          type="button"
          title="Show a cURL request sample for integrating this single prediction endpoint into another system."
          onClick={() => setIntegrationOpen(true)}
        >
          View cURL sample
        </button>
      </span>,
    );

    return () => setHeaderAction(null);
  }, [setHeaderAction]);

  const send = async () => {
    setSending(true);
    setResponse(null);
    const result = await sendApiTestRequest({
      endpoint: predictEndpoint,
      token,
      pathParam: "",
      query: {},
      body,
    });
    setResponse(result);
    setSending(false);
  };

  return (
    <div className="api-testing-page">
      <div className="api-workspace">
        <RequestBuilder
          endpoint={predictEndpoint}
          body={body}
          jsonValid={jsonValid}
          sending={sending}
          onBodyChange={setBody}
          onInsertBlank={() => {
            setBody(blankPredictionBody);
            setResponse(null);
          }}
          onInsertExample={() => {
            setBody(samplePredictionBody);
            setResponse(null);
          }}
          onFormat={() => {
            if (!body.trim()) return;
            try {
              setBody(JSON.stringify(JSON.parse(body), null, 2));
              setToast("JSON formatted.");
            } catch {
              setToast("Cannot format invalid JSON.");
            }
          }}
          onSend={() => void send()}
        />

        <ResponseViewer response={response} loading={sending} onCopied={() => setToast("Response copied.")} />
      </div>

      <IntegrationSampleModal
        apiBaseUrl={env.apiBaseUrl}
        body={body}
        endpointPath={predictEndpoint.path}
        open={integrationOpen}
        token={token}
        onClose={() => setIntegrationOpen(false)}
        onCopied={setToast}
      />

      {toast ? <div className="toast" role="status"><CheckCircle2 size={17} />{toast}</div> : null}
    </div>
  );
}
