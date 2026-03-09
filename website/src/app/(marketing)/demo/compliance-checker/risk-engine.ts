export type RiskLevel = "unacceptable" | "high" | "limited" | "minimal";

export interface RiskAssessment {
  level: RiskLevel;
  title: string;
  description: string;
  articles: string[];
  obligations: string[];
  timeline: string;
  fineRange: string;
  color: string;
  bgColor: string;
  borderColor: string;
  iconColor: string;
}

const RISK_METADATA: Record<RiskLevel, Omit<RiskAssessment, "articles" | "obligations">> = {
  unacceptable: {
    level: "unacceptable",
    title: "Unacceptable Risk",
    description:
      "Your AI system falls into a category that is prohibited under the EU AI Act. These systems pose a clear threat to safety, livelihoods, or fundamental rights.",
    timeline:
      "Prohibited systems must cease operation by February 2, 2025. If your system is still active, you are already past the deadline and face immediate enforcement action.",
    fineRange: "Up to 35 million EUR or 7% of global annual turnover, whichever is higher",
    color: "text-red-400",
    bgColor: "bg-red-500/10",
    borderColor: "border-red-500/30",
    iconColor: "text-red-500",
  },
  high: {
    level: "high",
    title: "High Risk",
    description:
      "Your AI system is classified as high risk under the EU AI Act. It must meet strict requirements before being placed on the EU market or put into service.",
    timeline:
      "High-risk AI systems must comply by August 2, 2026. You should begin conformity assessment, documentation, and risk management now to meet the deadline.",
    fineRange: "Up to 15 million EUR or 3% of global annual turnover, whichever is higher",
    color: "text-orange-400",
    bgColor: "bg-orange-500/10",
    borderColor: "border-orange-500/30",
    iconColor: "text-orange-500",
  },
  limited: {
    level: "limited",
    title: "Limited Risk",
    description:
      "Your AI system has limited risk and is subject to transparency obligations. Users must be informed that they are interacting with AI.",
    timeline:
      "Transparency obligations apply from August 2, 2026. Implement disclosure mechanisms and content labeling ahead of the deadline.",
    fineRange: "Up to 7.5 million EUR or 1.5% of global annual turnover, whichever is higher",
    color: "text-yellow-400",
    bgColor: "bg-yellow-500/10",
    borderColor: "border-yellow-500/30",
    iconColor: "text-yellow-500",
  },
  minimal: {
    level: "minimal",
    title: "Minimal Risk",
    description:
      "Your AI system is classified as minimal risk. No mandatory compliance obligations apply, though voluntary codes of practice are encouraged.",
    timeline:
      "No mandatory deadline, but voluntary codes of practice are available from August 2, 2025. Adopting them demonstrates responsible AI development.",
    fineRange: "No mandatory fines, but general product safety laws still apply",
    color: "text-emerald-400",
    bgColor: "bg-emerald-500/10",
    borderColor: "border-emerald-500/30",
    iconColor: "text-emerald-500",
  },
};

type SystemType =
  | "chatbot"
  | "content-generation"
  | "decision-support"
  | "biometric"
  | "medical"
  | "autonomous"
  | "education"
  | "other";

export function assessRiskLevel(
  systemType: SystemType,
  deploymentContext: Set<string>,
  otherDescription: string
): RiskAssessment {
  const level = determineRiskLevel(systemType, deploymentContext, otherDescription);
  const metadata = RISK_METADATA[level];
  const articles = getApplicableArticles(level, systemType, deploymentContext);
  const obligations = getObligations(level, systemType, deploymentContext);

  return {
    ...metadata,
    articles,
    obligations,
  };
}

function determineRiskLevel(
  systemType: SystemType,
  context: Set<string>,
  otherDescription: string
): RiskLevel {
  // Check for unacceptable risk patterns
  if (isUnacceptableRisk(systemType, context, otherDescription)) {
    return "unacceptable";
  }

  // Check for high risk patterns
  if (isHighRisk(systemType, context)) {
    return "high";
  }

  // Check for limited risk patterns
  if (isLimitedRisk(systemType, context)) {
    return "limited";
  }

  return "minimal";
}

function isUnacceptableRisk(
  systemType: SystemType,
  context: Set<string>,
  otherDescription: string
): boolean {
  // Biometric surveillance in public spaces
  if (systemType === "biometric" && context.has("interacts-with-users")) {
    return true;
  }

  // Social scoring patterns (check "other" description for keywords)
  const lowerDesc = otherDescription.toLowerCase();
  const socialScoringTerms = [
    "social scoring",
    "social credit",
    "citizen scoring",
    "behavioral scoring",
    "trustworthiness scoring",
  ];
  if (socialScoringTerms.some((term) => lowerDesc.includes(term))) {
    return true;
  }

  // Manipulative AI targeting vulnerable groups
  const manipulativeTerms = [
    "subliminal",
    "manipulat",
    "exploit vulnerab",
    "target children",
    "dark pattern",
  ];
  if (manipulativeTerms.some((term) => lowerDesc.includes(term))) {
    return true;
  }

  return false;
}

function isHighRisk(systemType: SystemType, context: Set<string>): boolean {
  // Decision support systems affecting individuals in regulated sectors
  if (systemType === "decision-support") {
    if (
      context.has("affects-individuals") ||
      context.has("regulated-sector")
    ) {
      return true;
    }
  }

  // Medical and healthcare AI
  if (systemType === "medical") {
    return true;
  }

  // Autonomous vehicles and robotics (critical infrastructure)
  if (systemType === "autonomous") {
    return true;
  }

  // Education AI that assesses or makes decisions about students
  if (systemType === "education" && context.has("affects-individuals")) {
    return true;
  }

  // Biometric systems that are not real-time public (those would be unacceptable)
  if (
    systemType === "biometric" &&
    context.has("processes-personal-data") &&
    !context.has("interacts-with-users")
  ) {
    return true;
  }

  // Any system in a regulated sector that processes personal data and affects individuals
  if (
    context.has("regulated-sector") &&
    context.has("processes-personal-data") &&
    context.has("affects-individuals")
  ) {
    return true;
  }

  return false;
}

