import { AtxEyebrow } from "@/components/atx/atx-eyebrow";
import { constructMetadata } from "@/lib/utils";
import Link from "next/link";

export const metadata = constructMetadata({
  title: "Bundle wire format v1",
  description:
    "Specification of the Attestix portability bundle wire format — the on-disk shape every export and import speaks. Identified by https://attestix.io/spec/bundle/v1.",
});

// The manifest field "attestix_bundle_format" carries this exact URI in every
// bundle. The route lives under the marketing layout group so the URL the
// manifest dereferences to (without /docs) resolves to this page.
const SPEC_URI = "https://attestix.io/spec/bundle/v1";
const PUBLISHED_DATE = "2026-05-28";

// Manifest fields. Pulled verbatim from
// attestix/portability/bundle_writer.py and the cloud worker at
// attestix-cloud/apps/workers/ts/src/exports.ts. Keep the two in lock-step.
const MANIFEST_FIELDS = [
  {
    field: "manifest_version",
    type: "string",
    required: true,
    meaning:
      "The version of this spec the manifest conforms to. v1 manifests carry the literal string \"1.0\". Verifiers MUST refuse any other value.",
    example: '"1.0"',
  },
  {
    field: "attestix_bundle_format",
    type: "string (URI)",
    required: true,
    meaning:
      "The dereferenceable identifier for this wire format. v1 carries the literal value https://attestix.io/spec/bundle/v1. Verifiers MUST refuse any other value.",
    example: '"https://attestix.io/spec/bundle/v1"',
  },
  {
    field: "workspace.id",
    type: "string (UUID for cloud, slug for OSS)",
    required: true,
    meaning:
      "The producer's internal workspace identifier. Cloud producers emit a Postgres UUID; the OSS exporter emits the tenant slug (the same value as workspace.slug).",
    example: '"11111111-1111-4111-8111-111111111111"',
  },
  {
    field: "workspace.slug",
    type: "string",
    required: true,
    meaning:
      "Human-readable workspace identifier. MUST match the tenant_id every audit_events row was chained against — verifiers re-derive the chain_hash using this value and will fail the bundle if it disagrees.",
    example: '"fixture-tenant"',
  },
  {
    field: "workspace.region",
    type: "string",
    required: true,
    meaning:
      "Cloud region the bundle was produced in (e.g. eu-west-1, us-east-1). OSS producers MUST emit the literal string \"local\".",
    example: '"eu-west-1"',
  },
  {
    field: "workspace.data_residency",
    type: "string",
    required: true,
    meaning:
      "Residency commitment for the producer (eu, uk, us, in, ap, self-host). Informational; not verified.",
    example: '"eu"',
  },
  {
    field: "exported_at",
    type: "string (ISO-8601 UTC)",
    required: true,
    meaning:
      "Wall-clock timestamp the bundle was assembled. RFC-3339 with millisecond precision and the trailing Z.",
    example: '"2026-05-28T12:00:00.000Z"',
  },
  {
    field: "exported_by.user_id",
    type: "string | null",
    required: true,
    meaning:
      "Identifier of the user who triggered the export. OSS producers emit the literal string \"local\"; cloud producers emit the requester's user UUID or null for automated jobs.",
    example: '"22222222-2222-4222-8222-222222222222"',
  },
  {
    field: "exported_by.email",
    type: "string | null",
    required: true,
    meaning:
      "Email of the requester. OSS producers emit \"self-host@local\"; cloud producers emit the requester's email or null.",
    example: '"operator@fixture.attestix.io"',
  },
  {
    field: "tables[]",
    type: "array of objects",
    required: true,
    meaning:
      "One entry per table in the bundle. Each entry is {name, format, row_count, bytes, sha256}. Order MUST match the on-disk member order so a reader can stream-verify the tarball without seeking.",
    example: 'see Section 5',
  },
  {
    field: "core_version",
    type: "string",
    required: true,
    meaning:
      "Producer build pin in the form attestix==<semver>. The OSS exporter stamps its installed package version; the cloud worker stamps the CORE_VERSION_PIN constant.",
    example: '"attestix==0.4.0"',
  },
  {
    field: "schemas.db_migration_max",
    type: "string (zero-padded migration number)",
    required: true,
    meaning:
      "Highest cloud database migration the producer knows about. Consumers compare against their own SUPPORTED_DB_MIGRATION_MAX and refuse strictly newer bundles with BundleSchemaTooNewError.",
    example: '"0010"',
  },
  {
    field: "notes[]",
    type: "array of strings",
    required: false,
    meaning:
      "Free-form producer notes. v1 producers append \"format=jsonl\" and may append \"exporter=oss\" (OSS) or a Parquet-best-effort note (cloud).",
    example: '["format=jsonl", "exporter=oss"]',
  },
];

