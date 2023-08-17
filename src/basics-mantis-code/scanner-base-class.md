# Scanner Base Class
---

When you are integrating a new scanner, the first thing to you need to know is that, if your scanner is a command line tool or an API, based on this there are two types of Scaner classes available.

- **ToolScanner**
- **APIScanner**

## 1. Tool Scanner 

From a recon automation perspective, command-line tools are tools that you typically install in your system using brew, apt, apt-install, or similar methods, and then run scans.  

`$ nuclei -u https://www.example.org -json -o nuclei.json -exclude-severity info -v`

*E.g. Amass, Subfinder, naabu, nuclei etc.*

### Functions to implement

To integrate a tool like nuclei, your new scanner class will needs to inherit the **ToolScanner**.

The functions you will need to implement as part of the ToolScanner are:


**get_commands()** - create the final tool command that needs to be run. 

**parse_report()** - parse the report produced by the command, match it to the db schema and create a dictionary

**db_operations()** - insert the dictionary from parse_report() into the database

## 2. API based Scanner 
Scanners that involve sending an HTTP request instead of running an OS command to perform a scan. 

```http
GET https://api.shodan.io/shodan/ports?key={YOUR_API_KEY}

```

*E.g. Shodan, SSLMate etc.*

### Functions to implement

**get_api_calls()** - create the HTTP request you need to send 

**parse_reponse()** - parse the HTTP response to get asset or findings information

**db_operations()** - insert the dictionary from parse_reponse() into the database

> ⏭️ We are now aware of the folder structure and Base Scanner classes, let us now look at a few utils function that will help us ease through new integrations.
