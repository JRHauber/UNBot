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

    async def add_delegate(self, id : int, guild : int):
        raise NotImplementedError()

    async def remove_delegate(self, id : int):
        raise NotImplementedError()

    async def get_delegates(self):
        raise NotImplementedError()

    async def get_all_delegates(self):
        raise NotImplementedError()

    async def activate_delegate(self, id : int):
        raise NotImplementedError()

    async def deactivitate_delegate(self, id : int):
        raise NotImplementedError()

    async def set_power(self, id : int, power : float):
        raise NotImplementedError()

    async def miss_vote(self, id : int, missed : int):
        raise NotImplementedError()

    async def add_guild(self, guild : int):
        raise NotImplementedError()

    async def set_guild_server(self, guild : int, server_id : int):
        raise NotImplementedError()

    async def set_guild_citizen(self, guild : int, citizen_role : int):
        raise NotImplementedError()

    async def set_members(self, guild : int, members : int):
        raise NotImplementedError()

    async def get_guilds(self):
        raise NotImplementedError()