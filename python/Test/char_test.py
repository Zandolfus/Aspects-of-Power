"""
Character Creator CLI
A user-friendly command-line interface for the improved Character Creator system.
"""
import os
import sys
import time
import csv
from typing import Optional, Tuple
from Character_Creator import (
    Character, ItemRepository, StatSource,
    STATS, META_INFO, DERIVED_META
)
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

def print_main_menu(character: Optional[Character] = None):
    """Print the main menu based on whether a character is loaded."""
    clear_screen()
    
    if character is None:
        print_header("Welcome to the AoP Character Creator")
        print("1. Create a new character")
        print("2. Load a character")
        print("0. Exit")
    else:
        print_header(f"Character: {character.name}")
        print_subheader("Character Menu")
        print("1. View character details")
        print("2. Update character stats")
        print("3. Update character meta information")
        print("4. Level up character")
        print("5. Combat simulator")
        print("6. Inventory management")
        print("7. Save character")
        print("8. Create character sheet")
        print("9. Allocate free points")
        print("10. Add blessing")
        print("11. Validate character stats")
        print("12. Start over (unload character)")
        print("0. Exit")

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
    print("0. Back to main menu")

# ============================================================================
# Character Management Functions
# ============================================================================

def create_character(item_repository) -> Character:
    """Create a new character with user input."""
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
        if info in DERIVED_META:
            print_info(f"{info} will be calculated automatically.")
            continue
            
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
    
    # Ask if the user wants automatic leveling or custom stats
    print_subheader("Character Stats Configuration")
    print("1. Automatic level-up (enter base stats only)")
    print("2. Custom stats (enter both base and current stats)")
    
    stat_choice = ""
    while stat_choice not in ["1", "2"]:
        stat_choice = input("\nEnter your choice (1 or 2): ").strip()
        if stat_choice not in ["1", "2"]:
            print_error("Invalid choice. Please enter 1 or 2.")
    
    # Collect base stats
    base_stats = {}
    print_subheader(f"Enter base stats for {name}")
    print_info("Default value is 5 if left empty. These represent the character's innate abilities.")
    
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
    
    # Create character with appropriate stats
    if stat_choice == "1":
        # Automatic level-up - just use base stats
        character = Character(
            name=name,
            stats=base_stats,
            meta=meta,
            item_repository=item_repository
        )
        
        # Check for missing free points for characters created with levels > 1
        class_level = int(meta.get("Class level", "0"))
        profession_level = int(meta.get("Profession level", "0"))
        
        if class_level > 1 or profession_level > 1:
            print_loading("Calculating level-up bonuses")
            validation = character.validate_stats()
            expected_free_points = validation["free_points"]["expected_total"]
            
            if expected_free_points > 0 and character.level_system.free_points == 0:
                print_warning(f"Character created with level {class_level}/{profession_level} but has 0 free points.")
                print_info(f"Expected free points: {expected_free_points}")
                print_info("This may indicate the level-up bonuses weren't properly applied.")
                
                if confirm_action("Do you want to add these free points to your character?"):
                    character.level_system.free_points = expected_free_points
                    print_success(f"Added {expected_free_points} free points to character.")
        
        print_success(f"Character {name} created successfully with automatic level-up!")
        
    else:
        # Custom stats - collect current stats and calculate the differences
        current_stats = {}
        print_subheader(f"Enter current stats for {name}")
        print_info("These represent the character's stats after all class, profession, and race bonuses.")
        
        for stat in STATS:
            while True:
                try:
                    base = base_stats[stat]
                    value = input(f"{stat.capitalize()} (base: {base}): ").strip()
                    if not value:
                        value = str(base)  # Default to base value
                    current_stats[stat] = int(value)
                    break
                except ValueError:
                    print_error("Please enter a valid integer.")
        
        # Create character with custom stats
        character = Character(
            name=name,
            stats=base_stats,  # Use base stats for initialization
            meta=meta,
            item_repository=item_repository
        )
        
        # Now manually set the stats
        stat_differences = {}
        for stat in STATS:
            diff = current_stats[stat] - base_stats[stat]
            if diff != 0:
                stat_differences[stat] = diff
                # Add the difference as a custom source
                character.data_manager.add_stat(stat, diff, "custom")
        
        if stat_differences:
            print_success(f"Character {name} created with custom stats!")
            print_subheader("Custom Stat Adjustments")
            for stat, diff in stat_differences.items():
                print(f"{stat.capitalize()}: {'+' if diff > 0 else ''}{diff}")
        else:
            print_success(f"Character {name} created successfully!")
    
    pause_screen()
    return character

