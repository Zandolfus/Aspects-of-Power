"""
Friendly Character Creator CLI
A user-friendly command-line interface for the Character Creator system.
"""
import os
import sys
import time
import random
import csv
from typing import Optional, Dict, Any, Tuple
from Character_Creator import (
    Character, ItemRepository, STATS, META_INFO, StatValidator
)
from tier_utils import (
    get_available_classes_for_tier, get_available_professions_for_tier,
    validate_class_tier_combination, validate_profession_tier_combination,
    get_tier_for_level, get_tier_summary
)
from game_data import DEFAULT_TIER_THRESHOLDS, races
from Item_Repo import items

# ============================================================================
# UI Utilities
# ============================================================================

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_colored(text: str, color: str = 'white', bold: bool = False):
    """Print colored text using ANSI escape codes."""
    colors = {
        'black': '30', 'red': '31', 'green': '32', 'yellow': '33',
        'blue': '34', 'magenta': '35', 'cyan': '36', 'white': '37'
    }
    
    bold_code = '1;' if bold else ''
    color_code = colors.get(color.lower(), '37')  # Default to white if color not found
    
    print(f"\033[{bold_code}{color_code}m{text}\033[0m")

def print_header(text: str):
    """Print a formatted header."""
    width = min(get_terminal_width(), 80)
    print()
    print_colored("=" * width, 'cyan', True)
    print_colored(text.center(width), 'cyan', True)
    print_colored("=" * width, 'cyan', True)
    print()

def print_subheader(text: str):
    """Print a formatted subheader."""
    width = min(get_terminal_width(), 80)
    print()
    print_colored("-" * width, 'green')
    print_colored(text.center(width), 'green', True)
    print_colored("-" * width, 'green')
    print()

def print_success(text: str):
    """Print a success message."""
    print_colored(f"✓ {text}", 'green')

def print_error(text: str):
    """Print an error message."""
    print_colored(f"✗ {text}", 'red')

def print_warning(text: str):
    """Print a warning message."""
    print_colored(f"⚠ {text}", 'yellow')

def print_info(text: str):
    """Print an informational message."""
    print_colored(f"ℹ {text}", 'blue')

def print_loading(text: str = "Loading", iterations: int = 3, delay: float = 0.2):
    """Print a loading animation."""
    for _ in range(iterations):
        for dots in range(4):
            clear_screen()
            print(f"{text}{'.' * dots}")
            time.sleep(delay)

def get_terminal_width() -> int:
    """Get the terminal width."""
    try:
        return os.get_terminal_size().columns
    except (AttributeError, OSError):
        return 80

def pause_screen():
    """Pause the screen until the user presses Enter."""
    input("\nPress Enter to continue...")

def confirm_action(prompt: str = "Are you sure?") -> bool:
    """Prompt the user to confirm an action."""
    response = input(f"{prompt} (y/n): ").strip().lower()
    return response in ('y', 'yes')

# ============================================================================
# Menu System
# ============================================================================

def print_inventory_menu(character: Character):
    """Print the inventory management menu."""
    clear_screen()
    print_header(f"{character.name}'s Inventory")
    
    # Display equipped items
    equipped_items = character.inventory.get_equipped_items()
    if equipped_items:
        print_subheader("Equipped Items")
        for i, item in enumerate(equipped_items, 1):
            print(f"{i}. {item.name} - {item.description}")
    else:
        print_info("No items equipped.")
    
    print()
    print_subheader("Inventory Menu")
    print("1. View available items")
    print("2. Add item to inventory")
    print("3. Remove item from inventory")
    print("4. Equip an item")
    print("5. Unequip an item")
    print("6. Reset equipment effects")
    print("0. Back to main menu")

# ============================================================================
# Character Management Functions
# ============================================================================

def create_character(item_repository) -> Character:
    """Create a new character with calculated progression bonuses."""
    clear_screen()
    print_header("Create a New Character")
    
    # Get character name
    while True:
        name = input("Enter character name: ").strip()
        if name:
            break
        print_error("Name cannot be empty.")
    
    # Collect meta information
    meta = {}
    print_subheader(f"Enter information for {name}")
    
    for info in META_INFO:
        while True:
            if "level" in info.lower():
                try:
                    value = input(f"{info}: ").strip()
                    if not value:
                        value = "0"
                    int(value)  # Check if it's a valid integer
                    meta[info] = value
                    break
                except ValueError:
                    print_error("Please enter a valid integer.")
            else:
                value = input(f"{info}: ").strip()
                meta[info] = value
                break
    
    # Collect base stats
    print_subheader(f"Enter base stats for {name}")
    print_info("Default value is 5 if left empty.")
    
    stats = {}
    for stat in STATS:
        while True:
            try:
                value = input(f"{stat.capitalize()}: ").strip()
                if not value:
                    value = "5"  # Default value
                stats[stat] = int(value)
                break
            except ValueError:
                print_error("Please enter a valid integer.")
    
    # Create character using factory method
    character = Character.create_calculated(
        name=name,
        stats=stats,
        meta=meta,
        item_repository=item_repository
    )
    
    print_success(f"Character {name} created successfully!")
    pause_screen()
    return character

def create_advanced_character(item_repository) -> Character:
    """Create a character with full tier history input."""
    clear_screen()
    print_header("Create Advanced Character")
    
    # Get character name
    while True:
        name = input("Enter character name: ").strip()
        if name:
            break
        print_error("Name cannot be empty.")
    
    # Get tier thresholds
    print_subheader(f"Tier Thresholds for {name}")
    print_info("Enter the levels where tier changes occur (e.g., 25, 50, 75)")
    print_info("Default: [25, 50, 75] - press Enter to use default")
    
    while True:
        try:
            threshold_input = input("Enter tier thresholds (comma-separated): ").strip()
            if not threshold_input:
                tier_thresholds = DEFAULT_TIER_THRESHOLDS.copy()
                break
            else:
                # Parse comma-separated values
                tier_thresholds = [int(x.strip()) for x in threshold_input.split(',')]
                tier_thresholds = sorted(list(set(tier_thresholds)))  # Remove duplicates and sort
                break
        except ValueError:
            print_error("Please enter valid integers separated by commas.")
    
    print_success(f"Tier thresholds set to: {tier_thresholds}")
    
    # Collect meta information
    meta = {}
    print_subheader(f"Enter information for {name}")
    
    for info in META_INFO:
        if info in ["Class level", "Profession level"]:
            while True:
                try:
                    value = input(f"{info}: ").strip()
                    if not value:
                        value = "0"
                    int(value)  # Check if it's a valid integer
                    meta[info] = value
                    break
                except ValueError:
                    print_error("Please enter a valid integer.")
        else:
            value = input(f"{info}: ").strip()
            meta[info] = value
    
    # Get class and profession levels for history creation
    class_level = int(meta.get("Class level", "0"))
    profession_level = int(meta.get("Profession level", "0"))
    
    # Create class history dynamically
    class_history = []
    if class_level > 0:
        print_subheader("Class History Setup")
        current_class = meta.get("Class", "")
        
        # Determine how many tiers the character has progressed through
        max_tier = get_tier_for_level(class_level, tier_thresholds)
        
        if max_tier > 1:
            print(f"Character level {class_level} spans {max_tier} tier(s)")
            print("You need to specify the class for each tier:")
            
            level_start = 1
            for tier in range(1, max_tier + 1):
                # Calculate level range for this tier
                if tier < len(tier_thresholds) + 1:
                    if tier == 1:
                        level_end = tier_thresholds[0] - 1
                    elif tier - 1 < len(tier_thresholds):
                        level_end = min(tier_thresholds[tier - 1] - 1, class_level) if tier < len(tier_thresholds) + 1 else class_level
                    else:
                        level_end = class_level
                else:
                    level_end = class_level
                
                # Get available classes for this tier
                available_classes = get_available_classes_for_tier(tier)
                if not available_classes:
                    print_error(f"No classes available for tier {tier}!")
                    pause_screen()
                    return None
                
                print(f"\nTier {tier} (levels {level_start}-{min(level_end, class_level)}):")
                print("Available classes:")
                for i, class_name in enumerate(available_classes, 1):
                    print(f"  {i}. {class_name}")
                
                if tier == max_tier and current_class:
                    tier_class = current_class
                    print(f"Using current class: {tier_class}")
                else:
                    tier_class = input(f"Enter tier {tier} class: ").strip()
                
                # Validate the class
                if not validate_class_tier_combination(tier_class, tier):
                    print_error(f"Invalid class '{tier_class}' for tier {tier}")
                    pause_screen()
                    return None
                
                class_history.append({
                    "class": tier_class,
                    "from_level": level_start,
                    "to_level": min(level_end, class_level) if tier < max_tier else None
                })
                
                level_start = level_end + 1
        else:
            # Single tier character
            class_history.append({
                "class": current_class,
                "from_level": 1,
                "to_level": None
            })
    
    # Create profession history dynamically
    profession_history = []
    if profession_level > 0:
        print_subheader("Profession History Setup")
        current_profession = meta.get("Profession", "")
        
        # Determine how many tiers the character has progressed through
        max_tier = get_tier_for_level(profession_level, tier_thresholds)
        
        if max_tier > 1:
            print(f"Character level {profession_level} spans {max_tier} tier(s)")
            print("You need to specify the profession for each tier:")
            
            level_start = 1
            for tier in range(1, max_tier + 1):
                # Calculate level range for this tier
                if tier < len(tier_thresholds) + 1:
                    if tier == 1:
                        level_end = tier_thresholds[0] - 1
                    elif tier - 1 < len(tier_thresholds):
                        level_end = min(tier_thresholds[tier - 1] - 1, profession_level) if tier < len(tier_thresholds) + 1 else profession_level
                    else:
                        level_end = profession_level
                else:
                    level_end = profession_level
                
                # Get available professions for this tier
                available_professions = get_available_professions_for_tier(tier)
                if not available_professions:
                    print_error(f"No professions available for tier {tier}!")
                    pause_screen()
                    return None
                
                print(f"\nTier {tier} (levels {level_start}-{min(level_end, profession_level)}):")
                print("Available professions:")
                for i, profession_name in enumerate(available_professions, 1):
                    print(f"  {i}. {profession_name}")
                
                if tier == max_tier and current_profession:
                    tier_profession = current_profession
                    print(f"Using current profession: {tier_profession}")
                else:
                    tier_profession = input(f"Enter tier {tier} profession: ").strip()
                
                # Validate the profession
                if not validate_profession_tier_combination(tier_profession, tier):
                    print_error(f"Invalid profession '{tier_profession}' for tier {tier}")
                    pause_screen()
                    return None
                
                profession_history.append({
                    "profession": tier_profession,
                    "from_level": level_start,
                    "to_level": min(level_end, profession_level) if tier < max_tier else None
                })
                
                level_start = level_end + 1
        else:
            # Single tier character
            profession_history.append({
                "profession": current_profession,
                "from_level": 1,
                "to_level": None
            })
    
    # Get base stats
    print_subheader(f"Enter base stats for {name}")
    print_info("These are the raw stat values before any class/profession/race bonuses.")
    print_info("Default value is 5 if left empty.")
    
    base_stats = {}
    for stat in STATS:
        while True:
            try:
                value = input(f"{stat.capitalize()}: ").strip()
                if not value:
                    value = "5"  # Default value
                base_stats[stat] = int(value)
                break
            except ValueError:
                print_error("Please enter a valid integer.")
    
    # Create character with history
    print_loading("Creating advanced character")
    
    # Create character using factory method
    character = Character.create_calculated(
        name=name,
        stats=base_stats,
        meta=meta,
        tier_thresholds=tier_thresholds,
        class_history=class_history,
        profession_history=profession_history,
        item_repository=item_repository
    )
    
    print_success(f"Advanced character {name} created successfully!")
    
    # Display the created history
    print_subheader("Created Character History")
    print(f"Tier thresholds: {tier_thresholds}")
    
    if class_history:
        print("Class History:")
        for entry in class_history:
            level_range = f"Level {entry['from_level']}"
            if entry['to_level'] is not None:
                level_range += f"-{entry['to_level']}"
            else:
                level_range += "+"
            print(f"  {entry['class']} ({level_range})")
    
    if profession_history:
        print("Profession History:")
        for entry in profession_history:
            level_range = f"Level {entry['from_level']}"
            if entry['to_level'] is not None:
                level_range += f"-{entry['to_level']}"
            else:
                level_range += "+"
            print(f"  {entry['profession']} ({level_range})")
    
    pause_screen()
    return character

