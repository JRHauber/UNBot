import database
import sqlite3
import asyncio
import re
from datetime import datetime

class DatabaseSqlite(database.Database):
    db = None
    database_name = "UNB_Database.db"
    lock = None


    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def setup_db(self, database_name : str = "UNB_Database.db") -> None:
        assert database_name

        self.db = sqlite3.connect(database_name, check_same_thread=False)

        self.lock = asyncio.Lock()

        self.db.execute(
        """
        CREATE TABLE IF NOT EXISTS proposals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            vote_text TEXT NOT NULL,
            completed BOOL DEFAULT FALSE,
            next_time INTEGER NOT NULL,
            discussed BOOL DEFAULT FALSE,
            extend_votes INTEGER DEFAULT 0
        );
        """
        )

        self.db.execute(
        """
        CREATE TABLE IF NOT EXISTS votes (
            proposal_id INTEGER NOT NULL,
            user INTEGER NOT NULL,
            vote INTEGER DEFAULT -2,
            PRIMARY KEY (proposal_id, user)
        );
        """
        )

        self.db.execute(
        """
        CREATE TABLE IF NOT EXISTS delegates (
          user INTEGER PRIMARY KEY,
          guild_id INTEGER NOT NULL,
          missed_votes INTEGER DEFAULT 0,
          active BOOL DEFAULT True,
          pop_power INT DEFAULT 0
        );
        """
        )

        self.db.execute(
        """
        CREATE TABLE IF NOT EXISTS guilds (
            guild INTEGER PRIMARY KEY,
            citizen_role INTEGER DEFAULT 0,
            server_id INTEGER DEFAULT 0,
            members INTEGER DEFAULT 0
        );
        """
        )

    def sanitize(self, stringy):
        return re.sub(r'[^a-zA-Z0-9 ]+', '', stringy)

    async def add_proposal(self, name : str, text : str, next_time : int):
        # Create a new proposal consisting of:
        # The Name of the Proposal
        # The Text of the Proposal, acquired from the initial forum post
        # The time discussion ends, 48 hours from the time the proposal is created
        # The time the voting ends, 36 hours after the discussion time ends
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
            INSERT INTO proposals
            (name, vote_text, next_time)
            VALUES ("{self.sanitize(name)}", "{self.sanitize(text)}", {next_time})
            RETURNING id;
            """)
            data = res.fetchone()
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()
        return data[0]

    async def add_vote(self, proposal_id: int, uid: int, vote: int):
        # Add a delegate vote, consisting of:
        # The proposal ID the delegate is voting on
        # The delegate's discord User ID
        # The delegate's vote (-2 for did not vote, -1 for Nay, 0 for Abstain, 1 for Yay)
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
            INSERT INTO votes
            (proposal_id, user, vote)
            VALUES ({proposal_id}, {uid}, {vote})
            ON CONFLICT(proposal_id, user) DO
            UPDATE
            SET vote = excluded.vote
            RETURNING *;
            """)
            data = res.fetchall()
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()
        return data

    async def get_votes(self, proposal_id : int):
        # Select all votes tied to a specific proposal ID
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
            SELECT * FROM votes
            WHERE proposal_id = {proposal_id};
            """)
            data = res.fetchall()
            cursor.close()
        finally:
            self.lock.release()
        return data

    async def get_proposal(self, proposal_id : int):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
            SELECT * FROM proposals
            WHERE id = {proposal_id};
            """)
            data = res.fetchall()
            cursor.close()
        finally:
            self.lock.release()
        return data[0]

    async def complete_vote(self, proposal_id : int):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
            UPDATE proposals
            SET completed = TRUE
            WHERE id = {proposal_id}
            RETURNING name, id;
            """)
            data = res.fetchall()
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()
        return data

    async def get_active_proposals(self):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
            SELECT name, id FROM proposals
            WHERE not completed;
            """)
            data = res.fetchall()
            cursor.close()
        finally:
            self.lock.release()
        return data

    async def get_timestamps(self):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
            SELECT id, next_time, discussed FROM proposals
            WHERE not completed
            ORDER BY next_time;
            """)
            data = res.fetchall()
            cursor.close()
        finally:
            self.lock.release()

        return data

    async def finish_discuss(self, id : int, time : int):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            cursor.execute(f"""
            UPDATE proposals
            SET discussed = TRUE, next_time = {time}, extend_votes = 0
            WHERE id = {id};
            """)
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()

    async def extend_vote(self, id : int):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
            UPDATE proposals
            SET extend_votes = extend_votes + 1
            WHERE id = {id}
            RETURNING id, extend_votes, next_time, discussed;
            """)
            data = res.fetchall()
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()

        return data[0]

    async def extend_time(self, id : int, time : int):
        await self.lock.acquire()

        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
            UPDATE proposals
            SET next_time = {time}
            WHERE id = {id};
            """)
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()

    async def get_delegates(self):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
            SELECT * FROM delegates
            WHERE active = True;
            """)
            data = res.fetchall()
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()

        return data

    async def get_all_delegates(self):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
            SELECT * FROM delegates;
            """)
            data = res.fetchall()
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()

        return data

    async def add_delegate(self, id, guild):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
            INSERT INTO delegates (user, guild_id)
            VALUES ({id}, {guild});
            """)
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()

    async def remove_delegate(self, id):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
            DELETE FROM delegates
            WHERE user = {id};
            """)
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()

    async def activate_delegate(self, id):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
            UPDATE delegates
            SET active = True, missed_votes = 0
            WHERE user = {id};
            """)
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()

    async def deactivate_delegate(self, id):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
            UPDATE delegates
            SET active = False
            WHERE user = {id};
            """)
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()

    async def set_power(self, id, power):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
            UPDATE delegates
            SET pop_power = {power}
            WHERE user = {id}
            RETURNING user, pop_power;
            """)
            data = res.fetchall()
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()
        return data

    async def miss_vote(self, id, missed):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
            UPDATE delegates
            SET missed_votes = {missed}
            WHERE user = {id}
            RETURNING user, missed_votes;
            """)
            data = res.fetchall()
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()
        return data

    async def add_guild(self, guild):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
            INSERT INTO guilds (guild)
            VALUES ({guild});
            """)
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()

    async def set_guild_server(self, guild, server_id):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
            UPDATE guilds
            SET server_id = {server_id}
            WHERE guild = {guild};
            """)
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()

    async def set_guild_citizen(self, guild, citizen_role):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
            UPDATE guilds
            SET citizen_role = {citizen_role}
            WHERE guild = {guild};
            """)
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()

    async def set_members(self, guild, members):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
            UPDATE guilds
            SET members = {members}
            WHERE guild = {guild};
            """)
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()

    async def get_guilds(self):
        await self.lock.acquire()
        try:
            cursor = self.db.cursor()
            res = cursor.execute(f"""
            SELECT * FROM guilds;
            """)
            data = res.fetchall()
            self.db.commit()
            cursor.close()
        finally:
            self.lock.release()
        return data