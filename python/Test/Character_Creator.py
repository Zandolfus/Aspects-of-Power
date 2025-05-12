"""
Improved Character structure with better separation of concerns and proper encapsulation
"""
from typing import Dict, List, Optional, Tuple, Any
import math
import random
import csv
import os
import json
from dataclasses import dataclass
from game_data import tier1_class_gains, tier2_class_gains, races, tier1_profession_gains, tier2_profession_gains

# Constants
STATS = ["vitality", "endurance", "strength", "dexterity", "toughness", 
         "intelligence", "willpower", "wisdom", "perception"]
META_INFO = ["Class", "Class level", "Race", "Profession", "Profession level"]
DERIVED_META = ["Race level", "Race rank"]  # Meta attributes that are derived/calculated automatically

# Configuration (could be moved to a JSON config file)
STAT_MODIFIER_FORMULA = {
    "base_value": 6000,
    "exp_factor": -0.001,
    "offset": 500,
    "adjustment": -2265
}

class StatSource:
    """Enum-like class to track where stat points came from"""
    BASE = "base"
    CLASS = "class" 
    PROFESSION = "profession"
    RACE = "race"
    ITEM = "item"
    BLESSING = "blessing"
    FREE_POINTS = "free_points"

class CharacterDataManager:
    """
    Central manager for character data with proper encapsulation and state management.
    Handles both stats and meta information with appropriate validation.
    """
    def __init__(self, stats: Optional[Dict[str, int]] = None, 
                 meta: Optional[Dict[str, Any]] = None):
        # Initialize stats
        self._base_stats = {stat: 5 for stat in STATS}
        if stats:
            for stat, value in stats.items():
                if stat in STATS:
                    self._base_stats[stat] = value
        
        # Keep track of where stats came from for proper recalculation
        self._stat_sources = {
            stat: {StatSource.BASE: self._base_stats[stat]} for stat in STATS
        }
        
        # Initialize meta data with defaults
        self._meta = {info: "" for info in META_INFO}
        if meta:
            for key, value in meta.items():
                if key in META_INFO:
                    self._meta[key] = value
        
        # Ensure numeric meta values are stored as strings for consistency
        for key in ["Class level", "Profession level"]:
            if self._meta[key] == "":
                self._meta[key] = "0"
            elif isinstance(self._meta[key], int):
                self._meta[key] = str(self._meta[key])
        
        # Initialize derived values
        for key in DERIVED_META:
            if key not in self._meta:
                self._meta[key] = "0" if "level" in key.lower() else ""
        
        # Calculate current stats from all sources
        self._current_stats = self._calculate_current_stats()
        
        # Calculate modifiers
        self._modifiers = self._calculate_modifiers()
    
    def _calculate_current_stats(self) -> Dict[str, int]:
        """Calculate current stats from all sources"""
        current = {stat: 0 for stat in STATS}
        
        # Sum up contributions from all sources
        for stat in STATS:
            current[stat] = sum(self._stat_sources[stat].values())
        
        return current
    
    def _calculate_modifiers(self) -> Dict[str, float]:
        """Calculate and return modifiers for all stats"""
        return {stat: self._calculate_modifier(value) 
                for stat, value in self._current_stats.items()}
    
    @staticmethod
    def _calculate_modifier(attribute: int) -> float:
        """Calculate modifier using the game's formula"""
        config = STAT_MODIFIER_FORMULA
        return int(round(
            (config["base_value"] / 
             (1 + math.exp(config["exp_factor"] * (attribute - config["offset"])))) + 
            config["adjustment"], 0
        ))
    
    def get_stat(self, stat: str) -> int:
        """Get a stat value"""
        if stat not in STATS:
            raise ValueError(f"Invalid stat: {stat}")
        return self._current_stats[stat]
    
    def get_stat_modifier(self, stat: str) -> float:
        """Get a stat modifier"""
        if stat not in STATS:
            raise ValueError(f"Invalid stat: {stat}")
        return self._modifiers[stat]
    
    def set_base_stat(self, stat: str, value: int) -> None:
        """Set a base stat value"""
        if stat not in STATS:
            raise ValueError(f"Invalid stat: {stat}")
        
        # Update base value
        self._base_stats[stat] = value
        self._stat_sources[stat][StatSource.BASE] = value
        
        # Recalculate current stats and modifiers
        self._current_stats = self._calculate_current_stats()
        self._modifiers = self._calculate_modifiers()
    
    def add_stat(self, stat: str, value: int, source: str) -> None:
        """Add to a stat from a specific source"""
        if stat not in STATS:
            raise ValueError(f"Invalid stat: {stat}")
        
        if source not in self._stat_sources[stat]:
            self._stat_sources[stat][source] = 0
        
        self._stat_sources[stat][source] += value
        
        # Recalculate current stats and modifiers
        self._current_stats = self._calculate_current_stats()
        self._modifiers = self._calculate_modifiers()
    
    def get_meta(self, key: str, default: Any = "") -> Any:
        """Get a meta attribute"""
        return self._meta.get(key, default)
    
    def set_meta(self, key: str, value: Any, force: bool = False) -> bool:
        """
        Set a meta attribute with validation
        Returns True if value was changed
        """
        # Validate key
        if key not in META_INFO and key not in DERIVED_META:
            raise ValueError(f"Invalid meta attribute: {key}")
        
        # Prevent direct modification of derived attributes unless forced
        if key in DERIVED_META and not force:
            raise ValueError(f"Cannot directly set derived attribute: {key}")
        
        # Store old value for comparison
        old_value = self._meta.get(key, "")
        
        # Set new value
        self._meta[key] = value
        
        # Return whether value changed
        return old_value != value
    
    def get_all_stats(self) -> Dict[str, int]:
        """Get all current stats"""
        return self._current_stats.copy()
    
    def get_all_modifiers(self) -> Dict[str, float]:
        """Get all stat modifiers"""
        return self._modifiers.copy()
    
    def get_all_meta(self) -> Dict[str, Any]:
        """Get all meta attributes"""
        return self._meta.copy()
    
    def get_stat_sources(self, stat: str) -> Dict[str, int]:
        """Get the breakdown of where a stat's points came from"""
        if stat not in STATS:
            raise ValueError(f"Invalid stat: {stat}")
        return self._stat_sources[stat].copy()
    
    def reset_stat_source(self, stat: str, source: str) -> None:
        """Reset a specific stat source to 0"""
        if stat not in STATS:
            raise ValueError(f"Invalid stat: {stat}")
        
        if source in self._stat_sources[stat]:
            self._stat_sources[stat][source] = 0
            
            # Recalculate current stats and modifiers
            self._current_stats = self._calculate_current_stats()
            self._modifiers = self._calculate_modifiers()
    
    def apply_item_stats(self, item_stats: Dict[str, int]) -> None:
        """Apply item bonuses to stats"""
        for stat, value in item_stats.items():
            if stat in STATS:
                self.add_stat(stat, value, StatSource.ITEM)
    
    def remove_item_stats(self, item_stats: Dict[str, int]) -> None:
        """Remove item bonuses from stats"""
        for stat, value in item_stats.items():
            if stat in STATS:
                self.add_stat(stat, -value, StatSource.ITEM)
    
    def apply_blessing(self, blessing_stats: Dict[str, int]) -> None:
        """Apply blessing bonuses to stats"""
        for stat, value in blessing_stats.items():
            if stat in STATS:
                self.add_stat(stat, value, StatSource.BLESSING)
    
    def remove_blessing(self, blessing_stats: Dict[str, int]) -> None:
        """Remove blessing bonuses from stats"""
        for stat, value in blessing_stats.items():
            if stat in STATS:
                self.add_stat(stat, -value, StatSource.BLESSING)

