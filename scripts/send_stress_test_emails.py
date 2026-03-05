from __future__ import annotations

import argparse
import base64
import os
import random
import string
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from typing import Callable

from app.gmail_client import get_gmail_service


Case = dict[str, str]
CaseBuilder = Callable[[str, random.Random, str], Case]


FIRST_NAMES = [
    "Alex",
    "Jordan",
    "Taylor",
    "Sam",
    "Morgan",
    "Casey",
    "Riley",
    "Avery",
    "Jamie",
    "Cameron",
]
LAST_NAMES = [
    "Lee",
    "Patel",
    "Kim",
    "Chen",
    "Garcia",
    "Singh",
    "Wong",
    "Brown",
    "Johnson",
    "Nguyen",
]
BANKS = ["Summit Bank", "North Harbor Bank", "Atlas Credit Union", "BluePeak Financial"]
CARRIERS = ["UPS", "FedEx", "DHL", "USPS"]
AIRPORT_CODES = ["SFO", "LAX", "SEA", "YVR", "JFK", "AUS", "ORD", "MIA"]
SENDER_COMPANIES = [
    "BrightPath",
    "Acme Media",
    "Nexa Labs",
    "Northstar Ventures",
    "Vertex Studio",
    "FlowForge",
]
PRODUCTS = ["Pro", "Business", "Teams", "Growth", "Analytics", "Enterprise"]
TOOLS = ["Figma", "Notion", "Slack", "HubSpot", "Linear", "ClickUp", "Asana", "Canva"]
MEETING_TOPICS = [
    "Q2 roadmap sync",
    "budget planning review",
    "launch readiness",
    "partner kickoff",
    "hiring plan check-in",
]
NEWSLETTER_TOPICS = [
    "conversion lift experiments",
    "founder content systems",
    "landing page teardown",
    "B2B outbound playbook",
    "customer retention tactics",
]
INCIDENT_ROOT_CAUSES = [
    "cache cluster failover",
    "database connection saturation",
    "rate-limit misconfiguration",
    "upstream provider timeout",
]
PHISHING_DOMAINS = [
    "secure-mailbox-check.example",
    "payroll-verify-now.example",
    "urgent-auth-reset.example",
    "mail-security-update.example",
]


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
    parser.add_argument(
        "--count",
        type=int,
        default=read_env_int("STRESS_TEST_COUNT", 15),
        help="How many randomized stress-test emails to send. Default: 15.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional random seed for reproducible test runs.",
    )
    args = parser.parse_args()
    if args.count <= 0:
        raise ValueError("--count must be greater than 0")
    return args


def read_env_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def prefixed(prefix: str, subject: str) -> str:
    clean_prefix = prefix.strip()
    return f"{clean_prefix} {subject}".strip() if clean_prefix else subject


def pretty_date(value: datetime) -> str:
    return value.strftime("%B %d, %Y").replace(" 0", " ")


def pretty_time(value: datetime) -> str:
    return value.strftime("%I:%M %p").lstrip("0")


def random_money(rng: random.Random, low: float, high: float) -> str:
    return f"${rng.uniform(low, high):,.2f}"


def random_digits(rng: random.Random, length: int) -> str:
    return "".join(rng.choice(string.digits) for _ in range(length))


def random_alnum(rng: random.Random, length: int) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(rng.choice(alphabet) for _ in range(length))


def random_name(rng: random.Random) -> str:
    return f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"


def infer_display_name(email: str) -> str:
    local = email.split("@", 1)[0]
    parts = [p for p in local.replace("_", ".").replace("-", ".").split(".") if p]
    if not parts:
        return "there"
    guessed = " ".join(p.capitalize() for p in parts[:2])
    return guessed if guessed else "there"


