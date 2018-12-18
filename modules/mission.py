from util.utils import Utils


class MissionModule(object):
    def __init__(self, config, stats):
        """Initializes the Expedition module.
        Args:
            config (Config): kcauto Config instance
        """
        self.enabled = True
        self.config = config
        self.stats = stats

    def mission_logic_wrapper(self):
        if (Utils.find_and_touch('mission_complete')):
            self.stats.increment_missions_done()
            Utils.script_sleep(0.5)
            while Utils.find_and_touch('collect_mission'):
                Utils.touch_randomly()
            Utils.touch_randomly(Region(12, 8, 45, 30))
            return True
        return False