class HealthManager:
    """Manages character health based on vitality stat"""
    
    def __init__(self, data_manager: CharacterDataManager):
        self.data_manager = data_manager
        self.max_health = self._calculate_max_health()
        self.current_health = self.max_health
    
    def _calculate_max_health(self) -> int:
        """Calculate max health based on vitality modifier"""
        return int(self.data_manager.get_stat_modifier("vitality"))
    
    def update_max_health(self, reason: str = "other") -> None:
        """
        Update max health based on current vitality modifier
        
        reason: The reason for the max health update
          - "level_up": From character leveling up
          - "item": From equipping/unequipping an item
          - "blessing": From adding/removing a blessing
          - "other": Default case
        """
        old_max = self.max_health
        self.max_health = self._calculate_max_health()
        
        if reason == "level_up" and self.max_health > old_max:
            # For level-up, always add the full difference to current health
            self.current_health += (self.max_health - old_max)
        elif reason in ["item", "blessing"]:
            # For items/blessings, adjust based on whether character is at full health
            if self.current_health == old_max:
                # At full health, increase current health to the new max
                self.current_health = self.max_health
            else:
                # Not at full health, keep the same percentage of health
                health_percentage = self.current_health / old_max if old_max > 0 else 1.0
                self.current_health = max(1, int(self.max_health * health_percentage))
        else:
            # Default case
            if self.max_health > old_max:
                self.current_health += (self.max_health - old_max)
            else:
                self.current_health = min(self.current_health, self.max_health)
    
    def take_damage(self, damage: int) -> None:
        """Reduce character health by damage amount"""
        self.current_health = max(0, self.current_health - damage)
    
    def heal(self, amount: int) -> None:
        """Heal character by amount, not exceeding max health"""
        self.current_health = min(self.max_health, self.current_health + amount)
    
    def reset_health(self) -> None:
        """Reset current health to max health"""
        self.current_health = self.max_health
    
    def is_alive(self) -> bool:
        """Check if character is alive"""
        return self.current_health > 0

@dataclass
class Item:
    """Represents an equippable item"""
    name: str
    description: str
    stats: Dict[str, int]
    equipped: bool = False
    
    @property
    def equippable(self) -> bool:
        """Check if item can be equipped"""
        return bool(self.stats)
    
    def __str__(self) -> str:
        equipped_str = " [Equipped]" if self.equipped else ""
        return f"{self.name.title()}{equipped_str}: {self.description}"

class Inventory:
    """Manages character inventory and equipment"""
    
    def __init__(self, item_repository):
        self.items: List[Item] = []
        self.item_repository = item_repository
    
    def add_item(self, item_name: str) -> bool:
        """Add an item to inventory"""
        try:
            item_data = self.item_repository.get_item(item_name)
            if not item_data:
                return False
            
            item = Item(
                name=item_name,
                description=item_data["description"],
                stats=item_data["stats"].copy()
            )
            self.items.append(item)
            return True
        except Exception as e:
            print(f"Error adding item: {e}")
            return False
    
    def remove_item(self, item_name: str) -> bool:
        """Remove an item from inventory"""
        item = self.get_item(item_name)
        if item:
            if item.equipped:
                return False  # Can't remove equipped items
            self.items.remove(item)
            return True
        return False
    
    def get_item(self, name: str) -> Optional[Item]:
        """Get an item by name"""
        for item in self.items:
            if item.name.lower() == name.lower():
                return item
        return None
    
    def equip_item(self, item_name: str) -> Tuple[bool, Optional[Item]]:
        """Equip an item"""
        item = self.get_item(item_name)
        if item and item.equippable and not item.equipped:
            item.equipped = True
            return True, item
        return False, None
    
    def unequip_item(self, item_name: str) -> Tuple[bool, Optional[Item]]:
        """Unequip an item"""
        item = self.get_item(item_name)
        if item and item.equipped:
            item.equipped = False
            return True, item
        return False, None
    
    def get_equipped_items(self) -> List[Item]:
        """Get all equipped items"""
        return [item for item in self.items if item.equipped]
    
    def __str__(self) -> str:
        if not self.items:
            return "Empty"
        return "\n".join(str(item) for item in self.items)