def create_manual_character(item_repository) -> Character:
    """Create a character with manual stat and level entry (no calculations)."""
    clear_screen()
    print_header("Create Custom Character")
    print_info("Enter final stats directly. No progression rules will be applied or validated.")
    print_warning("This character will not follow class/profession/race progression rules!")
    
    # Get character name
    while True:
        name = input("Enter character name: ").strip()
        if name:
            break
        print_error("Name cannot be empty.")
    
    # Get tier thresholds
    print_subheader(f"Tier Thresholds for {name}")
    print_info("Enter the levels where tier changes occur (e.g., 25, 50, 75)")
    print_info("Default: [25] - press Enter to use default")
    
    while True:
        try:
            threshold_input = input("Enter tier thresholds (comma-separated): ").strip()
            if not threshold_input:
                tier_thresholds = DEFAULT_TIER_THRESHOLDS.copy()
                break
            else:
                tier_thresholds = [int(x.strip()) for x in threshold_input.split(',')]
                tier_thresholds = sorted(list(set(tier_thresholds)))
                break
        except ValueError:
            print_error("Please enter valid integers separated by commas.")
    
    print_success(f"Tier thresholds set to: {tier_thresholds}")
    
    # Collect meta information
    meta = {}
    print_subheader(f"Enter information for {name}")
    
    for info in META_INFO:
        if info in ["Class level", "Profession level"]:
            while True:
                try:
                    value = input(f"{info}: ").strip()
                    if not value:
                        value = "0"
                    int(value)  # Validate it's an integer
                    meta[info] = value
                    break
                except ValueError:
                    print_error("Please enter a valid integer.")
        else:
            value = input(f"{info}: ").strip()
            meta[info] = value
    
    # Get custom stats
    print_subheader(f"Enter custom stats for {name}")
    print_info("Enter the final stat values you want (no calculations will be applied)")
    
    stats = {}
    for stat in STATS:
        while True:
            try:
                value = input(f"{stat.capitalize()}: ").strip()
                if not value:
                    value = "5"  # Default value
                stats[stat] = int(value)
                break
            except ValueError:
                print_error("Please enter a valid integer.")
    
    # Get free points
    while True:
        try:
            free_points = input("Enter available free points: ").strip()
            if not free_points:
                free_points = "0"
            free_points = int(free_points)
            break
        except ValueError:
            print_error("Please enter a valid integer.")
    
    # Create class and profession history if levels > 0
    class_history = []
    profession_history = []
    
    class_level = int(meta.get("Class level", "0"))
    if class_level > 0 and meta.get("Class"):
        class_history = [{
            "class": meta["Class"],
            "from_level": 1,
            "to_level": None
        }]
    
    profession_level = int(meta.get("Profession level", "0"))
    if profession_level > 0 and meta.get("Profession"):
        profession_history = [{
            "profession": meta["Profession"],
            "from_level": 1,
            "to_level": None
        }]
    
    # Create character with manual creation flag
    print_loading("Creating manual character")
    
    # Create character using factory method
    character = Character.create_manual(
        name=name,
        stats=stats,
        meta=meta,
        free_points=free_points,
        tier_thresholds=tier_thresholds,
        item_repository=item_repository
    )
    
    print_success(f"Manual character {name} created successfully!")
    print_info(f"Race level automatically calculated as: {character.data_manager.get_meta('Race level')}")
    
    # Show final character summary
    print_subheader("Character Summary")
    print(f"Name: {character.name}")
    for key, value in character.data_manager.get_all_meta().items():
        print(f"{key}: {value}")
    
    print_subheader("Final Stats")
    for stat in STATS:
        print(f"{stat.capitalize()}: {character.data_manager.get_stat(stat)}")
    
    if character.level_system.free_points > 0:
        print(f"Free Points: {character.level_system.free_points}")
    
    pause_screen()
    return character

