# Automation Architecture

## Verified workflow

The current n8n workflow is named **ISYS Administrative Quality Review • Demo Ready** and contains 33 nodes.

### 1. Intake

`Gmail Trigger - ISYS Reports` receives incoming report emails.

`Prepare - Intake & Primary Document`:

- captures the Gmail message metadata
- detects binary attachments
- records attachment count and names
- selects the first attachment as the primary document
- preserves the primary attachment for extraction

### 2. Document routing and extraction

`Route - Document Type` sends the primary attachment to the appropriate extraction path:

| Input | Extraction |
|---|---|
| PDF | Extract PDF |
| CSV | Extract CSV |
| XLS/XLSX | Extract Spreadsheet |
| TXT | Extract Text |
| HTML | Extract HTML |
| Other / unavailable | Unsupported Document |

The extraction branches feed into normalization nodes so the AI reviewer receives a consistent document representation.

### 3. AI quality review

`AI Quality Review` uses OpenAI `gpt-5-mini` with a structured output parser.

The reviewer receives the original Gmail message and the normalized primary document as separate sources. It checks:

- case and report identifiers
- queue and report type
- submission dates and deadlines
- missing information
- missing or unverifiable documents
- contradictions between sources
- invoice status
- customer requirements
- urgency
- escalation conditions
- recommended action
- whether follow-up communication is required

The system prompt explicitly prohibits invented facts and instructs the model not to claim that unseen attachments were reviewed.

### 4. Structured case storage

`Normalize - Review Result` converts the structured AI output into the database-ready object.

`Supabase - Create Case` stores the result in the `cases` table. The Supabase-generated `id` is excluded from automatic input mapping, while the Gmail message ID provides traceability back to the source email.

### 5. Business decision

`IF - Follow-up Required?` branches using the structured `email_required` value.

#### Follow-up path

```text
AI Follow-up Email Writer
        ↓
Build - Professional Email + Logo
        ↓
Gmail - Send Follow-up
        ↓
Supabase - Mark Email Sent
```

The email writer uses only the quality-review data and is instructed not to invent names, dates, amounts, requirements, or addresses. The email is rendered as professional HTML before being sent.

#### Clean completion path

```text
Supabase - Mark Completed
        ↓
Gmail - Mark Processed Read (No Follow-up)
```

Cases requiring no follow-up are marked completed and the original Gmail message is marked as read.

## Document evidence model

The workflow intentionally distinguishes:

1. **Email evidence**: sender, subject, Gmail message ID, message body, and stated requirements.
2. **Attachment evidence**: extracted content from the selected primary attachment.
3. **Attachment metadata**: attachment count, filenames, MIME type, and availability.

If an attachment exists but cannot be reliably extracted, the workflow marks it as unavailable for verification instead of pretending the content was reviewed.

## Status model

The AI review uses controlled status values:

- `document_status`: Complete, Missing Documents, Needs Review, Not Applicable
- `invoice_status`: Present, Missing, Inconsistent, Not Applicable, Unable to Verify
- `overall_status`: Ready, Needs Review, Missing Information, Escalation Required
- `urgency`: Low, Medium, High, Urgent
- `processing_status`: Reviewed during AI review, then updated to Email Sent or Completed
- `email_status`: Not Required, Pending, Sent, Failed

## Design principles

- **Evidence first:** never invent unavailable information.
- **Source separation:** email and attachment evidence remain distinct.
- **Contradiction detection:** conflicting information is flagged rather than silently resolved.
- **Structured output:** AI results use predictable fields before database storage.
- **Conditional automation:** follow-up communication occurs only when required.
- **Traceability:** Gmail message IDs and Supabase records connect the workflow stages.
- **Safe demonstration data:** the prototype uses fictional/sample information only.
- **Clear independence:** the workflow is inspired by a public job description and is not an official ISYS system.

## Current limitations identified from the exported workflow

### Primary attachment only

The intake code detects every binary attachment but selects only the first one for extraction. The AI prompt explicitly states that only the primary attachment was extracted in this workflow version.

A production version should iterate over all relevant attachments and preserve document-level metadata for each file.

### No dedicated business-level error path

The n8n workflow is configured to retain execution error data, but there is no dedicated error branch that retries failed operations, records a `Failed` case state, or notifies an operator.

### Follow-up read-state gap

The no-follow-up branch ends with a Gmail mark-as-read operation. The follow-up branch currently ends at `Supabase - Mark Email Sent`; it is not connected to a final Gmail mark-as-read node.

### Broad Gmail filter

The Gmail trigger uses a broad keyword query. A production implementation should use a more controlled label, sender/domain filter, subject convention, or other deterministic intake rule.

### Demo branding

The generated email contains `ISYS Quality Review` demonstration branding. This should be treated only as prototype presentation and must not be presented as official ISYS branding or communication.

## Production considerations

A production implementation would require:

- organization-specific validation rules
- secure credential and secret management
- authorization controls
- retry and failure handling
- monitoring and alerting
- audit logging
- document retention and deletion policies
- comprehensive multi-attachment processing
- rate-limit handling
- human approval for consequential decisions
- controlled email recipient logic