// One row per in-scope table. Order mirrors EXPORT_PLAN in
// attestix/portability/bundle_writer.py and EXPORT_TABLE_SPECS in the cloud
// worker exports.ts.
const TABLES = [
  {
    name: "identities",
    purpose:
      "Agent identity rows — DID, did_document, signing key reference (public material only), status, revocation metadata.",
    cloudOnly: false,
    notes: "Maps to the OSS identities collection. Each row carries the agent's full DID document for offline re-resolution.",
  },
  {
    name: "key_references",
    purpose: "Cloud-side KMS key handles. Not a v1 OSS concept — emitted empty by OSS producers.",
    cloudOnly: true,
    notes: "Empty JSONL on OSS. Cloud bundles may carry KMS ARNs / Vault key references — never the private key bytes.",
  },
  {
    name: "credentials",
    purpose:
      "W3C Verifiable Credential envelopes with proof intact. Each row is {id, workspace_id, credential} where credential is the full VC body.",
    cloudOnly: false,
    notes: "Round-trippable: a verifier can re-validate the Ed25519Signature2020 proof against the issuer DID in the same bundle.",
  },
  {
    name: "credential_schemas",
    purpose: "Custom credential schema registry (cloud-only).",
    cloudOnly: true,
    notes: "Empty JSONL on OSS.",
  },
  {
    name: "memberships",
    purpose: "Cloud workspace membership rows.",
    cloudOnly: true,
    notes: "Empty JSONL on OSS (single-tenant).",
  },
  {
    name: "team_invites",
    purpose: "Cloud team-invite rows.",
    cloudOnly: true,
    notes: "Empty JSONL on OSS.",
  },
  {
    name: "subscriptions",
    purpose: "Cloud billing-subscription rows.",
    cloudOnly: true,
    notes: "Empty JSONL on OSS.",
  },
  {
    name: "compliance_profiles",
    purpose:
      "EU AI Act compliance profiles — Article 43 risk classification, provider metadata, transparency obligations, required-obligation list.",
    cloudOnly: false,
    notes: "Maps to the OSS compliance.profiles list. One profile per agent_id.",
  },
  {
    name: "conformity_assessments",
    purpose:
      "Annex IV / Annex V conformity assessment records — assessor, result, findings, CE marking eligibility.",
    cloudOnly: false,
    notes: "Maps to the OSS compliance.assessments list. References its compliance_profile by agent_id.",
  },
  {
    name: "agent_dependencies",
    purpose: "Cloud agent dependency graph.",
    cloudOnly: true,
    notes: "Empty JSONL on OSS.",
  },
  {
    name: "audit_events",
    purpose:
      "Hash-chained audit event log (the Article 12 evidence body). Each row carries event_id, actor, action, target_id, target_collection, occurred_at, change_digest, prev_hash, and chain_hash.",
    cloudOnly: false,
    notes:
      "Order MUST be (created_at asc, id asc). Verifiers MUST re-run verify_chain end-to-end and abort on any break — see the verifier algorithm in Section 6.",
  },
  {
    name: "anchors",
    purpose:
      "Base L2 Sepolia anchor records — tx_hash, attestation_uid (EAS), schema_uid, attester address, block_number, gas_used, anchored_at, issuer_did, and the artifact_hash (Merkle root).",
    cloudOnly: false,
    notes: "Anchored on Base Sepolia testnet (chain_id 84532). Mainnet schema not yet registered.",
  },
  {
    name: "webhook_endpoints",
    purpose: "Cloud webhook subscription rows.",
    cloudOnly: true,
    notes: "Empty JSONL on OSS. Webhook deliveries are intentionally out of scope (dispatcher state, not customer data).",
  },
];

// Sample manifest extracted verbatim from
// tests/fixtures/bundles/sample-v1.tar.gz produced by
// tests/fixtures/bundles/generate_sample_bundle.py. The bytes below are
// canonical JCS — alphabetical keys, no whitespace, NFC-normalised strings.
const EXAMPLE_MANIFEST = `{"attestix_bundle_format":"https://attestix.io/spec/bundle/v1","core_version":"attestix==0.4.0rc2","exported_at":"2026-05-28T12:00:00.000Z","exported_by":{"email":"operator@fixture.attestix.io","user_id":"22222222-2222-4222-8222-222222222222"},"manifest_version":"1.0","notes":["format=jsonl","fixture=oss-roundtrip"],"schemas":{"db_migration_max":"0010"},"tables":[{"bytes":2004,"format":"jsonl","name":"identities","row_count":2,"sha256":"8e0fba149ead951d8412a8634cb7d29fa7f9c2749929d7dee0d83e561e7d992f"},{"bytes":0,"format":"jsonl","name":"key_references","row_count":0,"sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"},{"bytes":586,"format":"jsonl","name":"credentials","row_count":1,"sha256":"450e860134d4a00fdcbc66d76469fcbbea82181ae6f7740db042fb7d863d8575"},{"bytes":0,"format":"jsonl","name":"credential_schemas","row_count":0,"sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"},{"bytes":0,"format":"jsonl","name":"memberships","row_count":0,"sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"},{"bytes":0,"format":"jsonl","name":"team_invites","row_count":0,"sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"},{"bytes":0,"format":"jsonl","name":"subscriptions","row_count":0,"sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"},{"bytes":651,"format":"jsonl","name":"compliance_profiles","row_count":1,"sha256":"b58f382b75d0804e695fbe7e4708cf09326ca1f73498ca6504ec53fe7a8ae0fd"},{"bytes":383,"format":"jsonl","name":"conformity_assessments","row_count":1,"sha256":"e98f58b40249c985f05b8fb2203c8129b03184201b1059e3766b0d8d6bc9455e"},{"bytes":0,"format":"jsonl","name":"agent_dependencies","row_count":0,"sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"},{"bytes":1999,"format":"jsonl","name":"audit_events","row_count":3,"sha256":"e3a185627ed4cd67781cd64011f3ca20d6d942751a1f0665c37d1823b498b316"},{"bytes":798,"format":"jsonl","name":"anchors","row_count":1,"sha256":"58d9dc30f6151c89a2cb8f0ef85b16cb8e4d6521faa33d884447a522f7adc034"},{"bytes":0,"format":"jsonl","name":"webhook_endpoints","row_count":0,"sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}],"workspace":{"data_residency":"eu","id":"11111111-1111-4111-8111-111111111111","region":"eu-west-1","slug":"fixture-tenant"}}`;