class CombatSystem:
    """Handles combat mechanics"""
    
    def __init__(self, data_manager: CharacterDataManager, health_manager: HealthManager):
        self.data_manager = data_manager
        self.health_manager = health_manager
        self.finesse = False  # Set based on character class
    
    def set_finesse(self, value: bool) -> None:
        """Set whether character uses finesse in combat"""
        self.finesse = value
    
    @staticmethod
    def roll(dice: str) -> int:
        """Simulate dice roll (e.g., "2d6")"""
        num_dice, sides = map(int, dice.split("d"))
        return sum(random.randint(1, sides) for _ in range(num_dice))
    
    def calculate_hit_chance(self, target_data_manager: CharacterDataManager) -> Tuple[float, bool, int, float]:
        """Calculate chance to hit target"""
        roll = self.roll("1d20")
        
        # Calculate target's defense
        defense = int(round(
            target_data_manager.get_stat_modifier("dexterity") + 
            target_data_manager.get_stat_modifier("strength") * 0.3, 0
        ))
        
        # Calculate to-hit score
        to_hit = round(
            ((roll / 100) * 
             (self.data_manager.get_stat_modifier("dexterity") + 
              self.data_manager.get_stat_modifier("strength") * 0.6) + 
             self.data_manager.get_stat_modifier("dexterity") + 
             self.data_manager.get_stat_modifier("strength") * 0.6) * 0.911, 0
        )
        
        hit = to_hit >= defense
        return to_hit, hit, roll, defense
    
    def calculate_damage(self) -> Tuple[int, int]:
        """Calculate damage for an attack"""
        roll = self.roll("2d6")
        
        if not self.finesse:
            # Strength-based damage
            dmg = int(round(
                ((roll / 50) * self.data_manager.get_stat_modifier("strength") + 
                 self.data_manager.get_stat_modifier("strength")) * 0.5, 0
            ))
        else:
            # Finesse-based damage (strength + some dexterity)
            dmg = int(round(
                ((roll / 50) * 
                 (self.data_manager.get_stat_modifier("strength") + 
                  self.data_manager.get_stat_modifier("dexterity") * 0.25) + 
                 self.data_manager.get_stat_modifier("strength") + 
                 self.data_manager.get_stat_modifier("dexterity") * 0.25) * 0.6, 0
            ))
        
        return dmg, roll
    
    def attack(self, target) -> Tuple[bool, int, int]:
        """Perform attack against target"""
        # Calculate hit chance
        attack_score, hit, attack_roll, defense = self.calculate_hit_chance(target.data_manager)
        
        toughness = target.data_manager.get_stat_modifier("toughness")
        damage = 0
        net_damage = 0
        
        if hit:
            damage, dmg_roll = self.calculate_damage()
            net_damage = max(0, damage - toughness)
            
            if net_damage > 0:
                target.health_manager.take_damage(net_damage)
        
        return hit, damage, net_damage

