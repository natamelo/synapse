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


class SolicitationsServlet(RestServlet):
    PATTERNS = client_v2_patterns("/solicitations$")

    def __init__(self, hs):
        super(SolicitationsServlet, self).__init__()
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

        solicitations = yield self.store.get_solicitations(room_id=room_id, limit=limit)

        event_id_list = [solicitation["event_id"] for solicitation in solicitations]

        notif_events = yield self.store.get_events(event_id_list)

        returned_solicitations = []

        next_token = None

        for solicitation in solicitations:
            event = serialize_event(
                notif_events[solicitation["event_id"]],
                self.clock.time_msec(),
                event_format=format_event_for_client_v2_without_room_id,
            )
            event['content']["status"] = solicitation["status"]
            returned_pa = {
                "room_id": solicitation["room_id"],
                "profile_tag": solicitation["name"],
                "actions": [],
                "ts": solicitation["received_ts"],
                "event": event,
            }

            # if pa["room_id"] not in receipts_by_room:
            solicitation["read"] = False
            # else:
            #    receipt = receipts_by_room[pa["room_id"]]

            #    returned_pa["read"] = (
            #        receipt["topological_ordering"], receipt["stream_ordering"]
            #    ) >= (
            #        pa["topological_ordering"], pa["stream_ordering"]
            #    )
            returned_solicitations.append(returned_pa)
            next_token = str(solicitation["stream_ordering"])

        defer.returnValue((200, {
            "notifications": returned_solicitations,
            "next_token": next_token,
        }))


# TODO: Needs unit testing
class SolicitationSageCallRestServlet(RestServlet):
    PATTERNS = client_v2_patterns("/solicitations/sage_call$")

    def __init__(self, hs):
        super(SolicitationSageCallRestServlet, self).__init__()
        self.event_creation_handler = hs.get_event_creation_handler()
        self.room_solicitation_handler = hs.get_room_solicitation_handler()
        self.store = hs.get_datastore()

    @defer.inlineCallbacks
    def on_POST(self, request):
        # requester = yield self.auth.get_user_by_req(request, allow_guest=True)
        content = parse_json_object_from_request(request)

        sender_user_id = content['sender_user_id']
        action = content['action']
        substation_code = content['substation_code']
        equipment_type = content['equipment_type']
        equipment_code = content['equipment_code']

        if action not in ActionTypes.ALL_ACTION_TYPES:
            defer.returnValue((400, {
                "error": "Invalid Action Type"
            }))

        if equipment_type not in EquipmentTypes.ALL_EQUIPMENT_TYPES:
            defer.returnValue((400, {
                "error": "Invalid Equipment Type"
            }))

        if substation_code not in SubstationCode.ALL_SUBSTATION_CODES:
            defer.returnValue((400, {
                "error": "Invalid Substation Code"
            }))

        yield self.room_solicitation_handler.create_sage_call_solicitation(
            sender_user_id=sender_user_id,
            action=action,
            substation_code=substation_code,
            equipment_type=equipment_type,
            equipment_code=equipment_code,
        )

        defer.returnValue((201, {
            "Message": "Sage Call solicitation made by " + sender_user_id
        }))

    def on_GET(self, request):
        return (200, "Not implemented")


def register_servlets(hs, http_server):
    SolicitationsServlet(hs).register(http_server)
    SolicitationSageCallRestServlet(hs).register(http_server)