# Slack Notification
---

Mantis provides an advanced layered based Slack alerting, that includes:

- Teams
- Apps
- Assets/Findings
- Tagging

## Notifications Config

```yaml
notify:
  - teamName: web_team
    scanEfficiency: true 
    channel:
      slack:
        - https://hooks.slack.com/services/********/********
    app: [payments-dashboard, transactions-dashboard]
    assets:
      - subdomain: ['prateek.thakare']
      - certificate: ['praveen.kanniah']
    findings: 
      - vulnerability: []
      - secret: []
```

### Layer 1 (Teams)
---

A Team is a team within an organistion, e.g. web team, appsec team, infra team etc. With Mantis, you can create unique configurations for every team and alert them for what they need.

### Layer 2 (Apps)
---

In the background Mantis stores the identified assets, recon informtion and vulnerbailities in a **mongDB** database. Mantis lets you provide keywords to map a subdomain to an App, like this:

```yaml
app:
payments-dashboard: [payments, upi]
transactions-dashboard: [transactions, npci]
```
If a subdomain is discovered with these keywords, it will automatically map it to an app and store the context. A team can now receive alerts specific to an app.

### Layer 3 (Assets and Findings)
---

A team can also receive alerts based on an Asset Type or Findings Type

- **Assets**
    - TLD (Top Level Domain)
    - Subdomain
    - IP
    - Certificates
- **Findings**
    - Vulerabilities
    - Misconfigurations
    - Phishing
    - Secrets

You can add/delete the types you want to receive/ignore alerts for.


### Layer 4 (Tagging and Channels)
---

This layer is specific to Slack alerting, where in a group you can particularly tag a specific person for a particular alert.