class LevelSystem:
    """Manages character leveling and progression including race levels and free points"""
    
    def __init__(self, data_manager: CharacterDataManager):
        self.data_manager = data_manager
        self.free_points = 0
    
    def level_up(self, level_type: str, target_level: int) -> bool:
        """Level up character in specified category"""
        if level_type.lower() not in ["class", "profession"]:
            raise ValueError("Invalid level type. Must be 'Class' or 'Profession'.")
            
        try:
            current_level = int(self.data_manager.get_meta(f"{level_type} level", "0"))
        except ValueError:
            print(f"Warning: Invalid {level_type} level value.")
            return False
            
        if target_level <= current_level:
            print(f"{level_type} is already at or above level {target_level}.")
            return False
            
        print(f"Leveling up {level_type} from {current_level} to {target_level}")
        
        # Apply level-up effects for each level gained
        for level in range(current_level + 1, target_level + 1):
            # Update the level
            self.data_manager.set_meta(f"{level_type} level", str(level))
            
            # Apply appropriate stat changes
            if level_type.lower() == "class":
                self._apply_class_level_up(level)
            elif level_type.lower() == "profession":
                self._apply_profession_level_up(level)
        
        # Update race level after class/profession level change
        self._update_race_level()
        
        return True
    
    def _update_race_level(self) -> None:
        """Update race level based on class and profession level"""
        try:
            class_level = int(self.data_manager.get_meta("Class level", "0"))
            profession_level = int(self.data_manager.get_meta("Profession level", "0"))
            total_level = class_level + profession_level
            new_race_level = total_level // 2
            
            # Get current race level for comparison
            current_race_level = int(self.data_manager.get_meta("Race level", "0"))
            
            # If no change in level, nothing to do
            if new_race_level == current_race_level:
                return
                
            print(f"Updating race level from {current_race_level} to {new_race_level}")
            
            # For any level change
            if new_race_level != current_race_level:
                # Reset race contributions because we'll recalculate them
                for stat in STATS:
                    self.data_manager.reset_stat_source(stat, StatSource.RACE)
                    
                # Apply race level gains from 1 to new_race_level
                self._apply_race_level_up(0, new_race_level)
                
                # Update race level in meta data
                self.data_manager.set_meta("Race level", str(new_race_level), force=True)
        except ValueError as e:
            print(f"Warning: Invalid level values detected: {e}")
    
    def _apply_class_level_up(self, level: int) -> None:
        """Apply stat increases for class level-up"""
        
        class_name = self.data_manager.get_meta("Class", "").lower()
        if not class_name:
            print("Warning: Character has no class defined.")
            return
        
        # Check if class needs to be upgraded at level 25
        if level == 25:
            # In a real implementation, this would involve user input
            new_class = input("Enter your new class: ")
            self.data_manager.set_meta("Class", new_class)
            class_name = new_class.lower()
        
        # Determine which tier gains to apply
        if level <= 24:
            if class_name in tier1_class_gains:
                gains = tier1_class_gains[class_name]
            else:
                print(f"Warning: Class '{class_name}' not found in tier 1.")
                return
        else:
            if class_name in tier2_class_gains:
                gains = tier2_class_gains[class_name]
            else:
                print(f"Warning: Class '{class_name}' not found in tier 2.")
                return
        
        # Apply the stat gains
        for stat, gain in gains.items():
            if stat == "free_points":
                self.free_points += gain
                print(f"Class level-up: Added {gain} free points")
            elif stat in STATS:
                self.data_manager.add_stat(stat, gain, StatSource.CLASS)
    
    def _apply_profession_level_up(self, level: int) -> None:
        """Apply stat increases for profession level-up"""
        
        profession = self.data_manager.get_meta("Profession", "").lower()
        if not profession:
            print("Warning: Character has no profession defined.")
            return
        
        # Check if profession needs to be upgraded at level 25
        if level == 25:
            # In a real implementation, this would involve user input
            new_profession = input("Enter your new profession: ")
            self.data_manager.set_meta("Profession", new_profession)
            profession = new_profession.lower()
        
        # Determine which tier gains to apply
        if level <= 24:
            if profession in tier1_profession_gains:
                gains = tier1_profession_gains[profession]
            else:
                print(f"Warning: Profession '{profession}' not found in tier 1.")
                return
        else:
            if profession in tier2_profession_gains:
                gains = tier2_profession_gains[profession]
            else:
                print(f"Warning: Profession '{profession}' not found in tier 2.")
                return
        
        # Apply the stat gains
        for stat, gain in gains.items():
            if stat == "free_points":
                self.free_points += gain
                print(f"Profession level-up: Added {gain} free points")
            elif stat in STATS:
                self.data_manager.add_stat(stat, gain, StatSource.PROFESSION)
    
    def _apply_race_level_up(self, from_level: int, to_level: int) -> None:
        """Apply stat changes for race level-up from from_level to to_level"""
        race = self.data_manager.get_meta("Race", "").lower()
        if not race:
            return
        
        if race not in races:
            print(f"Warning: Race '{race}' not found in race data.")
            return
        
        race_data = races.get(race, {})
        rank_ranges = race_data.get("rank_ranges", [])
        
        if not rank_ranges:
            print(f"Warning: No rank ranges defined for race '{race}'.")
            return
        
        # Sort ranges by min_level for correct application
        sorted_ranges = sorted(rank_ranges, key=lambda x: x["min_level"])
        
        # Apply effects for each level gained
        for level in range(from_level + 1, to_level + 1):
            # Find applicable range for this level
            applicable_range = None
            for range_data in sorted_ranges:
                if range_data["min_level"] <= level <= range_data["max_level"]:
                    applicable_range = range_data
                    break
            
            if not applicable_range:
                continue
            
            # Update race rank if provided
            if "rank" in applicable_range:
                self.data_manager.set_meta("Race rank", applicable_range["rank"], force=True)
            
            # Apply stat gains
            if "stats" in applicable_range:
                for stat, gain in applicable_range["stats"].items():
                    if stat == "free_points":
                        # Free points are managed by LevelSystem
                        self.free_points += gain
                        print(f"Race level-up: Added {gain} free points")
                    elif stat in STATS:
                        self.data_manager.add_stat(stat, gain, StatSource.RACE)
    
    def change_class(self, new_class: str) -> bool:
        """Change character's class with proper recalculation"""
        old_class = self.data_manager.get_meta("Class", "")
        class_level = int(self.data_manager.get_meta("Class level", "0"))
        
        if old_class == new_class:
            return False
        
        # Update the class
        self.data_manager.set_meta("Class", new_class)
        
        # Recalculate class bonuses if character has class levels
        if class_level > 0:
            # Reset class stat bonuses and free points from class
            for stat in STATS:
                self.data_manager.reset_stat_source(stat, StatSource.CLASS)
            
            # Reapply class bonuses for all levels
            for level in range(1, class_level + 1):
                self._apply_class_level_up(level)
        
        return True
    
    def change_profession(self, new_profession: str) -> bool:
        """Change character's profession with proper recalculation"""
        old_profession = self.data_manager.get_meta("Profession", "")
        profession_level = int(self.data_manager.get_meta("Profession level", "0"))
        
        if old_profession == new_profession:
            return False
        
        # Update the profession
        self.data_manager.set_meta("Profession", new_profession)
        
        # Recalculate profession bonuses if character has profession levels
        if profession_level > 0:
            # Reset profession stat bonuses
            for stat in STATS:
                self.data_manager.reset_stat_source(stat, StatSource.PROFESSION)
            
            # Reapply profession bonuses for all levels
            for level in range(1, profession_level + 1):
                self._apply_profession_level_up(level)
        
        return True
    
    def change_race(self, new_race: str) -> bool:
        """Change character's race with proper recalculation"""
        old_race = self.data_manager.get_meta("Race", "")
        race_level = int(self.data_manager.get_meta("Race level", "0"))
        
        if old_race == new_race:
            return False
        
        # Update the race
        self.data_manager.set_meta("Race", new_race)
        
        # Recalculate race bonuses
        if race_level > 0:
            # Reset race stat bonuses
            for stat in STATS:
                self.data_manager.reset_stat_source(stat, StatSource.RACE)
            
            # Reapply race bonuses
            self._apply_race_level_up(0, race_level)
        
        return True
    
    def allocate_free_points(self, stat: str, amount: int) -> bool:
        """Allocate free points to a specific stat"""
        if stat not in STATS:
            print(f"Invalid stat: {stat}")
            return False
            
        if amount <= 0:
            print(f"Amount must be positive. Got: {amount}")
            return False
            
        if amount > self.free_points:
            print(f"Not enough free points. Have: {self.free_points}, Need: {amount}")
            return False
        
        # Apply the points
        self.data_manager.add_stat(stat, amount, StatSource.FREE_POINTS)
        self.free_points -= amount
        return True
    
    def allocate_random(self) -> None:
        """Randomly allocate all free points"""
        while self.free_points > 0:
            stat = random.choice(STATS)
            self.allocate_free_points(stat, 1)
    
    def calculate_all_level_bonuses(self) -> None:
        """
        Recalculate all level-based bonuses from scratch.
        Useful when loading a character or after changing class/profession/race.
        """
        # Clear all level-based stat sources
        for stat in STATS:
            self.data_manager.reset_stat_source(stat, StatSource.CLASS)
            self.data_manager.reset_stat_source(stat, StatSource.PROFESSION)
            self.data_manager.reset_stat_source(stat, StatSource.RACE)
        
        # Apply class level bonuses
        class_level = int(self.data_manager.get_meta("Class level", "0"))
        if class_level > 0:
            for level in range(1, class_level + 1):
                self._apply_class_level_up(level)
        
        # Apply profession level bonuses
        profession_level = int(self.data_manager.get_meta("Profession level", "0"))
        if profession_level > 0:
            for level in range(1, profession_level + 1):
                self._apply_profession_level_up(level)
        
        # Update and apply race level
        self._update_race_level()

