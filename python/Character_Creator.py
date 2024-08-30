import csv
import math
import random
import os
from random import randint
from typing import Dict, List, Optional

# Create seperate functions for the addition of stats and meta info to allow the user to create chars without of them or to not let users create one without the other.

class Character:
    STATS = ['vitality', 'endurance', 'strength', 'dexterity', 'toughness', 'intelligence', 'willpower', 'wisdom', 'perception']
    META  = ['Class', 'Class level', 'Race', 'Race level', 'Profession', 'Profession level', 'Race rank', 'Free points']

    def __init__(self, name: str, stats: Optional[Dict[str, int]] = None, meta: Optional[Dict[str, str]] = None, finesse: bool = False):
        self.name = name
        self.stats = stats or {stat: 0 for stat in self.STATS}
        self.meta = meta or {info: '0' if 'level' in info.lower() or info == 'Free points' else '' for info in self.META}
        self.modifiers = self.calculate_modifiers()
        self.max_health = self.modifiers['vitality']
        self.current_health = self.max_health
        self.finesse = finesse or self.meta['Class'].lower() == 'light warrior'

    def calculate_modifiers(self) -> Dict[str, float]:
        return {stat: self.calculate_modifier(value) for stat, value in self.stats.items()}

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
                    stats = {stat: int(value) for stat, value in row.items() if stat in cls.STATS}
                    meta = {info: value for info, value in row.items() if info in cls.META}
                    character = cls(name, stats, meta)
                    
                    free_points = int(meta.get('Free points', '0'))
                    if free_points > 0:
                        print(f"{name} has {free_points} unallocated free points.")
                        character._allocate_free_points()
                    
                    return character
        print(f'Character {character_name} not found in the CSV file.')
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
        if os.path.exists(filename):
            with open(filename, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['name'] == self.name:
                        character_exists = True
                    else:
                        existing_data.append(row)

        write_mode = 'w' if character_exists or mode == 'w' else 'a'
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
    
    def level_up(self, level_type: str):
        if level_type.lower() not in ['class', 'profession']:
            raise ValueError("Invalid level type. Must be 'Class' or 'Profession'.")

        current_level = int(self.meta[f'{level_type} level'])
        self.meta[f'{level_type} level'] = str(current_level + 1)

        if level_type.lower() == 'class':
            self._apply_class_level_up()
        elif level_type.lower() == 'profession':
            self._apply_profession_level_up()

        self._update_race_level()
        self.modifiers = self.calculate_modifiers()
        self.max_health = self.modifiers['vitality']
        self.current_health = self.max_health

    def _apply_class_level_up(self, current_level):
        class_name = self.meta['Class'].lower()
        class_stat_gains = {
            'mage': {'intelligence': 2, 'willpower': 2, 'wisdom': 1, 'perception': 1},
            'healer': {'willpower': 2, 'wisdom': 2, 'intelligence': 1, 'perception': 1},
            'archer': {'perception': 2, 'dexterity': 2, 'endurance': 1, 'vitality': 1},
            'heavy warrior': {'strength': 2, 'vitality': 2, 'endurance': 1, 'toughness': 1},
            'medium warrior': {'strength': 2, 'dexterity': 2, 'endurance': 1, 'vitality': 1},
            'light warrior': {'dexterity': 2, 'endurance': 2, 'vitality': 1, 'strength': 1}
        }

        if current_level <= 24:
            for stat, gain in class_stat_gains[class_name].items():
                self.stats[stat] += gain
            self.free_points += 2
        else:
            if class_name == 'light warrior':
                self.stats['dexterity'] += 5
                self.stats['endurance'] += 2
                self.stats['vitality'] += 3
                self.stats['strength'] += 4
            self.free_points += 4
            
    def _update_race_level(self):
        total_level = int(self.meta['Class level']) + int(self.meta['Profession level'])
        current_race_level = int(self.meta['Race level'])
        new_race_level = total_level // 2

        if new_race_level > current_race_level:
            self.meta['Race level'] = str(new_race_level)
            self._apply_race_level_up(new_race_level - current_race_level)

    def _apply_race_level_up(self, levels):
        race = self.meta['Race'].lower()
        total_level = int(self.meta['Class level']) + int(self.meta['Profession level'])

        for _ in range(levels):
            if race == 'human':
                for stat in self.STATS:
                    self.stats[stat] += 1

            if 0 <= total_level <= 9:
                self.meta['Race rank'] = 'G'
                bonus = 1
                free_points = 1
            elif 10 <= total_level <= 24:
                self.meta['Race rank'] = 'F'
                bonus = 1
                free_points = 2
            elif 25 <= total_level <= 99:
                self.meta['Race rank'] = 'E'
                bonus = 2
                free_points = 5
            else:  # 100+
                self.meta['Race rank'] = 'D'
                bonus = 6
                free_points = 15

            for stat in self.STATS:
                self.stats[stat] += bonus

            self.meta['Free points'] = str(int(self.meta['Free points']) + free_points)

    def _apply_profession_level_up(self):
        profession = self.meta['Profession'].lower()

        profession_stat_gains = {
            'beginner jeweler of the elements': {'wisdom': 2, 'dexterity': 2, 'vitality': 1, 'perception': 1},
            'beginner smith of the moonshadow': {'strength': 2, 'perception': 2, 'vitality': 1, 'intelligence': 1},
            'justiciar': {}
        }

        if profession in profession_stat_gains:
            for stat, gain in profession_stat_gains[profession].items():
                self.stats[stat] += gain

        self.free_points += 8 if profession == 'justiciar' else 2

    def _allocate_free_points(self):
        points = int(self.meta['Free points'])
        if points == 0:
            print("No free points available to allocate.")
            return

        print(f"\nYou have {points} free points to allocate.")
        allocate = input("Do you want to allocate these points now? (yes/no/random): ").lower()

        if allocate == 'yes':
            self._manual_allocation(points)
        elif allocate == 'random':
            self._random_allocation(points)
        else:
            print("Free points saved for later allocation.")

    def _manual_allocation(self, points):
        remaining_points = points
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

        self.meta['Free points'] = str(remaining_points)

    def _random_allocation(self):
        print("Randomly allocating free points...")
        for _ in range(self.free_points):
            stat = random.choice(self.STATS)
            self.stats[stat] += 1
        print("All free points have been randomly allocated.")
        self.meta['Free points'] = '0'
                
    def __str__(self) -> str:
        meta_str = ', '.join(f'{meta}: {value}' for meta, value in self.meta.items())
        stats_str = ', '.join(f'{stat}: {value} (modifier: {self.modifiers[stat]})' for stat, value in self.stats.items())
        return f'Character: {self.name}\nInfo: {meta_str}\nStats: {stats_str}'
    
class Simulator:
    @staticmethod
    def simulate_leveling(character: Character, levels: Dict[str, int]):
        for level_type, level_count in levels.items():
            print(f"\nSimulating {level_count} {level_type} level-ups for {character.name}")
            for _ in range(level_count):
                character.level_up(level_type)
                print(f"{level_type} level: {character.meta[f'{level_type} level']}")
                print(f"Race level: {character.meta['Race level']}, Rank: {character.meta['Race rank']}")

        character._allocate_free_points()
        print("\nFinal character stats:")
        print(character)
        

if __name__ == '__main__':
    char = Character("Test Character", 
                     meta={"Class": "Light Warrior", "Class level": "0", 
                           "Race": "Human", "Race level": "0", "Race rank": "G",
                           "Profession": "Justiciar", "Profession level": "0"},
                     stats={'vitality': 7, 'endurance': 8, 'strength': 7, 'dexterity': 9,
                              'intelligence': 10, 'willpower': 10, 'wisdom': 10, 'perception': 8, 'toughness': 5})
    char = Character.load_character('characters2.csv', 'Gabe')
    char.to_csv('characters2.csv', mode='a')
    char1 = Character.from_manual_input('Balanced_warrior')
    print(char1)
    char1.create_character_sheet()

    char1.to_csv('characters2.csv', mode='w')

    char2 = Character('Bob', {'vitality': 10, 'endurance': 8, 'strength': 12, 'dexterity': 14,
                              'intelligence': 13, 'willpower': 11, 'wisdom': 10, 'perception': 9})
    char2.to_csv('characters.csv', mode='a')
    char2.create_character_sheet()

    loaded_characters = Character.from_csv('characters.csv')
    for char in loaded_characters:
        print(char)
        char.create_character_sheet()