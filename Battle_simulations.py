import pandas as pd
import statistics
import tkinter.filedialog
from random import randint

def get_stats() -> pd.DataFrame:
    file = tkinter.filedialog.askopenfilename()

    if not file:
        print('No file specified. Please choose a file')

    stats = pd.read_csv(file)

    return stats

def to_hit_sim(df: pd.DataFrame, sims: int = 10) -> None:
    str_mod = df.loc[df['Attribute'] == 'Strength', 'Modifier'].iloc[0]
    dex_mod = df.loc[df['Attribute'] == 'Dexterity', 'Modifier'].iloc[0]
    sims = 15000
    
    # str_mod = 300
    # dex_mod = 1000

    defense = round(dex_mod + str_mod*0.3, 0)
    
    hit_scores = []
    hits = 0
    for sim in range(sims):
        roll = randint(0, 20)
        to_hit = round(((roll/100)*(dex_mod + str_mod*0.3) + dex_mod + str_mod*0.3)*0.911, 0)
        hit_scores.append(to_hit)
        
        # print(f'Roll: {roll}')
        # print(f'To_Hit: {to_hit}')
        # print(f'Melee Defense: {defense}', end='\n\n')
        
        if to_hit >= defense:
            hits += 1
    
    print(f'Hit rate for {sims} simulations: {(hits/sims*100)}%')
    print(f'Mean to_hit values: {statistics.mean(hit_scores)}')
    
def damage_sim(df: pd.DataFrame, sims: int = 10, dice: str = '2d6', dex: bool = True):
    str_mod = df.loc[df['Attribute'] == 'Strength', 'Modifier'].iloc[0]
    dex_mod = df.loc[df['Attribute'] == 'Dexterity', 'Modifier'].iloc[0]
    
    sims = 15000
    
    dmg_values = []
    for sim in range(sims):
        if dice == '2d6':
            roll1 = randint(1,6)
            roll2 = randint(1,6)
            roll = roll1 + roll2
        dmg = int(round(((roll/50)*(str_mod) + str_mod)*0.5, 0))
        
        if dex is True:
            dmg = int(round(((roll/50)*(str_mod + dex_mod*0.25) + str_mod + dex_mod*0.25)*0.6, 0))
                    
        # print(dmg)
        dmg_values.append(dmg)
    
    print(f'Mean of damage values: {statistics.mean(dmg_values)}')
    
def battle_sim(df: pd.DataFrame, sims: int = 10, dice: str = '2d6', dex: bool = True):
    str_mod = df.loc[df['Attribute'] == 'Strength', 'Modifier'].iloc[0]
    dex_mod = df.loc[df['Attribute'] == 'Dexterity', 'Modifier'].iloc[0]
    vit_mod = df.loc[df['Attribute'] == 'Vitality', 'Modifier'].iloc[0]
    tough_mod = df.loc[df['Attribute'] == 'Toughness', 'Modifier'].iloc[0]
    
    sims = 1000
    # str_mod = 143
    # dex = False
    # dex_mod = 1000
    
    for sim in range(sims):
        health = 0
        attk = 0
        dmg_values = []
        while True:
            if dice == '2d6':
                roll1 = randint(1,6)
                roll2 = randint(1,6)
                roll = roll1 + roll2
            dmg = int(round(((roll/50)*(str_mod) + str_mod)*0.5, 0))
            
            if dex is True:
                dmg = int(round(((roll/50)*(str_mod + dex_mod*0.25) + str_mod + dex_mod*0.25)*0.6, 0))
            
            attk += 1
            health -= dmg - tough_mod
                        
            # print(dmg)
            dmg_values.append(dmg)
            
            if health <= 0:
                break
        
        print(f'Attacks until death: {attk}')
        print(f'Mean of damage values: {statistics.mean(dmg_values)}')

    
def main() -> None:
    df = get_stats()
    to_hit_sim(df)
    damage_sim(df)

if __name__ == '__main__':
    df = get_stats()
    damage_sim(df)