class CharacterSerializer:
    """Handles saving and loading characters"""
    
    @staticmethod
    def save_to_csv(character, filename: str, mode: str = "a") -> bool:
        """Save character to CSV file"""
        try:
            # Define fields for the CSV
            # Base attributes
            fieldnames = ["Name"]
            
            # Add meta fields
            fieldnames += META_INFO + DERIVED_META
            
            # Add stat fields
            fieldnames += STATS
            
            # Add modifier fields
            fieldnames += [f"{stat}_modifier" for stat in STATS]
            
            # Add stat source fields for each source type
            for source in [StatSource.BASE, StatSource.CLASS, StatSource.PROFESSION, 
                           StatSource.RACE, StatSource.ITEM, StatSource.BLESSING, 
                           StatSource.FREE_POINTS]:
                fieldnames += [f"{stat}_{source}" for stat in STATS]
            
            # Add free points
            fieldnames += ["free_points"]
            
            # Check if file exists and if character already exists in it
            existing_data = []
            character_exists = False
            file_exists = os.path.exists(filename)
            
            if file_exists:
                with open(filename, "r", newline="") as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        if "Name" in row and row["Name"] == character.name:
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
                
                # Get data for current character
                stats = character.data_manager.get_all_stats()
                meta = character.data_manager.get_all_meta()
                modifiers = character.data_manager.get_all_modifiers()
                
                # Create row dictionary
                row = {"Name": character.name}
                
                # Add meta data
                for key, value in meta.items():
                    row[key] = value
                
                # Add current stats
                for stat, value in stats.items():
                    row[stat] = value
                
                # Add modifiers
                for stat, value in modifiers.items():
                    row[f"{stat}_modifier"] = value
                
                # Add stat sources
                for stat in STATS:
                    sources = character.data_manager.get_stat_sources(stat)
                    for source, value in sources.items():
                        row[f"{stat}_{source}"] = value
                
                # Add free points
                row["free_points"] = character.level_system.free_points
                
                writer.writerow(row)
            
            print(f"Character '{character.name}' {'updated' if character_exists else 'saved'} to {filename}")
            return True
        except Exception as e:
            print(f"Error saving character: {e}")
            return False
    
    @staticmethod
    def load_from_csv(filename: str, character_name: str, item_repository=None):
        """Load character from CSV file"""
        try:
            if not os.path.exists(filename):
                print(f"File not found: {filename}")
                return None
                
            with open(filename, "r", newline="") as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    if "Name" in row and row["Name"].lower() == character_name.lower():
                        # Found the character
                        
                        # Extract meta info
                        meta = {}
                        for key in META_INFO + DERIVED_META:
                            if key in row:
                                meta[key] = row[key]
                        
                        # Extract stats
                        stats = {}
                        for stat in STATS:
                            if stat in row:
                                try:
                                    stats[stat] = int(row[stat])
                                except ValueError:
                                    print(f"Warning: Invalid stat value for {stat}: {row[stat]}")
                                    stats[stat] = 5  # Default value
                        
                        # Extract free points
                        free_points = 0
                        if "free_points" in row:
                            try:
                                free_points = int(row["free_points"])
                            except ValueError:
                                print("Warning: Invalid free points value.")
                        
                        # Extract stat sources
                        stat_sources = {}
                        for stat in STATS:
                            stat_sources[stat] = {}
                            for source in [StatSource.BASE, StatSource.CLASS, StatSource.PROFESSION, 
                                           StatSource.RACE, StatSource.ITEM, StatSource.BLESSING, 
                                           StatSource.FREE_POINTS]:
                                source_key = f"{stat}_{source}"
                                if source_key in row:
                                    try:
                                        stat_sources[stat][source] = int(row[source_key])
                                    except ValueError:
                                        print(f"Warning: Invalid source value for {source_key}: {row[source_key]}")
                                        stat_sources[stat][source] = 0
                        
                        # Create and return a new character
                        character = Character(
                            name=row["Name"],
                            stats=stats,
                            meta=meta,
                            free_points=free_points,
                            stat_sources=stat_sources,
                            item_repository=item_repository
                        )
                        
                        print(f"Character '{character_name}' loaded from {filename}")
                        return character
                
                print(f"Character '{character_name}' not found in {filename}")
                return None
        except Exception as e:
            print(f"Error loading character: {e}")
            return None

