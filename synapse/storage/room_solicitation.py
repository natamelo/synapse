import logging

from synapse.storage._base import SQLBaseStore
from synapse.api.errors import StoreError

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
