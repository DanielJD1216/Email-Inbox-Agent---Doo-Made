from __future__ import annotations

import argparse
import base64
import os
from datetime import datetime, timezone
from email.message import EmailMessage

from app.gmail_client import get_gmail_service


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send synthetic stress-test emails to your Gmail inbox.")
    parser.add_argument(
        "--to-email",
        default=os.getenv("STRESS_TEST_TO_EMAIL", "").strip(),
        help=(
            "Recipient email. If omitted, script uses your authenticated Gmail address "
            "(users.getProfile userId='me')."
        ),
    )
    parser.add_argument(
        "--prefix",
        default="",
        help="Optional subject prefix override. Default: [AI-STRESS-YYYYMMDD-HHMMSS].",
    )
    return parser.parse_args()


def build_cases(prefix: str) -> list[dict[str, str]]:
    return [
        {
            "category": "Credit Card Statement",
            "subject": f"{prefix} Credit Card Statement Available - March 2026",
            "body": (
                "Hello Daniel,\n\n"
                "Your March 2026 statement is now available.\n"
                "Statement balance: $4,284.13\n"
                "Payment due date: March 22, 2026\n"
                "Minimum payment: $127.00\n\n"
                "You can review detailed transactions in your account portal.\n\n"
                "Banking Ops Team"
            ),
        },
        {
            "category": "Spam / Phishing",
            "subject": f"{prefix} Urgent: Confirm your mailbox within 30 minutes",
            "body": (
                "Dear user,\n\n"
                "Your mailbox will be permanently suspended unless you verify now.\n"
                "Click this unofficial link immediately: hxxp://mailbox-check-now.example\n\n"
                "Failure to act will result in data deletion.\n\n"
                "Mail Security Center"
            ),
        },
        {
            "category": "Ecommerce",
            "subject": f"{prefix} Your DooMade order DM-49382 has shipped",
            "body": (
                "Hi Daniel,\n\n"
                "Good news, your order DM-49382 is on the way.\n"
                "Carrier: UPS\n"
                "Tracking: 1Z84Y7XX0391821\n"
                "Estimated delivery: March 7, 2026\n\n"
                "Thanks for shopping with us."
            ),
        },
        {
            "category": "Events & Calendar",
            "subject": f"{prefix} Invite: Product Roadmap Sync (Fri 2:00 PM)",
            "body": (
                "Hi Daniel,\n\n"
                "Can you confirm attendance for Product Roadmap Sync?\n"
                "Date: Friday, March 6, 2026\n"
                "Time: 2:00 PM - 2:45 PM PT\n"
                "Agenda: Q2 priorities, launch risk review, hiring plan\n\n"
                "Please reply yes/no."
            ),
        },
        {
            "category": "Newsletter",
            "subject": f"{prefix} Weekly Growth Newsletter - 12 ideas for creators",
            "body": (
                "Hey Daniel,\n\n"
                "This week:\n"
                "- 3 short-form hooks that doubled engagement\n"
                "- A/B test framework for landing pages\n"
                "- Community retention checklist\n\n"
                "Read when you have time."
            ),
        },
        {
            "category": "Security/Admin",
            "subject": f"{prefix} Security alert: New admin login from unknown device",
            "body": (
                "Hello,\n\n"
                "We detected an admin login from a new device.\n"
                "Location: Bucharest, Romania\n"
                "Time: 2026-03-04 13:58 UTC\n\n"
                "If this wasn't you, reset your password and revoke sessions immediately."
            ),
        },
        {
            "category": "Receipts & Billing",
            "subject": f"{prefix} Receipt: Payment for DooMade Pro (Invoice #8452)",
            "body": (
                "Hi Daniel,\n\n"
                "Thanks for your payment.\n"
                "Amount: $49.00 USD\n"
                "Invoice: #8452\n"
                "Method: Visa ending 1029\n"
                "Date: March 4, 2026\n\n"
                "Attached invoice is available in your billing portal."
            ),
        },
        {
            "category": "SaaS & Tools",
            "subject": f"{prefix} [Status] API incident resolved - elevated latency",
            "body": (
                "Team,\n\n"
                "Today's API latency incident has been resolved.\n"
                "Impact window: 10:14-10:39 PT\n"
                "Root cause: cache node failover\n"
                "Action: no customer intervention required\n\n"
                "Postmortem tomorrow."
            ),
        },
        {
            "category": "Sales Outreach",
            "subject": f"{prefix} Quick idea to increase inbound demos by 30%",
            "body": (
                "Hi Daniel,\n\n"
                "I reviewed your site and found 3 funnel fixes that can improve demo conversion.\n"
                "If helpful, I can send a 5-minute teardown video.\n\n"
                "Open to it?"
            ),
        },
        {
            "category": "Professional Networking",
            "subject": f"{prefix} Partnership inquiry from Acme Media",
            "body": (
                "Hi Daniel,\n\n"
                "We'd like to discuss a co-marketing campaign for Q2.\n"
                "Could we set up a 20-minute call next week?\n\n"
                "Best,\n"
                "Maya\n"
                "Acme Media"
            ),
        },
        {
            "category": "Action Required",
            "subject": f"{prefix} Action required: Sign contractor agreement by Thursday",
            "body": (
                "Hi Daniel,\n\n"
                "Please review and sign the contractor agreement by Thursday EOD.\n"
                "Without signature, finance cannot release the next payment batch.\n\n"
                "Reply if you need redlines."
            ),
        },
        {
            "category": "Travel / Calendar",
            "subject": f"{prefix} Flight itinerary confirmed: YVR -> SFO (Mar 18)",
            "body": (
                "Hi Daniel,\n\n"
                "Your flight booking is confirmed.\n"
                "Departure: March 18, 2026 - 08:15 AM PT\n"
                "Return: March 20, 2026 - 06:40 PM PT\n"
                "Booking ref: R7Q9L2\n\n"
                "Please review baggage rules."
            ),
        },
        {
            "category": "SaaS Billing",
            "subject": f"{prefix} Renewal reminder: Figma Professional annual plan",
            "body": (
                "Hello Daniel,\n\n"
                "Your annual Figma Professional subscription renews in 5 days.\n"
                "Renewal amount: $192.00\n"
                "Renewal date: March 9, 2026\n\n"
                "No action required unless you want to change seats."
            ),
        },
        {
            "category": "Customer Support",
            "subject": f"{prefix} Customer issue: Cannot download invoice PDF",
            "body": (
                "Hi Daniel,\n\n"
                "A customer reports invoice downloads failing with a 500 error.\n"
                "Account: brightpath-studio\n"
                "First seen: 11:22 AM PT\n\n"
                "Can your team investigate and reply with ETA?"
            ),
        },
        {
            "category": "Security / Spear-Phish",
            "subject": f"{prefix} Urgent payroll update required before cutoff",
            "body": (
                "Daniel,\n\n"
                "Payroll processing is blocked. Please send your updated banking info now\n"
                "or your salary may be delayed.\n"
                "Use this form immediately: hxxp://secure-payroll-update.example\n\n"
                "HR Department"
            ),
        },
    ]