class Character:
    """Main character class that coordinates all subsystems"""
    
    def __init__(self, name: str, stats: Optional[Dict[str, int]] = None, 
                 meta: Optional[Dict[str, str]] = None, free_points: int = 0,
                 stat_sources: Optional[Dict[str, Dict[str, int]]] = None,
                 item_repository = None, blessing: Optional[Dict[str, int]] = None):
        self.name = name
        
        # Initialize all systems
        self.data_manager = CharacterDataManager(stats, meta)
        self.inventory = Inventory(item_repository)
        self.level_system = LevelSystem(self.data_manager)
        self.health_manager = HealthManager(self.data_manager)
        self.combat_system = CombatSystem(self.data_manager, self.health_manager)
        
        # Set free points
        self.level_system.free_points = free_points
        
        # If stat sources are provided, apply them directly
        if stat_sources:
            for stat in STATS:
                if stat in stat_sources:
                    for source, value in stat_sources[stat].items():
                        if source != StatSource.BASE:  # Base stats already set in data_manager init
                            self.data_manager.add_stat(stat, value, source)
        else:
            # No stat sources provided, calculate everything from levels
            self._calculate_and_apply_level_stats()
        
        # Set finesse based on class
        self._update_finesse()
        
        # Apply blessing if provided (stored at character level for tracking)
        self.blessing = None
        if blessing:
            self.add_blessing(blessing)
    
    def _calculate_and_apply_level_stats(self):
        """Calculate and apply stat gains based on current class/profession levels"""
        # Use the LevelSystem to calculate all level bonuses
        self.level_system.calculate_all_level_bonuses()
        
        # Update health
        self.health_manager.update_max_health()
    
    def _update_finesse(self) -> None:
        """Update finesse setting based on class"""
        class_name = self.data_manager.get_meta("Class", "").lower()
        self.combat_system.set_finesse(class_name == "light warrior")
    
    def update_meta(self, key: str, value: Any) -> bool:
        """Update meta information with validation and cascading updates"""
        if key not in META_INFO:
            print(f"Invalid meta info: {key}")
            return False
        
        # Handle special cases
        if key in DERIVED_META:
            print(f"Cannot directly update {key} as it is a derived attribute.")
            return False
        
        # Store old value
        old_value = self.data_manager.get_meta(key)
        
        # Update meta info
        try:
            changed = self.data_manager.set_meta(key, value)
            
            # Handle specific meta changes
            if changed:
                if key == "Class":
                    # Class changed, update finesse and recalculate class bonuses
                    self._update_finesse()
                    
                    # Recalculate class bonuses if character has class levels
                    self.level_system.change_class(value)
                    
                    # Update race level which depends on class level
                    self.level_system._update_race_level()
                
                elif key == "Profession":
                    # Profession changed, recalculate profession bonuses
                    self.level_system.change_profession(value)
                    
                    # Update race level which depends on profession level
                    self.level_system._update_race_level()
                
                elif key == "Race":
                    # Race changed, recalculate race bonuses
                    self.level_system.change_race(value)
            
            # Update health if needed
            self.health_manager.update_max_health()
            
            return True
        except ValueError as e:
            print(f"Error updating meta: {e}")
            return False
    
    def update_stat(self, stat: str, value: int) -> bool:
        """Update a base stat directly"""
        try:
            self.data_manager.set_base_stat(stat, value)
            self.health_manager.update_max_health()
            return True
        except ValueError as e:
            print(f"Error updating stat: {e}")
            return False
    
    def level_up(self, level_type: str, target_level: int) -> bool:
        """Level up character in specified category"""
        result = self.level_system.level_up(level_type, target_level)
        if result:
            self.health_manager.update_max_health(reason="level_up")
        return result
    
    def equip_item(self, item_name: str) -> bool:
        """Equip an item and apply its stats"""
        success, item = self.inventory.equip_item(item_name)
        if success and item:
            # Apply item stats
            self.data_manager.apply_item_stats(item.stats)
            
            # Update health if vitality changed
            self.health_manager.update_max_health(reason="item")
            return True
        return False
    
    def unequip_item(self, item_name: str) -> bool:
        """Unequip an item and remove its stats"""
        success, item = self.inventory.unequip_item(item_name)
        if success and item:
            # Remove item stats
            self.data_manager.remove_item_stats(item.stats)
            
            # Update health if vitality changed
            self.health_manager.update_max_health(reason="item")
            return True
        return False
    
    def add_blessing(self, blessing_stats: Dict[str, int]) -> None:
        """Add a blessing with stat bonuses"""
        if not blessing_stats:
            return
        
        # If there's already a blessing, remove it
        if self.blessing:
            self.remove_blessing()
        
        self.blessing = blessing_stats.copy()
        self.data_manager.apply_blessing(blessing_stats)
        self.health_manager.update_max_health(reason="blessing")
    
    def remove_blessing(self) -> None:
        """Remove current blessing if any"""
        if self.blessing:
            self.data_manager.remove_blessing(self.blessing)
            self.blessing = None
            self.health_manager.update_max_health(reason="blessing")
    
    def attack(self, target) -> Tuple[bool, int, int]:
        """Perform attack on another character"""
        return self.combat_system.attack(target)
    
    def allocate_free_points(self, stat: str, amount: int) -> bool:
        """Allocate free points to a specific stat"""
        success = self.level_system.allocate_free_points(stat, amount)
        if success:
            self.health_manager.update_max_health()
        return success
    
    def allocate_random(self) -> None:
        """Randomly allocate all free points"""
        self.level_system.allocate_random()
        self.health_manager.update_max_health()
        
    def validate_stats(self) -> Dict[str, Any]:
        """Validate character stats and return detailed results."""
        validator = StatValidator(self)
        return validator.validate()
    
    def save(self, filename: str, mode: str = "a") -> bool:
        """Save character to file"""
        return CharacterSerializer.save_to_csv(self, filename, mode)
    
    @classmethod
    def load(cls, filename: str, character_name: str, item_repository = None):
        """Load character from file"""
        return CharacterSerializer.load_from_csv(filename, character_name, item_repository)
    
    def reset_health(self) -> None:
        """Reset character health to maximum"""
        self.health_manager.reset_health()
    
    def is_alive(self) -> bool:
        """Check if character is alive"""
        return self.health_manager.is_alive()
        
    def __str__(self) -> str:
        """String representation of character"""
        meta = self.data_manager.get_all_meta()
        stats = self.data_manager.get_all_stats()
        modifiers = self.data_manager.get_all_modifiers()
        
        # Format meta info
        meta_str = ", ".join(f"{key}: {value}" for key, value in meta.items())
        
        # Format stats
        stats_str = []
        for stat in STATS:
            sources = self.data_manager.get_stat_sources(stat)
            current = stats[stat]
            modifier = modifiers[stat]
            
            # Format source breakdown if more than just base
            if len(sources) > 1:
                source_str = " (" + " + ".join(f"{source}: {value}" for source, value in sources.items() if source != StatSource.BASE and value != 0) + ")"
                stats_str.append(f"{stat}: {sources.get(StatSource.BASE, 0)}{source_str} = {current} (modifier: {modifier})")
            else:
                stats_str.append(f"{stat}: {current} (modifier: {modifier})")
        
        stats_display = ", ".join(stats_str)
        
        # Format free points info
        free_points_str = f"\nFree points: {self.level_system.free_points}" if self.level_system.free_points > 0 else ""
        
        # Format blessing info
        blessing_str = ""
        if self.blessing:
            blessing_details = ", ".join(f"{stat}: +{value}" for stat, value in self.blessing.items())
            blessing_str = f"\nBlessing: {blessing_details}"
        
        return (
            f"Character: {self.name}\n"
            f"Info: {meta_str}\n"
            f"Stats: {stats_display}\n"
            f"Health: {self.health_manager.current_health}/{self.health_manager.max_health}"
            f"{free_points_str}"
            f"{blessing_str}\n"
            f"Inventory: {self.inventory}"
        )