def create_reverse_engineered_character(item_repository) -> Character:
    """Create a character that follows progression rules via reverse engineering."""
    clear_screen()
    print_header("Create Reverse-Engineered Character")
    print_info("Enter base stats and current stats. The system will reverse-engineer stat allocation.")
    print_warning("This character must follow class/profession/race progression rules!")
    print()
    print_colored("This mode is perfect for:", 'cyan')
    print("• Importing characters from other character sheets")
    print("• Validating manual calculations")
    print("• Converting existing characters to use this system")
    print()
    
    # Get character name
    while True:
        name = input("Enter character name: ").strip()
        if name:
            break
        print_error("Name cannot be empty.")
    
    # Get tier thresholds
    print_subheader(f"Tier Thresholds for {name}")
    print_info("Enter the levels where tier changes occur (e.g., 25, 50, 75)")
    print_info("Default: [25] - press Enter to use default")
    
    while True:
        try:
            threshold_input = input("Enter tier thresholds (comma-separated): ").strip()
            if not threshold_input:
                tier_thresholds = DEFAULT_TIER_THRESHOLDS.copy()
                break
            else:
                # Parse comma-separated values
                tier_thresholds = [int(x.strip()) for x in threshold_input.split(',')]
                tier_thresholds = sorted(list(set(tier_thresholds)))  # Remove duplicates and sort
                break
        except ValueError:
            print_error("Please enter valid integers separated by commas.")
    
    print_success(f"Tier thresholds set to: {tier_thresholds}")
    
    # Collect meta information
    meta = {}
    print_subheader(f"Enter character information for {name}")
    
    for info in META_INFO:
        if info in ["Class level", "Profession level"]:
            while True:
                try:
                    value = input(f"{info}: ").strip()
                    if not value:
                        value = "0"
                    int(value)  # Check if it's a valid integer
                    meta[info] = value
                    break
                except ValueError:
                    print_error("Please enter a valid integer.")
        else:
            value = input(f"{info}: ").strip()
            meta[info] = value
    
    # Calculate race level for race history setup
    class_level = int(meta.get("Class level", "0"))
    profession_level = int(meta.get("Profession level", "0"))
    calculated_race_level = (class_level + profession_level) // 2
    
    print_info(f"Calculated race level: {calculated_race_level}")
    
    # Create class history if needed (existing logic)
    class_history = []
    if class_level > 0:
        current_class = meta.get("Class", "")
        if current_class:
            print_subheader("Class History Setup")
            
            # Determine how many tiers the character has progressed through
            max_tier = get_tier_for_level(class_level, tier_thresholds)
            
            if max_tier > 1:
                print(f"Character class level {class_level} spans {max_tier} tier(s)")
                print("You need to specify the class for each tier:")
                
                level_start = 1
                for tier in range(1, max_tier + 1):
                    # Calculate level range for this tier
                    if tier == 1:
                        level_end = tier_thresholds[0] - 1 if tier_thresholds else class_level
                    elif tier - 1 < len(tier_thresholds):
                        level_end = min(tier_thresholds[tier - 1] - 1, class_level) if tier < len(tier_thresholds) + 1 else class_level
                    else:
                        level_end = class_level
                    
                    # Get available classes for this tier
                    available_classes = get_available_classes_for_tier(tier)
                    if not available_classes:
                        print_error(f"No classes available for tier {tier}!")
                        pause_screen()
                        return None
                    
                    print(f"\nTier {tier} (levels {level_start}-{min(level_end, class_level)}):")
                    print("Available classes:")
                    for i, class_name in enumerate(available_classes, 1):
                        print(f"  {i}. {class_name}")
                    
                    if tier == max_tier and current_class:
                        tier_class = current_class
                        print(f"Using current class: {tier_class}")
                    else:
                        while True:
                            tier_class = input(f"Enter tier {tier} class: ").strip()
                            if validate_class_tier_combination(tier_class, tier):
                                break
                            print_error(f"Invalid class '{tier_class}' for tier {tier}")
                    
                    class_history.append({
                        "class": tier_class,
                        "from_level": level_start,
                        "to_level": min(level_end, class_level) if tier < max_tier else None
                    })
                    
                    level_start = level_end + 1
            else:
                # Single tier character
                class_history.append({
                    "class": current_class,
                    "from_level": 1,
                    "to_level": None
                })
    
    # Create profession history if needed (existing logic)
    profession_history = []
    if profession_level > 0:
        current_profession = meta.get("Profession", "")
        if current_profession:
            print_subheader("Profession History Setup")
            
            # Determine how many tiers the character has progressed through
            max_tier = get_tier_for_level(profession_level, tier_thresholds)
            
            if max_tier > 1:
                print(f"Character profession level {profession_level} spans {max_tier} tier(s)")
                print("You need to specify the profession for each tier:")
                
                level_start = 1
                for tier in range(1, max_tier + 1):
                    # Calculate level range for this tier
                    if tier == 1:
                        level_end = tier_thresholds[0] - 1 if tier_thresholds else profession_level
                    elif tier - 1 < len(tier_thresholds):
                        level_end = min(tier_thresholds[tier - 1] - 1, profession_level) if tier < len(tier_thresholds) + 1 else profession_level
                    else:
                        level_end = profession_level
                    
                    # Get available professions for this tier
                    available_professions = get_available_professions_for_tier(tier)
                    if not available_professions:
                        print_error(f"No professions available for tier {tier}!")
                        pause_screen()
                        return None
                    
                    print(f"\nTier {tier} (levels {level_start}-{min(level_end, profession_level)}):")
                    print("Available professions:")
                    for i, profession_name in enumerate(available_professions, 1):
                        print(f"  {i}. {profession_name}")
                    
                    if tier == max_tier and current_profession:
                        tier_profession = current_profession
                        print(f"Using current profession: {tier_profession}")
                    else:
                        while True:
                            tier_profession = input(f"Enter tier {tier} profession: ").strip()
                            if validate_profession_tier_combination(tier_profession, tier):
                                break
                            print_error(f"Invalid profession '{tier_profession}' for tier {tier}")
                    
                    profession_history.append({
                        "profession": tier_profession,
                        "from_level": level_start,
                        "to_level": min(level_end, profession_level) if tier < max_tier else None
                    })
                    
                    level_start = level_end + 1
            else:
                # Single tier character
                profession_history.append({
                    "profession": current_profession,
                    "from_level": 1,
                    "to_level": None
                })
    
    # NEW: Create race history if needed (following same pattern)
    race_history = []
    if calculated_race_level > 0:
        current_race = meta.get("Race", "")
        if current_race:
            print_subheader("Race History Setup")
            print(f"Character race level: {calculated_race_level}")
            
            # Check if character might have multiple races
            if calculated_race_level > 5:  # Arbitrary threshold where race changes become likely
                print_info("Characters at higher race levels may have undergone race changes.")
                has_race_changes = confirm_action("Has this character changed races during their progression?")
            else:
                has_race_changes = False
            
            if has_race_changes:
                print("You need to specify the race for different periods of character development:")
                print("Note: Race levels are calculated as (Class Level + Profession Level) ÷ 2")
                
                # Get available races
                available_races = list(races.keys())
                print_subheader("Available Races")
                for i, race in enumerate(available_races, 1):
                    print(f"  {i}. {race}")
                
                race_level_start = 1
                while race_level_start <= calculated_race_level:
                    print(f"\nRace from level {race_level_start} to level ?")
                    
                    # Get race for this period
                    while True:
                        race_choice = input("Enter race (number or name): ").strip()
                        
                        # Try to parse as number first
                        try:
                            race_num = int(race_choice)
                            if 1 <= race_num <= len(available_races):
                                period_race = available_races[race_num - 1]
                                break
                            else:
                                print_error(f"Please enter a number between 1 and {len(available_races)}")
                                continue
                        except ValueError:
                            # Try to match by name
                            period_race = race_choice.lower()
                            if period_race in available_races:
                                break
                            else:
                                print_error(f"Invalid race: {race_choice}")
                                continue
                    
                    # Get end level for this race (if not the last period)
                    if race_level_start < calculated_race_level:
                        while True:
                            try:
                                end_input = input(f"Race level {period_race} ends at level (max {calculated_race_level}): ").strip()
                                race_level_end = int(end_input)
                                
                                if race_level_end < race_level_start:
                                    print_error("End level must be >= start level.")
                                    continue
                                elif race_level_end > calculated_race_level:
                                    print_error(f"End level cannot exceed {calculated_race_level}.")
                                    continue
                                
                                break
                            except ValueError:
                                print_error("Please enter a valid integer.")
                    else:
                        race_level_end = None  # Current race
                    
                    # Add race history entry
                    race_history.append({
                        "race": period_race,
                        "from_race_level": race_level_start,
                        "to_race_level": race_level_end
                    })
                    
                    if race_level_end is None:
                        break
                    else:
                        race_level_start = race_level_end + 1
                
                # Validate current race matches the last entry
                if race_history and race_history[-1]["race"] != current_race.lower():
                    print_warning(f"Current race ({current_race}) doesn't match last race history entry ({race_history[-1]['race']})")
                    if confirm_action("Update current race to match history?"):
                        meta["Race"] = race_history[-1]["race"]
            else:
                # Single race throughout progression
                race_history.append({
                    "race": current_race,
                    "from_race_level": 1,
                    "to_race_level": None
                })
    
    # Get base stats (existing logic)
    print_subheader(f"Enter BASE stats for {name}")
    print_info("These are the character's original stats before ANY bonuses")
    print_info("(e.g., what they rolled for stats, or their starting values)")
    print_warning("Do NOT include class, profession, race, or free point bonuses!")
    
    base_stats = {}
    for stat in STATS:
        while True:
            try:
                value = input(f"Base {stat.capitalize()}: ").strip()
                if not value:
                    value = "5"  # Default value
                base_stats[stat] = int(value)
                break
            except ValueError:
                print_error("Please enter a valid integer.")
    
    # Show base stats summary
    print_subheader("Base Stats Summary")
    total_base = sum(base_stats.values())
    print(f"Base stats: {', '.join(f'{stat}: {value}' for stat, value in base_stats.items())}")
    print(f"Total base stat points: {total_base}")
    
    # Get current stats (existing logic)
    print_subheader(f"Enter CURRENT stats for {name}")
    print_info("These are the character's final stats after ALL bonuses are applied")
    print_info("(class bonuses + profession bonuses + race bonuses + free points + items + blessings)")
    print_warning("These should be the stats the character actually has right now!")
    
    current_stats = {}
    for stat in STATS:
        while True:
            try:
                # Show base stat as reference
                base_value = base_stats[stat]
                value = input(f"Current {stat.capitalize()} (base: {base_value}): ").strip()
                if not value:
                    value = str(base_value)  # Default to base stat if empty
                current_value = int(value)
                
                # Sanity check - current should generally be >= base
                if current_value < base_value:
                    if not confirm_action(f"Current {stat} ({current_value}) is less than base ({base_value}). Continue?"):
                        continue
                
                current_stats[stat] = current_value
                break
            except ValueError:
                print_error("Please enter a valid integer.")
    
    # Show current stats summary and differences
    print_subheader("Current Stats Summary")
    total_current = sum(current_stats.values())
    total_difference = total_current - total_base
    
    print("Current stats vs Base stats:")
    for stat in STATS:
        base = base_stats[stat]
        current = current_stats[stat]
        diff = current - base
        diff_str = f"+{diff}" if diff >= 0 else str(diff)
        print(f"  {stat.capitalize()}: {current} (base: {base}, difference: {diff_str})")
    
    print(f"\nTotal current stat points: {total_current}")
    print(f"Total difference from base: +{total_difference}")
    
    # Get remaining free points (existing logic)
    print_subheader("Free Points")
    print_info("Enter any free points that are currently unallocated")
    print_info("(These are free points the character has but hasn't spent yet)")
    
    while True:
        try:
            free_points_input = input("Enter remaining unallocated free points (default: 0): ").strip()
            if not free_points_input:
                free_points = 0
            else:
                free_points = int(free_points_input)
                if free_points < 0:
                    print_error("Free points cannot be negative.")
                    continue
            break
        except ValueError:
            print_error("Please enter a valid integer.")
    
    # Preview what will happen (updated to include race history and auto-correction)
    print_subheader("Preview")
    print("The system will:")
    print("1. Calculate expected bonuses from class/profession/race progression")
    print("2. Use the provided race history for race bonus calculations")
    print("3. Determine how free points were allocated based on stat differences") 
    print("4. Auto-correct free points if character is missing expected free points")
    print("5. Validate that the math works out correctly")
    print("6. Create a character with full stat source tracking")
    
    if not confirm_action("Create reverse-engineered character with this data?"):
        print_info("Character creation cancelled.")
        pause_screen()
        return None
    
    # Create character using factory method (updated to include race_history)
    print_loading("Creating character and reverse-engineering stat allocation")
    
    try:
        character = Character.create_reverse_engineered(
            name=name,
            base_stats=base_stats,
            current_stats=current_stats,
            meta=meta,
            free_points=free_points,
            tier_thresholds=tier_thresholds,
            class_history=class_history,
            profession_history=profession_history,
            race_history=race_history,  # NEW: Include race history
            item_repository=item_repository
        )
        
        print_success(f"Reverse-engineered character {name} created successfully!")
        
        # Show reverse engineering results (updated to show race history)
        print_subheader("Reverse Engineering Results")
        
        # Use StatValidator to get the analysis
        validator = StatValidator(character)
        analysis = validator.reverse_engineer_stat_allocation(base_stats, current_stats)
        
        # Display expected bonuses
        expected_bonuses = analysis["expected_bonuses"]
        print_colored("Expected Progression Bonuses:", 'cyan', True)
        
        if expected_bonuses["class_free_points"] > 0 or any(expected_bonuses["class"].values()):
            print("Class bonuses:")
            for stat, bonus in expected_bonuses["class"].items():
                if bonus > 0:
                    print(f"  {stat.capitalize()}: +{bonus}")
            if expected_bonuses["class_free_points"] > 0:
                print(f"  Free Points: +{expected_bonuses['class_free_points']}")
        
        if expected_bonuses["profession_free_points"] > 0 or any(expected_bonuses["profession"].values()):
            print("Profession bonuses:")
            for stat, bonus in expected_bonuses["profession"].items():
                if bonus > 0:
                    print(f"  {stat.capitalize()}: +{bonus}")
            if expected_bonuses["profession_free_points"] > 0:
                print(f"  Free Points: +{expected_bonuses['profession_free_points']}")
        
        if expected_bonuses["race_free_points"] > 0 or any(expected_bonuses["race"].values()):
            print("Race bonuses (using race history):")
            for stat, bonus in expected_bonuses["race"].items():
                if bonus > 0:
                    print(f"  {stat.capitalize()}: +{bonus}")
            if expected_bonuses["race_free_points"] > 0:
                print(f"  Free Points: +{expected_bonuses['race_free_points']}")
        
        # Display race history used
        if character.data_manager.race_history:
            print_colored("\nRace History Applied:", 'cyan', True)
            for entry in character.data_manager.race_history:
                level_range = f"Race Level {entry['from_race_level']}"
                if entry['to_race_level'] is not None:
                    level_range += f"-{entry['to_race_level']}"
                else:
                    level_range += "+"
                print(f"  {entry['race']}: {level_range}")
        
        # Display free points analysis (updated to show auto-correction)
        print_colored("\nFree Points Analysis:", 'cyan', True)
        print(f"Total free points from progression: {analysis['total_expected_free_points']}")
        print(f"Free points used in stat allocation: {analysis['total_free_points_used']}")
        
        # Check if free points were auto-corrected
        expected_remaining = analysis['remaining_free_points']
        actual_remaining = character.level_system.free_points
        
        if actual_remaining != free_points:
            print(f"Provided remaining free points: {free_points}")
            print(f"Auto-corrected remaining free points: {actual_remaining}")
            print_success(f"✓ Added {actual_remaining - free_points} missing free points")
        else:
            print(f"Remaining free points: {actual_remaining}")
        
        # Show the math
        total_accounted = analysis['total_free_points_used'] + actual_remaining
        if total_accounted == analysis['total_expected_free_points']:
            print_success(f"✓ Free points balance correctly: {analysis['total_free_points_used']} + {actual_remaining} = {analysis['total_expected_free_points']}")
        else:
            discrepancy = analysis['total_expected_free_points'] - total_accounted
            if discrepancy > 0:
                print_warning(f"⚠ Still missing {discrepancy} free points after correction")
            else:
                print_warning(f"⚠ Character has {abs(discrepancy)} excess free points")
        
        # Display detailed stat allocation
        print_colored("\nDetailed Stat Allocation:", 'cyan', True)
        for stat in STATS:
            stat_analysis = analysis["stat_allocations"][stat]
            base = stat_analysis["base"]
            class_bonus = stat_analysis["class_bonus"]
            profession_bonus = stat_analysis["profession_bonus"]
            race_bonus = stat_analysis["race_bonus"]
            free_points_used = stat_analysis["free_points_allocated"]
            current = stat_analysis["current"]
            
            # Build breakdown string
            parts = [f"Base: {base}"]
            if class_bonus > 0:
                parts.append(f"Class: +{class_bonus}")
            if profession_bonus > 0:
                parts.append(f"Profession: +{profession_bonus}")
            if race_bonus > 0:
                parts.append(f"Race: +{race_bonus}")
            if free_points_used > 0:
                parts.append(f"Free Points: +{free_points_used}")
            
            breakdown = " + ".join(parts)
            print(f"{stat.capitalize()}: {breakdown} = {current}")
            
            # Check for discrepancies
            if stat_analysis["discrepancy"] < 0:
                print_error(f"  ⚠ ISSUE: {stat} requires {abs(stat_analysis['discrepancy'])} more points than available!")
        
        # Validate the character (updated to account for auto-correction)
        print_subheader("Validation Results")
        validation_result = character.validate_stats()
        
        if validation_result["valid"]:
            print_success("✓ Character validation passed!")
            print_info("All stat allocations follow progression rules correctly.")
        else:
            print_error("✗ Character validation failed!")
            print_warning("There are issues with the stat allocation:")
            
            if validation_result.get("stat_discrepancies"):
                for stat, issue in validation_result["stat_discrepancies"].items():
                    print_error(f"  {stat}: {issue}")
            
            # Check if free points are still mismatched after auto-correction
            fp_info = validation_result.get("free_points", {})
            if not fp_info.get("free_points_match", True):
                expected = fp_info.get('calculated_remaining', 0)
                actual = fp_info.get('actual_remaining', 0)
                if expected != actual:
                    print_error(f"  Free points still mismatched after auto-correction: expected {expected}, got {actual}")
                    print_info("    This suggests an error in the progression rules or input data")
        
        # Additional check for impossible stat allocations
        impossible_allocations = []
        for stat in STATS:
            stat_analysis = analysis["stat_allocations"][stat]
            if stat_analysis["discrepancy"] < 0:
                impossible_allocations.append(f"{stat}: needs {abs(stat_analysis['discrepancy'])} more points")
        
        if impossible_allocations:
            print_error("✗ Impossible stat allocations detected:")
            for allocation in impossible_allocations:
                print_error(f"  {allocation}")
            print_info("These stats require more points than available from progression rules")
        
        # Show final character summary (existing logic)
        print_subheader("Character Summary")
        print(f"Name: {character.name}")
        
        for key, value in character.data_manager.get_all_meta().items():
            print(f"{key}: {value}")
        
        print("\nFinal Stats:")
        for stat in STATS:
            sources = character.data_manager.get_stat_sources(stat)
            current = character.data_manager.get_stat(stat)
            modifier = character.data_manager.get_stat_modifier(stat)
            
            # Show sources if more than just base
            if len([s for s, v in sources.items() if v > 0]) > 1:
                source_parts = []
                for source, value in sources.items():
                    if value > 0:
                        source_parts.append(f"{source}: {value}")
                source_str = " (" + " + ".join(source_parts) + ")"
                print(f"  {stat.capitalize()}: {current}{source_str} (modifier: {modifier})")
            else:
                print(f"  {stat.capitalize()}: {current} (modifier: {modifier})")
        
        if character.level_system.free_points > 0:
            print(f"\nUnallocated Free Points: {character.level_system.free_points}")
        
        # Final success message (updated to account for auto-correction)
        print()
        if validation_result["valid"]:
            print_success("🎉 Reverse-engineered character created and validated successfully!")
            if character.level_system.free_points > free_points:
                print_info(f"💡 Auto-corrected free points from {free_points} to {character.level_system.free_points}")
            print_info("This character can now be used normally in the system.")
        elif impossible_allocations:
            print_error("❌ Character creation failed due to impossible stat allocations.")
            print_info("Please review your input data - the current stats require more points than the progression rules provide.")
        else:
            print_warning("⚠ Character created but has validation issues.")
            print_info("You may want to review the input data and try again.")
        
        pause_screen()
        return character
        
    except Exception as e:
        print_error(f"Error creating reverse-engineered character: {str(e)}")
        print_info("Please check your input data and try again.")
        pause_screen()
        return None

def load_character(item_repository) -> Tuple[Optional[Character], Optional[str]]:
    """Load a character from a CSV file."""
    clear_screen()
    print_header("Load Character")
    
    filename = input("Enter the CSV filename to load from: ").strip()
    if not filename.endswith('.csv'):
        filename += '.csv'
    
    if not os.path.exists(filename):
        print_error(f"File {filename} does not exist.")
        pause_screen()
        return None, None
    
    name = input("Enter the character name to load: ").strip()
    if not name:
        print_error("Name cannot be empty.")
        pause_screen()
        return None, None
    
    try:
        print_loading("Loading character")
        # Use factory method for loading
        character = Character.load_from_file(filename, name, item_repository)
        
        if character:
            print_success(f"Character {name} loaded successfully!")
            pause_screen()
            return character, filename
        else:
            print_error(f"Character {name} not found in {filename}.")
            pause_screen()
            return None, None
    except Exception as e:
        print_error(f"Error loading character: {str(e)}")
        pause_screen()
        return None, None

def view_character(character: Character):
    """Display detailed character information."""
    clear_screen()
    print_header(f"Character Details: {character.name}")
    
    # Meta information
    print_subheader("Character Info")
    for meta, value in character.data_manager.get_all_meta().items():
        print(f"{meta}: {value}")
    
    # Stats
    print_subheader("Stats")
    for stat in STATS:
        sources = character.data_manager.get_stat_sources(stat)
        current = character.data_manager.get_stat(stat)
        modifier = character.data_manager.get_stat_modifier(stat)
        
        # Format source breakdown if more than just base
        if len(sources) > 1:
            source_str = " (" + " + ".join(f"{source}: {value}" for source, value in sources.items() if source != "base" and value != 0) + ")"
            print(f"{stat.capitalize()}: {sources.get('base', 0)}{source_str} = {current} (modifier: {modifier})")
        else:
            print(f"{stat.capitalize()}: {current} (modifier: {modifier})")
    
    # Health
    print_subheader("Health")
    print(f"Current Health: {character.health_manager.current_health}/{character.health_manager.max_health}")
    
    # Free points
    if character.level_system.free_points > 0:
        print_subheader("Free Points")
        print(f"Available: {character.level_system.free_points}")
    
    # Blessing
    if hasattr(character, 'blessing') and character.blessing:
        print_subheader("Blessing")
        for stat, value in character.blessing.items():
            print(f"{stat.capitalize()}: +{value}")
    
    # Inventory
    print_subheader("Equipped Items")
    equipped_items = character.inventory.get_equipped_items()
    if equipped_items:
        for item in equipped_items:
            print(f"{item.name}: {item.description}")
            if item.stats:
                print("  Stats: " + ", ".join(f"{s}: +{v}" for s, v in item.stats.items()))
    else:
        print("No items equipped.")
    
    pause_screen()

