from util.logger import Logger
from util.utils import Utils, Region


class RetirementModule(object):

    config = None
    stats = None

    def __init__(self, config, stats):
        """Initializes the Retirement module.

        Args:
            config (Config): ALAuto Config instance
            stats (Stats): ALAuto stats instance
        """
        self.config = config
        self.stats = stats

    def retirement_logic_wrapper(self):
        """Method that fires off the necessary child methods that encapsulates
        the entire action filtering and retiring ships
        """
        if self.need_to_retire:
            while not (Utils.find_and_touch('home_menu_build')):
                Utils.touch_randomly(Region(12, 8, 45, 30))
            Utils.wait_and_touch('build_menu_retire', 2)
            Utils.script_sleep(1)
            self.set_filters()
            Utils.script_sleep(1)
            done = False
            while not done:
                self.select_ships()
                if (Utils.exists('retire_none_selected')):
                    done = True
                # Click confirm button
                else:
                    self.retire_ships()
            Utils.touch_randomly(Region(12, 8, 45, 30))

    def select_ships(self):
        """Selects up to 10 ships for retirement
        """
        Logger.log_msg('Selecting ships for retirement.')
        x, y = 90, 180
        for i in range(0, 7):
            Utils.touch_randomly(Region(x + (i * 170), y, 30, 15))
        y = 412
        for i in range(0, 3):
            Utils.touch_randomly(Region(x + (i * 170), y, 30, 15))

    def retire_ships(self):
        """Clicks through the dialogs for retiring ships
        """
        Utils.find_and_touch('retire_confirm', 0.7)
        Utils.find_and_touch('retire_confirm', 0.7)
        Utils.find_and_touch('combat_items_received', 0.7)
        Utils.find_and_touch('retire_confirm', 0.7)
        Utils.find_and_touch('retire_disassemble', 0.7)
        Utils.find_and_touch('combat_items_received', 0.7)

    def set_filters(self):
        """Filters the ship list to only show rare and commmon ships
        """
        Utils.touch_randomly(Region(1090, 15, 150, 40))
        Utils.wait_for_exist('ship_filter_confirm', 1)
        Utils.touch_randomly(Region(300, 570, 100, 20))
        Utils.find_and_touch('ship_filter_rarity_common')
        Utils.find_and_touch('ship_filter_rarity_rare')
        Utils.find_and_touch('ship_filter_confirm')

    def need_to_retire(self):
        """Checks whether the script needs to retire ships

        Returns:
            bool: True if the script needs to retire ships
        """
        return self.stats.combat_done % self.config.combat['retire_cycle'] == 0