def finance_statement_case(prefix: str, rng: random.Random, display_name: str) -> Case:
    bank = rng.choice(BANKS)
    due_date = datetime.now(timezone.utc) + timedelta(days=rng.randint(4, 22))
    month_label = due_date.strftime("%B %Y")
    return {
        "category": "Finance",
        "subject": prefixed(prefix, f"{bank} statement available - {month_label}"),
        "body": (
            f"Hello {display_name},\n\n"
            f"Your {month_label} statement is now available.\n"
            f"Statement balance: {random_money(rng, 400, 8500)}\n"
            f"Payment due date: {pretty_date(due_date)}\n"
            f"Minimum payment: {random_money(rng, 25, 350)}\n\n"
            "You can review full transaction details in your account portal.\n\n"
            "Banking Operations Team"
        ),
    }


def phishing_mailbox_case(prefix: str, rng: random.Random, display_name: str) -> Case:
    minutes = rng.choice([15, 30, 45, 60])
    return {
        "category": "Security/Admin",
        "subject": prefixed(prefix, f"Urgent: Confirm your mailbox within {minutes} minutes"),
        "body": (
            f"Dear {display_name},\n\n"
            "Your mailbox will be permanently suspended unless you verify now.\n"
            f"Click this link immediately: hxxp://{rng.choice(PHISHING_DOMAINS)}\n\n"
            "Failure to act may result in account data deletion.\n\n"
            "Mailbox Security Center"
        ),
    }


def ecommerce_shipping_case(prefix: str, rng: random.Random, display_name: str) -> Case:
    order_id = f"DM-{random_digits(rng, 5)}"
    carrier = rng.choice(CARRIERS)
    eta = datetime.now(timezone.utc) + timedelta(days=rng.randint(1, 7))
    return {
        "category": "Receipts & Billing",
        "subject": prefixed(prefix, f"Your order {order_id} has shipped"),
        "body": (
            f"Hi {display_name},\n\n"
            f"Good news, your order {order_id} is on the way.\n"
            f"Carrier: {carrier}\n"
            f"Tracking: {random_alnum(rng, 14)}\n"
            f"Estimated delivery: {pretty_date(eta)}\n\n"
            "Thanks for shopping with us."
        ),
    }


def events_invite_case(prefix: str, rng: random.Random, display_name: str) -> Case:
    start = datetime.now(timezone.utc) + timedelta(days=rng.randint(1, 10), hours=rng.randint(8, 19))
    end = start + timedelta(minutes=rng.choice([30, 45, 60]))
    topic = rng.choice(MEETING_TOPICS).title()
    return {
        "category": "Events & Calendar",
        "subject": prefixed(prefix, f"Invite: {topic} ({start.strftime('%a')} {pretty_time(start)})"),
        "body": (
            f"Hi {display_name},\n\n"
            f"Can you confirm attendance for {topic}?\n"
            f"Date: {start.strftime('%A')}, {pretty_date(start)}\n"
            f"Time: {pretty_time(start)} - {pretty_time(end)} PT\n"
            "Please reply yes/no."
        ),
    }


def newsletter_case(prefix: str, rng: random.Random, display_name: str) -> Case:
    topic = rng.choice(NEWSLETTER_TOPICS)
    return {
        "category": "Newsletters",
        "subject": prefixed(prefix, f"Weekly update: {topic}"),
        "body": (
            f"Hi {display_name},\n\n"
            "This week:\n"
            f"- Insight #1 on {topic}\n"
            "- A practical checklist you can run in under 15 minutes\n"
            "- One benchmark from top-performing teams\n\n"
            "Read when you have time."
        ),
    }


def security_alert_case(prefix: str, rng: random.Random, _: str) -> Case:
    timestamp = datetime.now(timezone.utc) - timedelta(minutes=rng.randint(5, 300))
    locations = ["Bucharest, Romania", "Jakarta, Indonesia", "Berlin, Germany", "Toronto, Canada", "Austin, USA"]
    return {
        "category": "Security/Admin",
        "subject": prefixed(prefix, "Security alert: New admin login from unknown device"),
        "body": (
            "Hello,\n\n"
            "We detected an admin login from a new device.\n"
            f"Location: {rng.choice(locations)}\n"
            f"Time: {timestamp.strftime('%Y-%m-%d %H:%M UTC')}\n\n"
            "If this was not you, reset your password and revoke active sessions immediately."
        ),
    }