def view_character_history(character: Character):
    """Display character's class, profession, and race history."""
    clear_screen()
    print_header(f"Character History: {character.name}")
    
    # Display tier thresholds and summary
    print_subheader("Tier Information")
    print(f"Tier thresholds: {character.data_manager.tier_thresholds}")
    
    # Show tier summary
    tier_summary = get_tier_summary(character.data_manager.tier_thresholds)
    for tier, info in tier_summary.items():
        level_range = info["level_range"]
        if level_range[1] == 999:
            range_str = f"{level_range[0]}+"
        else:
            range_str = f"{level_range[0]}-{level_range[1]}"
        print(f"  Tier {tier}: Level {range_str}")
    
    # Display class history
    if character.data_manager.class_history:
        print_subheader("Class History")
        for entry in character.data_manager.class_history:
            level_range = f"Level {entry['from_level']}"
            if entry['to_level'] is not None:
                level_range += f"-{entry['to_level']}"
            else:
                level_range += "+"
            tier = get_tier_for_level(entry['from_level'], character.data_manager.tier_thresholds)
            print(f"  {entry['class']} ({level_range}) [Tier {tier}]")
    else:
        print_info("No class history available.")
    
    # Display profession history
    if character.data_manager.profession_history:
        print_subheader("Profession History")
        for entry in character.data_manager.profession_history:
            level_range = f"Level {entry['from_level']}"
            if entry['to_level'] is not None:
                level_range += f"-{entry['to_level']}"
            else:
                level_range += "+"
            tier = get_tier_for_level(entry['from_level'], character.data_manager.tier_thresholds)
            print(f"  {entry['profession']} ({level_range}) [Tier {tier}]")
    else:
        print_info("No profession history available.")
    
    # NEW: Display race history
    if character.data_manager.race_history:
        print_subheader("Race History")
        for entry in character.data_manager.race_history:
            level_range = f"Race Level {entry['from_race_level']}"
            if entry['to_race_level'] is not None:
                level_range += f"-{entry['to_race_level']}"
            else:
                level_range += "+"
            print(f"  {entry['race']} ({level_range})")
    else:
        print_info("No race history available.")
    
    pause_screen()
    
def manage_race_history(character: Character):
    """Manage character's race history."""
    while True:
        clear_screen()
        print_header(f"Race History Management: {character.name}")
        
        # Display current race and level
        current_race = character.data_manager.get_meta("Race", "")
        current_race_level = int(character.data_manager.get_meta("Race level", "0"))
        
        print_subheader("Current Race Status")
        print(f"Current Race: {current_race}")
        print(f"Current Race Level: {current_race_level}")
        
        # Display race history
        if character.data_manager.race_history:
            print_subheader("Race History")
            for i, entry in enumerate(character.data_manager.race_history, 1):
                level_range = f"Race Level {entry['from_race_level']}"
                if entry['to_race_level'] is not None:
                    level_range += f"-{entry['to_race_level']}"
                else:
                    level_range += "+"
                print(f"{i}. {entry['race']} ({level_range})")
        else:
            print_info("No race history available.")
        
        print_subheader("Race History Management")
        print("1. Add race change")
        print("2. View detailed race progression")
        print("0. Back to main menu")
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == '0':
            return
        elif choice == '1':
            add_race_change(character)
        elif choice == '2':
            view_race_progression(character)
        else:
            print_error("Invalid choice.")
            pause_screen()
            
def add_race_change(character: Character):
    """Add a race change to the character's history."""
    clear_screen()
    print_header("Add Race Change")
    
    current_race = character.data_manager.get_meta("Race", "")
    current_race_level = int(character.data_manager.get_meta("Race level", "0"))
    
    print_subheader("Current Status")
    print(f"Current Race: {current_race}")
    print(f"Current Race Level: {current_race_level}")
    
    # Display available races
    print_subheader("Available Races")
    available_races = list(races.keys())
    for i, race in enumerate(available_races, 1):
        print(f"{i}. {race}")
    
    # Get new race
    while True:
        choice = input("\nEnter new race (number or name): ").strip()
        
        # Try to parse as number first
        try:
            race_num = int(choice)
            if 1 <= race_num <= len(available_races):
                new_race = available_races[race_num - 1]
                break
            else:
                print_error(f"Please enter a number between 1 and {len(available_races)}")
                continue
        except ValueError:
            # Try to match by name
            new_race = choice.lower()
            if new_race in available_races:
                break
            else:
                print_error(f"Invalid race: {choice}")
                continue
    
    if new_race == current_race.lower():
        print_error("Character is already that race.")
        pause_screen()
        return
    
    # Get the race level at which the change occurs
    while True:
        try:
            change_level = input(f"At what race level does the change occur? (current: {current_race_level}): ").strip()
            if not change_level:
                change_level = current_race_level + 1
            else:
                change_level = int(change_level)
            
            if change_level < 1:
                print_error("Race level must be positive.")
                continue
            elif change_level <= current_race_level:
                if not confirm_action(f"This will change race at level {change_level}, affecting past progression. Continue?"):
                    continue
            
            break
        except ValueError:
            print_error("Please enter a valid integer.")
    
    # Confirm the change
    print_subheader("Confirm Race Change")
    print(f"Change from: {current_race}")
    print(f"Change to: {new_race}")
    print(f"At race level: {change_level}")
    
    if confirm_action("Apply this race change?"):
        success = character.change_race_at_level(new_race, change_level)
        
        if success:
            print_success(f"Race changed to {new_race} at race level {change_level}")
            print_info("Race bonuses have been recalculated.")
        else:
            print_error("Failed to change race.")
    else:
        print_info("Race change cancelled.")
    
    pause_screen()
    
def view_race_progression(character: Character):
    """View detailed race progression breakdown."""
    clear_screen()
    print_header("Detailed Race Progression")
    
    race_level = int(character.data_manager.get_meta("Race level", "0"))
    
    if race_level == 0:
        print_error("Character has no race levels.")
        pause_screen()
        return
    
    print_subheader("Race Progression Breakdown")
    
    # Show progression for each race level
    for level in range(1, race_level + 1):
        race_at_level = character.data_manager.get_race_at_race_level(level)
        
        if race_at_level:
            print(f"Race Level {level}: {race_at_level}")
            
            # Show what bonuses were gained at this level
            race_data = races.get(race_at_level.lower(), {})
            rank_ranges = race_data.get("rank_ranges", [])
            
            for range_data in sorted(rank_ranges, key=lambda x: x["min_level"]):
                if range_data["min_level"] <= level <= range_data["max_level"]:
                    bonuses = range_data.get("stats", {})
                    if bonuses:
                        bonus_strs = []
                        for stat, value in bonuses.items():
                            if value > 0:
                                bonus_strs.append(f"{stat}: +{value}")
                        if bonus_strs:
                            print(f"  Bonuses: {', '.join(bonus_strs)}")
                    
                    if "rank" in range_data:
                        print(f"  Rank: {range_data['rank']}")
                    break
        else:
            print(f"Race Level {level}: No race data")
    
    pause_screen()

def validate_character_stats(character: Character):
    """Enhanced validation display with automatic conversion."""
    clear_screen()
    print_header(f"Character Validation: {character.name}")
    
    # Show current character type
    creation_info = character.get_creation_info()
    print_subheader("Character Information")
    print(f"Type: {creation_info['current_type']}")
    if creation_info.get('original_type'):
        print(f"Originally: {creation_info['original_type']}")
        print(f"Converted: {creation_info['converted_at']}")
    print(f"Validation status: {character.validation_status}")
    
    print_loading("Validating character stats")
    
    # Get validation results (this may trigger conversion)
    validation_result = character.validate_stats()
    
    # Check if conversion happened
    if validation_result.get("converted_to_calculated", False):
        print()
        print_success("🎉 Manual character automatically converted to calculated character!")
        print_info(validation_result.get("conversion_message", "Character converted successfully"))
        print_warning("Original manual data archived in creation history")
        print()
    
    # Display validation results
    if validation_result["valid"]:
        print_success("Character validation passed!")
    else:
        print_error("Character validation failed!")
    
    print_subheader("Validation Details")
    print(f"Validation type: {validation_result.get('validation_type', 'unknown')}")
    print(f"Overall summary: {validation_result.get('overall_summary', 'No summary available')}")
    
    # Display specific validation results based on type
    if validation_result.get("validation_type") == "reverse_engineered_manual":
        # Show reverse engineering details
        if validation_result.get("details"):
            details = validation_result["details"]
            print_subheader("Reverse Engineering Analysis")
            print(f"Expected free points: {details.get('total_expected_free_points', 0)}")
            print(f"Used free points: {details.get('total_free_points_used', 0)}")
            print(f"Remaining: {details.get('remaining_free_points', 0)}")
    
    elif validation_result.get("validation_type") == "custom_manual":
        # Show custom validation results
        if validation_result.get("custom_validation"):
            custom = validation_result["custom_validation"]
            print_subheader("Custom Character Checks")
            print(f"Race level correct: {'✓' if custom.get('race_level_correct') else '✗'}")
            print(f"Stats reasonable: {'✓' if custom.get('stats_reasonable') else '✗'}")
            print(f"Free points valid: {'✓' if custom.get('free_points_valid') else '✗'}")
    
    elif validation_result.get("validation_type") == "calculated":
        # Show calculated character validation
        if validation_result.get("stat_discrepancies"):
            print_subheader("Stat Discrepancies")
            for stat, discrepancy in validation_result["stat_discrepancies"].items():
                status = discrepancy["status"]
                diff = discrepancy["difference"]
                print_error(f"{stat}: {status} by {abs(diff)} points")
    
    # Show warnings and errors
    if validation_result.get("warnings"):
        print_subheader("Warnings")
        for warning in validation_result["warnings"]:
            print_warning(warning)
    
    if validation_result.get("errors"):
        print_subheader("Errors") 
        for error in validation_result["errors"]:
            print_error(error)
    
    # Show character type after validation
    updated_creation_info = character.get_creation_info()
    if updated_creation_info != creation_info:
        print_subheader("Character Status Updated")
        print(f"New type: {updated_creation_info['current_type']}")
        print(f"Validation status: {character.validation_status}")
    
    pause_screen()

def show_detailed_stat_breakdown(character: Character, validation_result: Dict[str, Any]):
    """Show detailed breakdown of stat sources - same for all character types."""
    clear_screen()
    print_header("Detailed Stat Source Breakdown")
    
    # Show creation info
    creation_info = character.get_creation_info()
    print_subheader("Character Information")
    print(f"Type: {creation_info['current_type']}")
    if creation_info.get('original_type'):
        print(f"Originally: {creation_info['original_type']}")
    print(f"Validation status: {character.validation_status}")
    
    # Show stat sources - same for ALL character types
    print_subheader("Current Stat Sources")
    for stat in STATS:
        sources = character.data_manager.get_stat_sources(stat)
        current = character.data_manager.get_stat(stat)
        modifier = character.data_manager.get_stat_modifier(stat)
        
        # Build breakdown string
        source_parts = []
        for source, value in sources.items():
            if value > 0:
                source_parts.append(f"{source}: {value}")
        
        if len(source_parts) > 1:
            source_str = " (" + " + ".join(source_parts) + ")"
            print(f"{stat.capitalize()}: {current}{source_str} (modifier: {modifier})")
        else:
            print(f"{stat.capitalize()}: {current} (modifier: {modifier})")
    
    # Show free points if any
    if character.level_system.free_points > 0:
        print_subheader("Unallocated Points")
        print(f"Free points remaining: {character.level_system.free_points}")
    
    # Show validation-specific issues only if invalid
    if not validation_result.get("valid", True):
        print_subheader("Validation Issues")
        
        # Show stat discrepancies for any character type
        if validation_result.get("stat_discrepancies"):
            print("Stat discrepancies found:")
            for stat, discrepancy in validation_result["stat_discrepancies"].items():
                if "difference" in discrepancy:
                    diff = discrepancy["difference"]
                    diff_str = f"+{diff}" if diff > 0 else str(diff)
                    print_error(f"  {stat}: {diff_str} points")
                elif "impossible_allocation" in discrepancy:
                    print_error(f"  {stat}: impossible allocation")
        
        # Show free points issues
        if validation_result.get("free_points") and isinstance(validation_result["free_points"], dict):
            fp_info = validation_result["free_points"]
            if fp_info.get("difference", 0) != 0:
                diff = fp_info["difference"]
                print_error(f"Free points discrepancy: {diff}")
    
    pause_screen()

