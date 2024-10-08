import os
from Character_Creator import Character, Simulator

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu(character: Character):
    print("Character Creator Tester\n")
    
    if character is None:
        print("1. Create a new character")
        print("2. Load a character")
        print("0. Exit")
    else:
        print('\x1B[4m' + fr'Welcome {character.name}!' + '\x1B[0m' + '\n')
        print("1. View character details")
        print("2. Update character stats")
        print("3. Update character meta information")
        print("4. Level up character")
        print("5. Simulate combat")
        print("6. Save character to CSV")
        print("7. Create character sheet")
        print("8. Allocate free points")
        print("9. Add Blessing")
        print("10. Start Over")
        print("0. Exit")

def create_character():
    name = input("Enter character name: ")
    return Character.from_manual_input(name)

def load_character():
    filename = input(r"Enter the CSV filename to load from: ")
    _, ext = os.path.splitext(filename)
    
    if not ext:
            filename = filename + '.csv'
    else:
            if not ext.endswith('.csv'):
                raise ValueError('This is not a csv file! PLease provide a csv file path.')
            
    if not os.path.exists(filename):
        print('\n' + 'File does not exist'.center(50, '-'))
        print(f'This is your current directory: {os.getcwd()}')
        print('Starting over...')
        return None
    
    name = input("Enter the character name to load: ")
    return Character.load_character(filename, name), filename

def view_character(character: Character):
    if character:
        print(character)
    else:
        print("No character loaded.")

def update_stats(character: Character):
    if character:
        stat = input("Enter the stat to update: ").lower()
        if stat in character.STATS:
            value = int(input(f"Enter new value for {stat}: "))
            character.update_stat(stat, value)
            print(f"Updated {stat} to {value}")
        else:
            print("Invalid stat.")
    else:
        print("No character loaded.")

def update_meta(character: Character):
    if character:
        info = input("Enter the meta info to update: ")
        if info in character.META:
            value = input(f"Enter new value for {info}: ")
            character.update_meta(info, value)
            print(f"Updated {info} to {value}")
        else:
            print("Invalid meta info.")
    else:
        print("No character loaded.")

def level_up(character: Character):
    if character:
        level_type = input("Enter level type (Class or Profession): ")
        target_level = int(input("Enter target level: "))
        character.level_up(level_type, target_level)
        
        blessing = input('Do you want to add a blessing (yes/no)? ')
        
        if blessing.lower() == 'yes':
            character.add_blessing()
    else:
        print("No character loaded.")
        
def blessing(character: Character):
    character.add_blessing()
        
def level_up_incr_levels(character: Character):
    if character:
        level_type = input("Enter level type (Class or Profession): ")
        incr_levels = int(input("How many levels? "))
        target_level = int(character.meta[level_type]) + incr_levels
        character.level_up(level_type, target_level)
    else:
        print("No character loaded.")

def simulate_combat(character: Character):
    if character:
        print("Choose your opponent:")
        print("1. Fight against your own character")
        print("2. Fight against a hypothetical enemy (all stats 50)")
        choice = input("Enter your choice (1 or 2): ")
        
        if choice == '1':
            enemy = Character(f"{character.name}'s Clone", stats=character.stats.copy())
        elif choice == '2':
            enemy = Character("Enemy", stats={stat: 50 for stat in Character.STATS})
        else:
            print("Invalid choice. Defaulting to hypothetical enemy.")
            enemy = Character("Enemy", stats={stat: 50 for stat in Character.STATS})

        print(f"{character.name} vs {enemy.name}")
        for round in range(1, 6):
            print(f"\nRound {round}:")
            hit, damage, net_damage = character.attack(enemy)
            print(f"{character.name} {'hit' if hit else 'missed'} for {net_damage} damage")
            print(f"{enemy.name}'s health: {enemy.current_health}/{enemy.max_health}")
            if not enemy.is_alive():
                print("Enemy defeated!")
                break
            hit, damage, net_damage = enemy.attack(character)
            print(f"{enemy.name} {'hit' if hit else 'missed'} for {net_damage} damage")
            print(f"{character.name}'s health: {character.current_health}/{character.max_health}")
            if not character.is_alive():
                print(f"{character.name} was defeated!")
                break
        
        character.reset_health()
        print("Combat simulation complete.")
    else:
        print("No character loaded.")

def save_character(character: Character, file: str):
    if character and not file:
        filename = input(r"Enter the CSV filename to save to: ")
        character.to_csv(filename)
    elif file:
        character.to_csv(file)
    else:
        print("No character loaded.")

def create_sheet(character: Character):
    if character:
        character.create_character_sheet()
        print("Character sheet created.")
    else:
        print("No character loaded.")

def allocate_points(character: Character):
    if character:
        character.allocate_free_points()
    else:
        print("No character loaded.")

def main():
    character = None
    file = None
    while True:
        clear_screen()
        print_menu(character)
        choice = input("\nEnter your choice: ")
        
        if character is None:
            match choice:
                case '1':
                    character = create_character()
                case '2':
                    character, file = load_character()
                case '0':
                    print("Thank you for using the Character Creator Tester!")
                    break
                case _:
                    print("Invalid choice. Please try again.")
        else:
            match choice:
                case '1':
                    clear_screen()
                    view_character(character)
                case '2':
                    clear_screen()
                    update_stats(character)
                case '3':
                    clear_screen()
                    update_meta(character)
                case '4':
                    clear_screen()
                    level_up(character)
                case '5':
                    clear_screen() 
                    simulate_combat(character)
                case '6':
                    clear_screen()
                    save_character(character, file)
                case '7':
                    clear_screen()
                    create_sheet(character)
                case '8':
                    clear_screen()
                    allocate_points(character)
                case '9':
                    clear_screen()
                    blessing(character)
                case '10':
                    character = None
                case '0':
                    print("Thank you for using the Character Creator Tester!")
                    break
                case _:
                    print("Invalid choice. Please try again.")
        
        print()
        os.system('pause')

if __name__ == "__main__":
    main()