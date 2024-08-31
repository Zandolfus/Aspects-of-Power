import os
from Character_Creator import Character, Simulator

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu():
    print("\nCharacter Creator Tester")
    print("1. Create a new character")
    print("2. Load a character")
    print("3. View character details")
    print("4. Update character stats")
    print("5. Update character meta information")
    print("6. Level up character")
    print("7. Simulate combat")
    print("8. Save character to CSV")
    print("9. Create character sheet")
    print("10. Allocate free points")
    print("0. Exit")

def create_character():
    name = input("Enter character name: ")
    return Character.from_manual_input(name)

def load_character():
    filename = input("Enter the CSV filename to load from: ")
    name = input("Enter the character name to load: ")
    return Character.load_character(filename, name)

def view_character(character):
    if character:
        print(character)
    else:
        print("No character loaded.")

def update_stats(character):
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

def update_meta(character):
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

def level_up(character):
    if character:
        level_type = input("Enter level type (Class or Profession): ")
        target_level = int(input("Enter target level: "))
        character.level_up(level_type, target_level)
    else:
        print("No character loaded.")

def simulate_combat(character):
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

def save_character(character):
    if character:
        filename = input("Enter the CSV filename to save to: ")
        character.to_csv(filename)
    else:
        print("No character loaded.")

def create_sheet(character):
    if character:
        character.create_character_sheet()
        print("Character sheet created.")
    else:
        print("No character loaded.")

def allocate_points(character):
    if character:
        character.allocate_free_points()
    else:
        print("No character loaded.")

def main():
    character = None
    while True:
        clear_screen()
        print_menu()
        choice = input("Enter your choice: ")
        
        if choice == '1':
            character = create_character()
            print(character)
        elif choice == '2':
            character = load_character()
            print(character)
        elif choice == '3':
            view_character(character)
        elif choice == '4':
            update_stats(character)
        elif choice == '5':
            update_meta(character)
        elif choice == '6':
            level_up(character)
        elif choice == '7':
            simulate_combat(character)
        elif choice == '8':
            save_character(character)
        elif choice == '9':
            create_sheet(character)
        elif choice == '10':
            allocate_points(character)
        elif choice == '0':
            print("Thank you for using the Character Creator Tester!")
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()