function isLimitedRisk(systemType: SystemType, context: Set<string>): boolean {
  // Chatbots that interact with users
  if (systemType === "chatbot" && context.has("interacts-with-users")) {
    return true;
  }

  // Content generation systems
  if (systemType === "content-generation") {
    return true;
  }

  // Any system that generates content that could be mistaken for human-made
  if (context.has("generates-content")) {
    return true;
  }

  // Education AI without individual impact
  if (systemType === "education" && !context.has("affects-individuals")) {
    return true;
  }

  // Systems deployed in EU that interact with users
  if (context.has("eu-deployment") && context.has("interacts-with-users")) {
    return true;
  }

  return false;
}

function getApplicableArticles(
  level: RiskLevel,
  systemType: SystemType,
  context: Set<string>
): string[] {
  const articles: string[] = [];

  switch (level) {
    case "unacceptable":
      articles.push("Article 5 - Prohibited AI Practices");
      if (systemType === "biometric") {
        articles.push("Article 5(1)(d) - Real-time biometric identification in public spaces");
      }
      articles.push("Article 99 - Penalties for prohibited practices");
      break;

    case "high":
      articles.push("Article 6 - Classification rules for high-risk AI");
      articles.push("Article 9 - Risk management system");
      articles.push("Article 10 - Data and data governance");
      articles.push("Article 11 - Technical documentation");
      articles.push("Article 13 - Transparency and information to deployers");
      articles.push("Article 14 - Human oversight");
      articles.push("Article 15 - Accuracy, robustness, and cybersecurity");
      if (systemType === "medical") {
        articles.push("Annex III, Section 5(a) - Medical devices and in vitro diagnostics");
      }
      if (systemType === "decision-support" && context.has("regulated-sector")) {
        articles.push("Annex III, Section 5(b) - Creditworthiness and credit scoring");
      }
      if (systemType === "education") {
        articles.push("Annex III, Section 3 - Education and vocational training");
      }
      if (systemType === "autonomous") {
        articles.push("Annex III, Section 2 - Critical infrastructure management");
      }
      articles.push("Annex V - EU Declaration of Conformity");
      break;

    case "limited":
      articles.push("Article 50 - Transparency obligations for certain AI systems");
      if (
        systemType === "chatbot" ||
        (systemType === "other" && context.has("interacts-with-users"))
      ) {
        articles.push("Article 50(1) - Disclosure of AI interaction");
      }
      if (systemType === "content-generation" || context.has("generates-content")) {
        articles.push("Article 50(2) - Labeling of AI-generated content");
      }
      break;

    case "minimal":
      articles.push("Article 95 - Voluntary codes of conduct");
      if (context.has("eu-deployment")) {
        articles.push("Article 69 - Codes of practice (general-purpose AI)");
      }
      break;
  }

  return articles;
}

function getObligations(
  level: RiskLevel,
  systemType: SystemType,
  context: Set<string>
): string[] {
  const obligations: string[] = [];

  switch (level) {
    case "unacceptable":
      obligations.push(
        "Immediately cease operation of the prohibited AI system"
      );
      obligations.push(
        "Remove the system from any EU market or deployment context"
      );
      obligations.push(
        "Consult legal counsel regarding potential penalties and remediation"
      );
      obligations.push(
        "Document the decommissioning process for regulatory authorities"
      );
      break;

    case "high":
      obligations.push(
        "Establish and maintain a risk management system throughout the AI system lifecycle"
      );
      obligations.push(
        "Implement data governance practices with training, validation, and testing datasets"
      );
      obligations.push(
        "Create and maintain comprehensive technical documentation (Annex IV)"
      );
      obligations.push(
        "Design the system to allow effective human oversight during operation"
      );
      obligations.push(
        "Ensure appropriate levels of accuracy, robustness, and cybersecurity"
      );
      obligations.push(
        "Implement automatic logging capabilities for traceability"
      );
      obligations.push(
        "Complete conformity assessment before placing the system on the market"
      );
      if (context.has("eu-deployment")) {
        obligations.push(
          "Register the system in the EU database for high-risk AI systems"
        );
      }
      if (systemType === "medical") {
        obligations.push(
          "Coordinate with medical device regulations (MDR/IVDR) for dual compliance"
        );
      }
      break;

    case "limited":
      obligations.push(
        "Clearly inform users that they are interacting with an AI system"
      );
      if (systemType === "content-generation" || context.has("generates-content")) {
        obligations.push(
          "Label AI-generated content in a machine-readable format"
        );
        obligations.push(
          "Ensure AI-generated text, images, audio, or video are identifiable as synthetic"
        );
      }
      if (context.has("processes-personal-data")) {
        obligations.push(
          "Comply with GDPR requirements for personal data processing alongside transparency rules"
        );
      }
      obligations.push(
        "Maintain documentation of transparency measures implemented"
      );
      break;

    case "minimal":
      obligations.push(
        "No mandatory obligations, but adopting voluntary codes of practice is recommended"
      );
      obligations.push(
        "Consider implementing transparency measures as a best practice"
      );
      if (context.has("eu-deployment")) {
        obligations.push(
          "Monitor regulatory developments as your system may be reclassified"
        );
      }
      if (context.has("processes-personal-data")) {
        obligations.push(
          "Ensure GDPR compliance for any personal data processing"
        );
      }
      break;
  }

  return obligations;
}
