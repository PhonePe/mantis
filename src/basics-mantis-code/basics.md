# 📖 Mantis Code - Getting Started
---

Before you add a new module or scanner to Mantis yourself, it is important to understand the parts of the code that you'll be editing and certain functions that will come in handy.

In this walkthrough, we shall mainly focus on:

- [Mantis folder structure](/./mantis/basics-mantis-code/folder-structure.md) - This will help you understand exactly where you need to make changes for new integrations
- [Base scanner class](/./mantis/basics-mantis-code/scanner-base-class.md) - Based on the scanner that you want to integrate, this will help you choose the base class that you need to inherit
- [Important utility functions](/./mantis/basics-mantis-code/important-utils.md) - If your new scanner only accepts IP addresses, TLDs, or sometimes both, you don't have to write any queries or functions to validate the inputs. Mantis has built-in utility functions that can provide you with this input directly. 
- [DB models](/./mantis/basics-mantis-code/db-models.md) - After your new scanner completes its scan, you'll need to insert the results into MongoDB. To do so, you'll need to understand the schema that is in place. This will help you do that.

A basic understanding of the above will simplify any new integrations with Mantis.

> ⏭️ Let's begin with understanding the folder structure next.
