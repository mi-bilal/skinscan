from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

Severity = Literal["low", "moderate", "high"]


@dataclass(frozen=True)
class DiseaseInfo:
    description: str
    severity: Severity
    recommendation: str
    common_age: str
    contagious: bool
    symptoms: list[str]


DISEASE_INFO: dict[str, DiseaseInfo] = {
    "Acne": DiseaseInfo(
        description=(
            "Acne is a common skin condition where hair follicles become plugged with "
            "oil and dead skin cells, causing pimples, blackheads, and whiteheads. "
            "It primarily affects areas with the most oil glands such as the face, chest, and back."
        ),
        severity="low",
        recommendation="Use over-the-counter benzoyl peroxide or salicylic acid treatments. See a dermatologist if severe or scarring occurs.",
        common_age="Teenagers and young adults (12–30)",
        contagious=False,
        symptoms=["Pimples", "Blackheads", "Whiteheads", "Oily skin", "Scarring"],
    ),
    "Chickenpox": DiseaseInfo(
        description=(
            "Chickenpox is a highly contagious viral infection caused by the varicella-zoster virus, "
            "producing an itchy, blister-like rash that spreads across the body. "
            "It is most common in children but can affect adults with more severe symptoms."
        ),
        severity="moderate",
        recommendation="Rest, stay hydrated, and use antihistamines for itching. Consult a doctor immediately — antiviral medication may be needed for adults.",
        common_age="Children under 12",
        contagious=True,
        symptoms=["Itchy blisters", "Fever", "Fatigue", "Headache", "Red spots"],
    ),
    "Eczema": DiseaseInfo(
        description=(
            "Eczema (atopic dermatitis) is a chronic inflammatory skin condition that causes dry, "
            "itchy, and inflamed skin. It often flares periodically and may occur alongside "
            "asthma or hay fever, indicating an overactive immune response."
        ),
        severity="moderate",
        recommendation="Moisturize frequently, identify and avoid triggers. See a dermatologist for prescription treatments if OTC options are insufficient.",
        common_age="Infants, children, and adults of all ages",
        contagious=False,
        symptoms=["Dry skin", "Intense itching", "Red rash", "Cracked skin", "Swelling"],
    ),
    "Monkeypox": DiseaseInfo(
        description=(
            "Monkeypox is a viral zoonotic disease caused by monkeypox virus, presenting with "
            "a distinctive rash that progresses from macules to pustules. "
            "It spreads through close physical contact and is related to but less severe than smallpox."
        ),
        severity="high",
        recommendation="Seek medical attention immediately. Isolate from others and notify public health authorities. Antiviral treatment may be prescribed.",
        common_age="All ages",
        contagious=True,
        symptoms=["Rash with pustules", "Fever", "Swollen lymph nodes", "Muscle aches", "Exhaustion"],
    ),
    "Psoriasis": DiseaseInfo(
        description=(
            "Psoriasis is a chronic autoimmune condition that causes the rapid buildup of skin cells, "
            "resulting in scaling on the skin's surface. Scales are typically white-silver and develop "
            "in thick red patches that may crack and bleed."
        ),
        severity="moderate",
        recommendation="See a dermatologist for a management plan. Topical treatments, phototherapy, or biologics may be recommended depending on severity.",
        common_age="Adults 15–35 and 50–60",
        contagious=False,
        symptoms=["Red scaly patches", "Silvery scales", "Dry cracked skin", "Itching", "Thickened nails"],
    ),
    "Ringworm": DiseaseInfo(
        description=(
            "Ringworm (tinea corporis) is a fungal skin infection — not actually caused by a worm — "
            "that produces a ring-shaped, scaly rash. It spreads through direct contact with infected "
            "people, animals, or contaminated surfaces."
        ),
        severity="low",
        recommendation="Apply over-the-counter antifungal cream for 2–4 weeks. See a doctor if it spreads or doesn't improve, as prescription medication may be needed.",
        common_age="All ages, especially children",
        contagious=True,
        symptoms=["Ring-shaped rash", "Itching", "Scaling", "Red borders", "Hair loss on scalp"],
    ),
    "Basal Cell Carcinoma": DiseaseInfo(
        description=(
            "Basal cell carcinoma (BCC) is the most common form of skin cancer, arising from basal "
            "cells in the deepest layer of the epidermis. It rarely spreads but can cause significant "
            "local tissue damage if left untreated, often appearing as a pearly bump or flesh-colored patch."
        ),
        severity="high",
        recommendation="See a dermatologist or oncologist urgently. Early-stage BCC is highly treatable through surgical removal, Mohs surgery, or radiation therapy.",
        common_age="Adults over 50, but increasingly younger people",
        contagious=False,
        symptoms=["Pearly bump", "Flat flesh-colored lesion", "Bleeding sore", "Scar-like patch", "Pink growth"],
    ),
    "Melanoma": DiseaseInfo(
        description=(
            "Melanoma is the most dangerous form of skin cancer, developing in the melanocytes that "
            "produce pigment. It can spread rapidly to other organs if not caught early and is often "
            "triggered by UV radiation exposure."
        ),
        severity="high",
        recommendation="Seek urgent medical attention. Early detection is critical — survival rates drop significantly with delayed diagnosis. Do not wait.",
        common_age="Adults 20–60, risk increases with age",
        contagious=False,
        symptoms=["Asymmetric mole", "Irregular border", "Multiple colors", "Diameter >6mm", "Evolving lesion"],
    ),
    "Tinea Versicolor": DiseaseInfo(
        description=(
            "Tinea versicolor is a common fungal infection caused by Malassezia yeast that disrupts "
            "normal skin pigmentation, creating discolored patches that may be lighter or darker than "
            "surrounding skin. It typically worsens in warm, humid conditions."
        ),
        severity="low",
        recommendation="Use antifungal shampoo or cream as directed. The condition is not harmful, but recurrence is common — maintenance treatment may be needed.",
        common_age="Teenagers and young adults",
        contagious=False,
        symptoms=["Discolored patches", "Mild itching", "Scaling", "Fading tan", "Pale or pink spots"],
    ),
    "Vitiligo": DiseaseInfo(
        description=(
            "Vitiligo is a long-term autoimmune condition in which patches of skin lose their pigment "
            "due to the destruction of melanocytes. The condition can affect any part of the body and "
            "may spread over time, though it is not physically harmful."
        ),
        severity="low",
        recommendation="Consult a dermatologist to discuss options. Treatments include topical corticosteroids, phototherapy, and depigmentation of remaining skin.",
        common_age="Often begins before age 30",
        contagious=False,
        symptoms=["White patches", "Premature greying", "Hair depigmentation", "Eye discoloration"],
    ),
    "Warts": DiseaseInfo(
        description=(
            "Warts are small, rough skin growths caused by human papillomavirus (HPV) infection. "
            "They are contagious through direct contact and most commonly appear on hands and feet. "
            "Many resolve on their own, though treatment can speed resolution."
        ),
        severity="low",
        recommendation="Over-the-counter salicylic acid treatments are effective for most warts. Cryotherapy or minor surgery is available for persistent cases.",
        common_age="Children and young adults",
        contagious=True,
        symptoms=["Rough bumps", "Clotted blood vessels (black dots)", "Flat lesions", "Clustered growth"],
    ),
}

SEVERITY_COLOR: dict[Severity, str] = {
    "low": "#10b981",
    "moderate": "#f59e0b",
    "high": "#ef4444",
}

SEVERITY_BG: dict[Severity, str] = {
    "low": "rgba(16, 185, 129, 0.12)",
    "moderate": "rgba(245, 158, 11, 0.12)",
    "high": "rgba(239, 68, 68, 0.12)",
}


def get_info(class_name: str) -> DiseaseInfo | None:
    return DISEASE_INFO.get(class_name)


def severity_color(sev: Severity) -> str:
    return SEVERITY_COLOR.get(sev, "#64748b")


def severity_bg(sev: Severity) -> str:
    return SEVERITY_BG.get(sev, "rgba(100, 116, 139, 0.12)")
