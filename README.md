# ISYS-inspired Administrative Quality Review Automation

> **Independent portfolio prototype. Not an official ISYS system and not connected to ISYS internal systems.**

An **ISYS-inspired Administrative Quality Review Automation** prototype built with **n8n, Gmail, OpenAI, and Supabase** using fictional/sample data.

The project demonstrates how an administrative document-review process can be turned into a structured automation that receives reports, detects and routes supporting documents, performs an AI quality review, stores the result, decides whether follow-up is required, and generates a professional response when needed.

## Demo

**Video demonstration:** https://youtu.be/rCsg1Lq3xc0

The video shows the workflow from incoming Gmail report through document processing, AI review, Supabase case storage, decision-making, and follow-up email generation.

## Workflow

```text
Gmail Trigger
      ↓
Intake & Primary Document Detection
      ↓
Document Type Routing
 ┌────┼────┬────┬────┬──────────┐
PDF  CSV  XLSX  TXT HTML  Unsupported
 └────┴────┴────┴────┴──────────┘
      ↓
Document Normalization
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
AI Follow-up Email Writer      Mark Completed
   ↓                               ↓
Professional HTML Email        Mark Gmail Read
   ↓
Gmail Send
   ↓
Update Supabase
```

The exported n8n workflow was reviewed directly for this repository documentation. The current implementation contains **33 nodes**, including document routing/extraction, structured AI review, Supabase case tracking, conditional follow-up, Gmail sending, and demo labels.

## What it demonstrates

### Intake

- Receives incoming Gmail submissions.
- Captures Gmail message ID, sender, subject, body, and attachment metadata.
- Detects the number and names of attached files.
- Selects the first attachment as the primary document for the current workflow version.

### Document processing

The workflow routes the primary attachment by MIME type and supports:

- PDF
- CSV
- XLS/XLSX
- Plain text
- HTML
- Unsupported files

Supported documents are extracted and normalized into a common structure before review. Unsupported or unavailable documents are explicitly marked as **Unable to Verify** rather than being treated as successfully reviewed.

### AI quality review

The review agent uses **OpenAI `gpt-5-mini`** with a structured output parser.

Checks include:

- Case and report information
- Queue and report type
- Submission date and deadline
- Missing information and documents
- Contradictions between the email and document
- Invoice status
- Customer requirements
- Urgency and escalation
- Recommended action
- Whether follow-up communication is required

The AI is instructed to **use available evidence only**, never guess unavailable information, keep email and attachment evidence separate, and explicitly flag missing or contradictory information.

### Case tracking

The structured review is stored in a Supabase `cases` table, including:

- Case/report identifiers
- Quality findings
- Missing information
- Invoice/document status
- Customer requirements
- Deadline and urgency
- Recommended action
- Email status
- Gmail message ID
- Processing status
- Overall business status

### Conditional communication

If `email_required` is `true`, the workflow:

1. Generates a structured follow-up email.
2. Builds a professional HTML email.
3. Adds the prototype's generated Quality Review logo asset.
4. Sends the response through Gmail.
5. Updates the Supabase case to `Email Sent`.

If follow-up is not required, the workflow marks the case `Completed` and marks the source Gmail message as read.

## Technology

| Component | Purpose |
|---|---|
| **n8n** | Workflow orchestration, routing, extraction, branching, and automation |
| **Gmail** | Report intake and follow-up communication |
| **OpenAI** | Administrative quality review and follow-up email generation |
| **Supabase** | Structured case storage and status tracking |

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
- **Contradiction detection:** conflicting values are flagged instead of silently choosing one.
- **Structured output:** review results are normalized into predictable fields before database storage.
- **Conditional automation:** follow-up communication is generated only when the review determines it is required.
- **Traceability:** case and processing statuses are stored in Supabase.
- **Safe demonstration data:** all names, case numbers, documents, and values are fictional/sample data.

## Known implementation limitations

This is a portfolio prototype rather than a production deployment.

- **Primary attachment only:** the intake code detects all attachments but currently extracts only the first attachment as the primary document. The AI prompt explicitly prevents the reviewer from claiming unseen attachments were reviewed.
- **No dedicated error branch:** n8n execution error data is retained for debugging, but the workflow does not yet have a complete business-level failure/retry/notification path.
- **Follow-up read-state gap:** the current exported workflow sends the follow-up and updates Supabase, but the follow-up branch currently stops after `Supabase - Mark Email Sent` instead of connecting to a final `Mark Processed Read` node.
- **Broad Gmail intake query:** the Gmail trigger uses a broad keyword query and would need stricter filtering for a production environment.
- **Prototype branding:** the generated email branding is for the portfolio demonstration and should not be interpreted as official ISYS branding or an official ISYS communication.

## Production considerations

A production implementation would require organization-specific business rules, authentication, authorization, secrets management, security controls, document retention policies, monitoring, retries, audit logging, rate-limit handling, comprehensive attachment processing, and appropriate human review before consequential actions.

## Disclaimer

This prototype was independently created for portfolio and demonstration purposes, inspired by the administrative and quality-review responsibilities described in a public ISYS-related job posting. It was not commissioned by ISYS, does not use ISYS internal systems or data, and does not represent an official ISYS product or workflow.
