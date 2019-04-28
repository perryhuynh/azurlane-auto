from datetime import datetime, timedelta
from threading import Thread
from util.logger import Logger
from util.utils import Region, Utils
from scipy import spatial

class CombatModule(object):

    def __init__(self, config, stats):
        """Initializes the Combat module.

        Args:
            config (Config): ALAuto Config instance.
            stats (Stats): ALAuto Stats instance.
        """
        self.enabled = True
        self.config = config
        self.stats = stats
        self.morale = {}
        self.next_combat_time = datetime.now()
        self.resume_previous_sortie = False
        self.kills_needed = 0
        self.hard_mode = self.config.combat['hard_mode']
        self.sortie_map = self.config.combat['map']
        self.event_map = self.sortie_map.split('-')[0] == 'E'
        self.need_to_refocus = True
        self.avoided_ambush = True
        self.region = {
            'nav_back': Region(12, 8, 45, 30),
            'home_menu_attack': Region(1000, 365, 180, 60),
            'event_map': Region(1145, 140, 70, 40),
            'map_go_1': Region(875, 465, 115, 35),
            'map_go_2': Region(980, 600, 180, 55),
            'autobattle': Region(40, 30, 190, 40),
            'battle_start': Region(1000, 610, 125, 50),
            'switch_fleet': Region(850, 650, 180, 40),
            'unable_submarine': Region(1100, 500, 50, 30)
        }

    def combat_logic_wrapper(self):
        """Method that fires off the necessary child methods that encapsulates
        the entire action of sortieing combat fleets and resolving combat.

        Returns:
            bool: True if the combat cycle was complete
        """
        if self.check_need_to_sortie():
            Logger.log_msg('Navigating to map.')
            Utils.touch_randomly(self.region['home_menu_attack'])
            if not self.resume_previous_sortie:
                self.kills_needed = self.config.combat['kills_needed']
                if self.event_map:
                    Utils.touch_randomly(self.region['event_map'])
                if self.hard_mode:
                    Utils.update_screen()
                    Utils.find_and_touch('map_menu_hard')
                Utils.script_sleep(1)
                Utils.update_screen()
                Utils.find_and_touch('map_{}'.format(self.sortie_map), 0.85)
                Utils.touch_randomly(self.region['map_go_1'])
                Utils.touch_randomly(self.region['unable_submarine'])
                Utils.touch_randomly(self.region['map_go_2'])
                if self.config.combat['alt_clear_fleet']:
                    Logger.log_msg('Alternate clearing fleet enabled, ' +
                                   'switching to 2nd fleet to clear trash')
                    self.switch_fleet()
                    self.need_to_refocus = False
                Utils.script_sleep(2)
            # Trash
            if self.clear_trash():
                # Boss
                if self.config.combat['boss_fleet']:
                    Logger.log_msg('Switching to 2nd fleet to kill boss')
                    self.switch_fleet()
                self.clear_boss()
                self.stats.increment_combat_done()
                self.next_combat_time = datetime.now()
                Logger.log_success('Sortie complete. Navigating back home.')
                Utils.update_screen()
                while not (Utils.exists('home_menu_build')):
                    Utils.touch_randomly(self.region['nav_back'])
                    Utils.update_screen()
                self.set_next_combat_time({'seconds': 10})
            return True
        return False

    def get_enemies(self,blacklist=[]):
        l = []
        sim = 0.95
        while l == [] and sim >= 0.6:
            l1 = filter(lambda x:x[0] > 120, map(lambda x:[x[0], x[1] - 10], Utils.find_all('combat_enemy_fleet_1', sim)))
            l1 = [x for x in l1]
            l2 = filter(lambda x:x[0] > 120, map(lambda x:[x[0] + 20, x[1] + 20], Utils.find_all('combat_enemy_fleet_2', sim)))
            l2 = [x for x in l2]
            l3 = filter(lambda x:x[0] > 120, map(lambda x:[x[0] + 20, x[1] + 20], Utils.find_all('combat_enemy_fleet_3', sim)))
            l3 = [x for x in l3]
            l4 = filter(lambda x:x[0] > 120, map(lambda x:[x[0] + 20, x[1] + 20], Utils.find_all('combat_enemy_fleet_4', sim)))
            l4 = [x for x in l4]
            l = l1 + l2 + l3 + l4
            if l:
                a = spatial.KDTree(l)
                for coord in blacklist:
                    if l:
                        m = a.query(coord)
                        if m[0] <= 15:
                            del l[m[1]]
                            if l:
                                a = spatial.KDTree(l)
            sim -= 0.05
        if l == []:
            return []
        c = [l[0]]
        a = spatial.KDTree(c)
        del l[0]
        for x in l:
            if a.query(x)[0] >= 15:
                c.append(x)
                a=spatial.KDTree(c)
        return c

    def check_need_to_sortie(self):
        """Method to check whether the combat fleets need to sortie based on
        the stored next combat time.

        Returns:
            bool: True if the combat fleets need to sortie, False otherwise
        """
        if not self.enabled:
            return False
        if self.next_combat_time < datetime.now():
            return True
        return False

    def set_next_combat_time(self, delta={}):
        """Method to set the next combat time based on the provided hours,
        minutes, and seconds delta.

        Args:
            delta (dict, optional): Dict containing the hours, minutes, and
                seconds delta.
        """
        self.next_combat_time = datetime.now() + timedelta(
            hours=delta['hours'] if 'hours' in delta else 0,
            minutes=delta['minutes'] if 'minutes' in delta else 0,
            seconds=delta['seconds'] if 'seconds' in delta else 0)

    def get_fleet_location(self):
        """Method to get the fleet's current location. Note it uses the green
        fleet marker to find the location but returns around the area of the
        feet of the flagship

        Returns:
            array: An array containing the x and y coordinates of the fleet's
            current location.
        """
        coords = Utils.scroll_find('combat_fleet_marker',250,175,0.9)
        return [coords.x + 10, coords.y + 175]

    def get_closest_enemy(self, blacklist=[]):
        """Method to get the enemy closest to the fleet's current location. Note
        this will not always be the enemy that is actually closest due to the
        asset used to find enemies and when enemies are obstructed by terrain
        or the second fleet

        Args:
            blacklist(array, optional): Defaults to []. An array of
            coordinates to exclude when searching for the closest enemy

        Returns:
            array: An array containing the x and y coordinates of the closest
            enemy to the fleet's current location
        """
        x_dist = 125
        y_dist = 175
        swipes = [['n', 1.0], ['e', 1.0], ['s', 1.5], ['w', 1.5]]
        closest = None
        while closest is None:
            if self.need_to_refocus and self.config.combat['two_fleet']:
                self.refocus_fleet()
                Utils.script_sleep(2)
            current_location = self.get_fleet_location()
            for swipe in swipes:
                enemies = self.get_enemies(blacklist)                    
                if enemies:
                    Logger.log_msg('Current location is: {}'
                                   .format(current_location))
                    Logger.log_msg('Enemies found at: {}'.format(enemies))
                    closest = enemies[Utils.find_closest(
                                      enemies, current_location)[1]]
                    Logger.log_msg('Closest enemy is at {}'.format(closest))
                    return [closest[0], closest[1]]
                else:
                    direction, multiplier = swipe[0], swipe[1]
                    if direction == 'n':
                        current_location[1] = current_location[1] + (2 * y_dist * multiplier)
                        Utils.swipe(640, 360 - y_dist * multiplier, 640, 360 + y_dist * multiplier, 250)
                        y_dist *= 1.25
                    elif direction == 's':
                        current_location[1] = current_location[1] - (2 * y_dist * multiplier)
                        Utils.swipe(640, 360 + y_dist * multiplier, 640, 360 - y_dist * multiplier, 250)
                        y_dist *= 1.25
                    elif direction == 'e':
                        current_location[0] = current_location[0] + (2 * x_dist * multiplier)
                        Utils.swipe(640 + x_dist * multiplier, 360, 640 - x_dist * multiplier, 360, 250)
                        x_dist *= 1.25
                    elif direction == 'w':
                        current_location[0] = current_location[0] - (2 * x_dist * multiplier)
                        Utils.swipe(640 - x_dist * multiplier, 360, 640 + x_dist * multiplier, 360, 250)
                        x_dist *= 1.25
                self.need_to_refocus = True
        return None

    def conduct_prebattle_check(self):
        """Method to check morale and check if auto-battle is enabled before a
        sortie. Enables autobattle if not already enabled.

        Returns:
            bool: True if it is ok to proceed with the battle
        """
        ok = True
        Utils.update_screen()
        fleet_morale = self.check_morale()
        if fleet_morale['sad']:
            self.set_next_combat_time({'hours': 2})
            ok = False
        elif fleet_morale['neutral']:
            self.set_next_combat_time({'hours': 1})
            ok = False
        return ok

    def conduct_battle(self):
        """Method to start the battle and click through the rewards once the
        battle is complete.
        """
        Logger.log_msg('Starting battle')
        Utils.find_and_touch('combat_battle_start')
        Utils.update_screen()
        while (not Utils.exists('in_battle', 0.85)):
            if Utils.exists('not_autobattle', 0.85):
                Utils.touch_randomly(self.region['autobattle'])
                Utils.script_sleep(1)
                Utils.find_and_touch('i_know', 0.8)
            Utils.update_screen()
        while (Utils.exists('in_battle', 0.85)):
            Utils.update_screen()
        while not Utils.find_and_touch('combat_battle_confirm', 0.85):
            Utils.touch_randomly(Region(0,0,300,300))
            Utils.update_screen()
        Logger.log_msg('Battle complete.')
        Utils.script_sleep(1.5)
        Utils.update_screen()
        if Utils.find_and_touch('confirm'):
            Logger.log_msg('Dismissing urgent notification.')
            Utils.update_screen()
        return True

    def clear_trash(self):
        """Finds trash mobs closest to the current fleet location and battles
        them until the boss spawns
        """
        while self.kills_needed > 0:
            blacklist = []
            tries = 0
            if self.resume_previous_sortie:
                self.resume_previous_sortie = False
                Utils.update_screen()
                Utils.find_and_touch('combat_attack')
            else:
                self.avoided_ambush = True
            while not Utils.exists('combat_battle_start'):
                Utils.update_screen()
                if Utils.find_and_touch('combat_evade'):
                    Utils.script_sleep(2)
                    Utils.update_screen()
                    if Utils.exists('combat_battle_start'):
                        self.avoided_ambush = False
                    else:
                        Logger.log_msg('Successfully avoided ambush.')
                elif Utils.find_and_touch('combat_items_received'):
                    pass
                else:
                    enemy_coord = self.get_closest_enemy()
                    if tries > 2:
                        enemy_coord = [enemy_coord[0], enemy_coord[1]]
                        blacklist.append(enemy_coord)
                        enemy_coord = self.get_closest_enemy(blacklist)
                    Logger.log_msg('Navigating to enemy fleet at {}'
                                   .format(enemy_coord))
                    Utils.touch(enemy_coord)
                    tries += 1
                    Utils.script_sleep(3)
                    Utils.update_screen()
            if self.conduct_prebattle_check():
                self.conduct_battle()
                self.need_to_refocus = True
            if self.avoided_ambush:
                self.kills_needed -= 1
            Logger.log_msg('Kills left for boss to spawn: {}'
                           .format(self.kills_needed))
        return True

    def clear_boss(self):
        """Finds the boss and battles it
        """
        while not Utils.exists('combat_battle_start'):
            boss = None
            similarity = 0.8
            while boss is None:
                Utils.update_screen()
                boss = Utils.scroll_find(
                    'combat_enemy_boss', 250, 175, similarity)
                similarity -= 0.015
            Logger.log_msg('Boss found at: {}'.format([boss.x, boss.y]))
            # Click slightly above boss to be able to click on it in case
            # the boss is obstructed by another fleet or enemy
            boss_coords = [boss.x + 25, boss.y + 5]
            Utils.touch(boss_coords)
            Utils.update_screen()
            b = False
            if Utils.exists('combat_unable'):
                boss = Utils.scroll_find('combat_enemy_boss', 250, 175, 0.75)
                boss = [boss.x, boss.y]
                enemies = self.get_enemies()
                closest_to_boss = enemies[Utils.find_closest(enemies, boss)[1]]
                Utils.touch(closest_to_boss)
                Utils.update_screen()
                if Utils.exists('combat_unable'):
                    Utils.touch(self.get_closest_enemy())
                b = True
            Utils.script_sleep(3)
            Utils.update_screen()
            if Utils.find_and_touch('combat_evade'):
                Utils.script_sleep(2)
                Utils.update_screen()
                if Utils.exists('combat_battle_start'):
                    self.conduct_battle()
                    if not self.config.comabt['two_fleet']:
                        self.refocus_fleet()
            elif b and self.conduct_prebattle_check():
                self.conduct_battle()
        if self.conduct_prebattle_check():
            self.conduct_battle()

    def switch_fleet(self):
        """Method to switch the current fleet
        """
        Utils.touch_randomly(self.region['switch_fleet'])

    def refocus_fleet(self):
        """Method to refocus on the current fleet
        """
        Logger.log_msg('Refocusing fleet.')
        self.switch_fleet()
        self.switch_fleet()
        Utils.update_screen()

    def check_morale(self):
        """Method to multithread the detection of morale states of the fleet.

        Returns:
            dict: dict of bools of the different morale states
        """
        thread_check_neutral_morale = Thread(
            target=self.check_morale_func, args=('neutral',))
        thread_check_sad_morale = Thread(
            target=self.check_morale_func, args=('sad',))
        Utils.multithreader([
            thread_check_neutral_morale, thread_check_sad_morale])
        return self.morale

    def check_morale_func(self, status):
        """Child multithreaded method for checking morale states.

        Args:
            status (string): which morale status to check for
        """
        self.morale[status] = (
            True
            if (Utils.exists('morale_{}'.format(status)))
            else False)
