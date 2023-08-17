from mantis.models.args_model import ArgsModel

class BaseScanner:

    def __init__(self) -> None:
        self.results = {}


    def init(self, args: ArgsModel):
        raise NotImplementedError
    
   
    async def execute(self, tooltuple):
        raise NotImplementedError