from unittest import mock


def make_patch_by_path(path):
    def patch(new):
        return mock.patch(path, new=new)

    return patch


patch_db_manager = make_patch_by_path("bot.db_manager")
patch_cmd_start = make_patch_by_path("bot.cmd_start")
patch_learn_callback = make_patch_by_path("bot.Learn.learn_callback")
patch_saved_user_msg = make_patch_by_path("bot.saved_user_msg")
