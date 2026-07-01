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
    transaction_id: "fe_demo_single_high_drain_20260701_001",
    sender_id: "sender_fe_single_001",
    receiver_id: "receiver_fe_single_001",
    sender_balance: 750000,
    receiver_balance: 125000,
    amount: 750000,
    currency: "VND",
    timestamp: "2026-06-19T10:05:00+07:00",
    channel: "TRANSFER",
    device_id: "device-fe-single-001",
    location_country: "VN",
    location_region: "HCM",
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
