import asyncio
from addons import (AuthManager, InfluxDBManager,
                    TrafficLogger, SlackingPolicyEnforcer)

auth_manager = AuthManager()
influx_manager = InfluxDBManager()

asyncio.get_event_loop().create_task(influx_manager.init())

addons = [
    auth_manager,
    TrafficLogger(auth_manager, influx_manager),
    SlackingPolicyEnforcer(auth_manager, influx_manager),
]
