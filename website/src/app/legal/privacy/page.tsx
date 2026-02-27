import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy Policy",
  description: "Privacy Policy for Attestix by VibeTensor Private Limited.",
};

export default function PrivacyPolicy() {
  return (
    <>
      <h1>Privacy Policy</h1>
      <p className="text-muted-foreground">
        Last updated: February 27, 2026
      </p>

      <h2>1. Introduction</h2>
      <p>
        VibeTensor Private Limited (&quot;VibeTensor&quot;, &quot;we&quot;,
        &quot;us&quot;, or &quot;our&quot;) operates the Attestix website
        (attestix.vibetensor.com) and the Attestix open-source software. This
        Privacy Policy explains how we collect, use, disclose, and safeguard
        your information when you visit our website or use our services.
      </p>
      <p>
        This policy is drafted in compliance with the Information Technology
        Act, 2000 and the IT (Reasonable Security Practices and Procedures and
        Sensitive Personal Data or Information) Rules, 2011, the Digital
        Personal Data Protection Act, 2023 (DPDP Act), and the General Data
        Protection Regulation (GDPR) for users in the European Economic Area.
      </p>

      <h2>2. Data Controller</h2>
      <p>
        VibeTensor Private Limited is the data controller responsible for your
        personal data.
      </p>
      <ul>
        <li>
          <strong>Contact:</strong> info@vibetensor.com
        </li>
        <li>
          <strong>Grievance Officer:</strong> Pavan Kumar Dubasi,
          info@vibetensor.com
        </li>
      </ul>

      <h2>3. Information We Collect</h2>
      <h3>3.1 Information you provide</h3>
      <ul>
        <li>
          Contact information (name, email) when you contact us via email or
          forms
        </li>
        <li>Enterprise inquiry details submitted through our contact form</li>
      </ul>
      <h3>3.2 Information collected automatically</h3>
      <ul>
        <li>
          Standard server logs (IP address, browser type, operating system,
          referring URL, pages visited, date/time of access)
        </li>
        <li>
          Cloudflare analytics data (anonymized, no cookies required)
        </li>
      </ul>
      <h3>3.3 Information we do NOT collect</h3>
      <ul>
        <li>
          The Attestix software runs locally on your machine. We do not collect,
          transmit, or store any data processed by the Attestix MCP tools
        </li>
        <li>
          We do not collect Sensitive Personal Data or Information (SPDI) as
          defined under IT Rules 2011
        </li>
      </ul>

      <h2>4. Lawful Basis for Processing (GDPR)</h2>
      <ul>
        <li>
          <strong>Legitimate interest:</strong> Website analytics to improve user
          experience
        </li>
        <li>
          <strong>Consent:</strong> When you voluntarily submit your contact
          information
        </li>
        <li>
          <strong>Contractual necessity:</strong> Processing enterprise support
          inquiries
        </li>
      </ul>

      <h2>5. How We Use Your Information</h2>
      <ul>
        <li>To respond to your inquiries and support requests</li>
        <li>To improve our website and documentation</li>
        <li>To comply with legal obligations</li>
      </ul>

      <h2>6. Data Sharing and Transfers</h2>
      <p>
        We do not sell your personal data. We may share data with:
      </p>
      <ul>
        <li>
          <strong>Cloudflare:</strong> For website hosting, CDN, and DDoS
          protection (data processed in multiple jurisdictions under Cloudflare
          DPA)
        </li>
        <li>
          <strong>GitHub:</strong> For open-source project collaboration
          (governed by GitHub Privacy Statement)
        </li>
      </ul>
      <p>
        For transfers to countries outside India or the EEA, we rely on Standard
        Contractual Clauses (SCCs) or equivalent safeguards.
      </p>

      <h2>7. Data Retention</h2>
      <p>
        We retain personal data only as long as necessary for the purposes
        described above. Contact inquiries are retained for up to 2 years.
        Server logs are retained for up to 30 days.
      </p>

      <h2>8. Your Rights</h2>
      <h3>Under GDPR (EEA residents)</h3>
      <ul>
        <li>Right of access</li>
        <li>Right to rectification</li>
        <li>Right to erasure</li>
        <li>Right to restrict processing</li>
        <li>Right to data portability</li>
        <li>Right to object</li>
      </ul>
      <h3>Under DPDP Act (Indian residents)</h3>
      <ul>
        <li>Right to access information about personal data</li>
        <li>Right to correction and erasure</li>
        <li>Right to grievance redressal</li>
        <li>Right to nominate</li>
      </ul>
      <p>
        To exercise any of these rights, contact us at info@vibetensor.com. We
        will respond within 30 days.
      </p>

      <h2>9. Cookies</h2>
      <p>
        Our website uses only strictly necessary cookies for basic
        functionality (such as theme preference). We do not use analytics
        cookies, tracking cookies, or third-party advertising cookies. See our{" "}
        <a href="/legal/cookies">Cookie Policy</a> for details.
      </p>

      <h2>10. Children&#39;s Privacy</h2>
      <p>
        Our services are not directed at individuals under 18. We do not
        knowingly collect personal data from children. If you believe we have
        collected data from a minor, contact us immediately.
      </p>

      <h2>11. Security</h2>
      <p>
        We implement reasonable security practices and procedures to protect
        your data, including HTTPS encryption, security headers, and access
        controls, consistent with Rule 8 of the IT Rules 2011.
      </p>

      <h2>12. Grievance Redressal</h2>
      <p>
        If you have any concerns about our data practices, please contact our
        Grievance Officer:
      </p>
      <ul>
        <li>
          <strong>Name:</strong> Pavan Kumar Dubasi
        </li>
        <li>
          <strong>Email:</strong> info@vibetensor.com
        </li>
      </ul>
      <p>
        We will acknowledge your complaint within 48 hours and resolve it within
        30 days.
      </p>

      <h2>13. Changes to This Policy</h2>
      <p>
        We may update this Privacy Policy from time to time. Changes will be
        posted on this page with an updated &quot;Last updated&quot; date.
      </p>
    </>
  );
}
