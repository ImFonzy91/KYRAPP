"""Real Legal Rights Data from US Constitution and Federal Law"""

# These are REAL constitutional rights and federal laws - not AI generated
# Sources: US Constitution, Cornell Law Institute, Court Listener

CONSTITUTIONAL_RIGHTS = {
    "4th_amendment": {
        "title": "4th Amendment - Search & Seizure",
        "text": "The right of the people to be secure in their persons, houses, papers, and effects, against unreasonable searches and seizures, shall not be violated, and no Warrants shall issue, but upon probable cause, supported by Oath or affirmation, and particularly describing the place to be searched, and the persons or things to be seized.",
        "source": "U.S. Constitution, Amendment IV",
        "what_it_means": [
            "Police cannot search you without a warrant (with exceptions)",
            "Police cannot search your home without a warrant",
            "Police cannot search your car without probable cause or consent",
            "You have the right to refuse consent to searches",
            "Evidence obtained illegally may be thrown out in court"
        ],
        "keywords": ["search", "police", "warrant", "car", "home", "property", "seizure", "pulled over"]
    },
    "5th_amendment": {
        "title": "5th Amendment - Right to Remain Silent",
        "text": "No person shall be held to answer for a capital, or otherwise infamous crime, unless on a presentment or indictment of a Grand Jury... nor shall be compelled in any criminal case to be a witness against himself, nor be deprived of life, liberty, or property, without due process of law.",
        "source": "U.S. Constitution, Amendment V",
        "what_it_means": [
            "You have the right to remain silent",
            "You cannot be forced to testify against yourself",
            "You cannot be tried twice for the same crime (double jeopardy)",
            "You have the right to due process before losing liberty or property",
            "Say: 'I invoke my Fifth Amendment right to remain silent'"
        ],
        "keywords": ["silent", "remain silent", "testify", "interrogation", "questioning", "arrested", "police"]
    },
    "6th_amendment": {
        "title": "6th Amendment - Right to Attorney",
        "text": "In all criminal prosecutions, the accused shall enjoy the right to a speedy and public trial, by an impartial jury... to be informed of the nature and cause of the accusation; to be confronted with the witnesses against him... and to have the Assistance of Counsel for his defence.",
        "source": "U.S. Constitution, Amendment VI",
        "what_it_means": [
            "You have the right to an attorney",
            "If you can't afford one, one will be provided (public defender)",
            "You have the right to a speedy trial",
            "You have the right to know the charges against you",
            "You have the right to confront witnesses",
            "Say: 'I want a lawyer' - police must stop questioning"
        ],
        "keywords": ["lawyer", "attorney", "trial", "court", "arrested", "charges", "public defender"]
    },
    "1st_amendment": {
        "title": "1st Amendment - Freedom of Speech & Recording",
        "text": "Congress shall make no law respecting an establishment of religion, or prohibiting the free exercise thereof; or abridging the freedom of speech, or of the press; or the right of the people peaceably to assemble, and to petition the Government for a redress of grievances.",
        "source": "U.S. Constitution, Amendment I",
        "what_it_means": [
            "You can record police in public (established by federal courts)",
            "You have freedom of speech (with some limits)",
            "You can peacefully protest",
            "Police cannot delete your recordings",
            "You can criticize the government"
        ],
        "keywords": ["record", "recording", "video", "speech", "protest", "filming", "camera"]
    },
    "14th_amendment": {
        "title": "14th Amendment - Equal Protection",
        "text": "No State shall make or enforce any law which shall abridge the privileges or immunities of citizens of the United States; nor shall any State deprive any person of life, liberty, or property, without due process of law; nor deny to any person within its jurisdiction the equal protection of the laws.",
        "source": "U.S. Constitution, Amendment XIV",
        "what_it_means": [
            "All people must be treated equally under the law",
            "Police cannot discriminate based on race, religion, etc.",
            "States must follow due process",
            "Immigrants have rights under this amendment too",
            "Basis for many civil rights protections"
        ],
        "keywords": ["discrimination", "equal", "race", "civil rights", "immigrant", "protection"]
    }
}

