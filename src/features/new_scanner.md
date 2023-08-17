# Integrate new scanner in minutes
---
<product-team>product security teams</product-team> <bug-bounty>bug bounty hunters </bug-bounty>

## 🤔 Use-Case
**I want to:**
- *integrate new tools with a recon automation framework that the framework does not support by default* 
- *add scanners that are either a command-line tool or an API*
- *integrate scanners quickly and easily*


## 😃 Feature

Mantis is designed with the goal of minimizing the time it takes to integrate new scanners, whether for Mantis developers or external teams.

Mantis includes several functions that make integrating new scanners easy.

To add a new tool, this is what you need to do:
- Create a Python class for the scanner
    - Extend **ToolScanner** if you are integrating a new command line scanner
    - Extend **APIScanner** if you are integrating a new API scanner
- Implement three functions in the class
    - **get_commands() or get_api_calls()**, depends on whether you choose Tool or API, this basically gets your scan command or API HTTP request ready
    - **parse_report() or parse_response()**, again depends on whether you choose Tool or API, this is to parse the response
    - **db_operations()**, insert the information to database and this is where its simple, we have built-in functions that takes care of everything
- Add the install instructions in **DockerFile**

> INFO💡: For a more detailed understanding on how to integrate a new scanner, [Click here](/./new-scanner-integrations/new-scanner-integration.md)

