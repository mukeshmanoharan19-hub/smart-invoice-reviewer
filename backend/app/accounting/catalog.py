"""Fixed Northstar general ledger catalog.

The descriptions are also the prompt source of truth for GL suggestion.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class GlAccountCode(StrEnum):
    cleaning = "6100"
    building_maintenance = "6110"
    electrical = "6120"
    plumbing_hvac = "6130"
    equipment = "6140"
    office_supplies = "6150"
    professional_fees = "6160"
    travel_transport = "6170"
    utilities = "6180"
    miscellaneous = "6190"


@dataclass(frozen=True, slots=True)
class GLAccount:
    code: GlAccountCode
    name: str
    description: str


NORTHSTAR_GL_ACCOUNTS: tuple[GLAccount, ...] = (
    GLAccount(
        GlAccountCode.cleaning,
        "Cleaning services",
        "Janitorial, contract cleaning, waste disposal",
    ),
    GLAccount(
        GlAccountCode.building_maintenance,
        "Building maintenance",
        "General repairs, handyman work, routine upkeep",
    ),
    GLAccount(
        GlAccountCode.electrical,
        "Electrical services",
        "Electrician work, lighting, electrical repairs",
    ),
    GLAccount(
        GlAccountCode.plumbing_hvac,
        "Plumbing and HVAC",
        "Plumbing, heating, ventilation, air conditioning",
    ),
    GLAccount(
        GlAccountCode.equipment,
        "Equipment and tools",
        "Tool rental, small equipment, safety gear",
    ),
    GLAccount(
        GlAccountCode.office_supplies,
        "Office supplies",
        "Stationery, printer supplies, consumables",
    ),
    GLAccount(
        GlAccountCode.professional_fees,
        "Professional fees",
        "Legal, accounting, consulting",
    ),
    GLAccount(
        GlAccountCode.travel_transport,
        "Travel and transport",
        "Fuel, parking, mileage, public transport",
    ),
    GLAccount(
        GlAccountCode.utilities,
        "Utilities",
        "Electricity, water, gas",
    ),
    GLAccount(
        GlAccountCode.miscellaneous,
        "Miscellaneous operating expenses",
        "Everything the accounts above do not cover",
    ),
)

_BY_CODE = {account.code.value: account for account in NORTHSTAR_GL_ACCOUNTS}


def list_gl_accounts() -> list[GLAccount]:
    return list(NORTHSTAR_GL_ACCOUNTS)


def get_gl_account(code: str) -> GLAccount | None:
    return _BY_CODE.get(code.strip())


def gl_account_codes() -> tuple[str, ...]:
    return tuple(_BY_CODE.keys())


def catalog_prompt_lines() -> str:
    return "\n".join(
        f"- {account.code.value}: {account.name} — {account.description}"
        for account in NORTHSTAR_GL_ACCOUNTS
    )
