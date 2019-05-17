import logging

from synapse.storage._base import SQLBaseStore
from synapse.api.errors import StoreError
from twisted.internet import defer

import collections

logger = logging.getLogger(__name__)

RoomID = collections.namedtuple(
    "RoomID", ("room_id")
)


class RoomInterventionStore(SQLBaseStore):

    def create_intervention(self, event_id, state):
        try:
            self._simple_insert(
                table="interventions",
                values={
                    "id": self._intervention_list_id_gen.get_next(),
                    "event_id": event_id,
                    "status": state,
                }
            )
        except Exception as e:
            logger.warning("create_solicitation with event_id=%s failed: %s", event_id, e)
            raise StoreError(500, "Problem creating solicitation.")

    @defer.inlineCallbacks
    def update_intervention(self, room_id, state):
        intervention_id = yield self.get_intervention_id_by_room_id(room_id)
        try:
            self._simple_update(
                table="interventions",
                keyvalues={"id": intervention_id},
                updatevalues={"status": state},
                desc="update_intervention",
            )
        except Exception as e:
            logger.warning("update_solicitation with event_id=%s failed: %s", event_id, e)
            raise StoreError(500, "Problem updating solicitation.")

    @defer.inlineCallbacks
    def get_room_id_by_name(self, name):
        result = yield self._simple_select_one(table="room_names",
                                keyvalues={"name": name},
                                retcols=["room_id"],
                                desc="get_room_id_by_name")
        if result:
            defer.returnValue(result['room_id'])
        else:
            defer.returnValue(None)

    @defer.inlineCallbacks
    def get_room_id_by_event_id(self, event_id):
        result = yield self._simple_select_one(table="events",
                                               keyvalues={"event_id": event_id},
                                               retcols=["room_id"],
                                               desc="get_room_id_by_event_id")
        if result:
            defer.returnValue(result['room_id'])
        else:
            defer.returnValue(None)

    @defer.inlineCallbacks
    def get_intervention_id_by_room_id(self, event_id):
        def f(txn):
            args = [event_id]

            sql = (
                "SELECT intervention.id"
                " FROM interventions intervention, events intervention_event"
                " WHERE intervention_event.room_id = ?"
                " and intervention_event.event_id = intervention.event_id"
            )
            txn.execute(sql, args)
            return self.cursor_to_dict(txn)

        interventions = yield self.runInteraction(
            "get_intervention_id_by_event_id", f
        )

        intervention = None
        if interventions:
            intervention = interventions[0]

        defer.returnValue(intervention)

    @defer.inlineCallbacks
    def get_solicitation(self, event_id):
        def f(txn):
            args = [event_id]

            sql = (
                "SELECT solicitation.id, solicitation.event_id, solicitation.status, event.room_id,"
                " event.stream_ordering, event.topological_ordering,"
                " event.received_ts, room_name.name"
                " FROM solicitations solicitation, events event, room_names room_name"
                " WHERE solicitation.event_id = event.event_id and room_name.room_id = event.room_id"
                " and event.event_id = ?"
            )
            txn.execute(sql, args)
            return self.cursor_to_dict(txn)

        solicitations = yield self.runInteraction(
            "get_solicitation", f
        )

        solicitation = None
        if solicitations:
            solicitation = solicitations[0]

        defer.returnValue(solicitation)

    @defer.inlineCallbacks
    def get_solicitations(self, room_id, user_id=None, before=None,
                            limit=50, only_highlight=False):
        def f(txn):
            before_clause = ""
            #if before:
            #    before_clause = "AND event.stream_ordering < ?"
            #    args = [user_id, before, limit]
            #else:
            args = [room_id, limit]
            args = [limit]

            #if only_highlight:
            #    if len(before_clause) > 0:
            #        before_clause += " "
            #    before_clause += "AND epa.highlight = 1"

            # NB. This assumes event_ids are globally unique since
            # it makes the query easier to index
            sql = (
                "SELECT solicitation.event_id, solicitation.status, event.room_id,"
                " event.stream_ordering, event.topological_ordering,"
                " event.received_ts, room_name.name"
                " FROM solicitations solicitation, events event, room_names room_name"
                " WHERE solicitation.event_id = event.event_id"
                " ORDER BY event.stream_ordering DESC"
                " LIMIT ?"
                ##and room_name.room_id = event.room_id
                ##" and event.room_id = ?"
                #% (before_clause,)
            )
            txn.execute(sql, args)
            return self.cursor_to_dict(txn)

        solicitations = yield self.runInteraction(
            "get_solicitations", f
        )
        #for pa in push_actions:
        #    pa["actions"] = _deserialize_action(pa["actions"], pa["highlight"])
        defer.returnValue(solicitations)

    def create_sage_call_solicitation(self, sender_user_id, action, substation_code,
                                      equipment_type, equipment_code, event_id):
        try:
            self._simple_insert(
                table="solicitations",
                values={
                    "id": self._solicitation_list_id_gen.get_next(),
                    "status": "Solicitada",
                    "sender_user_id": sender_user_id,
                    "action": action,
                    "substation_code": substation_code,
                    "equipment_type": equipment_type,
                    "equipment_code": equipment_code,
                    "event_id": event_id
                }
            )
        except Exception as e:
            logger.warning("create_sage_call_solicitation for sender_user=%s failed: %s", sender_user_id, e)
            raise StoreError(500, "Problem creating solicitation.")

