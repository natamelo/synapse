# -*- coding: utf-8 -*-
# Copyright 2016 OpenMarket Ltd
# Copyright 2018 New Vector Ltd
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

from ._base import BaseHandler
from synapse.types import create_requester
from twisted.internet import defer
import simplejson as json

logger = logging.getLogger(__name__)

class RoomSolicitationHandler(BaseHandler):

    def __init__(self, hs):
        super(RoomSolicitationHandler, self).__init__(hs)
        self.hs = hs
        self.store = hs.get_datastore()
        self.state = hs.get_state_handler()
        self.event_creation_handler = hs.get_event_creation_handler()
        #self._message_handler = hs.get_message_handler()

    def create_solicitation(self, event_id, state):
        self.store.create_solicitation(event_id=event_id, state=state)

    def update_solicitation(self, event_id, state):
        self.store.update_solicitation(event_id=event_id, state=state)

    @defer.inlineCallbacks
    def create_sage_call_solicitation(self, sender_user_id, action, substation_code,
                                      equipment_type, equipment_code):
        self.store.create_sage_call_solicitation(sender_user_id=sender_user_id, action=action,
                                                 substation_code=substation_code, equipment_type=equipment_type,
                                                 equipment_code=equipment_code)

        requester = create_requester(sender_user_id)

        room_id = yield self.store.get_room_id_by_name(substation_code)

        event_dict = {
            "type": "m.room.message",
            "content": {
                'msgtype': 'm.text',
                'body': "Solicitação: " + str(action) + " " + str(equipment_type) + " " + equipment_code,
                'status': 'ABERTO'
            },
            "room_id": room_id,
            "sender": requester.user.to_string(),
        }

        yield self.event_creation_handler.create_and_send_nonmember_event(
            requester,
            event_dict
        )
