# System Requirements and Assumptions

## Functional requirements

- Create a short URL from a long URL
- Support custom alias generation or user-defined alias
- Redirect shortened URLs to their original target
- Track click events and basic analytics
- Provide governance layer for multi-step tasks and approvals

## Non-functional assumptions

- Suitable for prototype and demonstration workloads
- Not designed to replace a globally distributed production URL shortener
- PII minimization is enforced in analytics collection
- Approval gates are intentionally explicit and conservative