const EXAMPLE_MANIFEST_SHA = "b52c2baa896c82991f0c86afb6b771f4ab192d25dc153b463eb125183cf737c9";

const EXAMPLE_CREDENTIAL_ROW = `{"credential":{"credentialStatus":{"id":"urn:uuid:cred-fixture-0001#status","revocation_reason":null,"revoked":false,"revoked_at":null,"type":"RevocationList2021Status"},"credentialSubject":{"id":"attestix:fixture0000000001","role":"Fixture Subject"},"expirationDate":"2027-05-01T10:00:00Z","id":"urn:uuid:cred-fixture-0001","issuanceDate":"2026-05-01T10:00:00Z","issuer":{"id":"did:key:fixture-issuer","name":"Fixture Issuer"},"type":["VerifiableCredential","AgentIdentityCredential"]},"id":"cccccccc-cccc-4ccc-8ccc-cccccccccc01","workspace_id":"11111111-1111-4111-8111-111111111111"}`;

const EXAMPLE_AUDIT_FIRST_ROW = `{"action":"identity.create","actor":"user:operator@fixture.attestix.io","anchor_id":null,"chain_hash":"5d1034b220c98c5a839df512fef2dff46e34e86df7dfb2d288a96528c0dfac88","change_digest":"d36b020fbbdb0baacea68cd168bcad261b3d283b8eb69554f3d31eb193947fd2","created_at":"2026-05-01T10:00:01Z","event_id":"evt:fixture000000","id":"99999999-9999-4999-8999-999999999900","occurred_at":"2026-05-01T10:00:00+00:00","occurred_at_month":"2026-05-01","prev_hash":"0000000000000000000000000000000000000000000000000000000000000000","retention_days":7,"target_collection":"identities","target_id":"attestix:fixture0000000001","workspace_id":"11111111-1111-4111-8111-111111111111"}`;

const VERIFIER_ALGORITHM = `1. Open bundle.tar.gz; extract every member to memory (bundle cap: 256 MiB; per-member cap: 128 MiB).
2. Read manifest.json; parse as JSON object.
3. JCS-canonicalise the parsed manifest dict (sort_keys + tightest separators + ensure_ascii=False).
4. Compute SHA-256 of the canonical bytes; read manifest.sha256 side-car; refuse on mismatch.
5. For each entry in manifest.tables[]:
     read <entry.name>.jsonl from the bundle
     compute SHA-256 over the raw bytes (no normalisation — the writer
       already wrote JCS-canonical lines, so re-canonicalising would drift)
     compare to entry.sha256; refuse on mismatch
     count newline-terminated lines; compare to entry.row_count; refuse on mismatch
6. For audit_events specifically: walk the rows in stored order, verify
     row[i].prev_hash == row[i-1].chain_hash and recompute row[i].chain_hash
     from the JCS-canonical body; refuse on any chain break.
7. Compare manifest.schemas.db_migration_max to the verifier's
     SUPPORTED_DB_MIGRATION_MAX; raise BundleSchemaTooNewError if strictly newer.
8. If every check passes: bundle integrity verified.`;

