
import pandas as pd
from pathlib import Path

# Files are stored alongside this script.
FOLDER = Path(__file__).parent
DATA_FILE = FOLDER / "sample_access_register.csv"
MATRIX_FILE = FOLDER / "role_permission_matrix.csv"
OUTPUT_FILE = FOLDER / "access_review_findings.csv"

REVIEW_DATE = pd.Timestamp("2026-10-28")
DORMANT_DAYS = 90

# Load the fictional access register and role baseline.
df = pd.read_csv(DATA_FILE)
matrix_df = pd.read_csv(MATRIX_FILE)

df["last_login_date"] = pd.to_datetime(
    df["last_login_date"], errors="coerce"
)

# Build a lookup of role -> permitted permissions.
role_permissions = {}

for _, item in matrix_df.iterrows():
    role = str(item["job_role"]).strip().lower()

    allowed = {
        permission.strip().lower()
        for permission in str(item["allowed_permissions"]).split(";")
        if permission.strip()
    }

    role_permissions[role] = allowed

findings = []


def add_finding(row, category, severity, detail, recommendation):
    findings.append({
        "user_id": row["user_id"],
        "user_name": row["user_name"],
        "department": row["department"],
        "job_role": row["job_role"],
        "category": category,
        "severity": severity,
        "finding": detail,
        "recommended_action": recommendation,
        "status": "Open"
    })


for _, row in df.iterrows():

    permissions = {
        permission.strip().lower()
        for permission in str(
            row["assigned_permissions"]
        ).split(";")
        if permission.strip()
    }

    role = str(row["job_role"]).strip().lower()
    allowed = role_permissions.get(role)

    # CHECK 1: Compare actual permissions against the role baseline.
    if allowed is None:
        add_finding(
            row,
            "Role missing from baseline",
            "Medium",
            f"No baseline exists for role '{row['job_role']}'.",
            "Ask the role owner to define and approve standard permissions."
        )
    else:
        unexpected = permissions - allowed

        for permission in sorted(unexpected):
            sensitive_permissions = {
                "privileged admin",
                "payment approver",
                "payroll admin"
            }

            severity = (
                "High"
                if permission in sensitive_permissions
                else "Medium"
            )

            add_finding(
                row,
                "Permission outside role baseline",
                severity,
                f"'{permission}' is not listed in the baseline "
                f"for '{row['job_role']}'.",
                "Verify business need and approval with the access "
                "owner; remove access if it is not justified."
            )

    # CHECK 2: Leaver accounts.
    if str(row["employment_status"]).strip().lower() == "leaver":
        add_finding(
            row,
            "Leaver account",
            "High",
            "The account is listed for a leaver.",
            "Confirm the account is disabled and access revoked; "
            "retain evidence of completion."
        )

    # CHECK 3: Dormant accounts.
    last_login = row["last_login_date"]

    if pd.notna(last_login):
        days_since_login = (REVIEW_DATE - last_login).days

        if days_since_login > DORMANT_DAYS:
            add_finding(
                row,
                "Dormant account",
                "Medium",
                f"No login recorded for {days_since_login} days.",
                "Confirm access is still required; remove or disable "
                "it if no longer needed."
            )

    # CHECK 4: Privileged access approval.
    if (
        "privileged admin" in permissions
        and str(row["privileged_access_approved"]).strip().lower()
        != "yes"
    ):
        add_finding(
            row,
            "Privileged access approval",
            "High",
            "Privileged Admin is assigned but approval is not "
            "recorded as Yes.",
            "Verify the business need and approval; remove access "
            "if it is not authorised."
        )

    # CHECK 5: Illustrative segregation-of-duties rule.
    if (
        "payment initiator" in permissions
        and "payment approver" in permissions
    ):
        add_finding(
            row,
            "Potential segregation-of-duties conflict",
            "High",
            "The same account has Payment Initiator and "
            "Payment Approver permissions.",
            "Ask the system owner to review the conflict and "
            "separate duties or document an approved exception."
        )

# Export findings for human review.
columns = [
    "user_id",
    "user_name",
    "department",
    "job_role",
    "category",
    "severity",
    "finding",
    "recommended_action",
    "status"
]

findings_df = pd.DataFrame(findings, columns=columns)
findings_df.to_csv(OUTPUT_FILE, index=False)

print("IAM Access Review completed")
print(f"Review date: {REVIEW_DATE.date()}")
print(f"Accounts reviewed: {len(df)}")
print(f"Findings generated: {len(findings_df)}")

if not findings_df.empty:
    print("\nFindings by category:")
    print(findings_df["category"].value_counts().to_string())

print(f"\nDetailed findings saved to: {OUTPUT_FILE.name}")

