from typing import MutableMapping, Callable, Optional, Mapping, Any  # noqa  # pylint: disable=unused-import

# noinspection PyProtectedMember
from c2cwsgiutils.broadcast import utils, interface


class LocalBroadcaster(interface.BaseBroadcaster):
    """
    Fake implementation of broadcasting messages (will just answer locally)
    """
    def __init__(self) -> None:
        self._subscribers = {}  # type: MutableMapping[str, Callable]

    def subscribe(self, channel: str, callback: Callable) -> None:
        self._subscribers[channel] = callback

    def unsubscribe(self, channel: str) -> None:
        del self._subscribers[channel]

    def broadcast(self, channel: str, params: Mapping[str, Any], expect_answers: bool,
                  timeout: float) -> Optional[list]:
        subscriber = self._subscribers.get(channel, None)
        answers = [utils.add_host_info(subscriber(**params))] if subscriber is not None else []
        return answers if expect_answers else None
