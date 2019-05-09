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

from synapse.api.errors import AuthError, NotFoundError

from ._base import BaseHandler

from synapse.events.utils import (
    format_event_for_client_v2_without_room_id,
    serialize_event,
)

from twisted.internet import defer

from synapse.events.builder import event_type_from_format_version, create_local_event_from_event_dict
from synapse.api.constants import EventFormatVersions

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

    def update_solicitation(self, requester, event_id, state):
        self.store.update_solicitation(event_id=event_id, state=state)