# Security Notes

## ChromaDB security exception

The project currently uses ChromaDB 1.5.9 through the embedded
`PersistentClient` / local persistent storage model.

ChromaDB is not deployed as an independent HTTP server in this
application.

The application exposes the Company Policy Agent FastAPI service on
port 8000. It does not expose a ChromaDB HTTP API or ChromaDB server
port.

The following ChromaDB advisories reported by pip-audit are associated
with ChromaDB API/server functionality:

- PYSEC-2026-311
- PYSEC-2026-3813
- PYSEC-2026-3814
- PYSEC-2026-3815

These vulnerabilities are currently tracked as an accepted,
architecture-scoped exception because the vulnerable ChromaDB network
API is not exposed by this deployment.

This exception must be reviewed whenever:

1. ChromaDB is upgraded.
2. ChromaDB server/API functionality is introduced.
3. ChromaDB is deployed as a separate service.
4. The application architecture changes.
5. A security advisory provides a fixed version.

The application must never expose the vulnerable ChromaDB API directly
to an untrusted network.

## Dependency monitoring

`pip-audit` remains part of the CI security gate.

The ChromaDB exception must remain narrow and documented. Other
dependency vulnerabilities must not be ignored automatically.