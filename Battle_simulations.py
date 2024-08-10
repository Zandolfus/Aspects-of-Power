import pandas as pd
import statistics
import tkinter.filedialog
from random import randint
from Weapons import weapons

def get_stats() -> pd.DataFrame:
    file = tkinter.filedialog.askopenfilename(title='Pick your character!')

    if not file:
        raise FileNotFoundError('No file specified. Please choose a file')

    stats = pd.read_csv(file)
    names = file.split('/')[-1].strip('.csv')

    return stats, names

def to_hit(dex_mod: int, str_mod: int, defense: int):
    roll = randint(1, 20)
    
    to_hit = round(((roll/100)*(dex_mod + str_mod*0.3) + dex_mod + str_mod*0.3)*0.911, 0)
    
    if to_hit >= defense:
        hit = True
    else:
        hit = False
    
    return to_hit, hit, roll

def dmg(dmg_mod: int, dex_mod: int = None, dice: str = '2d6'):
    if (dices := int(dice.split('d')[0])) > 1:
        rolls = [randint(1, int(dice.split('d')[1])) for _ in range(dices)]
        roll = sum(rolls)
    else:
        roll = randint(1, int(dice.split('d')[1]))
    
    if dex_mod is None:
        dmg = int(round(((roll/50)*(dmg_mod) + dmg_mod)*0.5, 0))
    else:
        dmg = int(round(((roll/50)*(dmg_mod + dex_mod*0.25) + dmg_mod + dex_mod*0.25)*1.1, 0))
    
    return dmg, roll

def to_hit_sim(p1: pd.DataFrame, p2: pd.DataFrame = None, p1_name: str = None, p2_name: str = None, sims: int = 10) -> None:
    if p2 is None:
        str_mod = p1.loc[p1['Attribute'] == 'Strength', 'Modifier'].iloc[0]
        dex_mod = p1.loc[p1['Attribute'] == 'Dexterity', 'Modifier'].iloc[0]
        
        sims = 15000
        # str_mod = 300
        # dex_mod = 1000

        defense = round(dex_mod + str_mod*0.3, 0)
        
        hit_scores = []
        hits = []
        for sim in range(sims):
            score, hit, _ = to_hit(dex_mod, str_mod, defense)
            hit_scores.append(score)
            hits.append(hit)
        
        print(f'Hit rate for {sims} simulations: {(sum(hits)/sims*100)}%')
        print(f'Mean to_hit values: {statistics.mean(hit_scores)}')
    else:
        p1_str_mod = p1.loc[p1['Attribute'] == 'Strength', 'Modifier'].iloc[0]
        p1_dex_mod = p1.loc[p1['Attribute'] == 'Dexterity', 'Modifier'].iloc[0]
        p2_str_mod = p2.loc[p2['Attribute'] == 'Strength', 'Modifier'].iloc[0]
        p2_dex_mod = p2.loc[p2['Attribute'] == 'Dexterity', 'Modifier'].iloc[0]
        
        sims = 15000
        # str_mod = 300
        # dex_mod = 1000

        defense = int(round(p2_dex_mod + p2_str_mod*0.3, 0))
        
        hit_scores = []
        hits = []
        for sim in range(sims):
            score, hit, _ = to_hit(p1_dex_mod, p1_str_mod, defense)
            hit_scores.append(score)
            hits.append(hit)
        
        print(f'{p1_name} vs. {p2_name}'.center(20, '-'))
        print(f'Hit rate for {sims} simulations: {(sum(hits)/sims*100)}%')
        print(f'Defense: {defense}')
        print(f'Mean to_hit values: {statistics.mean(hit_scores)}')

def damage_sim(df: pd.DataFrame, sims: int = 10, dice: str = '2d6', dex: bool = False, spell: bool = False):
    if spell is False:
        dmg_mod = df.loc[df['Attribute'] == 'Strength', 'Modifier'].iloc[0]
        dex_mod = df.loc[df['Attribute'] == 'Dexterity', 'Modifier'].iloc[0]
        weapon_type = 'Martial'
    else:
        dmg_mod = df.loc[df['Attribute'] == 'Intelligence', 'Modifier'].iloc[0]
        dex_mod = None
        weapon_type = 'Spell'
    
    dex = False
    sims = 15000
    dmg_mod = 146
    dice = '2d6'
    
    dmg_values = []
    for sim in range(sims):
        dmg_score, _ = dmg(dmg_mod, dex_mod, dice)
                    
        # print(dmg)
        dmg_values.append(dmg_score)
    
    print(f'Attack type: {weapon_type}')
    print(f'Damage dice: {dice}')
    print(f'Mean of damage values: {statistics.mean(dmg_values)}')

