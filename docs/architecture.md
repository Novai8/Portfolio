# Automation Architecture

## Verified workflow

The current n8n workflow is named **ISYS Administrative Quality Review • Demo Ready**.

The workflow is an independent portfolio prototype using fictional/sample data. It is not an official ISYS system and is not connected to ISYS internal systems.

### 1. Gmail intake

`Gmail Trigger - ISYS Reports` processes unread messages matching the workflow's existing intake query.

The original Gmail message ID is preserved throughout the workflow so later status updates can target the source message rather than a generated follow-up email.

### 2. Attachment preparation

`Prepare - Intake & Primary Document` now prepares one processing item per detected attachment.

For each attachment it records:

- filename
- MIME type
- extension fallback when MIME metadata is unavailable
- attachment availability
- processing metadata

The existing document routing paths remain in place.

### 3. Document routing and extraction

`Route - Document Type` sends each attachment to the appropriate extraction path:

| Input | Extraction |
|---|---|
| PDF | Extract PDF |
| CSV | Extract CSV |
| XLS/XLSX | Extract Spreadsheet |
| TXT | Extract Text |
| HTML | Extract HTML |
| Other / unavailable | Unsupported / Not Reviewed |

After extraction, `Aggregate - Extracted Documents` combines all document results so the AI reviewer receives the complete set of successfully extracted documents.

Each document retains its filename, type, extraction status, and extracted text.

Unsupported or failed documents are explicitly represented as **not reviewed**. They are not silently omitted and the AI is instructed not to claim that they were inspected.

### 4. AI quality review

`AI Quality Review` uses OpenAI `gpt-5-mini` with structured output.

The reviewer receives the original Gmail content and the extracted document evidence as distinct sources. It checks:

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

The system prompt explicitly prohibits invented facts and prevents the model from claiming that unseen or unsupported attachments were reviewed.

### 5. Structured case storage

`Normalize - Review Result` converts the AI output into the database-ready object.

`Supabase - Create Case` stores the review in the existing `cases` table.

The original Gmail message ID remains available for traceability. No database schema changes were required for the current implementation.

### 6. Business decision

`IF - Follow-up Required?` branches using the structured `email_required` value.

#### Follow-up path

```text
AI Follow-up Email Writer
        ↓
Build - Professional Email
        ↓
Gmail - Send Follow-up
        ↓
Supabase - Mark Email Sent
        ↓
Gmail - Mark Processed Read
```

The final Gmail operation uses the original message ID from `Gmail Trigger - ISYS Reports`, ensuring that the incoming report is marked processed rather than the newly generated follow-up email.

The follow-up email no longer uses official-looking ISYS branding or a logo. It identifies the communication as part of an independent **Administrative Quality Review** portfolio prototype.

#### Clean completion path

```text
Supabase - Mark Completed
        ↓
Gmail - Mark Processed Read (No Follow-up)
```

Cases requiring no follow-up are marked completed and the original Gmail message is marked as read.

### 7. Error handling

The workflow contains an in-workflow error path:

```text
Error Trigger
     ↓
Error Diagnostics
```

Controlled retries are configured for relevant extraction, AI review, Supabase, and Gmail operations. n8n execution error data remains configured to be saved.

A failed operation is not treated as a successful business case.

## Document evidence model

The workflow distinguishes three evidence categories:

1. **Email evidence:** sender, subject, Gmail message ID, message body, and stated requirements.
2. **Attachment evidence:** extracted content from each successfully processed attachment.
3. **Attachment metadata:** filename, MIME type, extension, availability, and extraction status.

If a document cannot be reliably extracted or is unsupported, it remains visible to the AI as unavailable for verification instead of being treated as reviewed.

## Status model

The workflow uses controlled lifecycle and review values, including:

- `document_status`: Complete, Missing Documents, Needs Review, Not Applicable
- `invoice_status`: Present, Missing, Inconsistent, Not Applicable, Unable to Verify
- `overall_status`: Ready, Needs Review, Missing Information, Escalation Required
- `urgency`: Low, Medium, High, Urgent
- `processing_status`: Reviewed, Email Sent, Completed, or failure state where applicable
- `email_status`: Not Required, Pending, Sent, Failed

## Design principles

- **Evidence first:** never invent unavailable information.
- **Source separation:** email and attachment evidence remain distinct.
- **Document-level traceability:** every attachment retains its processing metadata.
- **Contradiction detection:** conflicting information is flagged rather than silently resolved.
- **Structured output:** AI results use predictable fields before database storage.
- **Conditional automation:** follow-up communication occurs only when required.
- **Failure visibility:** failed operations are surfaced instead of being represented as successful cases.
- **Traceability:** the original Gmail message ID connects intake, case storage, follow-up, and read-state updates.
- **Safe demonstration data:** the prototype uses fictional/sample information only.
- **Clear independence:** the workflow is inspired by a public job description and is not an official ISYS system.

## Validation status

The following paths were successfully verified during the final workflow review:

### Follow-up path

```text
Supabase - Mark Email Sent
        ↓
Gmail - Mark Processed Read
```

The original incoming Gmail message ID was preserved through the test.

### No-follow-up path

```text
Supabase - Mark Completed
        ↓
Gmail - Mark Processed Read (No Follow-up)
```

This path was also successfully tested.

### Multi-attachment limitation

The multi-attachment architecture is implemented and the graph/connections were verified. However, a true live Gmail execution containing multiple real binary attachments could not be performed through the available MCP interface because the Gmail trigger cannot be directly executed with injected binary attachments through that testing mechanism.

Therefore the repository does not claim that this exact multi-binary-input scenario was live-tested.

## Production considerations

A production implementation would require:

- organization-specific validation rules
- secure credential and secret management
- authorization controls
- retry and failure policies appropriate to business impact
- monitoring and alerting
- audit logging
- document retention and deletion policies
- comprehensive attachment processing and file-size handling
- rate-limit handling
- controlled email recipient logic
- human approval for consequential decisions
