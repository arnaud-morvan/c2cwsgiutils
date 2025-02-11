import pyramid.config
from typing import cast

from c2cwsgiutils import _utils, stats


def init(config: pyramid.config.Configurator) -> None:
    config.add_route("c2c_read_stats_json", _utils.get_base_path(config) + r"/stats.json",
                     request_method="GET")
    memory_backend = cast(stats.MemoryBackend, stats.BACKENDS['memory'])
    config.add_view(memory_backend.get_stats, route_name="c2c_read_stats_json",
                    renderer="fast_json", http_cache=0)
