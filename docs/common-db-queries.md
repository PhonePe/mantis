# Common MongoDB Queries for Mantis

This document is a quick-reference for the MongoDB queries that Mantis users
most frequently need. Every query targets the database that Mantis writes to
(default database name: `mantis`) and uses the three primary collections:

| Collection | Document model | What it stores |
|---|---|---|
| `assets_collection` | [`Assets`](../mantis/db/db_models.py) | Top-level domains, subdomains, IPs, certificates, third-party integrations |
| `extended_assets_collection` | [`Extended`](../mantis/db/db_models.py) | URL-level assets discovered on top of a base asset (e.g. endpoints, paths) |
| `findings_collection` | [`Findings`](../mantis/db/db_models.py) | Vulnerabilities, misconfigurations, secrets, phishing, informational |

The queries below are shown using the MongoDB Shell (`mongosh`) syntax. They
can be run as-is against a live Mantis database, or adapted for any Mongo
driver (PyMongo, Motor, Studio 3T, Compass, etc.).

Replace `<org>`, `<tld>`, `<app>` placeholders with real values from your
scans.

---

## Assets

### List every TLD under an organisation

```js
db.assets_collection.find(
  { org: "<org>", asset_type: "TLD" },
  { _id: 0, asset: 1 }
)
```

### Count TLDs grouped by organisation

```js
db.assets_collection.aggregate([
  { $match: { asset_type: "TLD" } },
  { $group: { _id: "$org", tlds: { $addToSet: "$asset" }, count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])
```

### All subdomains for a given TLD

```js
db.assets_collection.find(
  {
    org: "<org>",
    asset_type: "subdomain",
    asset: { $regex: "\\.<tld>$", $options: "i" }
  },
  { _id: 0, asset: 1, active_hosts: 1 }
)
```

> Escape dots in the TLD (e.g. `example\\.com`) — dot means "any char" in a
> regex otherwise.

### Subdomain count per TLD

```js
db.assets_collection.aggregate([
  { $match: { org: "<org>", asset_type: "subdomain" } },
  {
    $project: {
      tld: {
        $reduce: {
          input: { $slice: [ { $split: ["$asset", "."] }, -2 ] },
          initialValue: "",
          in: {
            $cond: [
              { $eq: ["$$value", ""] },
              "$$this",
              { $concat: ["$$value", ".", "$$this"] }
            ]
          }
        }
      }
    }
  },
  { $group: { _id: "$tld", subdomains: { $sum: 1 } } },
  { $sort: { subdomains: -1 } }
])
```

### Assets behind a CDN (e.g. Cloudflare)

```js
db.assets_collection.find(
  { org: "<org>", cdn_names: { $regex: "cloudflare", $options: "i" } },
  { _id: 0, asset: 1, cdn_names: 1 }
)
```

### Assets protected by a WAF

```js
db.assets_collection.find(
  { org: "<org>", waf: { $ne: null, $not: { $size: 0 } } },
  { _id: 0, asset: 1, waf: 1 }
)
```

### Assets exposing specific ports

```js
db.assets_collection.find(
  { org: "<org>", ports: { $in: [22, 3306, 6379] } },
  { _id: 0, asset: 1, ports: 1 }
)
```

### Assets by ASN / hosting provider

```js
db.assets_collection.find(
  { org: "<org>", as_name: { $regex: "AMAZON", $options: "i" } },
  { _id: 0, asset: 1, as_number: 1, as_name: 1, as_country: 1 }
)
```

### Stale (decommissioned) assets

```js
db.assets_collection.find(
  { org: "<org>", stale: true },
  { _id: 0, asset: 1, updated_timestamp: 1 }
)
```

### Recently discovered assets (last 7 days)

```js
const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();

db.assets_collection.find(
  { org: "<org>", created_timestamp: { $gte: sevenDaysAgo } },
  { _id: 0, asset: 1, asset_type: 1, created_timestamp: 1 }
).sort({ created_timestamp: -1 })
```

### All technologies used by an organisation

```js
db.assets_collection.aggregate([
  { $match: { org: "<org>", technologies: { $exists: true, $ne: [] } } },
  { $unwind: "$technologies" },
  { $group: { _id: "$technologies", assets: { $sum: 1 } } },
  { $sort: { assets: -1 } }
])
```

---

## Findings

### High and Critical severity issues for an organisation

```js
db.findings_collection.find(
  {
    org: "<org>",
    severity: { $in: ["HIGH", "CRITICAL"] },
    status: "Open",
    falsepositive: { $ne: true }
  },
  { _id: 0, host: 1, title: 1, severity: 1, tool_source: 1, cve_id: 1 }
).sort({ severity: -1, created_timestamp: -1 })
```

### Open findings grouped by severity

