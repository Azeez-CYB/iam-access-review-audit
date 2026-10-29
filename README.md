[README.md](https://github.com/user-attachments/files/34147113/README.md)
# IAM Access Review and Audit

## Project overview
This beginner-friendly portfolio project simulates an identity and access management (IAM) access review using fictional user and permission data. It flags accounts or permission combinations that should be investigated by an access owner or security team.

**Important:** All names and records are synthetic. This is an educational simulation, not a production security tool or a substitute for a formal access review.

## What it checks
1. **Leaver accounts:** a record marked `Leaver` still appears in the access register.
2. **Dormant accounts:** the last login is more than 90 days before the review date.
3. **Privileged access approval:** `Privileged Admin` is assigned but approval is not recorded as `Yes`.
4. **Potential segregation-of-duties conflict:** one account has both `Payment Initiator` and `Payment Approver`.

These are illustrative rules. Real organisations must confirm policy, exceptions, data quality and ownership before treating a result as a control failure.

## Files
- `sample_access_register.csv` — fictional sample data.
- `iam_access_review.py` — Python script that applies the review rules.
- `access_review_findings.csv` — generated when the script runs.
- `audit_report_template.md` — template for documenting results and remediation.

## Run on macOS
1. Install Python 3 if needed.
2. Open Terminal and move into this folder.
3. Install pandas: `python3 -m pip install pandas`
4. Run: `python3 iam_access_review.py`
5. Open `access_review_findings.csv` in Excel or Numbers.

## Suggested review workflow
1. Confirm the review date and data owner.
2. Review each generated finding; automated flags are leads for investigation, not proof of inappropriate access.
3. Record the reviewer decision and evidence needed.
4. Assign an owner and due date for remediation.
5. Track each item until it is resolved or an exception is formally approved.
6. Summarise the outcomes in the audit report template.

## Limitations and next improvements
- The script uses a fixed review date for reproducibility.
- The sample register does not include an authoritative role-to-permission matrix, so it cannot reliably prove that a permission is excessive for a user's job.
- The segregation-of-duties rule is illustrative and should be validated against a real policy.
- Next steps: add a role-permission baseline, exception register, remediation owner and due date, summary dashboard, and automated tests.

