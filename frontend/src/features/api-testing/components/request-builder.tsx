import { Braces, Check, Play, X } from "lucide-react";

import type { EndpointDefinition } from "@/features/api-testing/types";
import { Badge } from "@/shared/ui/badge";
import { Button } from "@/shared/ui/button";

interface RequestBuilderProps {
  endpoint: EndpointDefinition;
  body: string;
  jsonValid: boolean;
  sending: boolean;
  onBodyChange: (value: string) => void;
  onInsertBlank: () => void;
  onInsertExample: () => void;
  onFormat: () => void;
  onSend: () => void;
}

export function RequestBuilder(props: RequestBuilderProps) {
  return (
    <section className="request-builder">
      <div className="api-panel-heading">
        <div><span>Single transaction request</span><small>Dedicated predict endpoint</small></div>
      </div>

      <div className="request-builder__body">
        <label className="api-field">
          <span>Endpoint</span>
          <div className="endpoint-select endpoint-select--readonly">
            <Badge tone="accent">{props.endpoint.method}</Badge>
            <code>{props.endpoint.path}</code>
          </div>
          <small>{props.endpoint.description}</small>
        </label>

        <div className="body-editor-wrap">
          <div className="body-editor-heading">
            <span>Transaction payload</span>
            <div className="body-editor-actions">
              <div className="payload-template-actions" aria-label="Insert payload template">
                <button type="button" onClick={props.onInsertExample}>Example</button>
                <button type="button" onClick={props.onInsertBlank}>Blank JSON</button>
              </div>
              <div className="payload-tools">
                <span className={props.jsonValid ? "json-state json-state--valid" : "json-state json-state--invalid"}>
                  {props.jsonValid ? <Check size={12} /> : <X size={12} />}
                  {props.jsonValid ? "Valid JSON" : "Invalid JSON"}
                </span>
                <Button variant="ghost" size="sm" onClick={props.onFormat}><Braces size={14} /> Format</Button>
              </div>
            </div>
          </div>
          <textarea
            className="json-editor"
            value={props.body}
            onChange={(event) => props.onBodyChange(event.target.value)}
            spellCheck={false}
            placeholder='{ "transaction_id": "...", "amount": 1000000 }'
          />
        </div>
      </div>

      <div className="request-builder__actions">
        <Button variant="primary" onClick={props.onSend} disabled={props.sending || !props.jsonValid}>
          <Play size={15} fill="currentColor" /> {props.sending ? "Sending…" : "Run prediction"}
        </Button>
      </div>
    </section>
  );
}