def receipts_case(prefix: str, rng: random.Random, display_name: str) -> Case:
    invoice = random_digits(rng, 4)
    return {
        "category": "Receipts & Billing",
        "subject": prefixed(prefix, f"Receipt: Payment received (Invoice #{invoice})"),
        "body": (
            f"Hi {display_name},\n\n"
            "Thanks for your payment.\n"
            f"Amount: {random_money(rng, 19, 799)} USD\n"
            f"Invoice: #{invoice}\n"
            f"Method: Visa ending {random_digits(rng, 4)}\n"
            f"Date: {pretty_date(datetime.now(timezone.utc))}\n\n"
            "Your invoice PDF is available in the billing portal."
        ),
    }


def saas_status_case(prefix: str, rng: random.Random, _: str) -> Case:
    start = datetime.now(timezone.utc) - timedelta(minutes=rng.randint(40, 180))
    end = start + timedelta(minutes=rng.randint(8, 45))
    return {
        "category": "SaaS & Tools",
        "subject": prefixed(prefix, "[Status] API incident resolved - elevated latency"),
        "body": (
            "Team,\n\n"
            "Today's API latency incident has been resolved.\n"
            f"Impact window: {pretty_time(start)}-{pretty_time(end)} PT\n"
            f"Root cause: {rng.choice(INCIDENT_ROOT_CAUSES)}\n"
            "Action: no customer intervention required.\n\n"
            "Postmortem tomorrow."
        ),
    }


def sales_outreach_case(prefix: str, rng: random.Random, display_name: str) -> Case:
    uplift = rng.randint(12, 45)
    return {
        "category": "Sales & Outreach",
        "subject": prefixed(prefix, f"Quick idea to increase inbound demos by {uplift}%"),
        "body": (
            f"Hi {display_name},\n\n"
            "I reviewed your site and found funnel fixes that could improve demo conversion.\n"
            "If helpful, I can send a short teardown video with concrete edits.\n\n"
            "Open to it?"
        ),
    }


def professional_network_case(prefix: str, rng: random.Random, display_name: str) -> Case:
    contact = random_name(rng)
    company = rng.choice(SENDER_COMPANIES)
    return {
        "category": "Professional Network",
        "subject": prefixed(prefix, f"Partnership inquiry from {company}"),
        "body": (
            f"Hi {display_name},\n\n"
            f"I am {contact} from {company}. We would like to discuss a co-marketing campaign for next quarter.\n"
            "Would you be open to a 20-minute intro call next week?\n\n"
            "Best,\n"
            f"{contact}"
        ),
    }


def action_required_case(prefix: str, rng: random.Random, display_name: str) -> Case:
    due = datetime.now(timezone.utc) + timedelta(days=rng.randint(1, 4))
    task = rng.choice(
        [
            "sign contractor agreement",
            "approve budget request",
            "review legal redlines",
            "submit final invoice approval",
        ]
    )
    return {
        "category": "Action Required",
        "subject": prefixed(prefix, f"Action required: {task} by {due.strftime('%A')}"),
        "body": (
            f"Hi {display_name},\n\n"
            f"Please {task} by {due.strftime('%A')} EOD.\n"
            "Without completion, the related payment workflow may be delayed.\n\n"
            "Reply if you need context or documents."
        ),
    }


def travel_itinerary_case(prefix: str, rng: random.Random, display_name: str) -> Case:
    departure = datetime.now(timezone.utc) + timedelta(days=rng.randint(7, 45), hours=rng.randint(5, 18))
    return_time = departure + timedelta(days=rng.randint(1, 6), hours=rng.randint(2, 12))
    origin, destination = rng.sample(AIRPORT_CODES, 2)
    return {
        "category": "Events & Calendar",
        "subject": prefixed(prefix, f"Flight itinerary confirmed: {origin} -> {destination}"),
        "body": (
            f"Hi {display_name},\n\n"
            "Your flight booking is confirmed.\n"
            f"Departure: {pretty_date(departure)} - {pretty_time(departure)} PT\n"
            f"Return: {pretty_date(return_time)} - {pretty_time(return_time)} PT\n"
            f"Booking ref: {random_alnum(rng, 6)}\n\n"
            "Please review baggage rules."
        ),
    }


