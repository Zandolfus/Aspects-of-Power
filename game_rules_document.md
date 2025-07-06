# Aspects of Power
## Complete Game Rules Reference

---

## Table of Contents

1. [Character Basics](#character-basics)
2. [Core Statistics](#core-statistics)
3. [Character Types & Progression](#character-types--progression)
4. [Class & Profession System](#class--profession-system)
5. [Combat System](#combat-system)
6. [Character Creation & Validation](#character-creation--validation)
7. [Equipment & Items](#equipment--items)
8. [Advanced Systems](#advanced-systems)
9. [Quick Reference Tables](#quick-reference-tables)

---

## Character Basics

### The Nine Core Stats

Every character in Aspects of Power is defined by nine fundamental statistics that determine their capabilities in all aspects of the game:

| Stat | Purpose | Affects |
|------|---------|---------|
| **Vitality** | Life force and health | Maximum health points |
| **Endurance** | Physical stamina | Sustained activities, fatigue resistance |
| **Strength** | Raw physical power | Melee damage, carrying capacity |
| **Dexterity** | Speed and precision | Attack accuracy, defense, finesse damage |
| **Toughness** | Physical resistance | Damage reduction, armor effectiveness |
| **Intelligence** | Mental acuity | Magical power, learning ability |
| **Willpower** | Mental fortitude | Magic resistance, mental effects |
| **Wisdom** | Intuition and insight | Spiritual awareness, perception |
| **Perception** | Awareness and senses | Detection, initiative, ranged accuracy |

### Character Identity

Each character has essential identifying information:

- **Name**: Character's identifier
- **Character Type**: Standard Character, Familiar, or Monster
- **Race**: Determines racial abilities and progression
- **Class**: Primary combat/magical specialization (if applicable)
- **Profession**: Secondary skillset specialization (if applicable)

---

## Core Statistics

### Stat Calculation Formula

All stats use a sophisticated exponential modifier system that provides meaningful scaling:

```
Modifier = round((6000 / (1 + e^(-0.001 × (stat - 500)))) - 2265)
```

**Key Points:**
- Base stats start at 5 for new characters
- Modifiers become increasingly powerful at higher stat values
- The formula ensures smooth progression without sudden jumps

### Stat Source System

Character stats are built from **seven distinct sources** that stack additively:

| Source | Description | Examples |
|--------|-------------|----------|
| **Base** | Starting character foundation | Default 5 per stat |
| **Class** | Combat specialization bonuses | Mage gets +2 Intelligence |
| **Profession** | Skill specialization bonuses | Scholar gets +1 Wisdom |
| **Race** | Racial heritage bonuses | Elf gets +1 Dexterity |
| **Items** | Equipment bonuses | Magic sword gives +2 Strength |
| **Blessing** | Divine/magical enhancements | God's favor grants +3 Willpower |
| **Free Points** | Player-allocated bonuses | Distribute earned points freely |

**Total Stat = Base + Class + Profession + Race + Items + Blessing + Free Points**

### Health System

**Maximum Health = Vitality Modifier**

Health is directly tied to your Vitality stat's modifier value. As Vitality increases, the exponential formula means health grows significantly at higher levels.

---

## Character Types & Progression

### Standard Characters
*The primary player character type*

**Leveling Options:**
- ✅ **Class Levels**: Combat and magical specializations
- ✅ **Profession Levels**: Skill-based specializations  
- ✅ **Race Levels**: Racial abilities and heritage powers

**Characteristics:**
- Most versatile progression path
- Access to full tier system
- Can multiclass between different specializations
- Highest potential power level

### Familiars
*Magical companions and bonded creatures*

**Leveling Options:**
- ❌ **Class Levels**: Cannot take combat classes
- ❌ **Profession Levels**: Cannot take skill professions
- ✅ **Race Levels**: Only racial progression available

**Characteristics:**
- Simpler progression focused on natural abilities
- Tied to a master character
- Specialized racial powers
- Limited but focused growth

### Monsters
*Creatures, beasts, and antagonists*

**Leveling Options:**
- ❌ **Class Levels**: Cannot take combat classes
- ❌ **Profession Levels**: Cannot take skill professions  
- ✅ **Race Levels**: Only racial progression available

**Characteristics:**
- Similar to familiars but typically stronger
- Focus on natural weapons and abilities
- Varied power levels based on creature type
- NPC-focused design

---

## Class & Profession System

### Tier Structure

Character advancement is organized into **four progressive tiers** with customizable thresholds:

| Tier | Default Level Range | Power Level | Available Options |
|------|-------------------|-------------|-------------------|
| **Tier 1** | Levels 1-24 | Novice | Basic classes and professions |
| **Tier 2** | Levels 25-99 | Adept | Advanced specializations |
| **Tier 3** | Levels 100-199 | Expert | Master-level abilities |
| **Tier 4** | Levels 200+ | Legendary | Ultimate powers |

> **Note**: Each character can have **personalized tier thresholds** that differ from the defaults, allowing for customized progression pacing.

### Tier 1 Classes
*Foundation combat specializations*

Each Tier 1 class grants **8 total stat points** (6 fixed + 2 free allocation):

#### 🗡️ **Heavy Warrior**
*Armored frontline fighter*
- **Strength** +2, **Vitality** +2
- **Endurance** +1, **Toughness** +1
- **Free Points** +2
- *Focus: Tank, high damage, heavy armor*

#### ⚔️ **Medium Warrior** 
*Balanced combat specialist*
- **Strength** +2, **Dexterity** +2
- **Endurance** +1, **Vitality** +1
- **Free Points** +2
- *Focus: Versatile fighter, moderate armor*

#### 🗡️ **Light Warrior**
*Mobile skirmisher*
- **Dexterity** +2, **Endurance** +2
- **Vitality** +1, **Strength** +1
- **Free Points** +2
- *Focus: Speed, mobility, light armor*

#### 🏹 **Archer**
*Ranged combat expert*
- **Perception** +2, **Dexterity** +2
- **Endurance** +1, **Vitality** +1
- **Free Points** +2
- *Focus: Ranged attacks, precision, mobility*

#### 🔮 **Mage**
*Arcane spellcaster*
- **Intelligence** +2, **Willpower** +2
- **Wisdom** +1, **Perception** +1
- **Free Points** +2
- *Focus: Offensive magic, arcane knowledge*

#### ⚕️ **Healer**
*Divine spellcaster*
- **Willpower** +2, **Wisdom** +2
- **Intelligence** +1, **Perception** +1
- **Free Points** +2
- *Focus: Healing, support magic, divine power*

### Tier 2 Classes
*Advanced specializations requiring mastery*

Each Tier 2 class grants **18 total stat points** (14 fixed + 4 free allocation):

#### ⚡ **Thunder Puppet's Shadow**
*Lightning-fast assassin*
- **Dexterity** +5, **Strength** +4
- **Vitality** +3, **Endurance** +2
- **Free Points** +4
- *Focus: Speed, stealth, burst damage*

#### 🌟 **Astral Aetherologist**
*Master of cosmic magic*
- **Intelligence** +5, **Willpower** +4
- **Wisdom** +3, **Perception** +2
- **Free Points** +4
- *Focus: Reality manipulation, astral projection*

#### ✨ **Glamourweaver**
*Illusion and enchantment specialist*
- **Wisdom** +5, **Intelligence** +4
- **Willpower** +3, **Toughness** +2
- **Free Points** +4
- *Focus: Mind control, illusions, social manipulation*

#### 👁️ **Waywatcher**
*Elite scout and tracker*
- **Perception** +5, **Dexterity** +4
- **Wisdom** +3, **Toughness** +2
- **Free Points** +4
- *Focus: Tracking, survival, ranged combat*

#### 🌲 **Glade Guardian**
*Nature's protector*
- **Dexterity** +5, **Strength** +4
- **Toughness** +3, **Wisdom** +2
- **Free Points** +4
- *Focus: Nature magic, protection, balance*

#### 🎯 **Sniper**
*Master marksman*
- **Perception** +5, **Dexterity** +4
- **Endurance** +3, **Toughness** +2
- **Free Points** +4
- *Focus: Extreme range, precision, patience*

### Profession System

Professions follow the same tier structure as classes but focus on **non-combat specializations**:

- **Crafting**: Smithing, Alchemy, Enchanting
- **Social**: Diplomacy, Trading, Leadership  
- **Knowledge**: Scholarship, Investigation, Lore
- **Survival**: Wilderness, Navigation, Hunting

*Specific profession stat bonuses follow similar patterns to classes but emphasize different stat combinations*

---

## Combat System

### Initiative & Turn Order

**Initiative Formula**: `1d20 × (Perception Modifier ÷ 100) + Perception Modifier`

Higher Perception gives both better initiative rolls and higher base initiative, making perceptive characters consistently faster.

### Attack Resolution

Combat uses a **two-step process**: Hit Determination → Damage Calculation

#### Step 1: Hit Determination

**Attacker Rolls**: 1d20

**To-Hit Score Calculation**:
```
to_hit = round(((d20_roll ÷ 100) × (dex_mod + str_mod × 0.6) + dex_mod + str_mod × 0.6) × 0.911)
```

**Defender's Defense Score**:
```
defense = round(dex_mod + str_mod × 0.3)
```

**Hit Result**: Attack hits if `to_hit ≥ defense`

> **Key Insight**: Dexterity is the primary factor for both offense and defense, while Strength provides moderate offensive support.

#### Step 2: Damage Calculation

**Base Damage Roll**: 2d6

##### Standard Damage (Strength-based)
```
damage = round(((2d6_roll ÷ 50) × str_mod + str_mod) × 0.5)
```

##### Finesse Damage (Dexterity-enhanced)
```
damage = round(((2d6_roll ÷ 50) × (str_mod + dex_mod × 0.25) + str_mod + dex_mod × 0.25) × 0.6)
```

**Final Damage**: `max(0, calculated_damage - target_toughness_modifier)`

### Finesse Combat

Certain character classes and weapon types use **Finesse Combat**:

- **Who Gets It**: Light Warriors, Rogues, some Tier 2 classes
- **Benefit**: Incorporates Dexterity into damage calculations
- **Trade-off**: Slightly lower raw damage but benefits from Dex investment
- **Synergy**: Same stat (Dex) improves accuracy, defense, AND damage

### Combat Example

> **Example Combat Round**
> 
> **Attacker**: Medium Warrior (Str 15, Dex 12)
> - Str Modifier: 8, Dex Modifier: 6
> - Rolls 1d20: 14
> - To-hit: round(((14÷100) × (6 + 8×0.6) + 6 + 8×0.6) × 0.911) = round((0.14 × 10.8 + 10.8) × 0.911) = **11**
> 
> **Defender**: Light Warrior (Str 10, Dex 16)  
> - Defense: round(9 + 5×0.3) = **11**
> 
> **Result**: 11 ≥ 11 = **HIT!**
> 
> **Damage**: Rolls 2d6: 8
> - Standard damage: round(((8÷50) × 8 + 8) × 0.5) = round((1.28 + 8) × 0.5) = **5**
> - Target Toughness Modifier: 4
> - **Final Damage**: 5 - 4 = **1 point**

---

## Character Creation & Validation

### Creation Methods

#### Calculated Characters
*Recommended for most players*

**Process**:
1. Set base stats (default 5 each)
2. Choose race, class, profession
3. Level character through intended progression
4. System automatically applies all bonuses
5. Allocate earned free points

**Benefits**:
- Guaranteed rule compliance
- Automatic validation
- Clear progression tracking
- Detailed audit trail

#### Manual Characters  
*For advanced users and special cases*

**Process**:
1. Set any desired stat values directly
2. System tracks as "manual character"
3. Can later validate against progression rules
4. Auto-converts to calculated if valid

**Benefits**:
- Complete creative freedom
- Quick character concepts
- Can represent unique circumstances
- Convertible to standard rules

### Validation System

The game includes **comprehensive stat validation** that checks:

#### ✅ **Stat Allocation Accuracy**
- Total stats must equal: Base + Class + Profession + Race + Items + Blessing + Free Points
- Each source tracked separately
- Identifies over/under allocation

#### ✅ **Free Point Compliance**
- Cannot spend more free points than earned
- Tracks earning sources (class levels, profession levels, special awards)
- Prevents negative free point balances

#### ✅ **Tier Restrictions**
- Classes/professions must be available at character's tier
- Validates level requirements for advanced options
- Ensures logical progression path

#### ✅ **Character Type Rules**
- Familiars/Monsters cannot take class/profession levels
- Standard characters can access all systems
- Proper race-only progression for non-standard types

### Validation Results

When validated, characters receive detailed feedback:

```
✅ VALID CHARACTER
- All stat allocations correct
- Free points: 3 remaining
- Progression path: Legal
- Tier access: Appropriate

❌ INVALID CHARACTER  
- Strength: 2 points over-allocated
- Free points: -5 (overspent)
- Class tier: Requires Tier 2 (currently Tier 1)
```

---

## Equipment & Items

### Item Stat Bonuses

Equipment provides **temporary stat bonuses** that stack with all other sources:

#### Example Items

| Item | Type | Stat Bonuses | Description |
|------|------|--------------|-------------|
| Iron Sword | Weapon | Strength +2 | Basic warrior weapon |
| Leather Armor | Armor | Toughness +1, Dex +1 | Light protection |
| Mage Robes | Armor | Intelligence +3, Willpower +1 | Enhances spellcasting |
| Eagle Eye Bow | Weapon | Perception +2, Dex +1 | Precision ranged weapon |
| Ring of Vitality | Accessory | Vitality +2 | Increases health |

### Equipment Rules

- **Stacking**: All equipment bonuses stack with each other and other stat sources
- **Instant Effect**: Equipping/unequipping immediately changes stats and recalculates health
- **No Limits**: No restrictions on number of stat-boosting items
- **Permanent Until Removed**: Effects last until item is unequipped

### Dynamic Health Updates

When Vitality-boosting items are equipped:
- **Equipping**: Current health increases by the same amount as max health
- **Unequipping**: Current health decreases, but won't go below 1
- **No Healing Required**: Equipment changes are instant

---

## Advanced Systems

### Blessing System

**Blessings** represent divine favor, magical enhancements, or permanent character improvements.

#### Blessing Rules
- **One at a Time**: Only one blessing can be active
- **Permanent Effect**: Lasts until removed or replaced
- **Any Stats**: Can boost any combination of the nine stats
- **Stacks with Everything**: Combines with all other stat sources

#### Example Blessings

| Blessing | Effect | Source |
|----------|--------|--------|
| Warrior's Might | Str +3, Vit +2 | God of War |
| Scholar's Mind | Int +4, Wis +1 | Goddess of Knowledge |
| Nimble Spirit | Dex +2, Per +2, End +1 | Wind Elemental |

### Free Point Management

#### Earning Free Points
- **Class Levels**: Each class level grants 2-4 free points (varies by tier)
- **Profession Levels**: Each profession level grants 1-3 free points
- **Special Events**: GM awards, quest rewards, milestone bonuses

#### Allocation Options

1. **Manual Allocation**
   - Player chooses exactly which stats to improve
   - Full control over character development
   - Permanent once confirmed

2. **Random Allocation**  
   - System randomly distributes all available points
   - Quick option for less tactical players
   - Even distribution across all stats

3. **Save for Later**
   - Reserve points for future use
   - Accumulate larger bonuses
   - Strategic timing for important increases

### Bulk Character Management

The system supports **mass character operations**:

#### Bulk Leveling
- Process multiple characters from CSV files
- Specify level type (Class/Profession/Race) and levels gained
- Choose free point allocation method for all characters
- Batch validation and error reporting

#### Supported Operations
- **Mass Level Up**: Level many characters at once
- **Bulk Validation**: Check entire character rosters
- **Group Stat Changes**: Apply universal modifiers
- **Campaign Progression**: Advance entire parties simultaneously

---

## Quick Reference Tables

### Stat Modifier Quick Reference

| Stat Value | Modifier | Health (if Vitality) |
|------------|----------|---------------------|
| 5 (Base) | -11 | -11 |
| 10 | -8 | -8 |
| 15 | -5 | -5 |
| 20 | -2 | -2 |
| 25 | 1 | 1 |
| 30 | 4 | 4 |
| 40 | 10 | 10 |
| 50 | 16 | 16 |
| 75 | 31 | 31 |
| 100 | 46 | 46 |

### Combat Quick Reference

| Action | Formula |
|--------|---------|
| **Initiative** | `1d20 × (Per_mod ÷ 100) + Per_mod` |
| **To-Hit** | `round(((1d20 ÷ 100) × (dex + str×0.6) + dex + str×0.6) × 0.911)` |
| **Defense** | `round(dex_mod + str_mod × 0.3)` |
| **Standard Damage** | `round(((2d6 ÷ 50) × str_mod + str_mod) × 0.5)` |
| **Finesse Damage** | `round(((2d6 ÷ 50) × (str_mod + dex_mod×0.25) + str_mod + dex_mod×0.25) × 0.6)` |
| **Final Damage** | `max(0, damage - toughness_mod)` |

### Character Type Summary

| Type | Class Levels | Profession Levels | Race Levels | Complexity |
|------|--------------|-------------------|-------------|------------|
| **Character** | ✅ Yes | ✅ Yes | ✅ Yes | High |
| **Familiar** | ❌ No | ❌ No | ✅ Yes | Low |
| **Monster** | ❌ No | ❌ No | ✅ Yes | Low |

### Tier Progression Overview

| Tier | Level Range | Stat Points per Class Level | Available Options |
|------|-------------|----------------------------|-------------------|
| **1** | 1-24 | 8 (6 fixed + 2 free) | 6 basic classes |
| **2** | 25-99 | 18 (14 fixed + 4 free) | 6 advanced classes |
| **3** | 100-199 | TBD | Master specializations |
| **4** | 200+ | TBD | Legendary abilities |

---

*This completes the Aspects of Power game rules reference. For additional mechanics not covered here, consult the game master or refer to the source code documentation.*