def update_stats(character: Character):
    """Update character stats."""
    clear_screen()
    print_header(f"Update Stats: {character.name}")
    
    # Display current stats
    print_subheader("Current Stats")
    for stat in STATS:
        print(f"{stat.capitalize()}: {character.data_manager.get_stat(stat)}")
    
    # Get stat to update
    print()
    stat = input("Enter the stat to update (or 'cancel'): ").lower().strip()
    
    if stat == 'cancel':
        return
    
    if stat not in STATS:
        print_error(f"Invalid stat. Available stats: {', '.join(STATS)}")
        pause_screen()
        return
    
    # Get new value
    try:
        value = int(input(f"Enter new value for {stat}: "))
        
        # Confirm if the change is large
        current = character.data_manager.get_stat(stat)
        if abs(value - current) > 10:
            if not confirm_action(f"This is a large change ({current} to {value}). Are you sure?"):
                print_info("Update canceled.")
                pause_screen()
                return
        
        # Update the stat
        character.update_stat(stat, value)
        
        print_success(f"Updated {stat} to {value}")
    except ValueError:
        print_error("Please enter a valid integer.")
    
    pause_screen()

def update_meta(character: Character):
    """Update character meta information."""
    clear_screen()
    print_header(f"Update Meta Info: {character.name}")
    
    # Display current meta info
    print_subheader("Current Meta Info")
    for meta, value in character.data_manager.get_all_meta().items():
        print(f"{meta}: {value}")
    
    # Get meta info to update
    print()
    info = input("Enter the meta info to update (or 'cancel'): ").strip()
    
    if info.lower() == 'cancel':
        return
    
    if info not in META_INFO:
        print_error(f"Invalid meta info. Available meta info: {', '.join(META_INFO)}")
        pause_screen()
        return
    
    # Get new value
    value = input(f"Enter new value for {info}: ").strip()
    
    # Update the meta info
    result = character.update_meta(info, value)
    
    if result:
        print_success(f"Updated {info} to {value}")
    else:
        print_error(f"Failed to update {info}.")
    
    pause_screen()

def level_up_character(character: Character):
    """Level up a character with dynamic tier change detection."""
    clear_screen()
    print_header(f"Level Up: {character.name}")
    
    # Display current levels
    print_subheader("Current Levels")
    for info, value in character.data_manager.get_all_meta().items():
        if "level" in info.lower():
            print(f"{info}: {value}")
    
    # Display tier thresholds
    print_info(f"Tier thresholds: {character.data_manager.tier_thresholds}")
    
    # Get level type
    print()
    level_type = input("Enter level type (Class or Profession, or 'cancel'): ").strip()
    
    if level_type.lower() == 'cancel':
        return
    
    if level_type.lower() not in ["class", "profession"]:
        print_error("Invalid level type. Must be 'Class' or 'Profession'.")
        pause_screen()
        return
    
    # Get current level
    try:
        current_level = int(character.data_manager.get_meta(f"{level_type} level", "0"))
        
        # Get target level
        target_level = int(input(f"Enter target level (current: {current_level}): "))
        
        if target_level <= current_level:
            print_error(f"{character.name} is already at or above level {target_level} for {level_type}.")
            pause_screen()
            return
            
        # Check if crossing ANY tier threshold using character's thresholds
        next_threshold = character.data_manager.get_next_tier_threshold(current_level)
        
        if next_threshold and current_level < next_threshold <= target_level:
            current_tier = get_tier_for_level(current_level, character.data_manager.tier_thresholds)
            next_tier = current_tier + 1
            
            if level_type.lower() == "class":
                print_subheader(f"Class Tier {next_tier} Change")
                print(f"Ready to advance to tier {next_tier} class at level {next_threshold}!")
                
                # Display current class history
                if character.data_manager.class_history:
                    print_subheader("Class History")
                    for entry in character.data_manager.class_history:
                        level_range = f"Level {entry['from_level']}"
                        if entry['to_level'] is not None:
                            level_range += f"-{entry['to_level']}"
                        else:
                            level_range += "+"
                        tier = get_tier_for_level(entry['from_level'], character.data_manager.tier_thresholds)
                        print(f"  {entry['class']} ({level_range}) [Tier {tier}]")
                
                # Get available classes for the next tier
                available_classes = get_available_classes_for_tier(next_tier)
                
                if not available_classes:
                    print_error(f"No tier {next_tier} classes available yet!")
                    pause_screen()
                    return
                
                # Display options
                print_subheader(f"Available Tier {next_tier} Classes")
                for i, class_name in enumerate(available_classes, 1):
                    print(f"{i}. {class_name}")
                
                # Get selection
                while True:
                    selection = input(f"\nEnter your new tier {next_tier} class (number or name): ").strip()
                    
                    # Try to parse as number first
                    try:
                        choice_num = int(selection)
                        if 1 <= choice_num <= len(available_classes):
                            new_class = available_classes[choice_num - 1]
                            break
                        else:
                            print_error(f"Please enter a number between 1 and {len(available_classes)}")
                            continue
                    except ValueError:
                        # Try to match by name
                        new_class = selection.lower()
                        if validate_class_tier_combination(new_class, next_tier):
                            break
                        else:
                            print_error(f"Invalid tier {next_tier} class: {selection}")
                            continue
                
                # Change class before leveling up
                print_loading(f"Changing class to {new_class}")
                success = character.change_class(new_class, next_threshold)
                if not success:
                    print_error("Failed to change class. Aborting level up.")
                    pause_screen()
                    return
                    
                print_success(f"Class changed to {new_class} at level {next_threshold}")
                
            elif level_type.lower() == "profession":
                print_subheader(f"Profession Tier {next_tier} Change")
                print(f"Ready to advance to tier {next_tier} profession at level {next_threshold}!")
                
                # Display current profession history
                if character.data_manager.profession_history:
                    print_subheader("Profession History")
                    for entry in character.data_manager.profession_history:
                        level_range = f"Level {entry['from_level']}"
                        if entry['to_level'] is not None:
                            level_range += f"-{entry['to_level']}"
                        else:
                            level_range += "+"
                        tier = get_tier_for_level(entry['from_level'], character.data_manager.tier_thresholds)
                        print(f"  {entry['profession']} ({level_range}) [Tier {tier}]")
                
                # Get available professions for the next tier
                available_professions = get_available_professions_for_tier(next_tier)
                
                if not available_professions:
                    print_error(f"No tier {next_tier} professions available yet!")
                    pause_screen()
                    return
                
                # Display options
                print_subheader(f"Available Tier {next_tier} Professions")
                for i, profession_name in enumerate(available_professions, 1):
                    print(f"{i}. {profession_name}")
                
                # Get selection
                while True:
                    selection = input(f"\nEnter your new tier {next_tier} profession (number or name): ").strip()
                    
                    # Try to parse as number first
                    try:
                        choice_num = int(selection)
                        if 1 <= choice_num <= len(available_professions):
                            new_profession = available_professions[choice_num - 1]
                            break
                        else:
                            print_error(f"Please enter a number between 1 and {len(available_professions)}")
                            continue
                    except ValueError:
                        # Try to match by name
                        new_profession = selection.lower()
                        if validate_profession_tier_combination(new_profession, next_tier):
                            break
                        else:
                            print_error(f"Invalid tier {next_tier} profession: {selection}")
                            continue
                
                # Change profession before leveling up
                print_loading(f"Changing profession to {new_profession}")
                success = character.change_profession(new_profession, next_threshold)
                if not success:
                    print_error("Failed to change profession. Aborting level up.")
                    pause_screen()
                    return
                    
                print_success(f"Profession changed to {new_profession} at level {next_threshold}")
        
        # Now proceed with level up
        print_loading(f"Leveling up {level_type}")
        
        success = character.level_up(level_type, target_level)
        
        if success:
            print_success(f"Leveled up {level_type} to {target_level}")
            
            # Display stat gains
            print_subheader("Updated Stats")
            for stat in STATS:
                print(f"{stat.capitalize()}: {character.data_manager.get_stat(stat)}")
            
            # Check for free points
            if character.level_system.free_points > 0:
                print_info(f"You have {character.level_system.free_points} free points to allocate.")
            
            # Ask about blessing
            if confirm_action("Do you want to add a blessing?"):
                add_blessing(character)
        else:
            print_error(f"Failed to level up {level_type}.")
    
    except ValueError:
        print_error("Please enter valid integer values for levels.")
    
    pause_screen()
    
