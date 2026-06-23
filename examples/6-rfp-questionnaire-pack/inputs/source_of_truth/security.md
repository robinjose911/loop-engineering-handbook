# Information Security Policy

Source id: `SRC-SEC`

- All data in transit is encrypted with TLS 1.3.
- Data at rest is encrypted with AES-256.
- We enforce SSO with SAML 2.0 for all employees.
- Multi-factor authentication is required for all production access.
- Secrets are stored in a managed vault, never in source control.
- We run quarterly third-party penetration tests.
- Vulnerabilities are triaged within one business day.
- Production access is logged and reviewed monthly.
- We follow a documented secure-SDLC with mandatory code review.
- Endpoint disk encryption is enforced on all company laptops.
