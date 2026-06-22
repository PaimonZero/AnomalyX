import { Braces, Check, CheckCircle2, FileJson, Play, Upload, X, XCircle } from "lucide-react";
import { useRef, useState } from "react";

import type { BatchValidationResult } from "@/features/batch-scoring/types";
import { Button } from "@/shared/ui/button";

interface BatchInputPanelProps {
  rawJson: string;
  batchName: string;
  outputFormat: "JSON" | "CSV";
  validation: BatchValidationResult;
  jsonValid: boolean;
  running: boolean;
  onRawJsonChange: (value: string) => void;
  onBatchNameChange: (value: string) => void;
  onOutputFormatChange: (value: "JSON" | "CSV") => void;
  onLoadSample: () => void;
  onFormatJson: () => void;
  onRun: () => void;
  onCancel: () => void;
}

export function BatchInputPanel(props: BatchInputPanelProps) {
  const [mode, setMode] = useState<"upload" | "paste">("paste");
  const inputRef = useRef<HTMLInputElement>(null);
  const validCount = props.validation.transactions.length;
  const invalidRows = new Set(props.validation.errors.map((error) => error.index)).size;
  const canRun = props.validation.errors.length === 0 && validCount > 0;

  const loadFile = async (file?: File) => {
    if (!file) return;
    try {
      props.onRawJsonChange(await file.text());
      setMode("paste");
    } finally {
      if (inputRef.current) inputRef.current.value = "";
    }
  };

  return (
    <section className="batch-input-panel">
      <div className="batch-tabs">
        <button className={mode === "upload" ? "active" : ""} onClick={() => setMode("upload")}><Upload size={14} /> Upload file</button>
        <button className={mode === "paste" ? "active" : ""} onClick={() => setMode("paste")}><Braces size={14} /> Paste JSON</button>
      </div>

      <div className="batch-input-body">
        {mode === "upload" ? (
          <button className="batch-dropzone" type="button" onClick={() => inputRef.current?.click()}>
            <FileJson size={28} />
            <strong>Select JSON file</strong>
            <span>The frontend reads the local file only; nothing is uploaded before scoring.</span>
            <small>Or switch back and use the sample batch.</small>
            <input ref={inputRef} type="file" accept=".json,application/json" onChange={(event) => void loadFile(event.target.files?.[0])} hidden />
          </button>
        ) : (
          <>
            <div className="batch-editor-heading">
              <span>Transaction array</span>
              <div className="batch-editor-actions">
                <Button variant="ghost" size="sm" onClick={props.onLoadSample}><FileJson size={13} /> Sample</Button>
                <div className="batch-json-tools">
                  <span className={props.jsonValid ? "json-state json-state--valid" : "json-state json-state--invalid"}>
                    {props.jsonValid ? <Check size={12} /> : <X size={12} />}
                    {props.jsonValid ? "Valid JSON" : "Invalid JSON"}
                  </span>
                  <Button variant="ghost" size="sm" onClick={props.onFormatJson}><Braces size={14} /> Format</Button>
                </div>
              </div>
            </div>
            <textarea
              className="batch-json-editor"
              value={props.rawJson}
              onChange={(event) => props.onRawJsonChange(event.target.value)}
              spellCheck={false}
              placeholder='[{ "transaction_id": "...", "amount": 1000000 }]'
            />
          </>
        )}

        <div className="batch-config-grid">
          <label className="api-field batch-name-field">
            <span>Batch name</span>
            <input value={props.batchName} onChange={(event) => props.onBatchNameChange(event.target.value)} placeholder="june-vip-review" />
          </label>
          <label className="api-field">
            <span>Output</span>
            <select value={props.outputFormat} onChange={(event) => props.onOutputFormatChange(event.target.value as "JSON" | "CSV")}>
              <option>JSON</option>
              <option>CSV</option>
            </select>
          </label>
        </div>

        <section className={`validation-summary ${props.validation.errors.length ? "validation-summary--error" : "validation-summary--valid"}`}>
          <div className="validation-heading">
            <span>{props.validation.errors.length ? <XCircle size={15} /> : <CheckCircle2 size={15} />} Auto validation</span>
            <strong>{validCount} valid · {invalidRows} invalid</strong>
          </div>
          {props.validation.errors.length ? (
            <div className="validation-errors">
              {props.validation.errors.slice(0, 5).map((error, index) => (
                <div key={`${error.index}-${error.field}-${index}`}>
                  <code>Row {error.index + 1} · {error.field}</code>
                  <span>{error.message}</span>
                </div>
              ))}
              {props.validation.errors.length > 5 ? <small>+{props.validation.errors.length - 5} more errors</small> : null}
            </div>
          ) : <p>All transactions are valid and transaction IDs are unique.</p>}
        </section>
      </div>

      <div className="batch-input-actions">
        <div>
          {props.running ? <Button variant="secondary" onClick={props.onCancel}>Cancel</Button> : null}
          <Button variant="primary" onClick={props.onRun} disabled={!canRun || props.running}>
            <Play size={14} fill="currentColor" /> {props.running ? "Running…" : "Run batch"}
          </Button>
        </div>
      </div>
    </section>
  );
}
