from unittest import mock
from unittest.mock import MagicMock


def make_patch_by_path(path):
    def patch(new):
        return mock.patch(path, new=new)

    return patch


patch_db_manager = make_patch_by_path("db.db_manager")
patch_db_manager_get_cards = make_patch_by_path("handlers.cmd_get_cards.db_manager")
patch_db_manager_add = make_patch_by_path("handlers.scenario_add.db_manager")
patch_db_manager_learn = make_patch_by_path("handlers.scenario_learn.db_manager")
patch_redis = make_patch_by_path("handlers._redis_funcs.r")
patch_cmd_start = make_patch_by_path("handlers.cmd_start")
patch_learn_callback = make_patch_by_path("bot.Learn.learn_callback")
