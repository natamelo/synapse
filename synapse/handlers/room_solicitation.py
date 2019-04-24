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

logger = logging.getLogger(__name__)


class RoomSolicitationHandler(BaseHandler):

    def __init__(self, hs):
        super(RoomSolicitationHandler, self).__init__(hs)

        self.hs = hs

        self.store = hs.get_datastore()

    def create_solicitation(self, event_id, state):
        self.store.create_solicitation(event_id=event_id, state=state)

    def update_solicitation(self, event_id, state):
        self.store.update_solicitation(event_id=event_id, state=state)
