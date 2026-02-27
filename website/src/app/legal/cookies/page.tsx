import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Cookie Policy",
  description: "Cookie Policy for Attestix by VibeTensor Private Limited.",
};

export default function CookiePolicy() {
  return (
    <>
      <h1>Cookie Policy</h1>
      <p className="text-muted-foreground">
        Last updated: February 27, 2026
      </p>

      <h2>1. What Are Cookies</h2>
      <p>
        Cookies are small text files stored on your device when you visit a
        website. They help the website remember your preferences and improve
        your experience.
      </p>

      <h2>2. Cookies We Use</h2>
      <p>
        Attestix uses a minimal set of cookies, limited to strictly necessary
        functionality:
      </p>
      <table>
        <thead>
          <tr>
            <th>Cookie Name</th>
            <th>Purpose</th>
            <th>Type</th>
            <th>Duration</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>
              <code>theme</code>
            </td>
            <td>Stores your light/dark mode preference</td>
            <td>Strictly necessary</td>
            <td>1 year</td>
          </tr>
        </tbody>
      </table>

      <h2>3. Cookies We Do NOT Use</h2>
      <ul>
        <li>
          <strong>Analytics cookies:</strong> We do not use Google Analytics,
          Mixpanel, or similar tracking tools
        </li>
        <li>
          <strong>Marketing/advertising cookies:</strong> We do not serve ads or
          track users for advertising purposes
        </li>
        <li>
          <strong>Third-party tracking cookies:</strong> We do not embed social
          media widgets or third-party scripts that set cookies
        </li>
      </ul>

      <h2>4. Cloudflare</h2>
      <p>
        Our website is served through Cloudflare, which may set a{" "}
        <code>__cf_bm</code> cookie for bot protection. This is a strictly
        necessary security cookie that expires within 30 minutes.
      </p>

      <h2>5. Managing Cookies</h2>
      <p>
        You can control cookies through your browser settings. Most browsers
        allow you to:
      </p>
      <ul>
        <li>View what cookies are stored</li>
        <li>Delete individual or all cookies</li>
        <li>Block cookies from specific sites or all sites</li>
        <li>Block third-party cookies</li>
      </ul>
      <p>
        Note that disabling cookies may affect the functionality of the theme
        toggle on our website.
      </p>

      <h2>6. Changes to This Policy</h2>
      <p>
        If we introduce any new cookies (for example, analytics), we will update
        this page and implement a consent mechanism before they are set.
      </p>

      <h2>7. Contact</h2>
      <p>
        For questions about our cookie practices, contact us at
        info@vibetensor.com.
      </p>
    </>
  );
}