MIRANDA_RIGHTS = {
    "title": "Miranda Rights (Miranda v. Arizona, 1966)",
    "source": "Supreme Court Case: Miranda v. Arizona, 384 U.S. 436 (1966)",
    "text": "You have the right to remain silent. Anything you say can and will be used against you in a court of law. You have the right to an attorney. If you cannot afford an attorney, one will be provided for you.",
    "when_required": "Police must read Miranda rights BEFORE custodial interrogation (when you're not free to leave AND being questioned)",
    "what_to_do": [
        "Say clearly: 'I invoke my right to remain silent'",
        "Say clearly: 'I want a lawyer'",
        "Stop talking immediately after invoking rights",
        "Do not answer 'just a few questions'",
        "Do not sign anything without a lawyer"
    ],
    "keywords": ["miranda", "arrested", "rights", "silent", "lawyer", "questioning"]
}

TRAFFIC_STOP_RIGHTS = {
    "title": "Your Rights During Traffic Stops",
    "source": "4th, 5th, and 6th Amendments + State Laws",
    "legal_requirements": {
        "must_provide": [
            "Driver's license (if driving)",
            "Vehicle registration (if driving)",
            "Proof of insurance (if driving)"
        ],
        "not_required": [
            "Answer questions beyond identification",
            "Consent to vehicle search",
            "Perform field sobriety tests (varies by state - but license consequences)",
            "Exit vehicle (unless officer has safety concern)"
        ]
    },
    "magic_phrases": [
        "I do not consent to any searches.",
        "I am exercising my right to remain silent.",
        "Am I being detained or am I free to go?",
        "I want to speak to a lawyer."
    ],
    "keywords": ["traffic", "pulled over", "stop", "police", "car", "search", "dui", "checkpoint"]
}

TENANT_RIGHTS = {
    "title": "Tenant Rights (Federal & Common State Laws)",
    "source": "Fair Housing Act, State Landlord-Tenant Laws",
    "federal_protections": {
        "fair_housing_act": {
            "law": "Fair Housing Act (42 U.S.C. 3601-3619)",
            "protects_against": [
                "Discrimination based on race, color, national origin",
                "Discrimination based on religion",
                "Discrimination based on sex",
                "Discrimination based on familial status",
                "Discrimination based on disability"
            ]
        }
    },
    "common_tenant_rights": [
        "Right to habitable premises (heat, water, structural safety)",
        "Right to proper notice before eviction (varies 3-60 days by state)",
        "Right to security deposit return with itemized deductions",
        "Right to privacy - landlord must give notice before entering (24-48 hours typical)",
        "Protection from retaliation for complaints",
        "Right to withhold rent for serious habitability issues (varies by state)"
    ],
    "illegal_landlord_actions": [
        "Changing locks without court order",
        "Shutting off utilities to force you out",
        "Removing your belongings without court order",
        "Entering without proper notice (except emergencies)",
        "Retaliating for exercising legal rights"
    ],
    "keywords": ["tenant", "landlord", "rent", "eviction", "lease", "deposit", "housing"]
}

EMPLOYMENT_RIGHTS = {
    "title": "Employment & Workplace Rights",
    "source": "FLSA, OSHA, Title VII, ADA, FMLA",
    "federal_laws": {
        "flsa": {
            "name": "Fair Labor Standards Act (FLSA)",
            "rights": [
                "Federal minimum wage ($7.25/hr, states may be higher)",
                "Overtime pay (1.5x for hours over 40/week)",
                "Child labor protections",
                "Right to file wage complaints without retaliation"
            ]
        },
        "title_vii": {
            "name": "Title VII of Civil Rights Act",
            "protects_against": [
                "Discrimination based on race",
                "Discrimination based on color",
                "Discrimination based on religion",
                "Discrimination based on sex",
                "Discrimination based on national origin",
                "Sexual harassment"
            ]
        },
        "ada": {
            "name": "Americans with Disabilities Act (ADA)",
            "rights": [
                "Protection from disability discrimination",
                "Right to reasonable accommodations",
                "Applies to employers with 15+ employees"
            ]
        },
        "osha": {
            "name": "Occupational Safety and Health Act",
            "rights": [
                "Right to safe workplace",
                "Right to report safety hazards",
                "Protection from retaliation for safety complaints",
                "Right to request OSHA inspection"
            ]
        },
        "fmla": {
            "name": "Family and Medical Leave Act",
            "rights": [
                "Up to 12 weeks unpaid leave for medical/family reasons",
                "Job protection during leave",
                "Applies to employers with 50+ employees"
            ]
        }
    },
    "keywords": ["work", "job", "fired", "boss", "overtime", "wage", "harassment", "discrimination", "workplace"]
}