def load_character(item_repository) -> Tuple[Optional[Character], Optional[str]]:
    """Load a character from a CSV file."""
    clear_screen()
    print_header("Load Character")
    
    filename = input("Enter the CSV filename to load from: ").strip()
    
    # Add .csv extension if not provided
    if not filename.endswith('.csv'):
        filename += '.csv'
    
    if not os.path.exists(filename):
        print_error(f"File {filename} does not exist.")
        print_info(f"Current directory: {os.getcwd()}")
        pause_screen()
        return None, None
    
    name = input("Enter the character name to load: ").strip()
    if not name:
        print_error("Name cannot be empty.")
        pause_screen()
        return None, None
    
    try:
        print_loading("Loading character")
        character = Character.load(filename, name, item_repository)
        
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
    
    # Display all meta information, showing derived attributes with a note
    all_meta_keys = META_INFO + DERIVED_META
    for meta_key in all_meta_keys:
        value = character.data_manager.get_meta(meta_key)
        if meta_key in DERIVED_META:
            print(f"{meta_key}: {value} (derived)")
        else:
            print(f"{meta_key}: {value}")
    
    # Stats
    print_subheader("Stats")
    for stat in STATS:
        # Get all sources for this stat
        sources = character.data_manager.get_stat_sources(stat)
        base_value = sources.get(StatSource.BASE, 5)
        current_value = character.data_manager.get_stat(stat)
        modifier = character.data_manager.get_stat_modifier(stat)
        
        # Format source breakdown
        source_parts = []
        for source, value in sources.items():
            if source != StatSource.BASE and value != 0:
                source_parts.append(f"{source}: {'+' if value > 0 else ''}{value}")
        
        source_str = f" ({', '.join(source_parts)})" if source_parts else ""
        
        print(f"{stat.capitalize()}: {base_value}{source_str} = {current_value} (modifier: {modifier})")
    
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
        
        # Update the stat (as a base stat change)
        success = character.update_stat(stat, value)
        
        if success:
            print_success(f"Updated {stat} to {value}")
        else:
            print_error(f"Failed to update {stat}.")
    except ValueError:
        print_error("Please enter a valid integer.")
    
    pause_screen()

def update_meta(character: Character):
    """Update character meta information."""
    clear_screen()
    print_header(f"Update Meta Info: {character.name}")
    
    # Display current meta info
    print_subheader("Current Meta Info")
    for meta in META_INFO:
        value = character.data_manager.get_meta(meta)
        if meta in DERIVED_META:
            print(f"{meta}: {value} (derived - cannot be directly modified)")
        else:
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
    
    if info in DERIVED_META:
        print_error(f"Cannot directly update {info} as it is a derived attribute.")
        pause_screen()
        return
    
    # Get new value
    value = input(f"Enter new value for {info}: ").strip()
    
    # Update the meta info
    success = character.update_meta(info, value)
    
    if success:
        print_success(f"Updated {info} to {value}")
    else:
        print_error(f"Failed to update {info}.")
    
    pause_screen()

