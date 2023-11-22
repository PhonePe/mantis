# 🔗 New Scanner Integrations
---

To integrate a new scanner with Mantis, it should fall under one of these categories:
- [**Command Line Tool based scanner**](/./mantis/new-scanner-integrations/new-scanner-integration-command-line.md)
- [**API based scanner**](/./mantis/new-scanner-integrations/new-scanner-integration-api.md)

## Command Line based Scanner 
From a recon automation perspective, command-line tools are tools that you typically install in your system using brew, apt, apt-install, or similar methods, and then run scans.  

*E.g. Amass, Subfinder, naabu, nuclei etc.*

```zsh
$ nuclei -u https://www.example.org -json -o nuclei.json -exclude-severity info -v
```

## API based Scanner 
Scanners that involve sending an HTTP request instead of running an OS command to perform a scan. 

*E.g. Shodan, SSLMate etc.*

```http
GET https://api.shodan.io/shodan/ports?key={YOUR_API_KEY}

```
Now that you are aware of the scanner types that Mantis supports, let's get started