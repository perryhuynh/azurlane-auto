import argparse
from modules.combat import CombatModule
from modules.commission import CommissionModule
from modules.mission import MissionModule
from modules.retirement import RetirementModule
from util.adb import Adb
from util.config import Config
from util.logger import Logger
from util.stats import Stats


class ALAuto(object):
    modules = {
        'commissions': None,
        'combat': None,
        'missions': None,
        'retirement': None
    }

    def __init__(self, config):
        """Initializes the primary azurlane-auto instance with the passed in
        Config instance; creates the Stats instance and resets scheduled sleep
        timers.

        Args:
            config (Config): azurlane-auto Config instance
        """
        self.config = config
        self.stats = Stats(config)
        if self.config.commissions['enabled']:
            self.modules['commissions'] = CommissionModule(self.config, self.stats)
        if self.config.combat['enabled']:
            self.modules['combat'] = CombatModule(self.config, self.stats)
        if self.config.missions['enabled']:
            self.modules['missions'] = MissionModule(self.config, self.stats)
        if self.config.retirement['enabled']:
            self.modules['retirement'] = RetirementModule(self.config, self.stats)
        self.print_stats_check = True

    def run_combat_cycle(self):
        """Method to run the combat cycle.
        """
        if self.modules['combat']:
            if self.modules['combat'].combat_logic_wrapper():
                self.print_stats_check = True

    def run_commission_cycle(self):
        """Method to run the expedition cycle.
        """
        if self.modules['commissions']:
            if self.modules['commissions'].commissions_logic_wrapper():
                self.print_stats_check = True

    def run_mission_cycle(self):
        """Method to run the mission cycle
        """
        if self.modules['missions']:
            if self.modules['missions'].mission_logic_wrapper():
                self.print_stats_check = True

    def run_retirement_cycle(self):
        """Method to run the retirement cycle
        """
        if self.modules['retirement']:
            if self.modules['retirement'].retirement_logic_wrapper():
                self.print_stats_check = True

    def print_cycle_stats(self):
        """Method to print the cycle stats"
        """
        if self.print_stats_check:
            self.stats.print_stats()
        self.print_stats_check = False

    def run_test(self):
        pass
        # coords = Utils.find_all('combat_enemy_fleet', 0.88)
        # Logger.log_msg(coords)
        # exit()


# check run-time args
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config',
                    metavar=('CONFIG_FILE'),
                    help='Use the specified configuration file instead ' +
                         'of the default config.ini')
parser.add_argument('-d', '--debug', nargs=2,
                    metavar=('IMAGE_FILE', 'SIMILARITY'),
                    help='Finds the specified image on the screen at ' +
                         'the specified similarity')
parser.add_argument('--copyright',)
args = parser.parse_args()
# check args, and if none provided, load default config
if args and args.config:
    config = Config(args.config)
else:
    config = Config('config.ini')

script = ALAuto(config)
Adb.init()

while True:
    script.run_test()
    script.run_commission_cycle()
    script.run_combat_cycle()
    script.run_retirement_cycle()
    script.run_mission_cycle()
    script.print_cycle_stats()
