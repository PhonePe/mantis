# Setting App Context
---

> Warning 🚨 - Considering this feature is a string based match, this will not be 100 % accurate when you add strings that are of shorter length

Mantis lets you setup an App Context to the subdomains discovered. For e.g. if you organisation has multiple apps like upi, insurance, mutual funds etc. You can provide key words for every app and Mantis will automatically map this context to each subdomain discovered and also to findings.

```yml
app:
  upi: [upi,payments]
  insurance: [insurance.org.com]
  mutual-funds: [mutual-funds, mutual]
  
```

This will map: 

- upi.org.com, payments.org.com to **upi app**  
- buy.insurance.org.com, integrations.insurance.org.com to **insurance app**  
- mf.org.com, mf-buy.org.com, mf-api.org.com to **mutual-funds app**


