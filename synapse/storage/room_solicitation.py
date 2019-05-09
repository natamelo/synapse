import logging

from synapse.storage._base import SQLBaseStore
from synapse.api.errors import StoreError
from twisted.internet import defer

logger = logging.getLogger(__name__)


class RoomSolicitationStore(SQLBaseStore):

    def create_solicitation(self, event_id, state):
        try:
            self._simple_insert(
                table="solicitations",
                values={
                    "id": self._solicitation_list_id_gen.get_next(),
                    "event_id": event_id,
                    "status": state,
                }
            )
        except Exception as e:
            logger.warning("create_solicitation with event_id=%s failed: %s", event_id, e)
            raise StoreError(500, "Problem creating solicitation.")

    def update_solicitation(self, event_id, state):
        try:
            self._simple_update(
                table="solicitations",
                keyvalues={"event_id": event_id},
                updatevalues={"status": state},
                desc="update_solicitation",
            )
        except Exception as e:
            logger.warning("update_solicitation with event_id=%s failed: %s", event_id, e)
            raise StoreError(500, "Problem updating solicitation.")

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
                " WHERE solicitation.event_id = event.event_id and room_name.room_id = event.room_id"
                " and event.room_id = ?"
                " ORDER BY event.stream_ordering DESC"
                " LIMIT ?"
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