def saas_renewal_case(prefix: str, rng: random.Random, display_name: str) -> Case:
    tool = rng.choice(TOOLS)
    plan = rng.choice(PRODUCTS)
    renewal_date = datetime.now(timezone.utc) + timedelta(days=rng.randint(2, 21))
    return {
        "category": "SaaS & Tools",
        "subject": prefixed(prefix, f"Renewal reminder: {tool} {plan} annual plan"),
        "body": (
            f"Hello {display_name},\n\n"
            f"Your {tool} {plan} subscription renews in {rng.randint(2, 14)} days.\n"
            f"Renewal amount: {random_money(rng, 45, 650)}\n"
            f"Renewal date: {pretty_date(renewal_date)}\n\n"
            "No action required unless you want to change seats."
        ),
    }


def customer_support_case(prefix: str, rng: random.Random, display_name: str) -> Case:
    account = f"{rng.choice(['brightpath', 'northstar', 'summit', 'lumen'])}-{rng.choice(['studio', 'labs', 'media', 'agency'])}"
    first_seen = datetime.now(timezone.utc) - timedelta(minutes=rng.randint(5, 240))
    return {
        "category": "Action Required",
        "subject": prefixed(prefix, "Customer issue: Cannot download invoice PDF"),
        "body": (
            f"Hi {display_name},\n\n"
            "A customer reports invoice downloads failing with a 500 error.\n"
            f"Account: {account}\n"
            f"First seen: {pretty_time(first_seen)} PT\n\n"
            "Can your team investigate and reply with ETA?"
        ),
    }


def spear_phish_payroll_case(prefix: str, rng: random.Random, display_name: str) -> Case:
    return {
        "category": "Security/Admin",
        "subject": prefixed(prefix, "Urgent payroll update required before cutoff"),
        "body": (
            f"{display_name},\n\n"
            "Payroll processing is blocked. Please send updated banking details now\n"
            "or salary may be delayed.\n"
            f"Use this form immediately: hxxp://{rng.choice(PHISHING_DOMAINS)}\n\n"
            "HR Department"
        ),
    }


CASE_BUILDERS: list[CaseBuilder] = [
    finance_statement_case,
    phishing_mailbox_case,
    ecommerce_shipping_case,
    events_invite_case,
    newsletter_case,
    security_alert_case,
    receipts_case,
    saas_status_case,
    sales_outreach_case,
    professional_network_case,
    action_required_case,
    travel_itinerary_case,
    saas_renewal_case,
    customer_support_case,
    spear_phish_payroll_case,
]


def build_cases(prefix: str, count: int, rng: random.Random, display_name: str) -> list[Case]:
    chosen_builders = pick_builders(count, rng)
    return [builder(prefix, rng, display_name) for builder in chosen_builders]


def pick_builders(count: int, rng: random.Random) -> list[CaseBuilder]:
    pool = CASE_BUILDERS.copy()
    rng.shuffle(pool)
    chosen: list[CaseBuilder] = []
    while len(chosen) < count:
        if not pool:
            pool = CASE_BUILDERS.copy()
            rng.shuffle(pool)
        chosen.append(pool.pop())
    return chosen


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


def send_case(service, case: Case, to_email: str) -> str:
    msg = EmailMessage()
    msg["To"] = to_email
    msg["Subject"] = case["subject"]
    msg.set_content(case["body"])

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    return str(result.get("id", ""))


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)
    service = get_gmail_service()

    now_tag = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    prefix = args.prefix.strip() if args.prefix.strip() else f"[AI-STRESS-{now_tag}]"
    to_email = resolve_recipient_email(service, args.to_email)
    display_name = infer_display_name(to_email)
    cases = build_cases(prefix, args.count, rng, display_name)

    seed_display = "auto" if args.seed is None else str(args.seed)
    print(
        f"Sending {len(cases)} randomized stress-test emails to {to_email} "
        f"(seed={seed_display}) ..."
    )

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
