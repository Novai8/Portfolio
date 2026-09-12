# Test Cases

All data below is fictional and exists only for demonstration.

## 1. Complete case

**Case:** ISYS-73104  
**Report:** R-4216  
**Customer:** Summit General Insurance  
**Queue:** A  
**Report type:** Vehicle Damage Assessment

Everything required is present.

**Expected:**

- `email_required = false`
- `overall_status = Ready`
- Case completes without a follow-up email.

## 2. Missing document

**Case:** ISYS-59283  
**Report:** R-3371  
**Customer:** Harborview Claims Services  
**Queue:** A  
**Report type:** Property Damage Report

The required supporting invoice is missing.

**Expected:**

- `email_required = true`
- `overall_status = Missing Information`
- Follow-up email is generated and sent.

## 3. Contradiction

**Case:** ISYS-84621  
**Report:** R-5084  
**Customer:** Meridian Risk Partners  
**Queue:** D  
**Report type:** Commercial Property Inspection

The narrative gives September 6 as the inspection date while case notes give September 7. The customer requires consistent dates.

**Expected:**

- `email_required = true`
- `overall_status = Needs Review`
- Follow-up email requests clarification.

## 4. Serious escalation

**Case:** ISYS-91462  
**Report:** R-6198  
**Customer:** Evergreen Commercial Insurance  
**Queue:** D  
**Report type:** Commercial Property Damage Assessment

The narrative reports $48,500 damage while the repair estimate/invoice is $84,500. Additional structural damage is also absent from the narrative. Deadline: September 12, 2026.

**Expected:**

- `email_required = true`
- `urgency = Urgent`
- `overall_status = Escalation Required`
- Recommended action includes supervisor review.