def bulk_level_characters(item_repository):
    """Bulk level multiple characters from a CSV file with level type and target level."""
    clear_screen()
    print_header("Bulk Level Characters")
    
    # Get the CSV file with character leveling data
    leveling_file = input("Enter the CSV filename containing character target levels: ").strip()
    if not leveling_file.endswith('.csv'):
        leveling_file += '.csv'
    
    if not os.path.exists(leveling_file):
        print_error(f"File {leveling_file} does not exist.")
        print_info(f"Current directory: {os.getcwd()}")
        pause_screen()
        return
    
    # Get the main character database file
    character_file = input("Enter the character repo CSV filename: ").strip()
    if not character_file.endswith('.csv'):
        character_file += '.csv'
    
    if not os.path.exists(character_file):
        print_error(f"File {character_file} does not exist.")
        print_info(f"Current directory: {os.getcwd()}")
        pause_screen()
        return
    
    # Ask about free point allocation method
    print_subheader("Free Point Allocation Method")
    print("1. Ask for each character individually")
    print("2. Allocate randomly for all characters")
    print("3. Save all free points for later")
    
    allocation_method = input("Choose allocation method (1-3): ").strip()
    if allocation_method not in ['1', '2', '3']:
        print_error("Invalid choice.")
        pause_screen()
        return
    
    # Read character leveling data from CSV
    leveling_data = []
    try:
        # Use utf-8-sig encoding to automatically handle UTF-8 BOM from Excel
        with open(leveling_file, 'r', newline='', encoding='utf-8-sig') as file:
            # Try to detect if it has headers
            sample = file.read(1024)
            file.seek(0)
            
            # Check if first line looks like headers
            first_line = sample.split('\n')[0] if sample else ""
            has_header = any(keyword in first_line.lower() for keyword in ['name', 'level', 'type', 'target'])
            
            reader = csv.reader(file)
            
            if has_header:
                headers = next(reader)  # Skip header and store for reference
                print_info(f"Detected headers: {', '.join(headers)}")
            
            for row_num, row in enumerate(reader, start=2 if has_header else 1):
                if len(row) < 3:
                    print_warning(f"Skipping row {row_num}: insufficient columns (need 3, got {len(row)})")
                    continue
                
                if not all(cell.strip() for cell in row[:3]):  # Check first 3 columns aren't empty
                    print_warning(f"Skipping row {row_num}: empty required fields")
                    continue
                
                name = row[0].strip()
                level_type = row[1].strip()
                
                # Validate level type and normalize case
                if level_type.lower() not in ["class", "profession"]:
                    print_error(f"Row {row_num}: Invalid level type '{level_type}'. Must be 'Class' or 'Profession'.")
                    continue
                
                # Normalize case to match META_INFO constants
                level_type = level_type.lower().capitalize()  # "class" -> "Class", "profession" -> "Profession"
                
                # Validate target level
                try:
                    target_level = int(row[2].strip())
                    if target_level <= 0:
                        print_error(f"Row {row_num}: Target level must be positive, got {target_level}")
                        continue
                except ValueError:
                    print_error(f"Row {row_num}: Invalid target level '{row[2]}'. Must be a positive integer.")
                    continue
                
                leveling_data.append({
                    'name': name,
                    'level_type': level_type,
                    'target_level': target_level,
                    'row_num': row_num
                })
    
    except Exception as e:
        print_error(f"Error reading leveling data file: {str(e)}")
        pause_screen()
        return
    
    if not leveling_data:
        print_error("No valid leveling data found in the file.")
        pause_screen()
        return
    
    print_success(f"Found {len(leveling_data)} valid leveling operations:")
    for data in leveling_data:
        print(f"  - {data['name']}: {data['level_type']} level to {data['target_level']}")
    
    if not confirm_action(f"Process {len(leveling_data)} leveling operations?"):
        return
    
    # Process each character
    processed = 0
    errors = 0
    skipped = 0
    
    for i, data in enumerate(leveling_data, 1):
        name = data['name']
        level_type = data['level_type']
        target_level = data['target_level']
        
        clear_screen()
        print_header(f"Processing {i}/{len(leveling_data)}: {name}")
        print_info(f"Operation: {level_type} level to {target_level}")
        
        # Load the character
        try:
            character = Character.load(character_file, name, item_repository)
            
            if not character:
                print_error(f"Character '{name}' not found in {character_file}.")
                errors += 1
                pause_screen()  # Pause for errors
                continue
            
            # Check current level
            current_level = int(character.data_manager.get_meta(f"{level_type} level", "0"))
            
            if target_level <= current_level:
                print_warning(f"{name} is already at or above {level_type} level {target_level} (current: {current_level}).")
                skipped += 1
                # No pause for skipped characters - just continue
                continue
            
            print_info(f"Current {level_type} level: {current_level}")
            print_info(f"Target {level_type} level: {target_level}")
            
            # Check for tier changes using existing logic from level_up_character()
            needs_pause = False  # Track if user interaction occurred
            next_threshold = character.data_manager.get_next_tier_threshold(current_level)
            
            if next_threshold and current_level < next_threshold <= target_level:
                needs_pause = True  # Tier change requires user input
                current_tier = get_tier_for_level(current_level, character.data_manager.tier_thresholds)
                next_tier = current_tier + 1
                
                print_subheader(f"Tier Change Required for {name}")
                print_warning(f"Character will advance to tier {next_tier} at level {next_threshold}!")
                
                if level_type.lower() == "class":
                    # Get available classes for the next tier
                    available_classes = get_available_classes_for_tier(next_tier)
                    
                    if not available_classes:
                        print_error(f"No tier {next_tier} classes available!")
                        errors += 1
                        pause_screen()
                        continue
                    
                    # Display options
                    print_subheader(f"Available Tier {next_tier} Classes")
                    for j, class_name in enumerate(available_classes, 1):
                        print(f"{j}. {class_name}")
                    
                    # Get selection
                    while True:
                        selection = input(f"\nEnter new tier {next_tier} class for {name} (number or name): ").strip()
                        
                        # Try to parse as number first
                        try:
                            choice_num = int(selection)
                            if 1 <= choice_num <= len(available_classes):
                                new_class = available_classes[choice_num - 1]
                                break
                            else:
                                print_error(f"Please enter a number between 1 and {len(available_classes)}")
                                continue
                        except ValueError:
                            # Try to match by name
                            new_class = selection.lower()
                            if validate_class_tier_combination(new_class, next_tier):
                                break
                            else:
                                print_error(f"Invalid tier {next_tier} class: {selection}")
                                continue
                    
                    # Change class before leveling up
                    success = character.change_class(new_class, next_threshold)
                    if not success:
                        print_error("Failed to change class.")
                        errors += 1
                        pause_screen()
                        continue
                        
                    print_success(f"Class changed to {new_class} at level {next_threshold}")
                
                elif level_type.lower() == "profession":
                    # Get available professions for the next tier
                    available_professions = get_available_professions_for_tier(next_tier)
                    
                    if not available_professions:
                        print_error(f"No tier {next_tier} professions available!")
                        errors += 1
                        pause_screen()
                        continue
                    
                    # Display options
                    print_subheader(f"Available Tier {next_tier} Professions")
                    for j, profession_name in enumerate(available_professions, 1):
                        print(f"{j}. {profession_name}")
                    
                    # Get selection
                    while True:
                        selection = input(f"\nEnter new tier {next_tier} profession for {name} (number or name): ").strip()
                        
                        # Try to parse as number first
                        try:
                            choice_num = int(selection)
                            if 1 <= choice_num <= len(available_professions):
                                new_profession = available_professions[choice_num - 1]
                                break
                            else:
                                print_error(f"Please enter a number between 1 and {len(available_professions)}")
                                continue
                        except ValueError:
                            # Try to match by name
                            new_profession = selection.lower()
                            if validate_profession_tier_combination(new_profession, next_tier):
                                break
                            else:
                                print_error(f"Invalid tier {next_tier} profession: {selection}")
                                continue
                    
                    # Change profession before leveling up
                    success = character.change_profession(new_profession, next_threshold)
                    if not success:
                        print_error("Failed to change profession.")
                        errors += 1
                        pause_screen()
                        continue
                        
                    print_success(f"Profession changed to {new_profession} at level {next_threshold}")
            
            # Level up the character (no loading screen)
            success = character.level_up(level_type, target_level)
            
            if not success:
                print_error(f"Failed to level up {name}.")
                errors += 1
                pause_screen()  # Pause for errors
                continue
            
            print_success(f"Leveled up {name} to {level_type} level {target_level}")
            
            # Handle free points allocation
            if character.level_system.free_points > 0:
                needs_pause = True  # Point allocation requires user input
                print_info(f"{name} has {character.level_system.free_points} free points to allocate.")
                
                if allocation_method == '1':
                    # Ask for each character individually using existing function
                    print_subheader(f"Allocate Free Points for {name}")
                    print("1. Use existing allocation interface")
                    print("2. Allocate randomly") 
                    print("3. Save for later")
                    
                    choice = input("Choose allocation method (1-3): ").strip()
                    
                    if choice == '1':
                        # Use existing allocate_points function
                        allocate_points(character)
                    elif choice == '2':
                        # Random allocation
                        character.allocate_random()
                        print_success("Free points allocated randomly.")
                    # choice == '3' or invalid: save for later (do nothing)
                
                elif allocation_method == '2':
                    # Random allocation for all - no user input needed
                    character.allocate_random()
                    print_success("Free points allocated randomly.")
                    needs_pause = False  # No user interaction needed for auto-random
                
                # allocation_method == '3': save for later (do nothing)
                # needs_pause remains True to let user see the message
            
            # Save the character
            save_success = character.save(character_file)
            if save_success:
                print_success(f"Saved {name} to {character_file}")
                processed += 1
            else:
                print_error(f"Failed to save {name}")
                errors += 1
                needs_pause = True  # Pause for save errors
        
        except Exception as e:
            print_error(f"Error processing {name}: {str(e)}")
            errors += 1
            needs_pause = True  # Pause for exceptions
        
        # Only pause if there was user interaction or an error
        if needs_pause and i < len(leveling_data):
            pause_screen()
    
    # Summary
    clear_screen()
    print_header("Bulk Leveling Complete")
    print_success(f"Successfully processed: {processed} operations")
    if skipped > 0:
        print_info(f"Skipped (already at target level): {skipped} operations")
    if errors > 0:
        print_error(f"Errors encountered: {errors} operations")
    
    pause_screen()

def allocate_points(character: Character):
    """Allocate free points to character stats."""
    clear_screen()
    print_header(f"Allocate Free Points: {character.name}")
    
    free_points = character.level_system.free_points
    
    if free_points == 0:
        print_error("No free points available to allocate.")
        pause_screen()
        return
    
    print_info(f"You have {free_points} free points to allocate.")
    print_subheader("Current Stats")
    
    for stat in STATS:
        print(f"{stat.capitalize()}: {character.data_manager.get_stat(stat)}")
    
    # Ask how to allocate
    print()
    allocation_choice = input("How do you want to allocate points? (manual/random/cancel): ").lower().strip()
    
    if allocation_choice == "cancel":
        return
    
    if allocation_choice == "random":
        # Random allocation
        print_loading("Allocating points randomly")
        
        # Track stat gains for display
        stat_gains = {stat: 0 for stat in STATS}
        
        # Allocate points randomly
        for _ in range(free_points):
            stat = random.choice(STATS)
            character.allocate_free_points(stat, 1)
            stat_gains[stat] += 1
        
        # Display results
        print_success("All free points have been randomly allocated:")
        for stat, gain in stat_gains.items():
            if gain > 0:
                print(f"{stat.capitalize()}: +{gain}")
    
    elif allocation_choice == "manual":
        # Manual allocation
        remaining_points = free_points
        
        while remaining_points > 0:
            clear_screen()
            print_header(f"Manual Point Allocation: {remaining_points} points left")
            
            print_subheader("Current Stats")
            for stat in STATS:
                print(f"{stat.capitalize()}: {character.data_manager.get_stat(stat)}")
            
            print()
            stat = input("Enter the stat to increase (or 'done'): ").lower().strip()
            
            if stat == "done":
                print_info(f"{remaining_points} points saved for later.")
                break
            
            if stat not in STATS:
                print_error(f"Invalid stat. Available stats: {', '.join(STATS)}")
                pause_screen()
                continue
            
            # Get amount to allocate
            try:
                amount = int(input(f"How many points to allocate to {stat}? "))
                
                if amount <= 0:
                    print_error("Please enter a positive number.")
                elif amount > remaining_points:
                    print_error(f"You only have {remaining_points} points left.")
                else:
                    # Allocate points
                    success = character.allocate_free_points(stat, amount)
                    if success:
                        remaining_points -= amount
                        print_success(f"Increased {stat} by {amount}.")
                    else:
                        print_error("Failed to allocate points.")
            
            except ValueError:
                print_error("Please enter a valid number.")
            
            if remaining_points > 0:
                pause_screen()
    
    else:
        print_error("Invalid choice.")
    
    pause_screen()

def add_blessing(character: Character):
    """Add a blessing with stat bonuses."""
    clear_screen()
    print_header(f"Add Blessing: {character.name}")
    
    if hasattr(character, 'blessing') and character.blessing:
        print_warning("Character already has a blessing:")
        for stat, value in character.blessing.items():
            print(f"{stat.capitalize()}: +{value}")
        
        if not confirm_action("Do you want to replace the existing blessing?"):
            return
    
    print_info("A blessing provides permanent stat bonuses to your character.")
    print_subheader("Add Blessing Stats")
    
    blessing_stats = {}
    
    while True:
        # Display current blessing stats
        if blessing_stats:
            print_subheader("Current Blessing")
            for stat, value in blessing_stats.items():
                print(f"{stat.capitalize()}: +{value}")
        
        # Get stat to bless
        print()
        stat = input("Enter stat to bless (or 'done' to finish, 'cancel' to abort): ").lower().strip()
        
        if stat == "cancel":
            return
        
        if stat == "done":
            if not blessing_stats:
                print_error("No blessing stats added.")
                if confirm_action("Do you want to abort?"):
                    return
                continue
            break
        
        if stat not in STATS:
            print_error(f"Invalid stat. Available stats: {', '.join(STATS)}")
            pause_screen()
            clear_screen()
            print_header(f"Add Blessing: {character.name}")
            continue
        
        # Get blessing value
        try:
            value = int(input(f"Enter blessing value for {stat}: "))
            if value <= 0:
                print_error("Blessing value must be positive.")
                pause_screen()
                continue
            
            blessing_stats[stat] = value
            print_success(f"Added +{value} to {stat}.")
        
        except ValueError:
            print_error("Please enter a valid integer.")
        
        pause_screen()
        clear_screen()
        print_header(f"Add Blessing: {character.name}")
    
    # Apply the blessing
    if blessing_stats:
        print_loading("Applying blessing")
        character.add_blessing(blessing_stats)
        print_success("Blessing applied successfully!")
    
    pause_screen()

def save_character(character: Character, file: str = None):
    """Save a character to a CSV file."""
    clear_screen()
    print_header(f"Save Character: {character.name}")
    
    if not file:
        filename = input("Enter the CSV filename to save to: ").strip()
        
        # Add .csv extension if not provided
        if not filename.endswith('.csv'):
            filename += '.csv'
    else:
        filename = file
    
    try:
        print_loading("Saving character")
        success = character.save(filename)
        
        if success:
            print_success(f"Character {character.name} saved successfully to {filename}")
        else:
            print_error(f"Failed to save character to {filename}")
    
    except Exception as e:
        print_error(f"Error saving character: {str(e)}")
    
    pause_screen()

def create_character_sheet(character: Character):
    """Create a CSV character sheet with stats and modifiers."""
    clear_screen()
    print_header(f"Create Character Sheet: {character.name}")
    
    filename = f"{character.name.lower().replace(' ', '_')}_character_sheet.csv"
    
    try:
        print_loading("Creating character sheet")
        
        import csv
        with open(filename, "w", newline="") as file:
            writer = csv.writer(file)
            
            # Write header
            writer.writerow(["Attribute", "Base Value", "Current Value", "Modifier"])
            
            # Write stats
            for stat in STATS:
                sources = character.data_manager.get_stat_sources(stat)
                writer.writerow([
                    stat.capitalize(),
                    sources.get("base", 0),
                    character.data_manager.get_stat(stat),
                    character.data_manager.get_stat_modifier(stat)
                ])
        
        print_success(f"Character sheet created: {filename}")
    
    except Exception as e:
        print_error(f"Error creating character sheet: {str(e)}")
    
    pause_screen()

# ============================================================================
# Combat Simulator
# ============================================================================

def simulate_combat(character: Character, item_repository):
    """Simulate combat between the character and an enemy."""
    clear_screen()
    print_header("Combat Simulator")
    
    print_subheader("Choose Your Opponent")
    print("1. Fight against a clone of your character")
    print("2. Fight against a standard enemy (all stats 50)")
    print("3. Fight against a custom enemy")
    print("0. Cancel")
    
    choice = input("\nEnter your choice: ").strip()
    
    if choice == '0':
        return
    
    # Create the enemy
    if choice == '1':
        # Clone the player's character
        enemy_stats = character.data_manager.get_all_stats()
        enemy = Character(
            name=f"{character.name}'s Clone",
            stats=enemy_stats,
            meta=character.data_manager.get_all_meta(),
            finesse=character.combat_system.finesse,
            item_repository=item_repository
        )
    
    elif choice == '2':
        # Create a standard enemy
        enemy_stats = {stat: 50 for stat in STATS}
        enemy = Character(
            name="Standard Enemy",
            stats=enemy_stats,
            meta={info: "" for info in META_INFO},
            item_repository=item_repository
        )
    
    elif choice == '3':
        # Create a custom enemy
        clear_screen()
        print_header("Create Custom Enemy")
        
        enemy_name = input("Enter enemy name: ").strip() or "Custom Enemy"
        
        enemy_stats = {}
        print_subheader("Enter Enemy Stats")
        print_info("Default value is 50 if left empty.")
        
        for stat in STATS:
            while True:
                try:
                    value = input(f"{stat.capitalize()}: ").strip()
                    if not value:
                        value = "50"  # Default value
                    enemy_stats[stat] = int(value)
                    break
                except ValueError:
                    print_error("Please enter a valid integer.")
        
        enemy = Character(
            name=enemy_name,
            stats=enemy_stats,
            meta={info: "" for info in META_INFO},
            item_repository=item_repository
        )
    
    else:
        print_error("Invalid choice.")
        pause_screen()
        return
    
    # Run the combat simulation
    run_combat_simulation(character, enemy)