def battle_sim(p1: pd.DataFrame, p2: pd.DataFrame = None, p1_name: str = None, p2_name: str = None, sims: int = 10, dice: str = '2d6', dex: bool = True):
    if p2 is None:
        dmg_mod = p1.loc[p1['Attribute'] == 'Strength', 'Modifier'].iloc[0]
        dex_mod = p1.loc[p1['Attribute'] == 'Dexterity', 'Modifier'].iloc[0]
        vit_mod = p1.loc[p1['Attribute'] == 'Vitality', 'Modifier'].iloc[0]
        tough_mod = p1.loc[p1['Attribute'] == 'Toughness', 'Modifier'].iloc[0]

        sims = 15000
        # str_mod = 143
        # dex = False
        # dex_mod = 1000

        defense = int(round(dex_mod + dmg_mod*0.3, 0))

        all_dmg_values = []
        all_dmg_rolls = []
        all_hits = []
        for sim in range(sims):
            health = vit_mod
            sim_dmg_values = []
            sim_dmg_rolls = []
            sim_hits = []
            while True:
                to_hit_score, hit, to_hit_roll = to_hit(dex_mod, dmg_mod, defense)

                dmg_score, dmg_roll = dmg(dmg_mod, dex_mod, dice)
                net_dmg = dmg_score - tough_mod

                if hit is True and net_dmg > 0:
                    health -= net_dmg

                sim_dmg_values.append(dmg_score)
                sim_dmg_rolls.append(dmg_roll)
                sim_hits.append(hit)

                if health <= 0:
                    all_dmg_values.append(sim_dmg_values)
                    all_dmg_rolls.append(sim_dmg_rolls)
                    all_hits.append(sim_hits)
                    break
            
        print('\033[1m' + 'Summary Stats'.center(30) + '\033[0m')
        print(f'{p1_name} vs. {p1_name}'.center(20, '-'))
        print(f'Average amount of attacks until death: {statistics.mean([len(val) for val in all_dmg_values])}')
        print(f'Average hit rate(%): {round(statistics.mean([sum(hits)/len(hits)*100 for hits in all_hits]), 2)}%')
        print(f'Mean of damage values: {round(statistics.mean([val for values in all_dmg_values for val in values]), 2)}')
    else:
        p1_dmg_mod = p1.loc[p1['Attribute'] == 'Strength', 'Modifier'].iloc[0]
        p1_dex_mod = p1.loc[p1['Attribute'] == 'Dexterity', 'Modifier'].iloc[0]
        p2_dmg_mod = p2.loc[p2['Attribute'] == 'Strength', 'Modifier'].iloc[0]
        p2_dex_mod = p2.loc[p2['Attribute'] == 'Dexterity', 'Modifier'].iloc[0]
        vit_mod = p2.loc[p2['Attribute'] == 'Vitality', 'Modifier'].iloc[0]
        tough_mod = p2.loc[p2['Attribute'] == 'Toughness', 'Modifier'].iloc[0]

        sims = 15000
        # str_mod = 143
        # dex = False
        # p1_dex_mod = 1000

        defense = int(round(p2_dex_mod + p2_dmg_mod*0.3, 0))

        all_dmg_values = []
        all_dmg_rolls = []
        all_hits = []
        for sim in range(sims):
            health = vit_mod
            sim_dmg_values = []
            sim_dmg_rolls = []
            sim_hits = []
            while True:
                to_hit_score, hit, to_hit_roll = to_hit(p1_dex_mod, p1_dmg_mod, defense)

                dmg_score, dmg_roll = dmg(p1_dmg_mod, p1_dex_mod, dice)
                net_dmg = dmg_score - tough_mod

                if hit is True and net_dmg > 0:
                    health -= net_dmg

                sim_dmg_values.append(dmg_score)
                sim_dmg_rolls.append(dmg_roll)
                sim_hits.append(hit)

                if health <= 0:
                    all_dmg_values.append(sim_dmg_values)
                    all_dmg_rolls.append(sim_dmg_rolls)
                    all_hits.append(sim_hits)
                    break
            
        print('\033[1m' + 'Summary Stats'.center(30) + '\033[0m')
        print(f'{p1_name} vs. {p2_name}'.center(20, '-'))
        print(f'Average amount of attacks until death: {statistics.mean([len(val) for val in all_dmg_values])}')
        print(f'Average hit rate(%): {round(statistics.mean([sum(hits)/len(hits)*100 for hits in all_hits]), 2)}%')
        print(f'Mean of damage values: {round(statistics.mean([val for values in all_dmg_values for val in values]), 2)}')

def pvp() -> None:
    df1, name1 = get_stats()
    df2, name2 = get_stats()
    to_hit_sim(df1, df2, p1_name=name1, p2_name=name2)
    battle_sim(df1, df2, p1_name=name1, p2_name=name2)

def main() -> None:
    df, name = get_stats()
    to_hit_sim(df)
    damage_sim(df)

if __name__ == '__main__':
    df, name = get_stats()
    damage_sim(df)
