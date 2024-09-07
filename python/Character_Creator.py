import csv
import math
import random
import os
from random import randint
from typing import Dict, List, Optional

# Create seperate functions for the addition of stats and meta info to allow the user to create chars without of them or to not let users create one without the other.
# Handle class chnage from tier 1 to tier 2. When the character levels up to 25, prompt user to change class. Base class vs tier x class.

class Character:
    STATS = ['vitality', 'endurance', 'strength', 'dexterity', 'toughness', 'intelligence', 'willpower', 'wisdom', 'perception']
    META  = ['Class', 'Class level', 'Race', 'Race level', 'Race rank', 'Profession', 'Profession level']

    def __init__(self, name: str, stats: Optional[Dict[str, int]] = None, meta: Optional[Dict[str, str]] = None, finesse: bool = False, free_points: int = 0):
        self.name = name
        self.stats = stats or {stat: 0 for stat in self.STATS}
        self.meta = meta or {info: '' for info in self.META}
        self.modifiers = self.calculate_modifiers()
        self.max_health = self.modifiers['vitality']
        self.current_health = self.max_health
        self.finesse = finesse or self.meta['Class'].lower() == 'light warrior'
        self.free_points = free_points

    def calculate_modifiers(self) -> Dict[str, float]:
        return {stat: self.calculate_modifier(value) for stat, value in self.stats.items()}

    def _calculate_initial_free_points(self) -> int:
        class_level = int(self.meta['Class level'])
        profession_level = int(self.meta['Profession level'])
        total_level = (class_level + profession_level) // 2

        free_points = 0

        # Class free points
        free_points += min(class_level, 24) * 2  # 2 points per level up to 24
        free_points += max(0, class_level - 24) * 4  # 4 points per level from 25 onward

        # Profession free points
        profession = self.meta['Profession'].lower()
        free_points += profession_level * (8 if profession == 'justiciar' else 2)

        # Race free points
        for level in range(1, total_level+1):
            if 0 <= level <= 9:
                free_points += 1
            elif 10 <= level <= 24:
                free_points += 2
            elif 25 <= level <= 99:
                free_points += 5
            else:
                free_points += 15

        return free_points
    
    def _calculate_free_points(self, target_level: int, level_type: str) -> int:
        current_level = int(self.meta[f'{level_type} level'.capitalize()])
        professions = ['justiciar', 'judge', 'augur']
        race = self.meta['Race']
        free_points = 0

        for level in range(current_level + 1, target_level + 1):
            if level_type == 'Class':
                if level <= 24:
                    free_points += 2
                else:
                    free_points += 4
            elif level_type == 'Profession':
                profession = self.meta['Profession'].lower()
                free_points += 8 if profession in professions else 2
            elif level_type == 'Race':
                if race.lower() == 'human':
                    if 0 <= level <= 9:
                        free_points += 1
                    elif 10 <= level <= 24:
                        free_points += 2
                    elif 25 <= level <= 99:
                        free_points += 5
                    else:
                        free_points += 15
                elif race.lower() == 'half-asrai':
                    if 0 <= level <= 9:
                        free_points += 2
                    elif 10 <= level <= 24:
                        free_points += 4

        return free_points

    @staticmethod
    def calculate_modifier(attribute: int) -> float:
        return int(round((6000 / (1 + math.exp(-0.001 * (attribute - 500)))) - 2265, 0))
    
    @staticmethod
    def roll(dice: str) -> int:
        if (dices := int(dice.split('d')[0])) > 1:
            rolls = [randint(1, int(dice.split('d')[1])) for _ in range(dices)]
            roll = sum(rolls)
        else:
            roll = randint(1, int(dice.split('d')[1]))
        
        return roll

    @classmethod
    def from_manual_input(cls, name: str) -> 'Character':
        stats = {}
        meta = {}
        
        print(f'Enter information for {name}:'.center(20, '-'))
        for info in cls.META:
            while True:
                if 'level' in info:
                    try:
                        value = int(input(f'{info}: '))
                        meta[info] = value
                        break
                    except ValueError:
                        print('Please enter a valid integer.')
                else:
                    value = input(f'{info}: ')
                    meta[info] = value
                    break
        
        print('\n' + f'Enter stats for {name}:'.center(20, '-'))
        for stat in cls.STATS:
            while True:
                try:
                    value = int(input(f'{stat.capitalize()}: '))
                    stats[stat] = value
                    break
                except ValueError:
                    print('Please enter a valid integer.')
        return cls(name, stats, meta)

    @classmethod
    def from_csv(cls, filename: str) -> List['Character']:
        characters = []
        with open(filename, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row.pop('name')
                stats = {stat: int(value) for stat, value in row.items() if stat in cls.STATS}
                meta = {info: value for info, value in row.items() if info in cls.META}
                characters.append(cls(name, stats, meta))
        return characters
    
    @classmethod
    def load_character(cls, filename: str, character_name: str) -> Optional['Character']:
        with open(filename, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['name'].lower() == character_name.lower():
                    name = row.pop('name')
                    stats = {stat: int(row[stat]) for stat in cls.STATS}
                    meta = {info: row[info] for info in cls.META}
                    free_points = int(row['free_points'])
                    character = cls(name, stats, meta, free_points=free_points)
                    if free_points > 0:
                        print(f"Loaded character {name} has {free_points} unallocated free points.")
                    return character
        print(f"Character {character_name} not found in the CSV file.")
        return None
    
    def add_stats(self) -> None:
        print('\n' + f'Enter stats for {self.name}:'.center(20, '-'))
        stats = {}
        for stat in self.STATS:
            while True:
                try:
                    value = int(input(f'{stat.capitalize()}: '))
                    stats[stat] = value
                    break
                except ValueError:
                    print('Please enter a valid integer.')
        
        self.stats = stats
        self.modifiers = self.calculate_modifiers()
        self.max_health = self.modifiers['vitality']
        self.current_health = self.max_health

    def update_stat(self, stat: str, value: int) -> None:
        if stat in self.stats:
            self.stats[stat] = value
            self.modifiers = self.calculate_modifiers()
            if stat == 'vitality':
                self.max_health = self.modifiers['vitality']
                self.current_health = self.max_health
        else:
            print(f"Stat not found: {stat}. Available stats are: {', '.join(self.STATS)}")

    def add_meta(self) -> None:
        meta = {}
        print(f'Enter information for {self.name}:'.center(20, '-'))
        for info in self.META:
            while True:
                if 'level' in info:
                    try:
                        value = int(input(f'{info}: '))
                        meta[info] = value
                        break
                    except ValueError:
                        print('Please enter a valid integer.')
                else:
                    value = input(f'{info}: ')
                    meta[info] = value
                    break
        self.meta = meta
        self.finesse = self.meta['Class'].lower() == 'light warrior'

    def update_meta(self, info: str, value: str) -> None:
        if info in self.meta:
            self.meta[info] = value
        else:
            print(f"Meta info not found: {info}. Available meta info are: {', '.join(self.META)}")
    
    def update_character_sheet(self) -> None:
        filename = f'{self.name.lower().replace(" ", "_")}_character_sheet.csv'
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Attribute', 'Statistic', 'Modifier'])
            for stat in self.STATS:
                writer.writerow([stat.capitalize(), self.stats[stat], self.modifiers[stat]])
        print(f"Updated character sheet for {self.name}")

    def to_csv(self, filename: str, mode: str = 'a') -> None:
        fieldnames = ['name'] + self.META + self.STATS + [f'{stat}_modifier' for stat in self.STATS] + ['free_points']
        
        existing_data = []
        character_exists = False
        file_exists = os.path.exists(filename)
        if file_exists:
            with open(filename, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['name'] == self.name:
                        character_exists = True
                    else:
                        existing_data.append(row)

        write_mode = 'w' if character_exists or not file_exists or mode == 'w' else 'a'
        with open(filename, write_mode, newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if write_mode == 'w':
                writer.writeheader()
                for row in existing_data:
                    writer.writerow(row)
            row = {
                'name': self.name, 
                **self.meta, 
                **self.stats, 
                **{f'{stat}_modifier': mod for stat, mod in self.modifiers.items()},
                'free_points': self.free_points
            }
            writer.writerow(row)
        
        print(f"{'Updated' if character_exists else 'Added'} character data for {self.name} in {filename}")

    def create_character_sheet(self) -> None:
        filename = f'''{self.name.lower().replace(' ', '_')}_character_sheet.csv'''
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Attribute', 'Statistic', 'Modifier'])
            for stat in self.STATS:
                writer.writerow([stat.capitalize(), self.stats[stat], self.modifiers[stat]])
    
    def update_character_sheet(self) -> None:
        filename = f'{self.name.lower().replace(" ", "_")}_character_sheet.csv'
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Attribute', 'Statistic', 'Modifier'])
            for stat in self.STATS:
                writer.writerow([stat.capitalize(), self.stats[stat], self.modifiers[stat]])
        print(f"Updated character sheet for {self.name}")
    
    def is_alive(self) -> bool:
        return self.current_health > 0

    def reset_health(self) -> None:
        self.current_health = self.max_health
    
    def to_hit(self, target: 'Character'):
        roll = self.roll('1d20')
        defense = int(round(target.modifiers['dexterity'] + target.modifiers['strength']*0.3, 0))
        to_hit = round(((roll/100)*(self.modifiers['dexterity'] + self.modifiers['strength']*0.6) + self.modifiers['dexterity'] + self.modifiers['strength']*0.6)*0.911, 0)
        
        if to_hit >= defense:
            hit = True
        else:
            hit = False
        
        return to_hit, hit, roll, defense
    
    def dmg(self):
        roll = self.roll('2d6')
        
        if self.finesse is False:
            dmg = int(round(((roll/50)*(self.modifiers['strength']) + self.modifiers['strength'])*0.5, 0))
        else:
            dmg = int(round(((roll/50)*(self.modifiers['strength'] + self.modifiers['dexterity']*0.25) + self.modifiers['strength'] + self.modifiers['dexterity']*0.25)*0.6, 0))
        
        return dmg, roll
    
    def attack(self, target: 'Character'):
        attk_score, hit, attk_roll, defense = self.to_hit(target)
        toughness = target.modifiers['toughness']
        damage = 0
        net_dmg = 0
        
        if hit is True:
            damage, dmg_roll = self.dmg()
            net_dmg = damage - toughness
            
            if net_dmg > 0:
                target.current_health -= net_dmg
                
        return hit, damage, net_dmg
    
    def level_up(self, level_type: str, target_level: int):
        if level_type.lower() not in ['class', 'profession']:
            raise ValueError("Invalid level type. Must be 'Class' or 'Profession'.")

        current_level = int(self.meta[f'{level_type} level'])
        if target_level <= current_level:
            print(f"{self.name} is already at or above level {target_level} for {level_type}.")
            return

        for _ in range(current_level, target_level):
            current_level += 1
            self.meta[f'{level_type} level'] = str(current_level)

            if level_type == 'Class':
                self._apply_class_level_up(current_level)
            elif level_type == 'Profession':
                self._apply_profession_level_up(current_level)

            self._update_race_level()
        
        self.modifiers = self.calculate_modifiers()
        self.max_health = self.modifiers['vitality']
        self.current_health = self.max_health
        
    def _update_race_level(self):
        total_level = int(self.meta['Class level']) + int(self.meta['Profession level'])
        current_race_level = int(self.meta['Race level'])
        new_race_level = total_level // 2

        if new_race_level > current_race_level:
            for level in range(current_race_level + 1, new_race_level + 1):
                self._apply_race_level_up(level)
            self.meta['Race level'] = str(new_race_level)

    def _apply_class_level_up(self, current_level):
        if current_level == 25:
            self.meta['Class'] = input('Enter your new class: ')
        
        class_name = self.meta['Class'].lower()
        
        tier1_class_gains = {
            'mage': {'intelligence': 2, 'willpower': 2, 'wisdom': 1, 'perception': 1, 'free_points': 2},
            'healer': {'willpower': 2, 'wisdom': 2, 'intelligence': 1, 'perception': 1, 'free_points': 2},
            'archer': {'perception': 2, 'dexterity': 2, 'endurance': 1, 'vitality': 1, 'free_points': 2},
            'heavy warrior': {'strength': 2, 'vitality': 2, 'endurance': 1, 'toughness': 1, 'free_points': 2},
            'medium warrior': {'strength': 2, 'dexterity': 2, 'endurance': 1, 'vitality': 1, 'free_points': 2},
            'light warrior': {'dexterity': 2, 'endurance': 2, 'vitality': 1, 'strength': 1, 'free_points': 2},
        }
        
        tier2_class_gains = {
            '''thunder puppet's shadow''': {'dexterity': 5, 'strength': 4, 'vitality': 3, 'endurance': 2, 'free_points': 4},
            'glamourweaver': {'wisdom': 5, 'intelligence': 4, 'willpower': 3, 'toughness': 2, 'free_points': 4},
            'waywatcher': {'perception': 5, 'dexterity': 4, 'wisdom': 3, 'toughness': 2, 'free_points': 4},
            'glade guardian': {'dexterity': 5, 'strength': 4, 'toughness': 3, 'wisdom': 2, 'free_points': 4},
            'sniper': {'perception': 5, 'dexterity': 4, 'endurance': 3, 'toughness': 2, 'free_points': 4},
            'augur': {'wisdom': 8, 'willpower': 8, 'vitality': 8, 'free_points': 8}
        }
        
        if current_level <= 24:
            for stat, gain in tier1_class_gains[class_name].items():
                if stat != 'free_points':
                    self.stats[stat] += gain
                else:
                    self.free_points += gain
        else:
            for stat, gain in tier2_class_gains[class_name].items():
                if stat != 'free_points':
                    self.stats[stat] += gain
                else:
                    self.free_points += gain

    def _apply_race_level_up(self, level):
        race = self.meta['Race'].lower()

        if race == 'human':
            if 0 <= level <= 9:
                self.meta['Race rank'] = 'G'
                bonus = 1
                self.free_points += 1
            elif 10 <= level <= 24:
                self.meta['Race rank'] = 'F'
                bonus = 1
                self.free_points += 2
            elif 25 <= level <= 99:
                self.meta['Race rank'] = 'E'
                bonus = 2
                self.free_points += 5
            else:
                self.meta['Race rank'] = 'D'
                bonus = 6
                self.free_points += 15

            for stat in self.STATS:
                self.stats[stat] += bonus
                
        elif race == 'half-asrai':
            if 0 <= level <= 9:
                self.meta['Race rank'] = 'G'
                dex = 2
                wis = 2
                tough = 2
                per = 2
                self.free_points += 2
            elif 10 <= level <= 24:
                self.meta['Race rank'] = 'F'
                dex = 2
                wis = 2
                tough = 2
                per = 2
                self.free_points += 3
                
            race_stats = {'dexterity': dex, 'wisdom': wis, 'toughness': tough, 'perception': per}
            for stat, value in race_stats.items():
                self.stats[stat] += value
    
    def _apply_profession_level_up(self, current_level):
        if current_level == 25:
            self.meta['Profession'] = input('Enter your new profession: ')
        
        profession = self.meta['Profession'].lower()

        tier1_profession_gains = {
            'beginner jeweler of the elements': {'wisdom': 2, 'dexterity': 2, 'vitality': 1, 'perception': 1, 'free_points': 2},
            'beginner smith of the moonshadow': {'strength': 2, 'perception': 2, 'vitality': 1, 'intelligence': 1, 'free_points': 2},
            'justiciar': {'free_points': 8},
            'judge': {'free_points': 8},
            'gatherer': {'strength': 2, 'perception': 2, 'dexterity': 1, 'endurance': 1, 'free_points': 2},
            'chef': {'dexterity': 2, 'perception': 2, 'strength': 1, 'endurance': 1, 'free_points': 2},
            'student trapper of the asrai': {'perception': 2, 'dexterity': 2, 'vitality': 1, 'endurance': 1, 'free_points': 2},
            'pickpocket': {'perception': 2, 'dexterity': 2, 'strength': 1, 'endurance': 1, 'free_points': 2},
            'novice tailor': {'dexterity': 2, 'perception': 2, 'wisdom': 1, 'willpower': 1, 'free_points': 2},
            'builder': {'strength': 2, 'dexterity': 2, 'endurance': 1, 'intelligence': 1, 'free_points': 2}
            
        }

        tier2_profession_gains = {
            'crusher': {'strength': 8, 'dexterity': 4, 'endurance': 4, 'free_points': 2},
            'chef for the masses': {'perception': 5, 'dexterity': 4, 'strength': 3, 'endurance': 2, 'free_points': 4},
            'beginner trapper of the asrai': {'perception': 5, 'dexterity': 4, 'vitality': 3, 'endurance': 2, 'free_points': 4},
            'thief': {'dexterity': 5, 'perception': 4, 'endruance': 3, 'strength': 2, 'free_points': 4},
            'tailor of ingenuity': {'dexterity': 5, 'perception': 4, 'wisdom': 3, 'willpower': 2, 'free_points': 4}
        }
        
        if current_level <= 24:
            if profession in tier1_profession_gains:
                for stat, gain in tier1_profession_gains[profession].items():
                    if stat != 'free_points':
                        self.stats[stat] += gain
                    else:
                        self.free_points += gain
            else:
                print('This profession does not exist!')
        else:
            if profession in tier2_profession_gains:
                for stat, gain in tier2_profession_gains[profession].items():
                    if stat != 'free_points':
                        self.stats[stat] += gain
                    else:
                        self.free_points += gain
            else:
                print('This profession does not exist!')

    def allocate_free_points(self):
        if self.free_points == 0:
            print("No free points available to allocate.")
            return

        print(f"\nYou have {self.free_points} free points to allocate.")
        allocation_choice = input("Do you want to allocate these points now? (yes/no/random): ").lower()

        if allocation_choice == 'yes':
            self._manual_allocation()
        elif allocation_choice == 'random':
            self._random_allocation()
        else:
            print("Free points saved for later allocation.")
        
        self.modifiers = self.calculate_modifiers()

    def _manual_allocation(self):
        remaining_points = self.free_points

        while remaining_points > 0:
            print(f"\nRemaining points: {remaining_points}")
            stat = input("Enter the stat you want to increase (or 'done' to finish): ").lower()
            
            if stat == 'done':
                break

            if stat in self.STATS:
                while True:
                    try:
                        amount = int(input(f"How many points do you want to allocate to {stat}? "))
                        if amount <= 0:
                            print("Please enter a positive number.")
                        elif amount > remaining_points:
                            print(f"You only have {remaining_points} points left to allocate.")
                        else:
                            self.stats[stat] += amount
                            remaining_points -= amount
                            print(f"Increased {stat} by {amount}. New value: {self.stats[stat]}")
                            break
                    except ValueError:
                        print("Please enter a valid number.")
            else:
                print("Invalid stat. Please choose from:", ", ".join(self.STATS))

        self.free_points = remaining_points
        if remaining_points > 0:
            print(f"{remaining_points} points were left unallocated and saved for later.")

    def _random_allocation(self):
        print("Randomly allocating free points...")
        for _ in range(self.free_points):
            stat = random.choice(self.STATS)
            self.stats[stat] += 1
        print("All free points have been randomly allocated.")
        self.free_points = 0
                
    def __str__(self) -> str:
        meta_str = ', '.join(f'{meta}: {value}' for meta, value in self.meta.items())
        stats_str = ', '.join(f'{stat}: {value} (modifier: {self.modifiers[stat]})' for stat, value in self.stats.items())
        return f'Character: {self.name}\nInfo: {meta_str}\nStats: {stats_str}'
    
class Simulator:
    @staticmethod
    def simulate_leveling(character: Character, levels: Dict[str, int]):
        for level_type, target_level in levels.items():
            print(f"\nSimulating {level_type} level-up for {character.name} to level {target_level}")
            character.level_up(level_type, target_level)
            print(f"{level_type} level: {character.meta[f'{level_type} level']}")

        print("\nLeveling complete. Current character stats:")
        print(character)
        
        character.allocate_free_points()

if __name__ == '__main__':
    char = Character("Woody", 
                     meta={"Class": "Archer", "Class level": "0", 
                           "Race": "Human", "Race level": "0", "Race rank": "G",
                           "Profession": "Uninitiated", "Profession level": "0"},
                     stats={'vitality': 5, 'endurance': 5, 'strength': 5, 'dexterity': 5,
                              'intelligence': 5, 'willpower': 5, 'wisdom': 5, 'perception': 5, 'toughness': 5})
    # char = Character.load_character('all_chars.csv', 'Felicia')
    char.level_up('Class', 20)
    # char.level_up('Profession', 15)
    # char.update_meta('Race', 'Half-Asrai')
    # char.level_up('Class', 26)
    char.allocate_free_points()
    char.to_csv('all_chars.csv')
    # char = Character.load_character('Fei.csv', 'Fei')
    # char.update_meta('Race', 'Half-Asrai')
    # char.update_meta('Profession', 'Uninitiated')
    # char.level_up('Class', 26)
    # char.allocate_free_points()
    # char.to_csv('Fei.csv')
    # char1 = Character.from_manual_input('Balanced_warrior')
    # print(char1)
    # char1.create_character_sheet()

    # char1.to_csv('characters2.csv', mode='w')

    # char2 = Character('Bob', {'vitality': 10, 'endurance': 8, 'strength': 12, 'dexterity': 14,
    #                           'intelligence': 13, 'willpower': 11, 'wisdom': 10, 'perception': 9})
    # char2.to_csv('characters.csv', mode='a')
    # char2.create_character_sheet()

    # loaded_characters = Character.from_csv('characters.csv')
    # for char in loaded_characters:
    #     print(char)
    #     char.create_character_sheet()