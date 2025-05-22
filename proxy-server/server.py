import asyncio
from influxdb import InfluxDB
from db import Database
from addons import (AuthManager, TrafficLogger,
                    SlackingPolicyEnforcer, RedirectManager)

influxdb = InfluxDB()
db = Database()
auth_manager = AuthManager(db)

asyncio.get_event_loop().create_task(influxdb.init())


async def init():
    await db.connect()

asyncio.create_task(init())

addons = [
    auth_manager,
    RedirectManager(),
    TrafficLogger(auth_manager, influxdb),
    SlackingPolicyEnforcer(auth_manager, db, influxdb),
]