def run_combat_simulation(character: Character, enemy: Character):
    """Run a combat simulation between two characters."""
    clear_screen()
    print_header("Combat Simulation")
    
    print_subheader(f"{character.name} vs {enemy.name}")
    
    # Display character stats
    print(f"{character.name}'s Stats:")
    for stat in ["strength", "dexterity", "toughness", "vitality"]:
        print(f"  {stat.capitalize()}: {character.data_manager.get_stat(stat)}")
    
    print(f"\n{enemy.name}'s Stats:")
    for stat in ["strength", "dexterity", "toughness", "vitality"]:
        print(f"  {stat.capitalize()}: {enemy.data_manager.get_stat(stat)}")
    
    # Initialize combat
    character.health_manager.reset_health()
    enemy.health_manager.reset_health()
    
    print("\nPress Enter to start combat...")
    input()
    
    # Run the simulation for 5 rounds or until one character is defeated
    for round_num in range(1, 6):
        clear_screen()
        print_header(f"Combat Round {round_num}")
        
        # Display health
        print(f"{character.name}'s Health: {character.health_manager.current_health}/{character.health_manager.max_health}")
        print(f"{enemy.name}'s Health: {enemy.health_manager.current_health}/{enemy.health_manager.max_health}")
        print()
        
        # Character attacks enemy
        hit, damage, net_damage = character.combat_system.attack(enemy)
        
        if hit:
            print_success(f"{character.name} hit for {net_damage} damage!")
        else:
            print_error(f"{character.name} missed!")
        
        if not enemy.health_manager.is_alive():
            print_success(f"\n{enemy.name} was defeated in round {round_num}!")
            break
        
        # Enemy attacks character
        hit, damage, net_damage = enemy.combat_system.attack(character)
        
        if hit:
            print_error(f"{enemy.name} hit for {net_damage} damage!")
        else:
            print_success(f"{enemy.name} missed!")
        
        if not character.health_manager.is_alive():
            print_error(f"\n{character.name} was defeated in round {round_num}!")
            break
        
        # Pause between rounds
        if round_num < 5 and character.health_manager.is_alive() and enemy.health_manager.is_alive():
            input("\nPress Enter for next round...")
    
    # Check if both are still alive after 5 rounds
    if character.health_manager.is_alive() and enemy.health_manager.is_alive():
        print_info("\nBoth combatants are still standing after 5 rounds!")
    
    # Reset character's health after combat
    character.health_manager.reset_health()
    
    pause_screen()

# ============================================================================
# Inventory Management
# ============================================================================

def manage_inventory(character: Character, item_repository):
    """Manage character inventory."""
    while True:
        print_inventory_menu(character)
        choice = input("\nEnter your choice: ").strip()
        
        if choice == '0':
            return
        elif choice == '1':
            view_available_items(item_repository)
        elif choice == '2':
            add_item_to_inventory(character, item_repository)
        elif choice == '3':
            remove_item_from_inventory(character)
        elif choice == '4':
            equip_item(character)
        elif choice == '5':
            unequip_item(character)
        elif choice == '6':
            reset_equipment(character)
        else:
            print_error("Invalid choice.")
            pause_screen()

def view_available_items(item_repository):
    """View all available items in the item repository."""
    clear_screen()
    print_header("Available Items")
    
    if not item_repository.items:
        print_error("No items available in the repository.")
        pause_screen()
        return
    
    # Get items sorted by name
    item_names = sorted(item_repository.items.keys())
    
    for name in item_names:
        item_data = item_repository.items[name]
        print_subheader(name.title())
        print(f"Description: {item_data['description']}")
        
        if item_data["stats"]:
            print("Stats:")
            for stat, value in item_data["stats"].items():
                print(f"  {stat.capitalize()}: +{value}")
        else:
            print("Stats: None")
    
    pause_screen()

def add_item_to_inventory(character: Character, item_repository):
    """Add an item to the character's inventory."""
    clear_screen()
    print_header("Add Item to Inventory")
    
    # Get available items
    item_names = sorted(item_repository.items.keys())
    
    if not item_names:
        print_error("No items available in the repository.")
        pause_screen()
        return
    
    # Display available items
    print_subheader("Available Items")
    for i, name in enumerate(item_names, 1):
        print(f"{i}. {name.title()}")
    
    print("\n0. Cancel")
    
    # Get user choice
    try:
        choice = input("\nEnter item number or name: ").strip()
        
        if choice == '0':
            return
        
        # Check if choice is a number
        try:
            index = int(choice) - 1
            if 0 <= index < len(item_names):
                item_name = item_names[index]
            else:
                print_error("Invalid item number.")
                pause_screen()
                return
        except ValueError:
            # Assume choice is an item name
            item_name = choice.lower()
            if item_name not in item_repository.items:
                print_error(f"Item '{choice}' not found.")
                pause_screen()
                return
        
        # Add the item to inventory
        success = character.inventory.add_item(item_name)
        
        if success:
            print_success(f"Added {item_name.title()} to inventory.")
        else:
            print_error(f"Failed to add {item_name.title()} to inventory.")
    
    except Exception as e:
        print_error(f"Error adding item: {str(e)}")
    
    pause_screen()

def remove_item_from_inventory(character: Character):
    """Remove an item from the character's inventory."""
    clear_screen()
    print_header("Remove Item from Inventory")
    
    # Get character's inventory items
    inventory_items = character.inventory.items
    
    if not inventory_items:
        print_error("Inventory is empty.")
        pause_screen()
        return
    
    # Display inventory items
    print_subheader("Inventory Items")
    for i, item in enumerate(inventory_items, 1):
        equipped_str = " [Equipped]" if item.equipped else ""
        print(f"{i}. {item.name.title()}{equipped_str}")
    
    print("\n0. Cancel")
    
    # Get user choice
    try:
        choice = input("\nEnter item number or name to remove: ").strip()
        
        if choice == '0':
            return
        
        # Get the item
        item_to_remove = None
        
        # Check if choice is a number
        try:
            index = int(choice) - 1
            if 0 <= index < len(inventory_items):
                item_to_remove = inventory_items[index]
            else:
                print_error("Invalid item number.")
                pause_screen()
                return
        except ValueError:
            # Assume choice is an item name
            item_name = choice.lower()
            item_to_remove = character.inventory.get_item(item_name)
            
            if not item_to_remove:
                print_error(f"Item '{choice}' not found in inventory.")
                pause_screen()
                return
        
        # Check if item is equipped
        if item_to_remove.equipped:
            print_warning(f"{item_to_remove.name.title()} is currently equipped.")
            if not confirm_action("Do you want to unequip and remove it?"):
                return
            
            # Unequip the item first
            character.unequip_item(item_to_remove.name)
        
        # Remove the item
        success = character.inventory.remove_item(item_to_remove.name)
        
        if success:
            print_success(f"Removed {item_to_remove.name.title()} from inventory.")
        else:
            print_error(f"Failed to remove {item_to_remove.name.title()} from inventory.")
    
    except Exception as e:
        print_error(f"Error removing item: {str(e)}")
    
    pause_screen()

def equip_item(character: Character):
    """Equip an item from the character's inventory."""
    clear_screen()
    print_header("Equip Item")
    
    # Get character's unequipped inventory items
    unequipped_items = [item for item in character.inventory.items if not item.equipped]
    
    if not unequipped_items:
        print_error("No unequipped items in inventory.")
        pause_screen()
        return
    
    # Display unequipped items
    print_subheader("Unequipped Items")
    for i, item in enumerate(unequipped_items, 1):
        print(f"{i}. {item.name.title()}")
        if item.stats:
            print("   Stats: " + ", ".join(f"{s}: +{v}" for s, v in item.stats.items()))
    
    print("\n0. Cancel")
    
    # Get user choice
    try:
        choice = input("\nEnter item number or name to equip: ").strip()
        
        if choice == '0':
            return
        
        # Get the item
        item_to_equip = None
        
        # Check if choice is a number
        try:
            index = int(choice) - 1
            if 0 <= index < len(unequipped_items):
                item_to_equip = unequipped_items[index]
            else:
                print_error("Invalid item number.")
                pause_screen()
                return
        except ValueError:
            # Assume choice is an item name
            item_name = choice.lower()
            item_to_equip = character.inventory.get_item(item_name)
            
            if not item_to_equip:
                print_error(f"Item '{choice}' not found in inventory.")
                pause_screen()
                return
            
            if item_to_equip.equipped:
                print_error(f"{item_to_equip.name.title()} is already equipped.")
                pause_screen()
                return
        
        # Equip the item
        success = character.equip_item(item_to_equip.name)
        
        if success:
            print_success(f"Equipped {item_to_equip.name.title()}.")
        else:
            print_error(f"Failed to equip {item_to_equip.name.title()}.")
    
    except Exception as e:
        print_error(f"Error equipping item: {str(e)}")
    
    pause_screen()

def unequip_item(character: Character):
    """Unequip an item."""
    clear_screen()
    print_header("Unequip Item")
    
    # Get character's equipped inventory items
    equipped_items = character.inventory.get_equipped_items()
    
    if not equipped_items:
        print_error("No equipped items.")
        pause_screen()
        return
    
    # Display equipped items
    print_subheader("Equipped Items")
    for i, item in enumerate(equipped_items, 1):
        print(f"{i}. {item.name.title()}")
        if item.stats:
            print("   Stats: " + ", ".join(f"{s}: +{v}" for s, v in item.stats.items()))
    
    print("\n0. Cancel")
    
    # Get user choice
    try:
        choice = input("\nEnter item number or name to unequip: ").strip()
        
        if choice == '0':
            return
        
        # Get the item
        item_to_unequip = None
        
        # Check if choice is a number
        try:
            index = int(choice) - 1
            if 0 <= index < len(equipped_items):
                item_to_unequip = equipped_items[index]
            else:
                print_error("Invalid item number.")
                pause_screen()
                return
        except ValueError:
            # Assume choice is an item name
            item_name = choice.lower()
            item_to_unequip = character.inventory.get_item(item_name)
            
            if not item_to_unequip:
                print_error(f"Item '{choice}' not found in inventory.")
                pause_screen()
                return
            
            if not item_to_unequip.equipped:
                print_error(f"{item_to_unequip.name.title()} is not equipped.")
                pause_screen()
                return
        
        # Unequip the item
        success = character.unequip_item(item_to_unequip.name)
        
        if success:
            print_success(f"Unequipped {item_to_unequip.name.title()}.")
        else:
            print_error(f"Failed to unequip {item_to_unequip.name.title()}.")
    
    except Exception as e:
        print_error(f"Error unequipping item: {str(e)}")
    
    pause_screen()

def reset_equipment(character: Character):
    """Reset all equipment effects and reapply them."""
    clear_screen()
    print_header("Reset Equipment Effects")
    
    if not character.inventory.get_equipped_items():
        print_error("No equipped items to reset.")
        pause_screen()
        return
    
    print_info("This will reset all equipment effects and reapply them.")
    if not confirm_action("Are you sure?"):
        return
    
    try:
        print_loading("Resetting equipment effects")
        
        # Store current stats before reset
        old_stats = {stat: character.data_manager.get_stat(stat) for stat in STATS}
        
        # Reset equipment effects
        # First unequip all items
        equipped_items = character.inventory.get_equipped_items()
        for item in equipped_items:
            character.unequip_item(item.name)
        
        # Then re-equip all items
        for item in equipped_items:
            character.equip_item(item.name)
        
        # Show changes
        print_success("Equipment effects reset and reapplied.")
        
        print_subheader("Stat Changes")
        for stat in STATS:
            old = old_stats[stat]
            new = character.data_manager.get_stat(stat)
            
            if old != new:
                diff = new - old
                diff_str = f"+{diff}" if diff > 0 else str(diff)
                print(f"{stat.capitalize()}: {old} → {new} ({diff_str})")
    
    except Exception as e:
        print_error(f"Error resetting equipment effects: {str(e)}")
    
    pause_screen()

# ============================================================================
# Tier Management
# ============================================================================