def level_up_character(character: Character):
    """Level up a character."""
    clear_screen()
    print_header(f"Level Up: {character.name}")
    
    # Display current levels
    print_subheader("Current Levels")
    class_level = character.data_manager.get_meta("Class level")
    profession_level = character.data_manager.get_meta("Profession level")
    race_level = character.data_manager.get_meta("Race level")
    
    print(f"Class level: {class_level}")
    print(f"Profession level: {profession_level}")
    print(f"Race level: {race_level} (derived from Class and Profession levels)")
    
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
        
        # Level up
        print_loading(f"Leveling up {level_type}")
        
        success = character.level_up(level_type, target_level)
        
        if success:
            print_success(f"Leveled up {level_type} to {target_level}")
            
            # Display updated levels
            new_class_level = character.data_manager.get_meta("Class level")
            new_profession_level = character.data_manager.get_meta("Profession level")
            new_race_level = character.data_manager.get_meta("Race level")
            
            print(f"\nUpdated levels:")
            print(f"Class level: {new_class_level}")
            print(f"Profession level: {new_profession_level}")
            print(f"Race level: {new_race_level}")
            
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
        
        # Allocate points randomly using the built-in method
        character.allocate_random()
        
        # Display results
        print_success("All free points have been randomly allocated.")
        
        # Show updated stats
        print_subheader("Updated Stats")
        for stat in STATS:
            sources = character.data_manager.get_stat_sources(stat)
            free_points_used = sources.get(StatSource.FREE_POINTS, 0)
            if free_points_used > 0:
                print(f"{stat.capitalize()}: {character.data_manager.get_stat(stat)} (Free points: +{free_points_used})")
            else:
                print(f"{stat.capitalize()}: {character.data_manager.get_stat(stat)}")
    
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
                        print_error(f"Failed to allocate points to {stat}.")
            
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
        
        with open(filename, "w", newline="") as file:
            writer = csv.writer(file)
            
            # Write header
            writer.writerow(["Attribute", "Base Value", "Source Breakdown", "Current Value", "Modifier"])
            
            # Write stats
            for stat in STATS:
                sources = character.data_manager.get_stat_sources(stat)
                base_value = sources.get(StatSource.BASE, 5)
                
                # Format source breakdown
                source_parts = []
                for source, value in sources.items():
                    if source != StatSource.BASE and value != 0:
                        source_parts.append(f"{source}: {'+' if value > 0 else ''}{value}")
                
                source_str = ", ".join(source_parts) if source_parts else "None"
                
                writer.writerow([
                    stat.capitalize(),
                    base_value,
                    source_str,
                    character.data_manager.get_stat(stat),
                    character.data_manager.get_stat_modifier(stat)
                ])
            
            # Write meta info
            writer.writerow([])
            writer.writerow(["Meta Information", "Value"])
            for meta in META_INFO:
                writer.writerow([
                    meta,
                    character.data_manager.get_meta(meta)
                ])
            
            # Write derived meta info
            for meta in DERIVED_META:
                writer.writerow([
                    f"{meta} (derived)",
                    character.data_manager.get_meta(meta)
                ])
            
            # Write free points
            writer.writerow([])
            writer.writerow(["Free Points", character.level_system.free_points])
            
            # Write blessing if present
            if hasattr(character, 'blessing') and character.blessing:
                writer.writerow([])
                writer.writerow(["Blessing", "Value"])
                for stat, value in character.blessing.items():
                    writer.writerow([stat.capitalize(), f"+{value}"])
            
            # Write equipped items
            equipped_items = character.inventory.get_equipped_items()
            if equipped_items:
                writer.writerow([])
                writer.writerow(["Equipped Items", "Description", "Stats"])
                for item in equipped_items:
                    stats_str = ", ".join(f"{s}: +{v}" for s, v in item.stats.items()) if item.stats else "None"
                    writer.writerow([item.name, item.description, stats_str])
        
        print_success(f"Character sheet created: {filename}")
    
    except Exception as e:
        print_error(f"Error creating character sheet: {str(e)}")
    
    pause_screen()

