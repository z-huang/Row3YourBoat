from influxdb import InfluxDB
from db import Database
from addons import (AuthManager, TrafficLogger,
                    SlackingPolicyEnforcer, RedirectManager)

influxdb = InfluxDB()
db = Database()
auth_manager = AuthManager(db)

addons = [
    auth_manager,
    RedirectManager(),
    TrafficLogger(auth_manager, influxdb),
    SlackingPolicyEnforcer(auth_manager, db, influxdb),
]
