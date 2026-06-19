import type { EndpointDefinition } from "@/features/api-testing/types";

export const predictEndpoint: EndpointDefinition = {
  id: "predict",
  method: "POST",
  path: "/api/v1/predict",
  auth: true,
  description: "Score one transaction with rules and ML.",
};

export const samplePredictionBody = JSON.stringify(
  {
    transaction_id: "8f1c3a2b-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
    sender_id: "h:3a9f2b8c1d4e5f6a7b8c9d0e1f2a3b4c",
    receiver_id: "h:7b2c8d3e4f5a6b7c8d9e0f1a2b3c4d5e",
    sender_balance: 420000000,
    receiver_balance: 200000,
    amount: 390000000,
    currency: "VND",
    timestamp: "2026-06-19T09:14:03+07:00",
    channel: "TRANSFER",
    device_id: "device-demo-001",
    location_country: "VN",
    location_region: "HN",
  },
  null,
  2,
);

export const blankPredictionBody = JSON.stringify(
  {
    transaction_id: "",
    sender_id: "",
    receiver_id: "",
    sender_balance: "",
    receiver_balance: "",
    amount: "",
    currency: "",
    timestamp: "",
    channel: "",
    device_id: "",
    location_country: "",
    location_region: "",
  },
  null,
  2,
);
