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
from twisted.internet import defer

logger = logging.getLogger(__name__)


class RoomInterventionHandler(BaseHandler):

    def __init__(self, hs):
        super(RoomInterventionHandler, self).__init__(hs)
        self.hs = hs
        self.store = hs.get_datastore()
        self.state = hs.get_state_handler()
        self.event_creation_handler = hs.get_event_creation_handler()

    @defer.inlineCallbacks
    def create_intervention_and_send_event(self, requester, event_dict, state):
        event, context = yield self.event_creation_handler.create_and_no_send_nonmember_event(
            requester,
            event_dict
        )

        self.store.create_intervention(event_id=event.event_id, state=state)

        yield self.event_creation_handler.send_nonmember_event(
            requester,
            event,
            context,
            ratelimit=True,
        )
        defer.returnValue(event)

    def update_intervention(self, room_id, state):
        self.store.update_intervention(room_id=room_id, state=state)



