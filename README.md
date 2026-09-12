# Administrative Quality Review Automation

> **Independent portfolio prototype inspired by an ISYS-style administrative quality-review workflow. Not an official ISYS system and not connected to ISYS internal systems.**

An administrative document-review automation prototype built with **n8n, Gmail, OpenAI, and Supabase** using fictional/sample data.

The project demonstrates how an administrative report-review process can be automated from email intake through document extraction, AI quality review, structured case storage, conditional follow-up, and completion tracking.

## Demo

**Video demonstration:** https://youtu.be/rCsg1Lq3xc0

The demo shows the workflow processing incoming Gmail reports, handling supporting attachments, extracting available document content, performing an AI quality review, storing the result in Supabase, deciding whether follow-up is required, and sending a professional response when necessary.

## Workflow

```text
Gmail Trigger
      ↓
Prepare All Attachments
      ↓
Document Type Routing
 ┌────┼────┬────┬────┬──────────┐
PDF  CSV  XLSX  TXT HTML  Unsupported
 └────┴────┴────┴────┴──────────┘
      ↓
Document Extraction
      ↓
Aggregate All Extracted Documents
      ↓
AI Quality Review
      ↓
Structured Review Result
      ↓
Supabase Case Record
      ↓
Follow-up Required?
   ┌───────────────┴───────────────┐
  YES                             NO
   ↓                               ↓
AI Follow-up Writer           Mark Completed
   ↓                               ↓
Professional HTML Email       Mark Gmail Read
   ↓
Gmail Send
   ↓
Update Supabase
   ↓
Mark Original Gmail Read
```

## What it demonstrates

### Gmail intake

- Processes **unread** incoming Gmail messages matching the workflow's intake query.
- Preserves the original Gmail message ID for traceability.
- Captures sender, subject, message content, and attachment metadata.
- Creates one processing item per detected attachment.

### Multi-attachment document processing

The workflow detects attachment filename and MIME type, with extension fallback where MIME metadata is unavailable.

Supported extraction paths include:

- PDF
- CSV
- XLS/XLSX
- Plain text
- HTML
- Unsupported/unreviewed files

All successfully extracted documents are aggregated before the AI review. Each document retains its filename, type, extraction status, and extracted text.

Unsupported or failed documents are explicitly passed to the AI as **not reviewed** rather than being silently ignored.

### AI quality review

The review agent uses **OpenAI `gpt-5-mini`** with structured output.

Checks include:

- Case and report information
- Queue and report type
- Submission date and deadline
- Missing information and documents
- Contradictions between the email and supporting documents
- Invoice status
- Customer requirements
- Urgency and escalation conditions
- Recommended action
- Whether follow-up communication is required

The reviewer is instructed to use available evidence only and never claim that an unavailable or unreviewed document was inspected.

### Case tracking

The structured review is stored in a Supabase `cases` table, including case/report information, quality findings, document and invoice status, requirements, deadlines, urgency, recommended action, Gmail message ID, processing status, email status, and overall business status.

### Conditional communication

If follow-up is required, the workflow:

1. Generates a structured follow-up email.
2. Builds a professional HTML email.
3. Sends it through Gmail.
4. Updates the Supabase case to `Email Sent`.
5. Marks the **original incoming Gmail message** as processed/read.

If follow-up is not required, the workflow marks the case `Completed` and marks the original Gmail message as processed/read.

### Error handling

The workflow includes an in-workflow **Error Trigger → Error Diagnostics** path and controlled retries for extraction, AI review, Supabase, and Gmail operations.

Execution error data is retained, while failed operations are not represented as successful cases.

## Technology

| Component | Purpose |
|---|---|
| **n8n** | Workflow orchestration, routing, extraction, branching, retries, and automation |
| **Gmail** | Report intake and follow-up communication |
| **OpenAI** | Administrative quality review and follow-up email generation |
| **Supabase** | Structured case storage and lifecycle tracking |

## Test scenarios

The prototype is designed around four fictional test scenarios:

| Case | Scenario | Expected outcome |
|---|---|---|
| ISYS-73104 | Complete case | Ready, no follow-up |
| ISYS-59283 | Missing invoice | Missing Information, follow-up |
| ISYS-84621 | Date contradiction | Needs Review, follow-up |
| ISYS-91462 | Serious discrepancy | Escalation Required, urgent follow-up |

See [`docs/test-cases.md`](docs/test-cases.md) for the full scenarios and expected results.

## Documentation

- [`docs/architecture.md`](docs/architecture.md) - verified workflow architecture and implementation details
- [`docs/test-cases.md`](docs/test-cases.md) - fictional test scenarios and expected outcomes
- [`docs/database-schema.md`](docs/database-schema.md) - Supabase `cases` table and status values

## Key design principles

- **Evidence-first:** never invent or guess unavailable information.
- **Source separation:** email content and attachment content are treated as separate sources.
- **Document-level traceability:** each attachment retains filename, type, extraction status, and extracted content.
- **Contradiction detection:** conflicting values are flagged instead of silently choosing one.
- **Structured output:** review results are normalized before database storage.
- **Conditional automation:** follow-up communication is generated only when the review determines it is required.
- **Failure visibility:** extraction and automation failures are surfaced rather than treated as successful processing.
- **Traceability:** the original Gmail message ID remains linked to the Supabase case.
- **Safe demonstration data:** all names, case numbers, documents, and values are fictional/sample data.

## Known implementation limitation

The multi-attachment architecture has been implemented and the workflow paths have been verified, but a true live Gmail test containing multiple real binary attachments could not be executed through the available MCP testing interface. The Gmail trigger itself is not directly executable through that interface, so this specific end-to-end binary-input scenario remains a validation limitation rather than being falsely presented as live-tested.

## Production considerations

A production implementation would require organization-specific business rules, authentication, authorization, secrets management, security controls, document retention policies, monitoring, comprehensive audit logging, rate-limit handling, controlled recipient logic, and appropriate human review before consequential actions.

## Disclaimer

This prototype was independently created for portfolio and demonstration purposes, inspired by administrative and quality-review responsibilities described in a public ISYS-related job posting. It was not commissioned by ISYS, does not use ISYS internal systems or data, and does not represent an official ISYS product or workflow.