```js
db.findings_collection.aggregate([
  { $match: { org: "<org>", status: "Open", falsepositive: { $ne: true } } },
  { $group: { _id: "$severity", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])
```

### Findings by type (vulnerability / secret / phishing / misconfiguration)

```js
db.findings_collection.find(
  { org: "<org>", type: "secret", status: "Open" },
  { _id: 0, host: 1, title: 1, tool_source: 1, created_timestamp: 1 }
)
```

### All findings for a specific host

```js
db.findings_collection.find(
  { org: "<org>", host: "<host>" },
  { _id: 0, title: 1, severity: 1, type: 1, tool_source: 1, status: 1 }
).sort({ severity: -1 })
```

### Findings by CVE

```js
db.findings_collection.find(
  { cve_id: "CVE-2024-XXXXX" },
  { _id: 0, org: 1, host: 1, title: 1, severity: 1 }
)
```

### Top 10 affected hosts by finding count

```js
db.findings_collection.aggregate([
  { $match: { org: "<org>", status: "Open", falsepositive: { $ne: true } } },
  { $group: { _id: "$host", findings: { $sum: 1 } } },
  { $sort: { findings: -1 } },
  { $limit: 10 }
])
```

### Top tools by findings reported

```js
db.findings_collection.aggregate([
  { $match: { org: "<org>", status: "Open" } },
  { $group: { _id: "$tool_source", findings: { $sum: 1 } } },
  { $sort: { findings: -1 } }
])
```

### New findings in the last 24 hours

```js
const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();

db.findings_collection.find(
  {
    org: "<org>",
    created_timestamp: { $gte: yesterday },
    falsepositive: { $ne: true }
  },
  { _id: 0, host: 1, title: 1, severity: 1, type: 1 }
).sort({ created_timestamp: -1 })
```

### Phishing domains discovered for an organisation

```js
db.findings_collection.find(
  { org: "<org>", type: "phishing" },
  { _id: 0, host: 1, title: 1, info: 1, created_timestamp: 1 }
)
```

### Findings filtered by application (sub-scope)

```js
db.findings_collection.find(
  { org: "<org>", app: "<app>", status: "Open" },
  { _id: 0, host: 1, title: 1, severity: 1, type: 1 }
)
```

---

## Extended assets (URL-level)

### Verified URLs for an organisation

```js
db.extended_assets_collection.find(
  {
    org: "<org>",
    is_verified: "verified",
    availability_status: "Exists"
  },
  { _id: 0, asset: 1, url: 1, asset_type: 1 }
)
```

### Extended assets discovered in the last week

```js
const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();

db.extended_assets_collection.find(
  { org: "<org>", created_timestamp: { $gte: sevenDaysAgo } },
  { _id: 0, asset: 1, url: 1, created_timestamp: 1 }
).sort({ created_timestamp: -1 })
```

---

## Cross-collection queries

### Hosts with at least one Critical finding + their technologies

```js
const criticalHosts = db.findings_collection.distinct(
  "host",
  { org: "<org>", severity: "CRITICAL", status: "Open", falsepositive: { $ne: true } }
);

db.assets_collection.find(
  { org: "<org>", asset: { $in: criticalHosts } },
  { _id: 0, asset: 1, technologies: 1, webserver: 1, ports: 1 }
)
```

---

## Using these queries from Python (Motor)

All collection names and connection wiring live in
[`mantis/db/database.py`](../mantis/db/database.py). Re-using that module
from a script keeps credentials out of your code:

```python
import asyncio
from mantis.db.database import findings_collection

async def high_and_critical(org: str):
    cursor = findings_collection.find(
        {
            "org": org,
            "severity": {"$in": ["HIGH", "CRITICAL"]},
            "status": "Open",
            "falsepositive": {"$ne": True},
        },
        {"_id": 0, "host": 1, "title": 1, "severity": 1, "tool_source": 1, "cve_id": 1},
    )
    async for finding in cursor:
        print(finding)

asyncio.run(high_and_critical("example-org"))
```

---

## Indexing tips

Most of the queries above filter by `org` + one of: `asset_type`, `severity`,
`type`, `status`. If you run them regularly (especially from the dashboard or
alerter), consider adding compound indexes:

```js
db.assets_collection.createIndex({ org: 1, asset_type: 1 });
db.assets_collection.createIndex({ org: 1, stale: 1 });

db.findings_collection.createIndex({ org: 1, status: 1, severity: 1 });
db.findings_collection.createIndex({ org: 1, type: 1 });
db.findings_collection.createIndex({ cve_id: 1 });
db.findings_collection.createIndex({ host: 1 });

db.extended_assets_collection.createIndex({ org: 1, is_verified: 1 });
```

---

## Contributing

Have a query that you reach for often? Open a PR adding it to this document
with a short description of the use-case — the goal is to grow a shared
playbook of battle-tested Mantis queries.
