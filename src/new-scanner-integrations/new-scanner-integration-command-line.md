# Command Line Tool
---

This tutorial will guide you through the process of integrating a new command-line tool with Mantis.

Each section builds upon the previous one, but the tutorial is structured to separate topics, so that you can easily find the information you need to address your specific needs

It's also designed to serve as a future reference, enabling you to come back and find the information you need when you need it.

## ✍️ Let's Get Started
 
 Let's say that you're a bug bounty hunter or a product security engineer who thinks that a particular tool can make a specific module more efficient. 
 
For the purpose of this tutorial, let's assume that we need to strengthen the Discovery module, which identifies subdomains, by adding a new tool. [**Amass**](https://github.com/owasp-amass/amass). 
 
 [**Amass**](https://github.com/owasp-amass/amass) performs network mapping of attack surfaces and external asset discovery using open source information gathering and active reconnaissance techniques

## 📇 Files to be changed

 For integrating a command line scanner, these are the files you need to make changes:
 1. Add a **new class file** under the respective module
 2. Add the tool name in **config.yml**
 3. Add the installation instructions in **DockerFile**

 > ⏭️ Let's now integrate Amass tool into the Discovery module