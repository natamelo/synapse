# -*- coding: utf-8 -*-
# Copyright 2016 OpenMarket Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from twisted.internet import defer
from synapse.api.constants import ActionTypes, EquipmentTypes, SubstationCode

from synapse.events.utils import (
    format_event_for_client_v2_without_room_id,
    serialize_event,
)
from synapse.http.servlet import RestServlet, parse_integer, parse_string, parse_json_object_from_request

from ._base import client_v2_patterns

logger = logging.getLogger(__name__)


class InterventionsServlet(RestServlet):
    PATTERNS = client_v2_patterns("/interventions$")

    def __init__(self, hs):
        super(InterventionsServlet, self).__init__()
        self.store = hs.get_datastore()
        self.auth = hs.get_auth()
        self.clock = hs.get_clock()

    @defer.inlineCallbacks
    def on_GET(self, request):
        requester = yield self.auth.get_user_by_req(request)
        user_id = requester.user.to_string()

        limit = parse_integer(request, "limit", default=50)
        room_id = parse_string(request, "room_id", required=False)

        limit = min(limit, 500)

        interventions = yield self.store.get_interventions(room_id=room_id, limit=limit)

        event_id_list = [intervention["event_id"] for intervention in interventions]

        notif_events = yield self.store.get_events(event_id_list)

        returned_interventions = []

        next_token = None

        for intervention in interventions:
            event = serialize_event(
                notif_events[intervention["event_id"]],
                self.clock.time_msec(),
                event_format=format_event_for_client_v2_without_room_id,
            )
            event['content']["status"] = intervention["status"]
            returned_pa = {
                "room_id": intervention["room_id"],
                "profile_tag": intervention["name"],
                "actions": [],
                "ts": intervention["received_ts"],
                "event": event,
            }

            # if pa["room_id"] not in receipts_by_room:
            intervention["read"] = False
            # else:
            #    receipt = receipts_by_room[pa["room_id"]]

            #    returned_pa["read"] = (
            #        receipt["topological_ordering"], receipt["stream_ordering"]
            #    ) >= (
            #        pa["topological_ordering"], pa["stream_ordering"]
            #    )
            returned_interventions.append(returned_pa)
            next_token = str(intervention["stream_ordering"])

        defer.returnValue((200, {
            "notifications": returned_interventions,
            "next_token": next_token,
        }))




def register_servlets(hs, http_server):
    InterventionsServlet(hs).register(http_server)