export default function BundleSpecV1Page() {
  return (
    <section className="mx-auto max-w-[1080px] px-7 py-24">
      <AtxEyebrow>Specification</AtxEyebrow>
      <h1 className="mt-3 font-serif text-[clamp(36px,4.8vw,60px)] leading-[1.05] tracking-[-0.012em] text-atx-ink">
        Bundle wire format
        <br />
        <em className="italic text-atx-accent">v1.</em>
      </h1>
      <p className="mt-6 max-w-[760px] text-[15px] leading-[1.65] text-atx-ink-mid">
        The on-disk shape every Attestix portability bundle speaks. Tamper-evident,
        deterministic, JCS-canonical, and identical byte-for-byte across the OSS
        Python exporter and the cloud TypeScript worker. Published{" "}
        <span className="font-mono-atx text-[13px] text-atx-ink">{PUBLISHED_DATE}</span>.
        v1 is frozen.
      </p>

      {/* ----- Section 1: Identifier --------------------------------------- */}
      <h2 className="mt-16 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        01 / Identifier
      </h2>
      <p className="mt-3 max-w-[760px] text-[14px] leading-[1.7] text-atx-ink-mid">
        The canonical URI for this version of the spec is:
      </p>
      <pre className="mt-4 overflow-x-auto rounded-atx-md border border-atx-line-soft bg-atx-bg-sunken px-5 py-4 font-mono-atx text-[13px] text-atx-accent">
        {SPEC_URI}
      </pre>
      <p className="mt-4 max-w-[760px] text-[14px] leading-[1.7] text-atx-ink-mid">
        Every bundle produced by Attestix — Python core ≥ v0.4.0 via
        the <code className="font-mono-atx text-[12.5px] text-atx-ink">attestix.portability.bundle_writer</code>{" "}
        module, the TypeScript cloud worker, and both the{" "}
        <code className="font-mono-atx text-[12.5px] text-atx-ink">attestix export</code> and{" "}
        <code className="font-mono-atx text-[12.5px] text-atx-ink">attestix import</code>{" "}
        CLIs — emits this exact string as the{" "}
        <code className="font-mono-atx text-[12.5px] text-atx-ink">attestix_bundle_format</code>{" "}
        field in <code className="font-mono-atx text-[12.5px] text-atx-ink">manifest.json</code>.
        The URI is dereferenceable to this page so a verifier holding only the
        bundle on disk can find the spec.
      </p>

      {/* ----- Section 2: Wire format at a glance -------------------------- */}
      <h2 className="mt-16 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        02 / Wire format at a glance
      </h2>
      <div className="mt-6 overflow-hidden rounded-atx-md border border-atx-line-soft">
        <table className="w-full border-collapse text-left text-[13px]">
          <thead className="bg-atx-bg-sunken">
            <tr>
              <th className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
                Property
              </th>
              <th className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint">
                Value
              </th>
            </tr>
          </thead>
          <tbody>
            {[
              {
                k: "Container",
                v: "USTAR + gzip (.tar.gz). zstd planned for v2.",
              },
              {
                k: "Per-table file",
                v: "One JSONL per table; one row per line; trailing newline; empty tables write zero bytes.",
              },
              {
                k: "Canonicalization",
                v: 'JCS-style: json.dumps(sort_keys=True, separators=(",",":"), ensure_ascii=False) followed by Unicode NFC. NOT strict RFC 8785 — documented in the Python attestix.auth.crypto.canonicalize_json and the equivalent canonicalizeJson in the npm attestix package (today @vibetensor/attestix until the unscoped publish completes).',
              },
              {
                k: "Member order",
                v: "Alphabetical across every member of the tarball. Required for byte-stable re-exports.",
              },
              {
                k: "Tar timestamps",
                v: "info.mtime = 0; info.uid = info.gid = 0; info.uname = info.gname = \"\". Deterministic across runs.",
              },
              {
                k: "Gzip header",
                v: "mtime = 0. Deterministic across runs.",
              },
              {
                k: "Encoding",
                v: "UTF-8 throughout. No BOM. Manifest carries no whitespace between tokens.",
              },
              {
                k: "Size caps",
                v: "Bundle: 256 MiB. Single member: 128 MiB. Verifiers MUST refuse anything larger.",
              },
            ].map((row) => (
              <tr key={row.k} className="bg-atx-panel">
                <td className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[11.5px] text-atx-ink">
                  {row.k}
                </td>
                <td className="border-b border-atx-line-soft px-4 py-3 text-atx-ink-mid">
                  {row.v}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* ----- Section 3: Manifest schema ---------------------------------- */}
      <h2 className="mt-16 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        03 / Manifest schema
      </h2>
      <p className="mt-3 max-w-[760px] text-[14px] leading-[1.7] text-atx-ink-mid">
        Every bundle carries one{" "}
        <code className="font-mono-atx text-[12.5px] text-atx-ink">manifest.json</code>{" "}
        whose body is the JCS-canonical serialisation of the following object.
        Field order is irrelevant on the wire (the canonicaliser sorts keys);
        the table below lists fields in semantic order.
      </p>

      <pre className="mt-6 overflow-x-auto rounded-atx-md border border-atx-line-soft bg-atx-bg-sunken px-5 py-4 font-mono-atx text-[12px] leading-[1.55] text-atx-ink">
{`{
  "manifest_version": "1.0",
  "attestix_bundle_format": "${SPEC_URI}",
  "workspace": {
    "id": "<UUID or slug>",
    "slug": "<tenant slug>",
    "region": "<aws-style region or 'local'>",
    "data_residency": "<eu|uk|us|in|ap|self-host>"
  },
  "exported_at": "<RFC-3339 UTC, ms precision>",
  "exported_by": {
    "user_id": "<UUID|'local'|null>",
    "email": "<email|'self-host@local'|null>"
  },
  "tables": [
    { "name": "<table>", "format": "jsonl",
      "row_count": <int>, "bytes": <int>, "sha256": "<hex>" }
  ],
  "core_version": "attestix==<semver>",
  "schemas": { "db_migration_max": "<zero-padded migration number>" },
  "notes": [ "<free-form producer note>" ]
}`}
      </pre>

      <div className="mt-6 overflow-hidden rounded-atx-md border border-atx-line-soft">
        <table className="w-full border-collapse text-left text-[13px]">
          <thead className="bg-atx-bg-sunken">
            <tr>
              {["Field", "Type", "Req", "Meaning", "Example"].map((h) => (
                <th
                  key={h}
                  className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {MANIFEST_FIELDS.map((f) => (
              <tr key={f.field} className="bg-atx-panel align-top">
                <td className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[11.5px] text-atx-accent">
                  {f.field}
                </td>
                <td className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[11px] text-atx-ink-dim">
                  {f.type}
                </td>
                <td className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[11px]">
                  <span className={f.required ? "text-atx-ok" : "text-atx-ink-dim"}>
                    {f.required ? "yes" : "no"}
                  </span>
                </td>
                <td className="border-b border-atx-line-soft px-4 py-3 text-atx-ink-mid">
                  {f.meaning}
                </td>
                <td className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[11px] text-atx-ink">
                  {f.example}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* ----- Section 4: manifest.sha256 side-car ------------------------- */}
      <h2 className="mt-16 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        04 / Side-car: manifest.sha256
      </h2>
      <p className="mt-3 max-w-[760px] text-[14px] leading-[1.7] text-atx-ink-mid">
        A plain-text file inside the tarball alongside{" "}
        <code className="font-mono-atx text-[12.5px] text-atx-ink">manifest.json</code>.
        It contains the lowercase hex SHA-256 of the JCS-canonical manifest body
        followed by a single trailing newline (65 bytes total). Critical for
        verifier round-trips: the consumer can recompute the hash and compare
        without first parsing the manifest, and producers can transport the
        digest separately without round-tripping the full body.
      </p>
      <p className="mt-3 max-w-[760px] text-[14px] leading-[1.7] text-atx-ink-mid">
        The sha is computed over the manifest{" "}
        <em className="italic text-atx-ink">as it was written</em> — the
        manifest&apos;s own{" "}
        <code className="font-mono-atx text-[12.5px] text-atx-ink">sha256</code>{" "}
        appears only inside per-table entries; there is no self-reference at the
        manifest root, so no field needs to be stripped before re-canonicalising.
      </p>
      <pre className="mt-4 overflow-x-auto rounded-atx-md border border-atx-line-soft bg-atx-bg-sunken px-5 py-4 font-mono-atx text-[12px] text-atx-ink">
{`# Producer side
canonical = canonicalize_json(manifest)            # JCS bytes
sha = sha256(canonical).hexdigest()                # 64 hex chars
write_member("manifest.json", canonical)
write_member("manifest.sha256", sha + "\\n")

# Verifier side
canonical = canonicalize_json(json.loads(manifest_bytes))
assert sha256(canonical).hexdigest() == sidecar.strip()`}
      </pre>

      {/* ----- Section 5: per-table tables --------------------------------- */}
      <h2 className="mt-16 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        05 / Per-table tables
      </h2>
      <p className="mt-3 max-w-[760px] text-[14px] leading-[1.7] text-atx-ink-mid">
        Thirteen tables. Order in the manifest{" "}
        <code className="font-mono-atx text-[12.5px] text-atx-ink">tables[]</code>{" "}
        array and on-disk MUST match the order below — cloud and OSS producers
        agree on this byte-for-byte. Cloud-only tables are emitted as empty
        JSONL members by OSS producers so the bundle&apos;s member set stays
        symmetric across producers.
      </p>

      <div className="mt-6 overflow-hidden rounded-atx-md border border-atx-line-soft">
        <table className="w-full border-collapse text-left text-[13px]">
          <thead className="bg-atx-bg-sunken">
            <tr>
              {["#", "Table", "Purpose", "Notes"].map((h) => (
                <th
                  key={h}
                  className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {TABLES.map((t, i) => (
              <tr key={t.name} className="bg-atx-panel align-top">
                <td className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[11px] text-atx-ink-dim">
                  {String(i + 1).padStart(2, "0")}
                </td>
                <td className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[11.5px]">
                  <span className="text-atx-accent">{t.name}</span>
                  {t.cloudOnly ? (
                    <span className="ml-2 rounded-atx-xs border border-atx-line-soft px-1.5 py-0.5 text-[9.5px] uppercase tracking-[0.12em] text-atx-ink-dim">
                      cloud-only
                    </span>
                  ) : null}
                </td>
                <td className="border-b border-atx-line-soft px-4 py-3 text-atx-ink-mid">
                  {t.purpose}
                </td>
                <td className="border-b border-atx-line-soft px-4 py-3 text-atx-ink-mid">
                  {t.notes}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="mt-6 max-w-[760px] text-[14px] leading-[1.7] text-atx-ink-mid">
        Per-row schema for each table mirrors the Postgres column names used by
        the cloud database — snake_cased, with{" "}
        <code className="font-mono-atx text-[12.5px] text-atx-ink">Date</code>{" "}
        values rendered as ISO-8601 UTC strings,{" "}
        <code className="font-mono-atx text-[12.5px] text-atx-ink">bigint</code>{" "}
        values rendered as strings (JCS rejects numeric overflow),{" "}
        <code className="font-mono-atx text-[12.5px] text-atx-ink">Buffer</code>{" "}
        and <code className="font-mono-atx text-[12.5px] text-atx-ink">Uint8Array</code>{" "}
        rendered as lowercase hex, and{" "}
        <code className="font-mono-atx text-[12.5px] text-atx-ink">null</code>{" "}
        preserved verbatim. See the row projectors in{" "}
        <code className="font-mono-atx text-[12.5px] text-atx-ink">attestix.portability.bundle_writer</code>{" "}
        for the authoritative shape.
      </p>

      {/* ----- Section 6: verifier algorithm ------------------------------- */}
      <h2 className="mt-16 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        06 / Verifier algorithm (reference)
      </h2>
      <p className="mt-3 max-w-[760px] text-[14px] leading-[1.7] text-atx-ink-mid">
        Two reference implementations: Python in{" "}
        <code className="font-mono-atx text-[12.5px] text-atx-ink">attestix.portability.bundle_reader</code>{" "}
        (PyPI{" "}
        <a
          href="https://pypi.org/project/attestix/"
          target="_blank"
          rel="noopener noreferrer"
          className="font-mono-atx text-[12.5px] text-atx-accent hover:underline"
        >
          attestix
        </a>
        ) and TypeScript in attestix-js (today{" "}
        <code className="font-mono-atx text-[12.5px] text-atx-ink">@vibetensor/attestix@0.2.0</code>;
        unscoped{" "}
        <code className="font-mono-atx text-[12.5px] text-atx-ink">attestix</code>{" "}
        publish in flight). Both follow the same algorithm:
      </p>
      <pre className="mt-4 overflow-x-auto rounded-atx-md border border-atx-line-soft bg-atx-bg-sunken px-5 py-4 font-mono-atx text-[12px] leading-[1.6] text-atx-ink">
        {VERIFIER_ALGORITHM}
      </pre>

      {/* ----- Section 7: compatibility + versioning ----------------------- */}
      <h2 className="mt-16 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        07 / Compatibility and versioning
      </h2>
      <ul className="mt-4 space-y-3 text-[14px] leading-[1.7] text-atx-ink-mid">
        <li>
          <strong className="text-atx-ink">v1 is frozen.</strong> No breaking
          changes will land within v1. A future v2 will be published at a new
          URI (e.g. <code className="font-mono-atx text-[12.5px] text-atx-ink">/spec/bundle/v2</code>)
          and producers will stamp the new URI in{" "}
          <code className="font-mono-atx text-[12.5px] text-atx-ink">attestix_bundle_format</code>.
        </li>
        <li>
          <strong className="text-atx-ink">Forward compatibility.</strong>{" "}
          Producers MAY add fields to the manifest or new tables to{" "}
          <code className="font-mono-atx text-[12.5px] text-atx-ink">tables[]</code>;
          verifiers MUST ignore unknown manifest fields and MUST ignore unknown
          tables that are not referenced by a verification rule.
        </li>
        <li>
          <strong className="text-atx-ink">Schema gating.</strong> The{" "}
          <code className="font-mono-atx text-[12.5px] text-atx-ink">schemas.db_migration_max</code>{" "}
          field carries the producer&apos;s database migration version. Consumers
          refuse bundles whose{" "}
          <code className="font-mono-atx text-[12.5px] text-atx-ink">db_migration_max</code>{" "}
          is strictly newer than the consumer&apos;s supported max — see{" "}
          <code className="font-mono-atx text-[12.5px] text-atx-ink">BundleSchemaTooNewError</code>{" "}
          in <code className="font-mono-atx text-[12.5px] text-atx-ink">bundle_reader.py</code>.
        </li>
        <li>
          <strong className="text-atx-ink">v2 plans (non-binding).</strong>{" "}
          zstd compression in place of gzip; optional Parquet representation
          for{" "}
          <code className="font-mono-atx text-[12.5px] text-atx-ink">audit_events</code>{" "}
          for large tenants; manifest signed via the producer&apos;s DID using
          Ed25519Signature2020. In v1 the manifest is unsigned; integrity is by
          SHA-256 only.
        </li>
      </ul>

      {/* ----- Section 8: security model ----------------------------------- */}
      <h2 className="mt-16 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        08 / Security model
      </h2>
      <div className="mt-4 grid gap-5 md:grid-cols-2">
        <div className="rounded-atx-md border border-atx-ok/30 bg-atx-ok/[0.06] p-5">
          <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ok">
            Guarantees
          </div>
          <ul className="mt-3 space-y-2 text-[13.5px] leading-[1.65] text-atx-ink-mid">
            <li>
              <strong className="text-atx-ink">Byte-level tamper evidence.</strong>{" "}
              Any modification to a table body, the manifest, or a sha256 breaks
              verification.
            </li>
            <li>
              <strong className="text-atx-ink">Audit chain integrity.</strong>{" "}
              <code className="font-mono-atx text-[12px] text-atx-ink">audit_events</code>{" "}
              chain is re-verified end-to-end at import; any break aborts.
            </li>
            <li>
              <strong className="text-atx-ink">Row-count consistency.</strong>{" "}
              Per-table row counts in the manifest must match the JSONL line
              count.
            </li>
            <li>
              <strong className="text-atx-ink">Schema gating.</strong> Bundles
              from a strictly newer producer are refused rather than silently
              losing rows or columns.
            </li>
          </ul>
        </div>
        <div className="rounded-atx-md border border-atx-warn/40 bg-atx-warn/[0.06] p-5">
          <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-warn">
            Does NOT guarantee
          </div>
          <ul className="mt-3 space-y-2 text-[13.5px] leading-[1.65] text-atx-ink-mid">
            <li>
              <strong className="text-atx-ink">Confidentiality.</strong> Bundle
              contents are plaintext JCS. Encrypt at rest separately.
            </li>
            <li>
              <strong className="text-atx-ink">Producer authenticity.</strong>{" "}
              The manifest is UNSIGNED in v1 — anyone can produce a structurally
              valid bundle. v2 will add a DID-signed manifest.
            </li>
            <li>
              <strong className="text-atx-ink">Freshness.</strong> The manifest
              carries no nonce or anti-replay marker beyond{" "}
              <code className="font-mono-atx text-[12px] text-atx-ink">exported_at</code>.
              Consumers that need freshness MUST pair the bundle with a
              short-lived attestation.
            </li>
            <li>
              <strong className="text-atx-ink">Anchor freshness.</strong> An
              anchor row records that a hash was once posted to Base Sepolia;
              re-verifying the anchor against the chain is the consumer&apos;s
              responsibility.
            </li>
          </ul>
        </div>
      </div>
      <p className="mt-6 max-w-[760px] text-[14px] leading-[1.7] text-atx-ink-mid">
        <strong className="text-atx-ink">Recommended deployment.</strong> Pair
        every bundle export with a signed{" "}
        <code className="font-mono-atx text-[12.5px] text-atx-ink">BundleExportedCredential</code>{" "}
        (W3C VC) issued at export time that attests to the bundle&apos;s SHA-256.
        The credential provides producer authenticity that the v1 wire format
        does not, without bloating the manifest with signature material.
      </p>

      {/* ----- Section 9: example ------------------------------------------ */}
      <h2 className="mt-16 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        09 / Example
      </h2>
      <p className="mt-3 max-w-[760px] text-[14px] leading-[1.7] text-atx-ink-mid">
        The bytes below are extracted verbatim from the deterministic test
        fixture at{" "}
        <code className="font-mono-atx text-[12.5px] text-atx-ink">tests/fixtures/bundles/sample-v1.tar.gz</code>{" "}
        in the{" "}
        <a
          href="https://github.com/VibeTensor/attestix"
          target="_blank"
          rel="noopener noreferrer"
          className="text-atx-accent hover:underline"
        >
          attestix
        </a>{" "}
        repo. The bundle is{" "}
        <code className="font-mono-atx text-[12.5px] text-atx-ink">2,768</code>{" "}
        bytes on disk and contains 15 tar members (13 table JSONLs + manifest +
        sha side-car).
      </p>

      <h3 className="mt-8 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-faint">
        manifest.json (verbatim, JCS-canonical, 2,367 bytes)
      </h3>
      <pre className="mt-3 overflow-x-auto rounded-atx-md border border-atx-line-soft bg-atx-bg-sunken px-5 py-4 font-mono-atx text-[11.5px] leading-[1.55] text-atx-ink">
        {EXAMPLE_MANIFEST}
      </pre>

      <h3 className="mt-8 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-faint">
        manifest.sha256 (verbatim, 65 bytes including trailing newline)
      </h3>
      <pre className="mt-3 overflow-x-auto rounded-atx-md border border-atx-line-soft bg-atx-bg-sunken px-5 py-4 font-mono-atx text-[12.5px] text-atx-accent">
        {EXAMPLE_MANIFEST_SHA}
      </pre>

      <h3 className="mt-8 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-faint">
        credentials.jsonl (one row; full W3C VC envelope; 586 bytes)
      </h3>
      <pre className="mt-3 overflow-x-auto rounded-atx-md border border-atx-line-soft bg-atx-bg-sunken px-5 py-4 font-mono-atx text-[11.5px] leading-[1.55] text-atx-ink">
        {EXAMPLE_CREDENTIAL_ROW}
      </pre>

      <h3 className="mt-8 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-faint">
        audit_events.jsonl (first row of a 3-row hash chain)
      </h3>
      <pre className="mt-3 overflow-x-auto rounded-atx-md border border-atx-line-soft bg-atx-bg-sunken px-5 py-4 font-mono-atx text-[11.5px] leading-[1.55] text-atx-ink">
        {EXAMPLE_AUDIT_FIRST_ROW}
      </pre>
      <p className="mt-3 max-w-[760px] text-[13px] leading-[1.6] text-atx-ink-mid">
        The first row&apos;s{" "}
        <code className="font-mono-atx text-[12px] text-atx-ink">prev_hash</code>{" "}
        is the genesis sentinel (64 zero bytes). Each subsequent row&apos;s{" "}
        <code className="font-mono-atx text-[12px] text-atx-ink">prev_hash</code>{" "}
        equals the previous row&apos;s{" "}
        <code className="font-mono-atx text-[12px] text-atx-ink">chain_hash</code>;
        each row&apos;s own{" "}
        <code className="font-mono-atx text-[12px] text-atx-ink">chain_hash</code>{" "}
        is computed over the JCS-canonical row body using the canonicaliser
        documented above.
      </p>

      {/* ----- Section 10: test vectors ------------------------------------ */}
      <h2 className="mt-16 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        10 / Test vectors
      </h2>
      <p className="mt-3 max-w-[760px] text-[14px] leading-[1.7] text-atx-ink-mid">
        The deterministic fixture above is regenerated by{" "}
        <a
          href="https://github.com/VibeTensor/attestix/blob/main/tests/fixtures/bundles/generate_sample_bundle.py"
          target="_blank"
          rel="noopener noreferrer"
          className="text-atx-accent hover:underline"
        >
          <code className="font-mono-atx text-[12.5px]">tests/fixtures/bundles/generate_sample_bundle.py</code>
        </a>
        . Anyone building a third-party verifier can run the generator, byte-compare
        against the committed fixture, then assert their verifier accepts the
        clean bundle and rejects each of the three tamper variants the
        generator can produce (manifest body mutation, table body mutation, and
        schema-too-new bump).
      </p>
      <p className="mt-3 max-w-[760px] text-[14px] leading-[1.7] text-atx-ink-mid">
        The round-trip suite at{" "}
        <a
          href="https://github.com/VibeTensor/attestix/tree/main/tests/portability"
          target="_blank"
          rel="noopener noreferrer"
          className="text-atx-accent hover:underline"
        >
          <code className="font-mono-atx text-[12.5px]">tests/portability/</code>
        </a>{" "}
        exercises every code path on this page against the fixture and is part
        of the 585-test CI matrix.
      </p>

      {/* ----- Section 11: versions index ---------------------------------- */}
      <h2 className="mt-16 font-mono-atx text-[11px] uppercase tracking-[0.14em] text-atx-ink-dim">
        11 / Versions index
      </h2>
      <div className="mt-4 overflow-hidden rounded-atx-md border border-atx-line-soft">
        <table className="w-full border-collapse text-left text-[13px]">
          <thead className="bg-atx-bg-sunken">
            <tr>
              {["Version", "Status", "Published", "Identifier"].map((h) => (
                <th
                  key={h}
                  className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-faint"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr className="bg-atx-panel">
              <td className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[11.5px] text-atx-accent">
                v1
              </td>
              <td className="border-b border-atx-line-soft px-4 py-3">
                <span className="rounded-atx-xs border border-atx-ok/40 bg-atx-ok/[0.08] px-2 py-0.5 font-mono-atx text-[10.5px] uppercase tracking-[0.12em] text-atx-ok">
                  current
                </span>
              </td>
              <td className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[11.5px] text-atx-ink-dim">
                {PUBLISHED_DATE}
              </td>
              <td className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[11.5px] text-atx-ink">
                {SPEC_URI}
              </td>
            </tr>
            <tr className="bg-atx-panel">
              <td className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[11.5px] text-atx-ink-dim">
                v2
              </td>
              <td className="border-b border-atx-line-soft px-4 py-3">
                <span className="rounded-atx-xs border border-atx-line-soft px-2 py-0.5 font-mono-atx text-[10.5px] uppercase tracking-[0.12em] text-atx-ink-dim">
                  planned
                </span>
              </td>
              <td className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[11.5px] text-atx-ink-dim">
                —
              </td>
              <td className="border-b border-atx-line-soft px-4 py-3 font-mono-atx text-[11.5px] text-atx-ink-dim">
                /spec/bundle/v2 (not yet allocated)
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* ----- See also ---------------------------------------------------- */}
      <div className="mt-12 rounded-atx-md border border-atx-line-soft bg-atx-bg-sunken p-6">
        <div className="font-mono-atx text-[10.5px] uppercase tracking-[0.14em] text-atx-ink-dim">
          See also
        </div>
        <div className="mt-2 flex flex-wrap gap-4 text-[13.5px]">
          <a
            href="https://github.com/VibeTensor/attestix/blob/main/attestix/portability/bundle_writer.py"
            target="_blank"
            rel="noopener noreferrer"
            className="text-atx-accent hover:underline"
          >
            bundle_writer.py (Python producer)
          </a>
          <a
            href="https://github.com/VibeTensor/attestix/blob/main/attestix/portability/bundle_reader.py"
            target="_blank"
            rel="noopener noreferrer"
            className="text-atx-accent hover:underline"
          >
            bundle_reader.py (Python verifier)
          </a>
          <Link href="/security" className="text-atx-accent hover:underline">
            Security
          </Link>
          <Link href="/changelog" className="text-atx-accent hover:underline">
            Changelog
          </Link>
        </div>
        <p className="mt-4 text-[12.5px] leading-[1.6] text-atx-ink-dim">
          Apache 2.0 license. Maintained by{" "}
          <a
            href="https://vibetensor.com"
            target="_blank"
            rel="noopener noreferrer"
            className="text-atx-accent hover:underline"
          >
            VibeTensor
          </a>
          . Report errors in this spec at{" "}
          <a
            href="https://github.com/VibeTensor/attestix/issues"
            target="_blank"
            rel="noopener noreferrer"
            className="text-atx-accent hover:underline"
          >
            github.com/VibeTensor/attestix/issues
          </a>
          .
        </p>
      </div>
    </section>
  );
}