def validate_character_stats(character: Character):
    """Validate character stats and show results."""
    clear_screen()
    print_header(f"Validate Character Stats: {character.name}")
    
    print_info("Checking if character stats are properly allocated...")
    
    try:
        # Validate character
        result = character.validate_stats()
        
        # Check for custom stats
        has_custom_stats = result.get("has_custom_stats", False)
        if has_custom_stats:
            custom_stats = result.get("custom_stat_values", {})
            print_subheader("Character Has Custom Stat Adjustments")
            print_info("This character has custom stat adjustments beyond standard level-up bonuses.")
            print("Custom adjustments:")
            for stat, value in custom_stats.items():
                print(f"  {stat.capitalize()}: {'+' if value > 0 else ''}{value}")
            print()
            print_info("The validation below excludes these custom adjustments.")
            print()
        
        # Display results
        if result["valid"]:
            print_success("Character stats are valid. All stats are properly allocated.")
        else:
            print_error("Character stats validation failed.")
            print("\nDetailed Results:")
            print(result["overall_summary"])
            
            # Print stat discrepancies
            if result["stat_discrepancies"]:
                print_subheader("Stat Discrepancies")
                for stat, info in result["stat_discrepancies"].items():
                    # For custom stats, show more detailed information
                    if has_custom_stats and stat in custom_stats:
                        custom_val = custom_stats[stat]
                        if info["difference"] > 0:
                            print_error(
                                f"{stat.capitalize()}: Base rules expect {info['expected_total']}, "
                                f"found {info['actual']} without custom adjustment "
                                f"(over-allocated by {info['difference']})"
                            )
                            print(f"  Custom adjustment: {'+' if custom_val > 0 else ''}{custom_val}")
                            print(f"  Final value: {info.get('full_actual', info['actual'] + custom_val)}")
                        else:
                            print_warning(
                                f"{stat.capitalize()}: Base rules expect {info['expected_total']}, "
                                f"found {info['actual']} without custom adjustment "
                                f"(under-allocated by {abs(info['difference'])})"
                            )
                            print(f"  Custom adjustment: {'+' if custom_val > 0 else ''}{custom_val}")
                            print(f"  Final value: {info.get('full_actual', info['actual'] + custom_val)}")
                    else:
                        # Standard display for non-custom stats
                        if info["difference"] > 0:
                            print_error(f"{stat.capitalize()}: {info['actual']} (expected {info['expected_total']}, over-allocated by {info['difference']})")
                        else:
                            print_warning(f"{stat.capitalize()}: {info['actual']} (expected {info['expected_total']}, under-allocated by {abs(info['difference'])})")
            
            # Print free points discrepancy
            fp = result["free_points"]
            print_subheader("Free Points")
            print(f"Current: {fp['current']}")
            print(f"Total received: {fp['expected_total']}")
            print(f"Spent: {fp['spent']}")
            
            if fp["difference"] != 0:
                if fp["difference"] > 0:
                    print_warning(f"Discrepancy: {fp['difference']} unaccounted for")
                else:
                    print_error(f"Discrepancy: {abs(fp['difference'])} too many spent")
        
        # Offer repair options if invalid
        if not result["valid"]:
            print_subheader("Repair Options")
            print_info("Unfortunately, automatic repair is not implemented yet.")
            print_info("Please manually adjust your character stats based on the discrepancies reported above.")
    
    except Exception as e:
        print_error(f"Error validating character: {str(e)}")
    
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
        enemy_stats = {stat: character.data_manager.get_stat(stat) for stat in STATS}
        enemy_meta = {info: character.data_manager.get_meta(info) for info in META_INFO if info not in DERIVED_META}
        
        enemy = Character(
            name=f"{character.name}'s Clone",
            stats=enemy_stats,
            meta=enemy_meta,
            item_repository=item_repository
        )
    
    elif choice == '2':
        # Create a standard enemy
        enemy_stats = {stat: 50 for stat in STATS}
        enemy = Character(
            name="Standard Enemy",
            stats=enemy_stats,
            meta={"Class": "Monster", "Class level": "10", "Profession": "Destroyer", "Profession level": "10", "Race": "Monster"},
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
            meta={"Class": "Custom", "Class level": "1", "Profession": "Custom", "Profession level": "1", "Race": "Custom"},
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
        hit, damage, net_damage = character.attack(enemy)
        
        if hit:
            print_success(f"{character.name} hit for {net_damage} damage!")
        else:
            print_error(f"{character.name} missed!")
        
        if not enemy.health_manager.is_alive():
            print_success(f"\n{enemy.name} was defeated in round {round_num}!")
            break
        
        # Enemy attacks character
        hit, damage, net_damage = enemy.attack(character)
        
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
        
        # Record stats before equipping
        before_stats = {stat: character.data_manager.get_stat(stat) for stat in STATS}
        
        # Equip the item
        success = character.equip_item(item_to_equip.name)
        
        if success:
            print_success(f"Equipped {item_to_equip.name.title()}.")
            
            # Show stat changes
            after_stats = {stat: character.data_manager.get_stat(stat) for stat in STATS}
            changed_stats = []
            
            for stat in STATS:
                if after_stats[stat] != before_stats[stat]:
                    diff = after_stats[stat] - before_stats[stat]
                    changed_stats.append(f"{stat.capitalize()}: {before_stats[stat]} → {after_stats[stat]} ({'+' if diff > 0 else ''}{diff})")
            
            if changed_stats:
                print_subheader("Stat Changes")
                for change in changed_stats:
                    print(change)
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
        
        # Record stats before unequipping
        before_stats = {stat: character.data_manager.get_stat(stat) for stat in STATS}
        
        # Unequip the item
        success = character.unequip_item(item_to_unequip.name)
        
        if success:
            print_success(f"Unequipped {item_to_unequip.name.title()}.")
            
            # Show stat changes
            after_stats = {stat: character.data_manager.get_stat(stat) for stat in STATS}
            changed_stats = []
            
            for stat in STATS:
                if after_stats[stat] != before_stats[stat]:
                    diff = after_stats[stat] - before_stats[stat]
                    changed_stats.append(f"{stat.capitalize()}: {before_stats[stat]} → {after_stats[stat]} ({'+' if diff > 0 else ''}{diff})")
            
            if changed_stats:
                print_subheader("Stat Changes")
                for change in changed_stats:
                    print(change)
        else:
            print_error(f"Failed to unequip {item_to_unequip.name.title()}.")
    
    except Exception as e:
        print_error(f"Error unequipping item: {str(e)}")
    
    pause_screen()

# ============================================================================
# Main Application
# ============================================================================

def main():
    """Main application entry point."""
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
            # No character loaded menu
            if choice == '1':
                character = create_character(item_repository)
            elif choice == '2':
                character, save_file = load_character(item_repository)
            elif choice == '0':
                print_success("Thank you for using the AoP Character Creator!")
                sys.exit(0)
            else:
                print_error("Invalid choice.")
                pause_screen()
        else:
            # Character loaded menu
            if choice == '1':
                view_character(character)
            elif choice == '2':
                update_stats(character)
            elif choice == '3':
                update_meta(character)
            elif choice == '4':
                level_up_character(character)
            elif choice == '5':
                simulate_combat(character, item_repository)
            elif choice == '6':
                manage_inventory(character, item_repository)
            elif choice == '7':
                save_character(character, save_file)
            elif choice == '8':
                create_character_sheet(character)
            elif choice == '9':
                allocate_points(character)
            elif choice == '10':
                add_blessing(character)
            elif choice == '11':
                validate_character_stats(character)
            elif choice == '12':
                if confirm_action("Are you sure you want to unload the current character?"):
                    character = None
                    save_file = None
            elif choice == '0':
                if character and confirm_action("Do you want to save before exiting?"):
                    save_character(character, save_file)
                print_success("Thank you for using the AoP Character Creator!")
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