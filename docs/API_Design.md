# API Design

## API Conventions
The ThreatLens API is a RESTful API designed with the following conventions:
- **Base URL**: `/api/v1`
- **Content Type**: `application/json` for requests and responses.
- **Error Responses**: All error responses return a standardized error block:
  ```json
  {
    "detail": "Error description or validation issues message"
  }
  ```

## Authentic Company Configurations

### `GET /companies`
Retrieve a list of tracked corporate companies and their legitimate configurations.
- **Response `200 OK`**:
  ```json
  [
    {
      "id": 1,
      "name": "Acme Corp",
      "legitimate_domains": ["acme.com", "acme-portal.com"],
      "logo_url": "/assets/logos/acme.png"
    }
  ]
  ```

### `POST /companies`
Register a company configuration profile.
- **Request Body**:
  ```json
  {
    "name": "Acme Corp",
    "legitimate_domains": ["acme.com"]
  }
  ```
- **Response `201 Created`**

---

## Scan Jobs Queue

### `POST /scan-jobs`
Submit a suspicious target website URL for analysis.
- **Request Body**:
  ```json
  {
    "target_url": "https://secure-acme-verify.com",
    "company_id": 1
  }
  ```
- **Response `202 Accepted`**:
  ```json
  {
    "job_id": "8f3b9c7a-5d0e-47af-bf32-e0c1f6a19f2a",
    "status": "PENDING"
  }
  ```

### `GET /scan-jobs/{job_id}`
Retrieve the execution status and results of a submitted scan.
- **Response `200 OK`**:
  ```json
  {
    "job_id": "8f3b9c7a-5d0e-47af-bf32-e0c1f6a19f2a",
    "status": "SUCCESS",
    "target_url": "https://secure-acme-verify.com",
    "risk_score": 85,
    "completed_at": "2026-08-06T14:50:00Z"
  }
  ```

---

## Detections and Campaigns

### `GET /detections`
Fetch identified malicious or suspicious targets.
- **Query Parameters**:
  - `min_risk_score`: Filter by minimum risk threshold.
  - `status`: Filter by analysis status (`SUSPICIOUS`, `CONFIRMED`, `BENIGN`).
- **Response `200 OK`**:
  ```json
  [
    {
      "id": 12,
      "target_url": "https://secure-acme-verify.com",
      "risk_score": 85,
      "status": "SUSPICIOUS",
      "campaign_id": 3
    }
  ]
  ```

### `GET /campaigns`
List identified phishing campaigns grouping multiple targets.
- **Response `200 OK`**:
  ```json
  [
    {
      "id": 3,
      "name": "Acme Login Phish Campaign - Aug 2026",
      "associated_domains_count": 5,
      "identified_at": "2026-08-06T12:00:00Z"
    }
  ]
  ```

---

## Investigation Reports

### `GET /detections/{detection_id}/report`
Generate a comprehensive analyst-friendly takedown report.
- **Response `200 OK`**:
  ```json
  {
    "detection_id": 12,
    "summary": "Impersonation website cloned Acme Corp brand login assets.",
    "abuse_email": "abuse@registrar-domain.com",
    "evidence": {
      "ip_address": "192.168.1.100",
      "dns_records": ["A", "MX"],
      "opencv_logo_similarity": 0.94,
      "structural_tag_similarity": 0.88
    },
    "takedown_draft_template": "Subject: Urgent Brand Abuse Takedown Request...\n\nDear abuse desk..."
  }
  ```