def resolve_recipient_email(service, explicit_to_email: str) -> str:
    if explicit_to_email and explicit_to_email.strip():
        return explicit_to_email.strip()

    profile = service.users().getProfile(userId="me").execute()
    to_email = str(profile.get("emailAddress", "")).strip()
    if not to_email:
        raise RuntimeError(
            "Could not resolve authenticated Gmail address. "
            "Pass --to-email or set STRESS_TEST_TO_EMAIL."
        )
    return to_email


def send_case(service, case: dict[str, str], to_email: str) -> str:
    msg = EmailMessage()
    msg["To"] = to_email
    msg["Subject"] = case["subject"]
    msg.set_content(case["body"])

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    return str(result.get("id", ""))


def main() -> None:
    args = parse_args()
    service = get_gmail_service()
    now_tag = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    prefix = args.prefix.strip() if args.prefix.strip() else f"[AI-STRESS-{now_tag}]"
    to_email = resolve_recipient_email(service, args.to_email)
    cases = build_cases(prefix)
    print(f"Sending {len(cases)} stress-test emails to {to_email} ...")

    sent_ids: list[str] = []
    for index, case in enumerate(cases, start=1):
        message_id = send_case(service, case, to_email)
        sent_ids.append(message_id)
        print(
            f"{index:02d}. [{case['category']}] sent | "
            f"subject={case['subject']} | message_id={message_id}"
        )

    print(f"Done. Sent {len(sent_ids)} emails with prefix {prefix}")


if __name__ == "__main__":
    main()
