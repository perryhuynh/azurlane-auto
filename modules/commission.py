from util.utils import Utils


class CommissionModule(object):

    def __init__(self, config, stats):
        """Initializes the Expedition module.

        Args:
            config (Config): ALAuto Config instance
            stats (Stats): ALAuto stats instance
        """
        self.enabled = True
        self.config = config
        self.stats = stats

    def commission_logic_wrapper(self):
        if (Utils.find_and_touch('notification_commission_complete')):
            Logger.log_msg('Completed commissions found.' +
                           'Opening commission panel.')
            while Utils.find_and_touch('commission_complete'):
                Logger.log_msg('Completed commission found.' +
                               'Redeeming reward.')
                Utils.touch_randomly()
                Utils.script_sleep(1)
                Utils.touch_randomly()
                Utils.script_sleep(1)
            if Utils.find_and_touch('commission_go'):
                # Ensure the list is scrolled up to the top before
                # checking in progress commissions
                Utils.swipe(190, 190, 75, 650)
                in_progress = len(
                    Utils.find_all('commission_in_action', 0.87)[0])
                while in_progress < 4:
                    Utils.swipe(190, 190, 650, 75)
                    if Utils.find_and_touch('commission_select'):
                        Utils.find_and_touch('commission_advice')
                        Utils.find_and_touch('commission_start')
                        Utils.touch_randomly(Region(120, 60, 140, 650))
                        in_progress += 1
                    else:
                        break
            Utils.find_and_touch('navigate_back_home')
            Utils.touch_randomly(Region(530, 60, 740, 590))
        return False
