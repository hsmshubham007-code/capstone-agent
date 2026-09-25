# Security Notes

## ChromaDB Security Exception

The project currently uses:

* ChromaDB `1.5.9`
* `langchain-chroma` `1.1.0`

The dependency is currently flagged by `pip-audit` for four unique security advisories:

* **PYSEC-2026-311**

  * CVE-2026-45829
  * GHSA-f4j7-r4q5-qw2c
* **PYSEC-2026-3813**

  * CVE-2026-45830
  * GHSA-2wm9-hf6c-p5cr
* **PYSEC-2026-3814**

  * CVE-2026-45833
  * GHSA-36p7-vc44-83pf
* **PYSEC-2026-3815**

  * CVE-2026-45831
  * GHSA-xph7-9rjv-w5fr

`pip-audit` currently reports no fixed version for these findings.

## Deployment Architecture

ChromaDB is used through the application's embedded/local persistent storage model.

ChromaDB is not deployed as an independent HTTP server in this application.

The application exposes the Company Policy Agent FastAPI service on port `8000`. It does not expose a ChromaDB HTTP API or ChromaDB server port.

The application architecture is:

```text
Internet
   |
   v
FastAPI :8000
   |
   v
Company Policy Agent
   |
   v
Local ChromaDB storage
```

## Exposure Assessment

The reported vulnerabilities include ChromaDB API/server code-injection and authorization issues.

The affected code-injection findings involve ChromaDB API operations that accept model repository configuration and `trust_remote_code`.

The authorization findings concern ChromaDB server-side authorization and tenant/resource scoping.

The current application does not expose a standalone ChromaDB HTTP server or provide untrusted clients with direct access to those APIs.

This reduces the application's exposure to the documented attack paths.

This is an architectural mitigation, not a software fix. The ChromaDB dependency remains flagged by `pip-audit`.

The application must never expose the vulnerable ChromaDB API directly to an untrusted network.

## Security Verification

The following checks were performed against the project virtual environment.

### Dependency consistency

Command:

```powershell
python -m pip check
```

Result:

```text
No broken requirements found.
```

### Installed versions

```text
chromadb==1.5.9
langchain-chroma==1.1.0
pip-audit==2.10.1
```

### Security audit

Command:

```powershell
python -m pip_audit
```

Result:

```text
Found 5 known vulnerabilities in 1 package
```

The five audit records contain four unique vulnerabilities because `PYSEC-2026-311` is reported twice by the audit database.

No other installed package was reported as vulnerable in this audit result.

## Dependency Decision

The project retains ChromaDB `1.5.9` temporarily because:

1. The current `pip-audit` output reports no fixed versions for the identified findings.
2. A compatible patched stable release has not yet been confirmed.
3. Downgrading would not provide a reliable remediation.
4. Using an unreleased development build solely to clear the audit finding is not appropriate for this production build.
5. The application does not expose a standalone ChromaDB server.

The dependency is therefore treated as a temporary, explicitly documented security exception.

The absence of a fix version in the audit output does not establish that no remediation exists. The project must continue checking upstream advisories and releases.

## Required Review Conditions

This exception must be reviewed whenever:

1. ChromaDB is upgraded.
2. ChromaDB server/API functionality is introduced.
3. ChromaDB is deployed as a separate service.
4. The application architecture changes.
5. A stable ChromaDB release provides fixes for the affected vulnerabilities.
6. A new security advisory changes the exposure assessment.

## Dependency Monitoring

`pip-audit` remains part of the CI security checks.

The ChromaDB exception must remain narrow and documented.

Other dependency vulnerabilities must not be ignored automatically.

The CI audit is currently configured as non-blocking using `continue-on-error: true`. This allows the workflow to complete while the findings are investigated; it does not mean the dependency is vulnerability-free.

When a compatible patched stable ChromaDB release becomes available, the project should:

1. Upgrade ChromaDB in a separate branch.
2. Rebuild the vector store if required.
3. Run the full pytest suite.
4. Run retrieval evaluation.
5. Run injection-resistance evaluation.
6. Verify `/health` and `/ready`.
7. Verify `/metrics`.
8. Verify `/chat`.
9. Re-run `pip-audit`.
10. Rebuild and test the Docker image.

After remediation is verified, remove the non-blocking audit exception and require the security audit to pass.

## Secrets and Sensitive Data

* Store API keys and credentials in environment variables or an appropriate secrets manager.
* Do not commit `.env` files, API keys, passwords, or tokens to Git.
* Keep audit logs and company policy documents out of public repositories unless they have been reviewed and approved for publication.
* Rotate any credential that is accidentally exposed.
* Avoid logging secrets or unnecessary sensitive employee information.

## Security Review

Review this document and the dependency audit findings whenever security controls, dependencies, deployment configuration, or upstream advisories change.

**Current ChromaDB status:** Remediation pending; continue monitoring and testing.
