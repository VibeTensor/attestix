// ---------------------------------------------------------------------------
// Billing seam: DOCUMENTED, NOT WIRED.
// ---------------------------------------------------------------------------
//
// Self-serve checkout is intentionally NOT live yet. Two things are missing:
//   1. Payment-provider keys (STRIPE_PUBLISHABLE_KEY / RAZORPAY_KEY_ID), which
//      the founder has not provisioned.
//   2. The cloud billing backend (M4, `attestix-cloud/apps/api`) that mints a
//      checkout session against a plan + region. It is not built.
//
// Until BOTH exist, every "buy" intent routes to a waitlist (the /demo-call
// page) where we onboard customers directly. There is deliberately NO dead
// Stripe button and NO fake checkout. The honest "billing launching soon,
// we onboard you directly" state is the correct one for this stage.
//
// WHEN BILLING IS LIVE (M4):
//   - Set STRIPE_PUBLISHABLE_KEY (int'l cards) and RAZORPAY_KEY_ID (INR/UPI,
//     for Indian customers, per issue #13) as NEXT_PUBLIC_* env vars.
//   - Replace the `waitlist` branch below with a real call to the billing API:
//       POST {BILLING_API}/v1/checkout/session  { plan, region, provider }
//     then redirect to the returned provider checkout URL. Choose the provider
//     by region: Razorpay for `in` (INR/UPI), Stripe for everything else.
//   - Add `@stripe/stripe-js` + the Razorpay checkout script ONLY at that point.
//     They are intentionally NOT dependencies today (no keys, no backend) to
//     avoid dead weight and supply-chain surface until the integration is real.
// ---------------------------------------------------------------------------

export type BillingPlan = "free" | "pro" | "enterprise";
export type BillingRegion = "in" | "intl";

export interface CheckoutResult {
	/** Whether a real provider checkout was started. Always false today. */
	started: false;
	/** Why no checkout ran. */
	reason: "billing_not_enabled";
	/** Where the caller should send the user instead (the waitlist). */
	redirect: string;
	/** Which provider WOULD have been used once billing is wired. */
	intendedProvider: "stripe" | "razorpay";
}

/**
 * Returns true once both the payment keys and the M4 billing API are present.
 * Today this is always false: the env vars are unset and the backend is unbuilt.
 */
export function isBillingEnabled(): boolean {
	const stripe = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY;
	const razorpay = process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID;
	const api = process.env.NEXT_PUBLIC_BILLING_API_URL;
	return Boolean((stripe || razorpay) && api);
}

/**
 * Pick the payment provider for a region. Razorpay handles INR/UPI for Indian
 * customers (issue #13); Stripe handles international cards. This decision is
 * already correct; only the checkout-session call behind it is stubbed.
 */
export function providerForRegion(region: BillingRegion): "stripe" | "razorpay" {
	return region === "in" ? "razorpay" : "stripe";
}

/**
 * Stubbed checkout entry point.
 *
 * Today it NEVER starts a real checkout: it returns a sentinel telling the
 * caller to route the user to the waitlist (`/demo-call?plan=<plan>`). When the
 * M4 billing API and provider keys land, replace the body's waitlist branch
 * with the real `POST /v1/checkout/session` call (see file header).
 */
export function startCheckout(
	plan: Exclude<BillingPlan, "free">,
	region: BillingRegion = "intl",
): CheckoutResult {
	// SEAM: when isBillingEnabled() is true, call the billing API here and
	// return the provider checkout URL instead of the waitlist redirect.
	return {
		started: false,
		reason: "billing_not_enabled",
		redirect: `/demo-call?plan=${plan}`,
		intendedProvider: providerForRegion(region),
	};
}

/** Indicative INR conversion for display only, NOT a billed rate. */
export const USD_TO_INR_INDICATIVE = 84; // ~2026-05; review before billing goes live.

/** Pro price, single source of truth for the page copy. */
export const PRO_PRICE_USD = 99;
export const PRO_PRICE_INR_INDICATIVE = PRO_PRICE_USD * USD_TO_INR_INDICATIVE; // ≈ 8,316