CRIMINAL_DEFENSE_RIGHTS = {
    "title": "Criminal Defense Rights",
    "source": "4th, 5th, 6th, 8th Amendments",
    "core_rights": [
        {
            "right": "Presumption of Innocence",
            "meaning": "You are innocent until proven guilty beyond reasonable doubt"
        },
        {
            "right": "Right to Remain Silent",
            "meaning": "5th Amendment - you cannot be forced to testify against yourself"
        },
        {
            "right": "Right to Attorney",
            "meaning": "6th Amendment - you have right to lawyer, free if you can't afford"
        },
        {
            "right": "Right Against Unreasonable Search",
            "meaning": "4th Amendment - police need warrant or exception to search"
        },
        {
            "right": "Right to Speedy Trial",
            "meaning": "6th Amendment - cannot be held indefinitely without trial"
        },
        {
            "right": "Right to Confront Witnesses",
            "meaning": "6th Amendment - you can cross-examine witnesses against you"
        },
        {
            "right": "Protection from Excessive Bail",
            "meaning": "8th Amendment - bail cannot be unreasonably high"
        },
        {
            "right": "Protection from Double Jeopardy",
            "meaning": "5th Amendment - cannot be tried twice for same crime"
        }
    ],
    "what_to_say_when_arrested": [
        "I am exercising my right to remain silent.",
        "I want a lawyer.",
        "I do not consent to any searches."
    ],
    "then_stop_talking": "After saying these phrases, STOP TALKING. Do not explain, do not justify, do not answer 'just a few questions.' Wait for your lawyer.",
    "keywords": ["arrest", "criminal", "jail", "police", "charges", "court", "bail", "trial"]
}

IMMIGRATION_RIGHTS = {
    "title": "Immigration Rights",
    "source": "U.S. Constitution applies to all persons, not just citizens",
    "all_persons_have": [
        "4th Amendment protection against unreasonable search",
        "5th Amendment right to remain silent",
        "6th Amendment right to attorney in criminal cases",
        "14th Amendment equal protection",
        "Right to refuse to answer questions about immigration status",
        "Right to not sign documents you don't understand"
    ],
    "ice_encounters": {
        "at_home": [
            "Do not open door unless they show judicial warrant signed by judge",
            "Administrative warrants (Form I-200) do NOT allow entry",
            "You can speak through closed door",
            "Say: 'I do not consent to your entry'"
        ],
        "in_public": [
            "You have right to remain silent",
            "You do not have to show immigration documents",
            "Do not run or resist",
            "Say: 'I am exercising my right to remain silent'"
        ]
    },
    "keywords": ["immigration", "ice", "deportation", "visa", "immigrant", "undocumented", "border"]
}

CONSUMER_RIGHTS = {
    "title": "Consumer Protection Rights",
    "source": "FDCPA, FCRA, FTC Act",
    "debt_collection": {
        "law": "Fair Debt Collection Practices Act (FDCPA)",
        "protections": [
            "Collectors cannot call before 8am or after 9pm",
            "Collectors cannot harass or threaten you",
            "You can demand they stop calling (in writing)",
            "You can request debt validation in writing",
            "Collectors cannot discuss debt with others",
            "You can sue for violations ($1,000 + damages)"
        ],
        "magic_letter": "Send cease and desist letter via certified mail to stop calls"
    },
    "credit_reporting": {
        "law": "Fair Credit Reporting Act (FCRA)",
        "rights": [
            "Free credit report annually from each bureau",
            "Right to dispute inaccurate information",
            "Bureaus must investigate disputes within 30 days",
            "Right to know who accessed your credit report"
        ]
    },
    "keywords": ["debt", "collector", "credit", "consumer", "bill", "collection", "harassment"]
}

