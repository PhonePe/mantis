# Setup Dashboard
---

## AppSmith Dashboard Setup

Once you install the dashboard, you should be able access it from the https://DASHBOARD_IP:1337/

- Access this dashboard URL, you should be prompted to create an AppSmith account.
- Remember/bookmark this base url as AppSmith uses a multi-application construct with "My first application" as the default. We will be importing the appropriate Application and Pages in the following steps.
- Navigate to Applications with the "a_" icon on the upper left or using the link included.
- In the upper right of the Applications page, there is an orange button "Create new" as well as 3 dots, click the orange "Create new" button to expand a drop-down.
- The drop-down menu has 3 items: "Application", "Templates", and "Import" ... select "Import" by clicking it.
- From there, import the template JSON file. It is located in the cloned repo: in the dashboard_templates folder. (mantis\dashboard_templates\Mantis Dashboard.json)
-You will be asked to enter db information for the included MongoDB that was created. Enter the following:
    - host: DATABASE_IP/DOMAIN
    - port: 27017
    - default db: mantis


## Mantis Proprietary Dashboard Setup (coming soon)

