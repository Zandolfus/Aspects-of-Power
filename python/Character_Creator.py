import csv
import math
import random
import os
from string import capwords
from random import randint
from typing import Dict, List, Optional
from Item_Repo import items

class Character:
    """
    Represents a character in the game with various attributes, stats, and methods for character management.
    """

    STATS = ["vitality", "endurance", "strength", "dexterity", "toughness", "intelligence", "willpower", "wisdom", "perception"]
    META  = ["Class", "Class level", "Race", "Race level", "Race rank", "Profession", "Profession level"]

    def __init__(self, name: str, stats: Optional[Dict[str, int]] = None, 
                 base_stats: Optional[Dict[str, int]] = None, meta: Optional[Dict[str, str]] = None, 
                 finesse: bool = False, free_points: int = 0, blessing: bool = False):
        """
        Initialize a new Character instance.

        Args:
            name (str): The character's name.
            stats (Optional[Dict[str, int]]): The character's current stats.
            meta (Optional[Dict[str, str]]): The character's meta information.
            finesse (bool): Whether the character uses finesse-based combat.
            free_points (int): The number of unallocated stat points.
        """
        self.name = name
        self.stats = stats or {stat: 5 for stat in self.STATS}
        self.meta = meta or {info: "" for info in self.META}
        self.modifiers = self.calculate_modifiers()
        self.max_health = self.modifiers["vitality"]
        self.current_health = self.max_health
        self.finesse = finesse or self.meta["Class"].lower() == "light warrior"
        self.free_points = free_points
        self.inventory = Inventory()
        self.item_repo = ItemRepository()
        self.raw_stats = stats.copy()
        self.base_stats = base_stats or self.derive_base_stats()
        self.blessing = self.add_blessing(init=True) if blessing is True else None
    
    def derive_base_stats(self) -> Dict[str, int]:
        if self.meta["Class level"] == 0 and self.meta["Race level"] == 0 and self.meta["Profession level"] == 0:
            return self.stats.copy()
        else:
            return {stat: 5 for stat in self.STATS}

    def calculate_modifiers(self) -> Dict[str, float]:
        """
        Calculate and return the modifiers for all stats.

        Returns:
            Dict[str, float]: A dictionary of stat modifiers.
        """
        return {stat: self.calculate_modifier(value) for stat, value in self.stats.items()}

    def _calculate_initial_free_points(self) -> int:
        """
        Calculate the initial number of free points based on class, profession, and race levels.

        Returns:
            int: The total number of initial free points.
        """
        class_level = int(self.meta["Class level"])
        profession_level = int(self.meta["Profession level"])
        total_level = (class_level + profession_level) // 2

        free_points = 0

        # Calculate free points from class levels
        free_points += min(class_level, 24) * 2  # 2 points per level up to 24
        free_points += max(0, class_level - 24) * 4  # 4 points per level from 25 onward

        # Calculate free points from profession levels
        profession = self.meta["Profession"].lower()
        free_points += profession_level * (8 if profession == "justiciar" else 2)

        # Calculate free points from race levels
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

    @staticmethod
    def calculate_modifier(attribute: int) -> float:
        """
        Calculate the modifier for a given attribute value.

        Args:
            attribute (int): The attribute value.

        Returns:
            float: The calculated modifier.
        """
        return int(round((6000 / (1 + math.exp(-0.001 * (attribute - 500)))) - 2265, 0))

    @staticmethod
    def roll(dice: str) -> int:
        """
        Simulate rolling dice.

        Args:
            dice (str): A string representing the dice roll (e.g., "2d6").

        Returns:
            int: The result of the dice roll.
        """
        dices, sides = map(int, dice.split("d"))
        return sum(randint(1, sides) for _ in range(dices))

    @classmethod
    def from_manual_input(cls, name: str) -> "Character":
        """
        Create a Character instance from manual user input.

        Args:
            name (str): The character"s name.

        Returns:
            Character: A new Character instance.
        """
        stats = {}
        meta = {}

        print(f"Enter information for {name}:".center(20, "-"))
        for info in cls.META:
            while True:
                if "level" in info:
                    try:
                        value = int(input(f"{info}: "))
                        meta[info] = value
                        break
                    except ValueError:
                        print("Please enter a valid integer.")
                else:
                    value = input(f"{info}: ")
                    meta[info] = value
                    break

        print("\n" + f"Enter stats for {name}:".center(20, "-"))
        for stat in cls.STATS:
            while True:
                try:
                    value = int(input(f"{stat.capitalize()}: "))
                    stats[stat] = value
                    break
                except ValueError:
                    print("Please enter a valid integer.")

        if meta["Class level"] == 0 and meta["Race level"] == 0 and meta["Class level"] == 0:
            return cls(name=name, base_stats=stats, stats=stats, meta=meta)
        else:
            return cls(name=name, stats=stats, meta=meta)

    @classmethod
    def from_csv(cls, filename: str) -> List["Character"]:
        """
        Create multiple Character instances from a CSV file.

        Args:
            filename (str): The name of the CSV file to read from.

        Returns:
            List[Character]: A list of Character instances.
        """
        characters = []
        with open(filename, "r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row.pop("name")
                stats = {stat: int(value) for stat, value in row.items() if stat in cls.STATS}
                meta = {info: value for info, value in row.items() if info in cls.META}
                characters.append(cls(name, stats, meta))
        return characters

    @classmethod
    def load_character(cls, filename: str, character_name: str) -> Optional["Character"]:
        """
        Load a specific character from a CSV file.

        Args:
            filename (str): The name of the CSV file to read from.
            character_name (str): The name of the character to load.

        Returns:
            Optional[Character]: The loaded Character instance, or None if not found.
        """
        with open(filename, "r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["Name"].lower() == character_name.lower():
                    name = row.pop("Name")
                    stats = {stat: int(row[stat]) for stat in cls.STATS}
                    meta = {info: row[info] for info in cls.META}
                    free_points = int(row["free_points"])
                    character = cls(name=name, stats=stats, meta=meta, free_points=free_points)
                    if free_points > 0:
                        print(f"Loaded character {name} has {free_points} unallocated free points.")
                    return character
        print(f"Character {character_name} not found in the CSV file.")
        return None

    def add_stats(self) -> None:
        """
        Manually add stats to the character.
        """
        print("\n" + f"Enter stats for {self.name}:".center(20, "-"))
        stats = {}
        for stat in self.STATS:
            while True:
                try:
                    value = int(input(f"{stat.capitalize()}: "))
                    stats[stat] = value
                    break
                except ValueError:
                    print("Please enter a valid integer.")

        self.stats = stats
        self.modifiers = self.calculate_modifiers()
        self.max_health = self.modifiers["vitality"]
        self.current_health = self.max_health

    def update_stat(self, stat: str, value: int, add: bool = False) -> None:
        """
        Update a specific stat for the character.

        Args:
            stat (str): The name of the stat to update.
            value (int): The new value for the stat.
            add (bool): Adds the value instead of replacing.
        """
        if stat in self.stats:
            if add is False:
                self.stats[stat] = value
            else:
                self.stats[stat] += value
            self.modifiers = self.calculate_modifiers()
            if stat == "vitality":
                self.max_health = self.modifiers["vitality"]
                self.current_health = self.max_health
        else:
            print(f"Stat not found: {stat}. Available stats are: {', '.join(self.STATS)}")

        self.raw_stats = self.stats.copy()

    def add_meta(self) -> None:
        """
        Manually add meta information to the character.
        """
        meta = {}
        print(f"Enter information for {self.name}:".center(20, "-"))
        for info in self.META:
            while True:
                if "level" in info:
                    try:
                        value = int(input(f"{info}: "))
                        meta[info] = value
                        break
                    except ValueError:
                        print("Please enter a valid integer.")
                else:
                    value = input(f"{info}: ")
                    meta[info] = value
                    break
        self.meta = meta
        self.finesse = self.meta["Class"].lower() == "light warrior"

    def update_meta(self, info: str, value: str) -> None:
        """
        Update a specific meta information for the character.

        Args:
            info (str): The name of the meta information to update.
            value (str): The new value for the meta information.
        """
        if info in self.meta:
            self.meta[info] = value
        else:
            print(f"Meta info not found: {info}. Available meta info are: {', '.join(self.META)}")

    def update_character_sheet(self) -> None:
        """
        Update the character"s CSV file with current stats and modifiers.
        """
        filename = f"{self.name.lower().replace(' ', '_')}_character_sheet.csv"
        with open(filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Attribute", "Statistic", "Modifier"])
            for stat in self.STATS:
                writer.writerow([stat.capitalize(), self.stats[stat], self.modifiers[stat]])
        print(f"Updated character sheet for {self.name}")

    def to_csv(self, filename: str, mode: str = "a") -> None:
        """
        Save the character"s information to a CSV file.

        Args:
            filename (str): The name of the CSV file to save to.
            mode (str): The file opening mode ("a" for append, "w" for write).
        """
        fieldnames = ["Name"] + self.META + self.STATS + [f"{stat}_modifier" for stat in self.STATS] + ["free_points"] + [f"{stat}_base" for stat in self.STATS]

        existing_data = []
        character_exists = False
        file_exists = os.path.exists(filename)
        if file_exists:
            with open(filename, "r", newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["Name"] == self.name:
                        character_exists = True
                    else:
                        existing_data.append(row)

        write_mode = "w" if character_exists or not file_exists or mode == "w" else "a"
        with open(filename, write_mode, newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if write_mode == "w":
                writer.writeheader()
                for row in existing_data:
                    writer.writerow(row)
            row = {
                "Name": self.name, 
                **self.meta, 
                **self.stats, 
                **{f"{stat}_modifier": mod for stat, mod in self.modifiers.items()},
                "free_points": self.free_points,
                **{f"{stat}_base": value for stat, value in self.base_stats.items()}
            }
            writer.writerow(row)

        print(f"{'Updated' if character_exists else 'Added'} character data for {self.name} in {filename}")

    def create_character_sheet(self) -> None:
        """
        Create a CSV file with the character"s current stats and modifiers.
        """
        filename = f"{self.name.lower().replace(' ', '_')}_character_sheet.csv"
        with open(filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Attribute", "Statistic", "Modifier"])
            for stat in self.STATS:
                writer.writerow([stat.capitalize(), self.stats[stat], self.modifiers[stat]])

    def update_character_sheet(self) -> None:
        filename = f"{self.name.lower().replace(' ', '_')}_character_sheet.csv"
        with open(filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Attribute", "Statistic", "Modifier"])
            for stat in self.STATS:
                writer.writerow([stat.capitalize(), self.stats[stat], self.modifiers[stat]])
        print(f"Updated character sheet for {self.name}")

    def is_alive(self) -> bool:
        """
        Check if the character is alive (has more than 0 health).
        """
        return self.current_health > 0

    def reset_health(self) -> None:
        """
        Reset the character"s current health to their maximum health.
        """
        self.current_health = self.max_health

    def to_hit(self, target: "Character"):
        """
        Calculate the chance to hit a target.

        Args:
            target (Character): The target character.

        Returns:
            tuple: A tuple containing the to-hit score, whether the attack hit, the roll, and the target"s defense.
        """
        roll = self.roll("1d20")
        defense = int(round(target.modifiers["dexterity"] + target.modifiers["strength"]*0.3, 0))
        to_hit = round(((roll/100)*(self.modifiers["dexterity"] + self.modifiers["strength"]*0.6) + self.modifiers["dexterity"] + self.modifiers["strength"]*0.6)*0.911, 0)

        hit = to_hit >= defense

        return to_hit, hit, roll, defense

    def dmg(self):
        """
        Calculate damage for an attack.

        Returns:
            tuple: A tuple containing the calculated damage and the damage roll.
        """
        roll = self.roll("2d6")

        if not self.finesse:
            dmg = int(round(((roll/50)*(self.modifiers["strength"]) + self.modifiers["strength"])*0.5, 0))
        else:
            dmg = int(round(((roll/50)*(self.modifiers["strength"] + self.modifiers["dexterity"]*0.25) + self.modifiers["strength"] + self.modifiers["dexterity"]*0.25)*0.6, 0))

        return dmg, roll

    def attack(self, target: "Character"):
        """
        Perform an attack on a target character.

        Args:
            target (Character): The target character.

        Returns:
            tuple: A tuple containing whether the attack hit, the damage dealt, and the net damage after toughness.
        """
        attk_score, hit, attk_roll, defense = self.to_hit(target)
        toughness = target.modifiers["toughness"]
        damage = 0
        net_dmg = 0

        if hit:
            damage, dmg_roll = self.dmg()
            net_dmg = damage - toughness

            if net_dmg > 0:
                target.current_health -= net_dmg

        return hit, damage, net_dmg

    def level_up(self, level_type: str, target_level: int):
        """
        Level up the character in a specific category.

        Args:
            level_type (str): The type of level to increase ('Class' or 'Profession').
            target_level (int): The target level to reach.
        """
        if level_type.lower() not in ["class", "profession"]:
            raise ValueError("Invalid level type. Must be 'Class' or 'Profession'.")

        current_level = int(self.meta[f"{level_type} level"])
        if target_level <= current_level:
            print(f"{self.name} is already at or above level {target_level} for {level_type}.")
            return

        for _ in range(current_level, target_level):
            current_level += 1
            self.meta[f"{level_type} level"] = str(current_level)

            if level_type == "Class":
                self._apply_class_level_up(current_level)
            elif level_type == "Profession":
                self._apply_profession_level_up(current_level)

            self._update_race_level()

        self.modifiers = self.calculate_modifiers()
        self.max_health = self.modifiers["vitality"]
        self.current_health = self.max_health
        self.raw_stats = self.stats.copy()

    def add_blessing(self, init: bool = False):
        print("Adding a blessing...")

        blessing = {}
        choice = "yes"
        while choice.lower() != "no":
            stat = input("Enter the stat you want to increase: ")
            if stat in self.STATS:
                value = int(input(f"Enter the value to add for {stat}: "))
                self.update_stat(stat, value, add=True)
                blessing[stat] = value
                print(f"Updated {stat} to {self.stats[stat]}")
            else:
                print(f"Invalid stat! Available stats: {self.STATS}")
            choice = input("Do you want to continue (yes/no)? ")
            
        confirmation = input("Was a blessing added (yes/no)? ")
        if confirmation.lower() == 'yes':
            if init is False:
                self.blessing = blessing
            else:
                return blessing 

    def _update_race_level(self):
        """
        Update the character"s race level based on their total level.
        """
        total_level = int(self.meta["Class level"]) + int(self.meta["Profession level"])
        current_race_level = int(self.meta["Race level"])
        new_race_level = total_level // 2

        if new_race_level > current_race_level:
            for level in range(current_race_level + 1, new_race_level + 1):
                self._apply_race_level_up(level)
            self.meta["Race level"] = str(new_race_level)

    def _apply_class_level_up(self, current_level):
        """
        Apply stat increases for class level-up.

        Args:
            current_level (int): The current level after leveling up.
        """
        if current_level == 25:
            self.meta["Class"] = input("Enter your new class: ")

        class_name = self.meta["Class"].lower()

        # Define stat gains for tier 1 and tier 2 classes
        tier1_class_gains = {
            "mage": {
                "intelligence": 2,
                "willpower": 2,
                "wisdom": 1,
                "perception": 1,
                "free_points": 2,
            },
            "healer": {
                "willpower": 2,
                "wisdom": 2,
                "intelligence": 1,
                "perception": 1,
                "free_points": 2,
            },
            "archer": {
                "perception": 2,
                "dexterity": 2,
                "endurance": 1,
                "vitality": 1,
                "free_points": 2,
            },
            "heavy warrior": {
                "strength": 2,
                "vitality": 2,
                "endurance": 1,
                "toughness": 1,
                "free_points": 2,
            },
            "medium warrior": {
                "strength": 2,
                "dexterity": 2,
                "endurance": 1,
                "vitality": 1,
                "free_points": 2,
            },
            "light warrior": {
                "dexterity": 2,
                "endurance": 2,
                "vitality": 1,
                "strength": 1,
                "free_points": 2,
            },
        }

        tier2_class_gains = {
            "thunder puppet's shadow": {
                "dexterity": 5,
                "strength": 4,
                "vitality": 3,
                "endurance": 2,
                "free_points": 4,
            },
            "glamourweaver": {
                "wisdom": 5,
                "intelligence": 4,
                "willpower": 3,
                "toughness": 2,
                "free_points": 4,
            },
            "waywatcher": {
                "perception": 5,
                "dexterity": 4,
                "wisdom": 3,
                "toughness": 2,
                "free_points": 4,
            },
            "glade guardian": {
                "dexterity": 5,
                "strength": 4,
                "toughness": 3,
                "wisdom": 2,
                "free_points": 4,
            },
            "sniper": {
                "perception": 5,
                "dexterity": 4,
                "endurance": 3,
                "toughness": 2,
                "free_points": 4,
            },
            "augur": {
                "wisdom": 8, 
                "willpower": 8, 
                "vitality": 8, 
                "free_points": 8
            },
            "monk": {
                "dexterity": 5,
                "strength": 4,
                "toughness": 3,
                "vitality": 2,
                "free_points": 4,
            },
            "spearman": {
                "strength": 5,
                "dexterity": 4,
                "vitality": 3,
                "endurance": 2,
                "free_points": 4,
            },
            "knife artist": {
                "dexterity": 5,
                "perception": 4,
                "vitality": 3,
                "endurance": 2,
                "free_points": 4,
            },
            "bloodmage": {
                "intelligence": 5,
                "wisdom": 4,
                "vitality": 3,
                "willpower": 2,
                "free_points": 4,
            },
            "aspiring blade of light": {
                "strength": 5,
                "dexterity": 4,
                "vitality": 3,
                "endurance": 2,
                "free_points": 4,
            },
            "beginner assassin": {
                "dexterity": 5,
                "strength": 4,
                "perception": 3,
                "endurance": 2,
                "free_points": 4,
            },
            "hydromancer": {
                "intelligence": 5,
                "willpower": 4,
                "vitality": 3,
                "perception": 2,
                "free_points": 4,
            },
            "clergyman": {
                "wisdom": 5,
                "willpower": 4,
                "vitality": 3,
                "endurance": 2,
                "free_points": 4,
            },
            "swashbuckler": {
                "strength": 5,
                "dexterity": 4,
                "vitality": 3,
                "endurance": 2,
                "free_points": 4,
            },
            "witch of ages": {
                "willpower": 5,
                "intelligence": 4,
                "wisdom": 3,
                "vitality": 2,
                "free_points": 4,
            },
            "curse eater": {
                "willpower": 5,
                "perception": 4,
                "vitality": 3,
                "dexterity": 2,
                "free_points": 4,
            },
            "fireborne": {
                "intelligence": 5,
                "willpower": 4,
                "vitality": 3,
                "toughness": 2,
                "free_points": 4,
            },
            "windcaller": {
                "intelligence": 5,
                "perception": 4,
                "wisdom": 3,
                "willpower": 2,
                "free_points": 4,
            },
            "overwatch": {
                "perception": 5,
                "dexterity": 4,
                "endurance": 3,
                "strength": 2,
                "free_points": 4,
            }
        }

        # Apply stat gains based on current level and class
        if current_level <= 24:
            for stat, gain in tier1_class_gains[class_name].items():
                if stat != "free_points":
                    self.stats[stat] += gain
                else:
                    self.free_points += gain
        else:
            for stat, gain in tier2_class_gains[class_name].items():
                if stat != "free_points":
                    self.stats[stat] += gain
                else:
                    self.free_points += gain

    def _apply_race_level_up(self, level):
        """
        Apply stat increases for race level-up.

        Args:
            level (int): The current race level after leveling up.
        """
        race = self.meta["Race"].lower()

        races = {
            "human": {
                "rank": {
                    0 <= level <= 9: {
                        "dexterity": 1,
                        "strength": 1,
                        "vitality": 1,
                        "endurance": 1,
                        "toughness": 1,
                        "willpower": 1,
                        "wisdom": 1,
                        "intelligence": 1,
                        "perception": 1,
                        "free_points": 1,
                        "rank": "G"
                    },
                    10 <= level <= 24: {
                        "dexterity": 1,
                        "strength": 1,
                        "vitality": 1,
                        "endurance": 1,
                        "toughness": 1,
                        "willpower": 1,
                        "wisdom": 1,
                        "intelligence": 1,
                        "perception": 1,
                        "free_points": 2,
                        "rank": "F"
                    },
                    25 <= level <= 99: {
                        "dexterity": 2,
                        "strength": 2,
                        "vitality": 2,
                        "endurance": 2,
                        "toughness": 2,
                        "willpower": 2,
                        "wisdom": 2,
                        "intelligence": 2,
                        "perception": 2,
                        "free_points": 5,
                        "rank": "E"
                    },
                    level > 99: {
                        "dexterity": 6,
                        "strength": 6,
                        "vitality": 6,
                        "endurance": 6,
                        "toughness": 6,
                        "willpower": 6,
                        "wisdom": 6,
                        "intelligence": 6,
                        "perception": 6,
                        "free_points": 15,
                        "rank": "D"
                    },
                }
            },
            "half-asrai": {
                "rank": {
                    0 <= level <= 9: {
                        "dexterity": 2,
                        "toughness": 2,
                        "wisdom": 2,
                        "perception": 2,
                        "free_points": 2,
                        "rank": "G"
                    },
                    10 <= level <= 24: {
                        "dexterity": 2,
                        "toughness": 2,
                        "wisdom": 2,
                        "perception": 2,
                        "free_points": 3,
                        "rank": "F"
                    },
                },
            },
            "asrai": {
                "rank": {
                    0 <= level <= 24: {
                        "dexterity": 3,
                        "toughness": 2,
                        "wisdom": 2,
                        "perception": 2,
                        "vitality": 2,
                        "rank": "F"
                    },
                },
            },
            "monster": {
                "rank": { 
                    0<= level <= 24: {
                        "free_points": 42,
                        "rank": "F"                      
                    },
                    25 <= level <= 99: {
                        "free_points": 63,
                        "rank": "E"
                    },
                }
            },
        }

        for rank, stats in races[race]["rank"].items():
            if rank:
                for stat, value in stats.items():
                    if stat != "free_points" and stat != "rank":
                        self.stats[stat] += value
                    elif stat == "free_points":
                        self.free_points += value
                    else:
                        self.meta["Race rank"] = value
                break

    def _apply_profession_level_up(self, current_level):
        """
        Apply stat increases for profession level-up.

        Args:
            current_level (int): The current profession level after leveling up.
        """
        if current_level == 25:
            self.meta["Profession"] = input("Enter your new profession: ")

        profession = self.meta["Profession"].lower()

        # Define stat gains for tier 1 and tier 2 professions
        tier1_profession_gains = {
            "beginner jeweler of the elements": {
                "wisdom": 2,
                "dexterity": 2,
                "vitality": 1,
                "perception": 1,
                "free_points": 2,
            },
            "beginner smith of the moonshadow": {
                "strength": 2,
                "perception": 2,
                "vitality": 1,
                "intelligence": 1,
                "free_points": 2,
            },
            "justiciar": {
                "free_points": 8
            },
            "judge": {
                "free_points": 8
            },
            "magistrate": {
                "free_points": 8
            },
            "gatherer": {
                "strength": 2,
                "perception": 2,
                "dexterity": 1,
                "endurance": 1,
                "free_points": 2,
            },
            "chef": {
                "dexterity": 2,
                "perception": 2,
                "strength": 1,
                "endurance": 1,
                "free_points": 2,
            },
            "student trapper of the asrai": {
                "perception": 2,
                "dexterity": 2,
                "vitality": 1,
                "endurance": 1,
                "free_points": 2,
            },
            "pickpocket": {
                "perception": 2,
                "dexterity": 2,
                "strength": 1,
                "endurance": 1,
                "free_points": 2,
            },
            "novice tailor": {
                "dexterity": 2,
                "perception": 2,
                "wisdom": 1,
                "willpower": 1,
                "free_points": 2,
            },
            "builder": {
                "strength": 2,
                "dexterity": 2,
                "endurance": 1,
                "intelligence": 1,
                "free_points": 2,
            },
            "windlord's keeper": {
                "intelligence": 2,
                "dexterity": 2,
                "willpower": 1,
                "toughness": 1,
                "free_points": 2,
            },
            "beginner leatherworker of the cosmos": {
                "dexterity": 2,
                "willpower": 2,
                "strength": 1,
                "intelligence": 1,
                "free_points": 2,
            },
            "seed of new life": {
                "willpower": 2,
                "wisdom": 2,
                "perception": 1,
                "vitality": 1,
                "free_points": 2,
            },
            "vanguard of new growth": {
                "perception": 2,
                "vitality": 2,
                "strength": 1,
                "toughness": 1,
                "free_points": 2,
            },
            "student shaper of the asrai": {
                "dexterity": 2,
                "perception": 2,
                "willpower": 1,
                "wisdom": 1,
                "free_points": 2,
            },
            "alchemist of flame's heart": {
                "wisdom": 2,
                "perception": 2,
                "willpower": 1,
                "intelligence": 1,
                "free_points": 2,
            }
        }

        tier2_profession_gains = {
            "crusher": {
                "strength": 8,
                "dexterity": 4,
                "endurance": 4,
                "free_points": 2,
            },
            "chef for the masses": {
                "perception": 5,
                "dexterity": 4,
                "strength": 3,
                "endurance": 2,
                "free_points": 4,
            },
            "beginner trapper of the asrai": {
                "perception": 5,
                "dexterity": 4,
                "vitality": 3,
                "endurance": 2,
                "free_points": 4,
            },
            "thief": {
                "dexterity": 5,
                "perception": 4,
                "endruance": 3,
                "strength": 2,
                "free_points": 4,
            },
            "tailor of ingenuity": {
                "dexterity": 5,
                "perception": 4,
                "wisdom": 3,
                "willpower": 2,
                "free_points": 4,
            },
            "architect": {
                "strength": 5,
                "dexterity": 4,
                "endurance": 3,
                "willpower": 2,
                "free_points": 4,
            }
            
        }

        # Apply stat gains based on current level and profession
        if current_level <= 24:
            if profession in tier1_profession_gains:
                for stat, gain in tier1_profession_gains[profession].items():
                    if stat != "free_points":
                        self.stats[stat] += gain
                    else:
                        self.free_points += gain
            else:
                print("This profession does not exist!")
        else:
            if profession in tier2_profession_gains:
                for stat, gain in tier2_profession_gains[profession].items():
                    if stat != "free_points":
                        self.stats[stat] += gain
                    else:
                        self.free_points += gain
            else:
                print("This profession does not exist!")

    def allocate_free_points(self):
        """
        Allow the user to allocate free points to stats.
        """
        if self.free_points == 0:
            print("No free points available to allocate.")
            return

        print(f"\nYou have {self.free_points} free points to allocate.")
        allocation_choice = input("Do you want to allocate these points now? (yes/no/random): ").lower()

        if allocation_choice == "yes":
            self._manual_allocation()
        elif allocation_choice == "random":
            self._random_allocation()
        else:
            print("Free points saved for later allocation.")

        self.modifiers = self.calculate_modifiers()
        self.raw_stats = self.stats.copy()

    def _manual_allocation(self):
        """
        Manually allocate free points to stats.
        """
        remaining_points = self.free_points

        while remaining_points > 0:
            print(f"\nRemaining points: {remaining_points}")
            stat = input("Enter the stat you want to increase (or 'done' to finish): ").lower()

            if stat == "done":
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
        """
        Randomly allocate free points to stats.
        """
        print("Randomly allocating free points...")
        for _ in range(self.free_points):
            stat = random.choice(self.STATS)
            self.stats[stat] += 1
        print("All free points have been randomly allocated.")
        self.free_points = 0

    def add_item(self, item_name: str):
        self.inventory.add_item(item_name)

    def remove_item(self, item_name: str):
        self.inventory.remove_item(item_name)

    def equip_item(self, item_name: str):
        self.inventory.equip_item(item_name)
        self._update_stats()

    def unequip_item(self, item_name: str):
        self.inventory.unequip_item(item_name)
        self._update_stats()

    def _update_stats(self):
        self.stats = self.raw_stats.copy()
        for item in self.inventory.get_equipped_items():
            for stat, value in item.stats.items():
                if stat in self.stats:
                    self.stats[stat] += value
        self.modifiers = self.calculate_modifiers()

    def print_all_items(self):
        self.item_repo.available_items()

    def __str__(self) -> str:
        meta_str = ", ".join(f"{meta}: {value}" for meta, value in self.meta.items())
        stats_str = ", ".join(f"{stat}: {value} (modifier: {self.modifiers[stat]})" for stat, value in self.stats.items())
        return f"Character: {self.name}\nInfo: {meta_str}\nStats: {stats_str}\nInventory: {self.inventory}"

class ItemRepository:
    def __init__(self):
        self.items = items
        
    def available_items(self):
        """
        Prints all items and their properties from the item repository in a nicely formatted manner.
        """
        print("=== Item Repository ===")
        print(f"Total items: {len(self.items)}\n")

        for item_name, item_data in self.items.items():
            print(f"Item: {capwords(item_name)}")
            print(f"Description: {item_data['description']}")
            
            if item_data["stats"]:
                print("Stats:")
                for stat, value in item_data["stats"].items():
                    print(f"  - {stat.capitalize()}: +{value}")
            else:
                print("Stats: None")
            
            print("-" * 30)

class Item:
    def __init__(self, name: str):
        if name not in items:
            raise ValueError(f"Item '{name}' not found in the item repository.")
        
        item_data = items[name]
        self.name = name
        self.description = item_data["description"]
        self.stats = item_data["stats"]
        self.equippable = bool(self.stats)  # If the item has stats, it's equippable
        self.equipped = False
    
    def __str__(self):
        return f"{self.name.title()}: {self.description}"

class Inventory:
    def __init__(self):
        self.items: List[Item] = []

    def add_item(self, item_name: str):
        item = Item(item_name)
        self.items.append(item)
        print(f"Added {item.name} to inventory.")

    def remove_item(self, item_name: str):
        item = self.get_item(item_name)
        if item:
            self.items.remove(item)
            print(f"Removed {item.name} from inventory.")
        else:
            print(f"Item '{item_name}' not found in inventory.")

    def get_item(self, name: str) -> Optional[Item]:
        for item in self.items:
            if item.name.lower() == name.lower():
                return item
        return None

    def equip_item(self, item_name: str):
        item = self.get_item(item_name)
        if item:
            if item.equippable and not item.equipped:
                item.equipped = True
                print(f"{item.name} equipped.")
            elif not item.equippable:
                print(f"{item.name} is not equippable.")
            else:
                print(f"{item.name} is already equipped.")
        else:
            print(f"Item '{item_name}' not found in inventory.")

    def unequip_item(self, item_name: str):
        item = self.get_item(item_name)
        if item:
            if item.equipped:
                item.equipped = False
                print(f"{item.name} unequipped.")
            else:
                print(f"{item.name} is not equipped.")
        else:
            print(f"Item '{item_name}' not found in inventory.")

    def get_equipped_items(self) -> List[Item]:
        return [item for item in self.items if item.equipped]

    def __str__(self):
        return "\n".join(str(item) for item in self.items)

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

if __name__ == "__main__":
    # char = Character.from_manual_input("test")
    char = Character("Gabriel_2", 
                     meta={"Class": "Light Warrior", "Class level": 0, 
                           "Race": "Human", "Race level": 0, "Race rank": "G",
                           "Profession": "Justiciar", "Profession level": 0},
                     stats={"vitality": 7, "endurance": 8, "strength": 7, "dexterity": 10,
                              "intelligence": 10, "willpower": 10, "wisdom": 10, "perception": 8, "toughness": 5},
                     blessing=True)
    # char = Character.load_character("all_chars.csv", "Fei")
    char.level_up("Class", 34)
    char.level_up("Profession", 10)
    # char.update_meta("Race", "Half-Asrai")
    # char.level_up("Class", 26)
    char.allocate_free_points()
    char.to_csv("me_test.csv")
    # char = Character.load_character("Fei.csv", "Fei")
    # char.update_meta("Race", "Half-Asrai")
    # char.update_meta("Profession", "Uninitiated")
    # char.level_up("Class", 26)
    # char.allocate_free_points()
    # char.to_csv("Fei.csv")
    # char1 = Character.from_manual_input("Balanced_warrior")
    # print(char1)
    # char1.create_character_sheet()

    # char1.to_csv("characters2.csv", mode="w")

    # char2 = Character("Bob", {"vitality": 10, "endurance": 8, "strength": 12, "dexterity": 14,
    #                           "intelligence": 13, "willpower": 11, "wisdom": 10, "perception": 9})
    # char2.to_csv("characters.csv", mode="a")
    # char2.create_character_sheet()

    # loaded_characters = Character.from_csv("characters.csv")
    # for char in loaded_characters:
    #     print(char)
    #     char.create_character_sheet()