# Combine all rights for search
ALL_RIGHTS_DATA = {
    "constitutional": CONSTITUTIONAL_RIGHTS,
    "miranda": MIRANDA_RIGHTS,
    "traffic": TRAFFIC_STOP_RIGHTS,
    "tenant": TENANT_RIGHTS,
    "employment": EMPLOYMENT_RIGHTS,
    "criminal": CRIMINAL_DEFENSE_RIGHTS,
    "immigration": IMMIGRATION_RIGHTS,
    "consumer": CONSUMER_RIGHTS
}

def search_rights(query: str) -> list:
    """Search all rights data for matching content"""
    query_lower = query.lower()
    results = []
    
    # Search constitutional rights
    for key, right in CONSTITUTIONAL_RIGHTS.items():
        if any(kw in query_lower for kw in right.get("keywords", [])):
            results.append({
                "type": "constitutional",
                "id": key,
                "title": right["title"],
                "source": right["source"],
                "text": right["text"],
                "what_it_means": right["what_it_means"]
            })
    
    # Search Miranda
    if any(kw in query_lower for kw in MIRANDA_RIGHTS.get("keywords", [])):
        results.append({
            "type": "miranda",
            "id": "miranda_rights",
            "title": MIRANDA_RIGHTS["title"],
            "source": MIRANDA_RIGHTS["source"],
            "text": MIRANDA_RIGHTS["text"],
            "what_to_do": MIRANDA_RIGHTS["what_to_do"]
        })
    
    # Search traffic rights
    if any(kw in query_lower for kw in TRAFFIC_STOP_RIGHTS.get("keywords", [])):
        results.append({
            "type": "traffic",
            "id": "traffic_stop_rights",
            "title": TRAFFIC_STOP_RIGHTS["title"],
            "source": TRAFFIC_STOP_RIGHTS["source"],
            "legal_requirements": TRAFFIC_STOP_RIGHTS["legal_requirements"],
            "magic_phrases": TRAFFIC_STOP_RIGHTS["magic_phrases"]
        })
    
    # Search tenant rights
    if any(kw in query_lower for kw in TENANT_RIGHTS.get("keywords", [])):
        results.append({
            "type": "tenant",
            "id": "tenant_rights",
            "title": TENANT_RIGHTS["title"],
            "source": TENANT_RIGHTS["source"],
            "common_rights": TENANT_RIGHTS["common_tenant_rights"],
            "illegal_landlord_actions": TENANT_RIGHTS["illegal_landlord_actions"]
        })
    
    # Search employment rights
    if any(kw in query_lower for kw in EMPLOYMENT_RIGHTS.get("keywords", [])):
        results.append({
            "type": "employment",
            "id": "employment_rights",
            "title": EMPLOYMENT_RIGHTS["title"],
            "source": EMPLOYMENT_RIGHTS["source"],
            "federal_laws": EMPLOYMENT_RIGHTS["federal_laws"]
        })
    
    # Search criminal rights
    if any(kw in query_lower for kw in CRIMINAL_DEFENSE_RIGHTS.get("keywords", [])):
        results.append({
            "type": "criminal",
            "id": "criminal_defense_rights",
            "title": CRIMINAL_DEFENSE_RIGHTS["title"],
            "source": CRIMINAL_DEFENSE_RIGHTS["source"],
            "core_rights": CRIMINAL_DEFENSE_RIGHTS["core_rights"],
            "what_to_say": CRIMINAL_DEFENSE_RIGHTS["what_to_say_when_arrested"]
        })
    
    # Search immigration rights
    if any(kw in query_lower for kw in IMMIGRATION_RIGHTS.get("keywords", [])):
        results.append({
            "type": "immigration",
            "id": "immigration_rights",
            "title": IMMIGRATION_RIGHTS["title"],
            "source": IMMIGRATION_RIGHTS["source"],
            "all_persons_have": IMMIGRATION_RIGHTS["all_persons_have"],
            "ice_encounters": IMMIGRATION_RIGHTS["ice_encounters"]
        })
    
    # Search consumer rights
    if any(kw in query_lower for kw in CONSUMER_RIGHTS.get("keywords", [])):
        results.append({
            "type": "consumer",
            "id": "consumer_rights",
            "title": CONSUMER_RIGHTS["title"],
            "source": CONSUMER_RIGHTS["source"],
            "debt_collection": CONSUMER_RIGHTS["debt_collection"],
            "credit_reporting": CONSUMER_RIGHTS["credit_reporting"]
        })
    
    return results
