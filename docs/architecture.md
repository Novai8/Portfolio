# Automation Architecture

## Workflow

1. **Gmail Trigger - ISYS Reports** receives an incoming report email.
2. **Prepare - Intake & Primary Document** separates the message, sender details, primary report, and supporting files.
3. **Route - Document Type** identifies PDF, CSV, spreadsheet, text, HTML, or unsupported documents.
4. Document-specific extraction nodes convert supported attachments into usable text/data.
5. **Normalize** nodes create a consistent document representation for the reviewer.
6. **AI Quality Review** compares the email and attachment as separate sources.
7. **Structured Parser - Quality Review** converts the AI result into predictable fields.
8. **Supabase - Create Case** stores the review result in the `cases` table.
9. **IF - Follow-up Required?** chooses the business outcome.
10. Follow-up path creates and sends a professional clarification email, then updates the case and marks the Gmail message processed.
11. Completion path marks the case completed and marks the Gmail message processed.

## Design principles

- Do not invent missing information.
- Do not guess when evidence is unavailable.
- Keep email and attachment evidence distinct.
- Flag contradictions instead of silently choosing a value.
- Store structured review results for downstream automation.
- Use fictional/sample data only.
- Clearly separate this prototype from any real ISYS system.

## Supported document types

- PDF
- CSV
- Spreadsheet
- Text
- HTML
- Unsupported files, which are normalized as unavailable for reliable review
