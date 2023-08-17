from rocketry import Rocketry
from mantis.config_parsers.config_client import ConfigProvider
from time import sleep
import os

app = Rocketry(config={"task_execution": "main"})

workflows  = ConfigProvider.get_config().workflow

print(workflows)
i = 0
for workflow in workflows:
    for cmd in workflow.cmd:
        i += 1
        exec(f'@app.task("{workflow.schedule}")\ndef workflow_{workflow.workflowName}_{str(i)}(): os.system("{cmd} -w {workflow.workflowName}")')

if __name__ == "__main__":
    app.run()