def manage_tier_thresholds(character: Character):
    """Manage character's tier thresholds."""
    while True:
        clear_screen()
        print_header(f"Tier Threshold Management: {character.name}")
        
        # Display current thresholds and tier info
        print_subheader("Current Tier Configuration")
        print(f"Tier thresholds: {character.data_manager.tier_thresholds}")
        
        # Show tier summary
        tier_summary = get_tier_summary(character.data_manager.tier_thresholds)
        print("\nTier Breakdown:")
        for tier, info in tier_summary.items():
            level_range = info["level_range"]
            if level_range[1] == 999:
                range_str = f"{level_range[0]}+"
            else:
                range_str = f"{level_range[0]}-{level_range[1]}"
            print(f"  Tier {tier}: Level {range_str} ({info['level_span']} levels)")
        
        # Show character's current position
        class_level = int(character.data_manager.get_meta("Class level", "0"))
        profession_level = int(character.data_manager.get_meta("Profession level", "0"))
        
        if class_level > 0 or profession_level > 0:
            print_subheader("Character's Current Position")
            if class_level > 0:
                class_tier = character.data_manager.get_tier_for_level(class_level)
                print(f"Class Level {class_level} → Tier {class_tier}")
            if profession_level > 0:
                prof_tier = character.data_manager.get_tier_for_level(profession_level)
                print(f"Profession Level {profession_level} → Tier {prof_tier}")
        
        print_subheader("Threshold Management")
        print("1. Add new tier threshold")
        print("2. Remove tier threshold")
        print("3. Set custom threshold list")
        print("4. Reset to default thresholds")
        print("5. Validate thresholds with character")
        print("6. Preview threshold changes")
        print("0. Back to main menu")
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == '0':
            return
        elif choice == '1':
            add_tier_threshold(character)
        elif choice == '2':
            remove_tier_threshold(character)
        elif choice == '3':
            set_custom_thresholds(character)
        elif choice == '4':
            reset_default_thresholds(character)
        elif choice == '5':
            validate_thresholds(character)
        elif choice == '6':
            preview_threshold_changes(character)
        else:
            print_error("Invalid choice.")
            pause_screen()

def add_tier_threshold(character: Character):
    """Add a new tier threshold."""
    clear_screen()
    print_header("Add Tier Threshold")
    
    print_subheader("Current Thresholds")
    print(f"Current: {character.data_manager.tier_thresholds}")
    
    try:
        threshold = int(input("Enter new tier threshold level: "))
        
        if threshold <= 0:
            print_error("Threshold must be positive.")
            pause_screen()
            return
        
        success = character.data_manager.add_tier_threshold(threshold)
        
        if success:
            print_success(f"Added tier threshold at level {threshold}")
            print(f"New thresholds: {character.data_manager.tier_thresholds}")
            
            # Show impact
            print_subheader("Impact Analysis")
            validation = character.data_manager.validate_tier_thresholds_with_character()
            if validation["warnings"]:
                for warning in validation["warnings"]:
                    print_warning(warning)
            if validation["errors"]:
                for error in validation["errors"]:
                    print_error(error)
        else:
            print_error(f"Threshold {threshold} already exists.")
    
    except ValueError:
        print_error("Please enter a valid integer.")
    
    pause_screen()

def remove_tier_threshold(character: Character):
    """Remove a tier threshold."""
    clear_screen()
    print_header("Remove Tier Threshold")
    
    print_subheader("Current Thresholds")
    current_thresholds = character.data_manager.tier_thresholds
    print(f"Current: {current_thresholds}")
    
    if not current_thresholds:
        print_error("No thresholds to remove.")
        pause_screen()
        return
    
    try:
        threshold = int(input("Enter tier threshold to remove: "))
        
        success, message = character.data_manager.remove_tier_threshold(threshold)
        
        if success:
            print_success(message)
            print(f"New thresholds: {character.data_manager.tier_thresholds}")
        else:
            print_error(message)
    
    except ValueError:
        print_error("Please enter a valid integer.")
    
    pause_screen()

def set_custom_thresholds(character: Character):
    """Set completely custom tier thresholds."""
    clear_screen()
    print_header("Set Custom Tier Thresholds")
    
    print_subheader("Current Thresholds")
    print(f"Current: {character.data_manager.tier_thresholds}")
    
    print_info("Enter new tier thresholds as comma-separated values (e.g., 25,50,75,100)")
    print_warning("This will replace ALL existing thresholds!")
    
    try:
        threshold_input = input("Enter new thresholds: ").strip()
        
        if not threshold_input:
            print_error("Cannot set empty threshold list.")
            pause_screen()
            return
        
        # Parse comma-separated values
        new_thresholds = [int(x.strip()) for x in threshold_input.split(',')]
        
        # Show preview
        print_subheader("Preview")
        print(f"Old: {character.data_manager.tier_thresholds}")
        print(f"New: {sorted(new_thresholds)}")
        
        if not confirm_action("Apply these new thresholds?"):
            print_info("Cancelled.")
            pause_screen()
            return
        
        success, message = character.data_manager.set_tier_thresholds(new_thresholds)
        
        if success:
            print_success(message)
            
            # Show validation results
            validation = character.data_manager.validate_tier_thresholds_with_character()
            if validation["warnings"]:
                print_subheader("Warnings")
                for warning in validation["warnings"]:
                    print_warning(warning)
            if validation["errors"]:
                print_subheader("Errors")
                for error in validation["errors"]:
                    print_error(error)
        else:
            print_error(message)
    
    except ValueError:
        print_error("Please enter valid integers separated by commas.")
    
    pause_screen()

def reset_default_thresholds(character: Character):
    """Reset to default tier thresholds."""
    clear_screen()
    print_header("Reset to Default Thresholds")
    
    print_subheader("Current vs Default")
    print(f"Current: {character.data_manager.tier_thresholds}")
    print(f"Default: {DEFAULT_TIER_THRESHOLDS}")
    
    if character.data_manager.tier_thresholds == DEFAULT_TIER_THRESHOLDS:
        print_info("Character is already using default thresholds.")
        pause_screen()
        return
    
    if confirm_action("Reset to default tier thresholds?"):
        success, message = character.data_manager.set_tier_thresholds(DEFAULT_TIER_THRESHOLDS.copy())
        
        if success:
            print_success("Reset to default tier thresholds.")
            print(message)
        else:
            print_error(f"Failed to reset: {message}")
    else:
        print_info("Cancelled.")
    
    pause_screen()

def validate_thresholds(character: Character):
    """Validate tier thresholds against character progression."""
    clear_screen()
    print_header("Validate Tier Thresholds")
    
    validation = character.data_manager.validate_tier_thresholds_with_character()
    
    if validation["valid"]:
        print_success("Tier thresholds are valid for this character!")
    else:
        print_error("Tier threshold validation failed!")
    
    # Show current tier positions
    print_subheader("Current Tier Positions")
    if validation["current_tiers"]["class"] > 0:
        print(f"Class: Tier {validation['current_tiers']['class']}")
    if validation["current_tiers"]["profession"] > 0:
        print(f"Profession: Tier {validation['current_tiers']['profession']}")
    
    # Show progression analysis
    if validation["progression_analysis"]:
        print_subheader("Progression Analysis")
        for progression_type, info in validation["progression_analysis"].items():
            print(f"{progression_type.capitalize()}:")
            print(f"  Current: Level {info['current_level']} (Tier {info['current_tier']})")
            print(f"  Next tier: {info['next_tier']} at level {info['next_threshold']}")
            print(f"  Levels needed: {info['levels_to_next_tier']}")
    
    # Show warnings and errors
    if validation["warnings"]:
        print_subheader("Warnings")
        for warning in validation["warnings"]:
            print_warning(warning)
    
    if validation["errors"]:
        print_subheader("Errors")
        for error in validation["errors"]:
            print_error(error)
    
    pause_screen()

def preview_threshold_changes(character: Character):
    """Preview what would happen with different tier thresholds."""
    clear_screen()
    print_header("Preview Tier Threshold Changes")
    
    print_info("Enter potential tier thresholds to see their impact")
    print_info("Current thresholds: " + str(character.data_manager.tier_thresholds))
    
    try:
        threshold_input = input("Enter thresholds to preview (comma-separated): ").strip()
        
        if not threshold_input:
            return
        
        preview_thresholds = [int(x.strip()) for x in threshold_input.split(',')]
        preview_thresholds = sorted(list(set(preview_thresholds)))  # Remove duplicates and sort
        
        print_subheader("Threshold Comparison")
        print(f"Current: {character.data_manager.tier_thresholds}")
        print(f"Preview: {preview_thresholds}")
        
        # Show tier breakdown for both
        print_subheader("Current Tier Structure")
        current_summary = get_tier_summary(character.data_manager.tier_thresholds)
        for tier, info in current_summary.items():
            level_range = info["level_range"]
            range_str = f"{level_range[0]}-{level_range[1]}" if level_range[1] != 999 else f"{level_range[0]}+"
            print(f"  Tier {tier}: Level {range_str}")
        
        print_subheader("Preview Tier Structure")
        preview_summary = get_tier_summary(preview_thresholds)
        for tier, info in preview_summary.items():
            level_range = info["level_range"]
            range_str = f"{level_range[0]}-{level_range[1]}" if level_range[1] != 999 else f"{level_range[0]}+"
            print(f"  Tier {tier}: Level {range_str}")
        
        # Show impact on character
        class_level = int(character.data_manager.get_meta("Class level", "0"))
        profession_level = int(character.data_manager.get_meta("Profession level", "0"))
        
        if class_level > 0 or profession_level > 0:
            print_subheader("Impact on Character")
            
            if class_level > 0:
                current_tier = get_tier_for_level(class_level, character.data_manager.tier_thresholds)
                preview_tier = get_tier_for_level(class_level, preview_thresholds)
                print(f"Class Level {class_level}: Tier {current_tier} → Tier {preview_tier}")
                if current_tier != preview_tier:
                    print_warning(f"  Class tier would change!")
            
            if profession_level > 0:
                current_tier = get_tier_for_level(profession_level, character.data_manager.tier_thresholds)
                preview_tier = get_tier_for_level(profession_level, preview_thresholds)
                print(f"Profession Level {profession_level}: Tier {current_tier} → Tier {preview_tier}")
                if current_tier != preview_tier:
                    print_warning(f"  Profession tier would change!")
    
    except ValueError:
        print_error("Please enter valid integers separated by commas.")
    
    pause_screen()

def print_main_menu(character: Optional[Character] = None):
    """Print the main menu with race history option."""
    clear_screen()
    
    if character is None:
        print_header("Welcome to the Character Creator")
        print("1. Create a new character (calculated bonuses)")
        print("2. Create an advanced character (with tier history)")
        print("3. Create a custom character (manual stats, no progression)")
        print("4. Create a reverse-engineered character (base + current stats)")
        print("5. Load a character")
        print("6. Bulk level characters")
        print("0. Exit")
    else:
        print_header(f"Character: {character.name}")
        print_subheader("Character Menu")
        print("1. View character details")
        print("2. View character history")
        print("3. Update character stats")
        print("4. Update character meta information")
        print("5. Level up character")
        print("6. Combat simulator")
        print("7. Inventory management")
        print("8. Save character")
        print("9. Create character sheet")
        print("10. Allocate free points")
        print("11. Add blessing")
        print("12. Validate character stats")
        print("13. Manage tier thresholds")
        print("14. Manage race history")  # NEW
        print("15. Start over (unload character)")
        print("0. Exit")

# ============================================================================
# Main Application
# ============================================================================

def main():
    """Main application entry point with race history support."""
    # Initialize item repository
    try:
        item_repository = ItemRepository(items)
    except Exception as e:
        print_error(f"Error initializing item repository: {str(e)}")
        print_info("Starting with an empty item repository.")
        item_repository = ItemRepository({})
    
    character = None
    save_file = None
    
    while True:
        print_main_menu(character)
        choice = input("\nEnter your choice: ").strip()
        
        if character is None:
            # Character creation menu (unchanged)
            if choice == '1':
                character = create_character(item_repository)
            elif choice == '2':
                character = create_advanced_character(item_repository)
            elif choice == '3':
                character = create_manual_character(item_repository)
            elif choice == '4':
                character = create_reverse_engineered_character(item_repository)
            elif choice == '5':
                character, save_file = load_character(item_repository)
            elif choice == '6':
                bulk_level_characters(item_repository)
            elif choice == '0':
                print_success("Thank you for using the Character Creator!")
                sys.exit(0)
            else:
                print_error("Invalid choice.")
                pause_screen()
        else:
            # Character loaded menu (ADD NEW OPTION)
            if choice == '1':
                view_character(character)
            elif choice == '2':
                view_character_history(character)  # Now includes race history
            elif choice == '3':
                update_stats(character)
            elif choice == '4':
                update_meta(character)
            elif choice == '5':
                level_up_character(character)
            elif choice == '6':
                simulate_combat(character, item_repository)
            elif choice == '7':
                manage_inventory(character, item_repository)
            elif choice == '8':
                save_character(character, save_file)
            elif choice == '9':
                create_character_sheet(character)
            elif choice == '10':
                allocate_points(character)
            elif choice == '11':
                add_blessing(character)
            elif choice == '12':
                validate_character_stats(character)
            elif choice == '13':
                manage_tier_thresholds(character)
            elif choice == '14':  # NEW
                manage_race_history(character)
            elif choice == '15':  # Updated number
                if confirm_action("Are you sure you want to unload the current character?"):
                    character = None
                    save_file = None
            elif choice == '0':
                if character and confirm_action("Do you want to save before exiting?"):
                    save_character(character, save_file)
                print_success("Thank you for using the Character Creator!")
                sys.exit(0)
            else:
                print_error("Invalid choice.")
                pause_screen()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print_error(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)