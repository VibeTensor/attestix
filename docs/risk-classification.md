# EU AI Act Risk Classification Guide

How to determine the risk category for your AI system under the EU AI Act (Regulation 2024/1689).

## Quick Decision Tree

```
Is your AI system used for any PROHIBITED purpose?
  --> YES --> UNACCEPTABLE RISK (banned, cannot deploy)
  --> NO  --> Continue

Is your AI system listed in Annex III?
  --> YES --> HIGH RISK (heavy compliance requirements)
  --> NO  --> Continue

Does your AI system interact directly with people,
generate synthetic content, or perform emotion recognition?
  --> YES --> LIMITED RISK (transparency obligations)
  --> NO  --> MINIMAL RISK (no specific obligations)
```

## Unacceptable Risk (PROHIBITED - Article 5)

These AI systems are banned entirely. Attestix will block creation of compliance profiles for these:

- Social scoring by governments or on their behalf
- Manipulation through subliminal, deceptive, or exploitative techniques
- Exploitation of vulnerabilities (age, disability, social/economic situation)
- Untargeted scraping of facial images from internet or CCTV
- Emotion inference in workplace or education (with limited exceptions)
- Biometric categorization using sensitive characteristics (race, political opinions, etc.)
- Individual predictive policing based solely on profiling
- Real-time remote biometric identification in public spaces for law enforcement (with limited exceptions)

## High Risk (Annex III Categories)

If your AI system falls under any of these categories, it is high-risk:

| Category | Examples |
|----------|---------|
| **1. Biometrics** | Facial recognition, fingerprint matching, voice identification, remote biometric ID |
| **2. Critical infrastructure** | Safety components in electricity, gas, water, transport, digital infrastructure management |
| **3. Education & training** | Student assessment, exam scoring, admission decisions, learning path determination |
| **4. Employment** | CV screening, interview assessment, recruitment ranking, termination decisions, performance monitoring |
| **5. Essential services** | Credit scoring, insurance pricing, social benefit eligibility, emergency dispatch prioritization |
| **6. Law enforcement** | Evidence reliability assessment, recidivism prediction, profiling during investigation, lie detection |
| **7. Migration & border** | Visa application assessment, border crossing risk assessment, irregular migration detection |
| **8. Justice & democracy** | Judicial decision support, legal research interpretation, election/referendum outcome influence |

### High-Risk Requirements

High-risk AI systems must comply with Articles 8-15:

- Risk management system (Article 9)
- Data governance and management (Article 10)
- Technical documentation (Article 11)
- Record keeping and automatic logging (Article 12)
- Transparency and user information (Article 13)
- Human oversight capability (Article 14)
- Accuracy, robustness, and cybersecurity (Article 15)
- Conformity assessment before deployment (Article 43)
- Registration in EU database (Article 49)
- Post-market monitoring (Article 72)

### Conformity Assessment for High-Risk

Most Annex III high-risk systems can use **internal control** (self-assessment under Annex VI). However, **biometric systems** (Category 1) require **third-party assessment** by a notified body under Annex VII.

Attestix currently requires third-party assessment for all high-risk systems (more conservative than the Act requires). This will be refined in a future release.

## Limited Risk (Article 50 Transparency)

These systems must meet transparency obligations:

| System Type | Required Disclosure |
|-------------|-------------------|
| AI chatbots | Must inform users they are interacting with AI |
| Emotion recognition | Must inform subjects their emotions are being inferred |
| Biometric categorization | Must inform subjects they are being categorized |
| Deepfake generators | Must label AI-generated content as artificial |
| AI-generated text (published to inform on public interest matters) | Must label as AI-generated |

## Minimal Risk

AI systems that do not fall into any of the above categories:

- Spam filters
- AI in video games
- Inventory management systems
- AI-powered search (internal)
- Code completion tools
- Content recommendation (non-manipulative)

No specific regulatory obligations, though voluntary codes of conduct are encouraged.

## Common Examples

| AI System | Risk Category | Why |
|-----------|--------------|-----|
| Medical diagnosis AI | High | Category 1 (biometrics) or essential services (healthcare) |
| Credit scoring model | High | Category 5 (essential services) |
| Resume screening tool | High | Category 4 (employment) |
| Customer service chatbot | Limited | Interacts with people |
| AI-generated marketing images | Limited | Synthetic content generation |
| Code completion tool (Copilot) | Minimal | Not in Annex III |
| Email spam filter | Minimal | Not in Annex III |
| AI-powered recommendation engine | Minimal | Unless manipulative |
| Facial recognition access control | High | Category 1 (biometrics) |
| Autonomous vehicle perception | High | Category 2 (critical infrastructure) |
| Student grading AI | High | Category 3 (education) |
| AI lie detector | High (or Unacceptable) | Category 6 (law enforcement) |

## Choosing Your Risk Category in Attestix

When creating a compliance profile, use one of these values:

```
create_compliance_profile(
  agent_id="attestix:...",
  risk_category="high",     # "minimal", "limited", or "high"
  provider_name="...",
  ...
)
```

If you are unsure about your risk category, consult with a legal professional specializing in EU AI regulation. Incorrect classification can result in non-compliance.

## Further Reading

- [EU AI Act Full Text](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689)
- [EU AI Act Annex III (High-Risk Categories)](https://artificialintelligenceact.eu/annex/iii/)
- [EU AI Act Article 6 (Classification Rules)](https://artificialintelligenceact.eu/article/6/)
- [EU AI Act Implementation Timeline](https://artificialintelligenceact.eu/implementation-timeline/)