class ItemRepository:
    """Repository of all available items"""
    
    def __init__(self, items_data: Dict = None):
        self.items = items_data or {}
    
    def get_item(self, item_name: str) -> Optional[Dict]:
        """Get item data by name"""
        return self.items.get(item_name.lower())
    
    def add_item(self, name: str, description: str, stats: Dict[str, int]) -> None:
        """Add a new item to the repository"""
        self.items[name.lower()] = {
            "description": description,
            "stats": stats
        }
    
    def remove_item(self, item_name: str) -> bool:
        """Remove an item from the repository"""
        if item_name.lower() in self.items:
            del self.items[item_name.lower()]
            return True
        return False
    
    def save_to_json(self, filename: str) -> bool:
        """Save item repository to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.items, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving items: {e}")
            return False
    
    @classmethod
    def load_from_json(cls, filename: str):
        """Load item repository from JSON file"""
        try:
            with open(filename, 'r') as f:
                items_data = json.load(f)
            return cls(items_data)
        except Exception as e:
            print(f"Error loading items: {e}")
            return cls()
    
    def list_items(self) -> List[str]:
        """Get list of all item names"""
        return list(self.items.keys())
    
    def __str__(self) -> str:
        """String representation of item repository"""
        if not self.items:
            return "No items available"
        
        result = []
        for name, data in self.items.items():
            stats_str = ", ".join(f"{stat}: +{val}" for stat, val in data["stats"].items()) if data["stats"] else "No stats"
            result.append(f"{name.title()}: {data['description']} ({stats_str})")
        
        return "\n".join(result)

class StatValidator:
    """
    Validates a character's stats against expected values based on their attributes.
    """
    
    def __init__(self, character):
        """
        Initialize the validator with a character.
        
        Args:
            character: The character to validate
        """
        self.character = character
        # No need to import game_data as it's already available in the main script
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate the character's stats and return detailed results.
        
        Returns:
            A dictionary containing validation results including any discrepancies
        """
        # Initialize result dictionary
        result = {
            "valid": True,
            "stat_discrepancies": {},
            "free_points": {
                "current": self.character.level_system.free_points,
                "expected_total": 0,
                "spent": 0,
                "difference": 0
            },
            "overall_summary": "",
            "details": {}
        }
        
        # Calculate expected stats from each source
        base_stats = self._get_base_stats()
        class_stats = self._get_class_stats()
        profession_stats = self._get_profession_stats()
        race_stats = self._get_race_stats() 
        item_stats = self._get_item_stats()
        blessing_stats = self._get_blessing_stats()
        
        # Calculate expected free points
        expected_free_points = (
            class_stats.get("free_points", 0) +
            profession_stats.get("free_points", 0) +
            race_stats.get("free_points", 0)
        )
        result["free_points"]["expected_total"] = expected_free_points
        
        # Calculate expected base stats (without free point allocation)
        expected_base_stats = {}
        for stat in STATS:
            expected_base_stats[stat] = (
                base_stats.get(stat, 5) +
                class_stats.get(stat, 0) +
                profession_stats.get(stat, 0) +
                race_stats.get(stat, 0) +
                item_stats.get(stat, 0) +
                blessing_stats.get(stat, 0)
            )
        
        # Get actual stats and their sources
        actual_stats = self.character.data_manager.get_all_stats()
        stat_sources = {stat: self.character.data_manager.get_stat_sources(stat) for stat in STATS}
        
        # Calculate free points spent
        free_points_spent = 0
        for stat in STATS:
            sources = stat_sources[stat]
            if StatSource.FREE_POINTS in sources:
                free_points_spent += sources[StatSource.FREE_POINTS]
        
        result["free_points"]["spent"] = free_points_spent
        
        # Check discrepancies for each stat
        for stat in STATS:
            # Expected value from all sources except free points
            expected_base = expected_base_stats[stat]
            
            # Actual value
            actual = actual_stats[stat]
            
            # Free points used for this stat
            free_points_used = stat_sources[stat].get(StatSource.FREE_POINTS, 0)
            
            # Expected total including free points
            expected_total = expected_base + free_points_used
            
            # Check if there's a discrepancy
            if actual != expected_total:
                diff = actual - expected_total
                result["valid"] = False
                result["stat_discrepancies"][stat] = {
                    "expected_base": expected_base,
                    "free_points_used": free_points_used,
                    "expected_total": expected_total,
                    "actual": actual,
                    "difference": diff,
                    "status": "over_allocated" if diff > 0 else "under_allocated"
                }
        
        # Check overall free points balance
        total_free_points_received = expected_free_points
        total_free_points_accounted = free_points_spent + self.character.level_system.free_points
        free_points_diff = total_free_points_received - total_free_points_accounted
        
        result["free_points"]["difference"] = free_points_diff
        
        if free_points_diff != 0:
            result["valid"] = False
        
        # Store detailed information for reference
        result["details"] = {
            "base_stats": base_stats,
            "class_stats": class_stats,
            "profession_stats": profession_stats,
            "race_stats": race_stats,
            "item_stats": item_stats,
            "blessing_stats": blessing_stats,
            "expected_base_stats": expected_base_stats,
            "actual_stats": actual_stats,
            "stat_sources": stat_sources
        }
        
        # Create human-readable summary
        result["overall_summary"] = self._create_summary(result)
        
        return result
    
    def _create_summary(self, result: Dict[str, Any]) -> str:
        """Create a human-readable summary of the validation results."""
        if result["valid"]:
            return "Character stats are valid. All stats are properly allocated."
        
        summary_parts = []
        
        # Summarize stat discrepancies
        if result["stat_discrepancies"]:
            over_allocated = {}
            under_allocated = {}
            
            for stat, info in result["stat_discrepancies"].items():
                if info["difference"] > 0:
                    over_allocated[stat] = info["difference"]
                else:
                    under_allocated[stat] = abs(info["difference"])
            
            if over_allocated:
                over_text = ", ".join(f"{stat}: +{points}" for stat, points in over_allocated.items())
                summary_parts.append(f"Over-allocated stats: {over_text}")
            
            if under_allocated:
                under_text = ", ".join(f"{stat}: -{points}" for stat, points in under_allocated.items())
                summary_parts.append(f"Under-allocated stats: {under_text}")
        
        # Summarize free points discrepancy
        free_points_diff = result["free_points"]["difference"]
        if free_points_diff != 0:
            if free_points_diff > 0:
                summary_parts.append(
                    f"Free points discrepancy: {free_points_diff} unaccounted for. "
                    f"Expected total: {result['free_points']['expected_total']}, "
                    f"Spent: {result['free_points']['spent']}, "
                    f"Current: {result['free_points']['current']}"
                )
            else:
                summary_parts.append(
                    f"Free points discrepancy: {abs(free_points_diff)} too many spent. "
                    f"Expected total: {result['free_points']['expected_total']}, "
                    f"Spent: {result['free_points']['spent']}, "
                    f"Current: {result['free_points']['current']}"
                )
        
        return "\n".join(summary_parts)
    
    def _get_base_stats(self) -> Dict[str, int]:
        """Get the base stats (usually 5 for each stat)."""
        return {stat: 5 for stat in STATS}
    
    def _get_class_stats(self) -> Dict[str, int]:
        """Calculate total stat bonuses from class levels."""
        stats = {stat: 0 for stat in STATS}
        stats["free_points"] = 0
        
        class_name = self.character.data_manager.get_meta("Class", "").lower()
        class_level = int(self.character.data_manager.get_meta("Class level", "0"))
        
        if not class_name or class_level <= 0:
            return stats
        
        # Apply tier 1 class bonuses (levels 1-24)
        tier1_limit = min(class_level, 24)
        if tier1_limit > 0 and class_name in tier1_class_gains:  # Using global game_data
            tier1_gains = tier1_class_gains[class_name]
            for stat, gain_per_level in tier1_gains.items():
                stats[stat] += gain_per_level * tier1_limit
        
        # Apply tier 2 class bonuses (levels 25+)
        tier2_levels = max(0, class_level - 24)
        if tier2_levels > 0 and class_name in tier2_class_gains:  # Using global game_data
            tier2_gains = tier2_class_gains[class_name]
            for stat, gain_per_level in tier2_gains.items():
                stats[stat] += gain_per_level * tier2_levels
        
        return stats
    
    def _get_profession_stats(self) -> Dict[str, int]:
        """Calculate total stat bonuses from profession levels."""
        stats = {stat: 0 for stat in STATS}
        stats["free_points"] = 0
        
        profession_name = self.character.data_manager.get_meta("Profession", "").lower()
        profession_level = int(self.character.data_manager.get_meta("Profession level", "0"))
        
        if not profession_name or profession_level <= 0:
            return stats
        
        # Apply tier 1 profession bonuses (levels 1-24)
        tier1_limit = min(profession_level, 24)
        if tier1_limit > 0 and profession_name in tier1_profession_gains:  # Using global game_data
            tier1_gains = tier1_profession_gains[profession_name]
            for stat, gain_per_level in tier1_gains.items():
                stats[stat] += gain_per_level * tier1_limit
        
        # Apply tier 2 profession bonuses (levels 25+)
        tier2_levels = max(0, profession_level - 24)
        if tier2_levels > 0 and profession_name in tier2_profession_gains:  # Using global game_data
            tier2_gains = tier2_profession_gains[profession_name]
            for stat, gain_per_level in tier2_gains.items():
                stats[stat] += gain_per_level * tier2_levels
        
        return stats
    
    def _get_race_stats(self) -> Dict[str, int]:
        """Calculate total stat bonuses from race levels."""
        stats = {stat: 0 for stat in STATS}
        stats["free_points"] = 0
        
        race_name = self.character.data_manager.get_meta("Race", "").lower()
        race_level = int(self.character.data_manager.get_meta("Race level", "0"))
        
        if not race_name or race_level <= 0 or race_name not in races:  # Using global game_data
            return stats
        
        race_data = races[race_name]
        rank_ranges = race_data.get("rank_ranges", [])
        
        # For each level, find the applicable rank range and apply stats
        for level in range(1, race_level + 1):
            for range_data in rank_ranges:
                if range_data["min_level"] <= level <= range_data["max_level"]:
                    for stat, gain in range_data.get("stats", {}).items():
                        stats[stat] += gain
                    break
        
        return stats
    
    def _get_item_stats(self) -> Dict[str, int]:
        """Calculate total stat bonuses from equipped items."""
        stats = {stat: 0 for stat in STATS}
        
        for item in self.character.inventory.get_equipped_items():
            for stat, value in item.stats.items():
                if stat in STATS:
                    stats[stat] += value
        
        return stats
    
    def _get_blessing_stats(self) -> Dict[str, int]:
        """Calculate total stat bonuses from blessings."""
        stats = {stat: 0 for stat in STATS}
        
        if hasattr(self.character, 'blessing') and self.character.blessing:
            for stat, value in self.character.blessing.items():
                if stat in STATS:
                    stats[stat] += value
        
        return stats