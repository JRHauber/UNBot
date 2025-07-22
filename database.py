class Database():
    def __init__(self, **kwargs) -> None:
        self.setup_db(**kwargs)

    def setup_db(self):
        raise NotImplementedError()

    async def get_timestamps(self, timestamp: int):
        raise NotImplementedError()

    async def add_vote(self, proposal_id: int, uid: int, vote: int):
        raise NotImplementedError()

    async def get_votes(self, proposal_id: int):
        raise NotImplementedError()

    async def get_proposal(self, proposal_id: int):
        raise NotImplementedError()

    async def add_proposal(self, name: str, text: str, next_time : int):
        raise NotImplementedError()

    async def complete_vote(self, proposal_id: int):
        raise NotImplementedError()

    async def get_active_proposals(self):
        raise NotImplementedError()

    async def finish_discuss(self, id : int, time : int):
        raise NotImplementedError()

    async def extend_vote(self, id : int):
        raise NotImplementedError()

    async def extend_time(self, id : int, time : int):
        raise NotImplementedError()