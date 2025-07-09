// module/documents/actor.mjs
import { CharacterDataModel, CreatureDataModel } from '../data-models.mjs';

/**
 * Enhanced Actor document for Aspects of Power
 * @extends {Actor}
 */
export class AspectsofPowerActor extends Actor {
  
  /** @override */
  prepareData() {
    super.prepareData();
  }

  /** @override */
  prepareBaseData() {
    // Set up data model based on actor type
    const systemData = this.system;
    
    // Ensure we have proper data structure
    if (this.type === 'character' && !(systemData instanceof CharacterDataModel)) {
      // Migration or initialization logic here if needed
    }
  }

  /** @override */
  prepareDerivedData() {
    const systemData = this.system;
    
    // Call the data model's preparation method
    if (typeof systemData.prepareDerivedData === 'function') {
      systemData.prepareDerivedData();
    }
    
    // Additional actor-level calculations
    this._prepareEquipmentEffects();
    this._prepareCombatStats();
  }

  /**
   * Apply equipment effects to derived stats
   */
  _prepareEquipmentEffects() {
    const systemData = this.system;
    
    // Reset equipment bonuses
    let defenseBonus = 0;
    let attackBonus = 0;
    let damageBonus = 0;
    
    // Process equipped items
    for (let item of this.items) {
      if (!item.system.equipped?.value) continue;
      
      // Apply armor bonuses
      if (item.type === 'armor') {
        defenseBonus += item.system.defense?.value || 0;
      }
      
      // Apply weapon bonuses
      if (item.type === 'weapon' && item.system.equipped.slot === 'mainhand') {
        attackBonus += item.system.attack?.bonus || 0;
        damageBonus += item.system.damage?.bonus || 0;
      }
    }
    
    // Apply bonuses to derived stats
    if (systemData.derived) {
      systemData.derived.defense += defenseBonus;
      systemData.combat = systemData.combat || {};
      systemData.combat.toHitBonus += attackBonus;
      systemData.combat.damageBonus += damageBonus;
    }
  }

  /**
   * Prepare combat statistics using game formulas
   */
  _prepareCombatStats() {
    const systemData = this.system;
    if (!systemData.abilities) return;
    
    const str = systemData.abilities.strength;
    const dex = systemData.abilities.dexterity;
    const per = systemData.abilities.perception;
    const tough = systemData.abilities.toughness;
    
    // Combat formulas from game rules
    if (systemData.combat) {
      // To-hit calculation base (before bonuses)
      systemData.combat.toHitBase = Math.round(
        (dex.value + str.value * 0.6) * 0.911
      );
      
      // Standard damage base
      systemData.combat.standardDamageBase = Math.round(
        str.mod * 0.5
      );
      
      // Finesse damage base  
      systemData.combat.finesseDamageBase = Math.round(
        (str.mod + dex.mod * 0.25) * 0.6
      );
      
      // Final damage reduction from toughness
      systemData.combat.damageReduction = tough.mod;
    }
  }

  /**
   * Level up a character in a specific progression type
   */
  async levelUp(progressionType, levels = 1, allocation = 'manual') {
    if (this.type !== 'character') {
      ui.notifications.warn("Only characters can level up with class/profession progression.");
      return;
    }

    const updates = {};
    const systemData = this.system;
    
    switch (progressionType) {
      case 'race':
        updates['system.attributes.race.level'] = systemData.attributes.race.level + levels;
        // Race levels give 1 point to all stats
        for (let ability of Object.keys(systemData.abilities)) {
          updates[`system.abilities.${ability}.value`] = systemData.abilities[ability].value + levels;
        }
        break;
        
      case 'class':
        updates['system.attributes.class.level'] = systemData.attributes.class.level + levels;
        const tier = this._getClassTier(systemData.attributes.class.level + levels);
        updates['system.attributes.class.tier'] = tier;
        
        // Calculate stat points based on tier
        const statPoints = this._getStatPointsForTier(tier) * levels;
        const freePoints = this._getFreePointsForTier(tier) * levels;
        
        // Apply fixed stat increases based on class
        await this._applyClassStatIncrease(systemData.attributes.class.name, statPoints - freePoints);
        
        // Add free points for manual allocation
        updates['system.attributes.freePoints'] = systemData.attributes.freePoints + freePoints;
        break;
        
      case 'profession':
        updates['system.attributes.profession.level'] = systemData.attributes.profession.level + levels;
        // Profession levels give specific stat bonuses
        await this._applyProfessionStatIncrease(systemData.attributes.profession.name, levels);
        break;
    }
    
    // Apply updates
    await this.update(updates);
    
    // Show level up dialog if needed
    if (allocation === 'manual' && updates['system.attributes.freePoints']) {
      this._showLevelUpDialog();
    } else if (allocation === 'random' && updates['system.attributes.freePoints']) {
      await this._allocatePointsRandomly();
    }
    
    ui.notifications.info(`${this.name} gained ${levels} ${progressionType} level(s)!`);
  }

  /**
   * Get class tier based on level
   */
  _getClassTier(level) {
    if (level <= 24) return 1;
    if (level <= 99) return 2;
    if (level <= 199) return 3;
    return 4;
  }

  /**
   * Get stat points per level for tier
   */
  _getStatPointsForTier(tier) {
    switch (tier) {
      case 1: return 8;  // 6 fixed + 2 free
      case 2: return 18; // 14 fixed + 4 free
      case 3: return 24; // TBD - placeholder
      case 4: return 30; // TBD - placeholder
      default: return 8;
    }
  }

  /**
   * Get free points per level for tier
   */
  _getFreePointsForTier(tier) {
    switch (tier) {
      case 1: return 2;
      case 2: return 4;
      case 3: return 6; // TBD - placeholder
      case 4: return 8; // TBD - placeholder
      default: return 2;
    }
  }

  /**
   * Apply fixed stat increases for class leveling
   */
  async _applyClassStatIncrease(className, points) {
    // This would be based on your class definitions
    // For now, a basic implementation
    const classStatMappings = {
      'warrior': ['strength', 'vitality', 'toughness'],
      'rogue': ['dexterity', 'perception', 'intelligence'],
      'mage': ['intelligence', 'willpower', 'wisdom'],
      'cleric': ['wisdom', 'willpower', 'vitality'],
      'ranger': ['dexterity', 'perception', 'endurance'],
      'bard': ['intelligence', 'wisdom', 'perception']
    };
    
    const primaryStats = classStatMappings[className] || ['strength', 'vitality', 'endurance'];
    const pointsPerStat = Math.floor(points / primaryStats.length);
    const remainder = points % primaryStats.length;
    
    const updates = {};
    for (let i = 0; i < primaryStats.length; i++) {
      const stat = primaryStats[i];
      const increase = pointsPerStat + (i < remainder ? 1 : 0);
      updates[`system.abilities.${stat}.value`] = this.system.abilities[stat].value + increase;
    }
    
    await this.update(updates);
  }

  /**
   * Apply profession stat increases
   */
  async _applyProfessionStatIncrease(professionName, levels) {
    // Profession-specific stat bonuses
    const professionBonuses = {
      'blacksmith': { strength: 2, endurance: 1 },
      'merchant': { intelligence: 2, perception: 1 },
      'scholar': { intelligence: 3 },
      'athlete': { strength: 1, dexterity: 1, endurance: 1 }
    };
    
    const bonuses = professionBonuses[professionName] || { intelligence: 1 };
    const updates = {};
    
    for (let [stat, bonus] of Object.entries(bonuses)) {
      updates[`system.abilities.${stat}.value`] = this.system.abilities[stat].value + (bonus * levels);
    }
    
    await this.update(updates);
  }

  /**
   * Allocate free points randomly
   */
  async _allocatePointsRandomly() {
    const freePoints = this.system.attributes.freePoints;
    if (freePoints <= 0) return;
    
    const abilities = Object.keys(this.system.abilities);
    const updates = {};
    let remainingPoints = freePoints;
    
    while (remainingPoints > 0) {
      const randomStat = abilities[Math.floor(Math.random() * abilities.length)];
      const currentValue = this.system.abilities[randomStat].value;
      updates[`system.abilities.${randomStat}.value`] = (updates[`system.abilities.${randomStat}.value`] || currentValue) + 1;
      remainingPoints--;
    }
    
    updates['system.attributes.freePoints'] = 0;
    await this.update(updates);
  }

  /**
   * Show level up dialog for manual point allocation
   */
  _showLevelUpDialog() {
    new Dialog({
      title: `Level Up - ${this.name}`,
      content: `
        <p>You have ${this.system.attributes.freePoints} points to allocate.</p>
        <p>Use the character sheet to manually distribute these points, or:</p>
      `,
      buttons: {
        random: {
          label: "Allocate Randomly",
          callback: () => this._allocatePointsRandomly()
        },
        manual: {
          label: "Allocate Manually",
          callback: () => {}
        }
      }
    }).render(true);
  }

  /**
   * Roll initiative using game formula
   */
  async rollInitiative(options = {}) {
    const per = this.system.abilities.perception;
    
    // Game formula: 1d20 × (Per_mod ÷ 100) + Per_mod
    const formula = `1d20 * (@per_mod / 100) + @per_mod`;
    const rollData = { per_mod: per.mod };
    
    const roll = new Roll(formula, rollData);
    await roll.evaluate();
    
    await roll.toMessage({
      speaker: ChatMessage.getSpeaker({ actor: this }),
      flavor: "Initiative Roll"
    });
    
    return roll;
  }

  /**
   * Roll attack using game formula
   */
  async rollAttack(weaponType = 'standard', options = {}) {
    const str = this.system.abilities.strength;
    const dex = this.system.abilities.dexterity;
    const combat = this.system.combat;
    
    // Game formula: round(((1d20 ÷ 100) × (dex + str×0.6) + dex + str×0.6) × 0.911)
    const baseValue = dex.value + str.value * 0.6;
    const formula = `round(((1d20 / 100) * ${baseValue} + ${baseValue}) * 0.911) + @bonus`;
    const rollData = { bonus: combat.toHitBonus };
    
    const roll = new Roll(formula, rollData);
    await roll.evaluate();
    
    await roll.toMessage({
      speaker: ChatMessage.getSpeaker({ actor: this }),
      flavor: `${weaponType.charAt(0).toUpperCase() + weaponType.slice(1)} Attack`
    });
    
    return roll;
  }

  /**
   * Roll damage using game formulas
   */
  async rollDamage(damageType = 'standard', options = {}) {
    const str = this.system.abilities.strength;
    const dex = this.system.abilities.dexterity;
    const combat = this.system.combat;
    
    let formula;
    let rollData = { bonus: combat.damageBonus };
    
    if (damageType === 'standard') {
      // Standard: round(((2d6 ÷ 50) × str_mod + str_mod) × 0.5)
      formula = `round(((2d6 / 50) * @str_mod + @str_mod) * 0.5) + @bonus`;
      rollData.str_mod = str.mod;
    } else if (damageType === 'finesse') {
      // Finesse: round(((2d6 ÷ 50) × (str_mod + dex_mod×0.25) + str_mod + dex_mod×0.25) × 0.6)
      const modTotal = str.mod + dex.mod * 0.25;
      formula = `round(((2d6 / 50) * ${modTotal} + ${modTotal}) * 0.6) + @bonus`;
    }
    
    const roll = new Roll(formula, rollData);
    await roll.evaluate();
    
    await roll.toMessage({
      speaker: ChatMessage.getSpeaker({ actor: this }),
      flavor: `${damageType.charAt(0).toUpperCase() + damageType.slice(1)} Damage`
    });
    
    return roll;
  }

  /**
   * Get roll data for formulas
   */
  getRollData() {
    const data = super.getRollData();
    
    // Add ability values and modifiers for easy access
    if (this.system.abilities) {
      for (let [key, ability] of Object.entries(this.system.abilities)) {
        data[key] = ability.value;
        data[`${key}_mod`] = ability.mod;
      }
    }
    
    // Add derived stats
    if (this.system.derived) {
      data.health = this.system.derived.health;
      data.mana = this.system.derived.mana;
      data.defense = this.system.derived.defense;
    }
    
    // Add combat stats
    if (this.system.combat) {
      data.combat = this.system.combat;
    }
    
    return data;
  }

  /**
   * Apply damage with toughness reduction
   */
  async applyDamage(damage, type = 'standard') {
    const toughness = this.system.abilities.toughness;
    const finalDamage = Math.max(0, damage - toughness.mod);
    
    const currentHealth = this.system.derived.health.value;
    const newHealth = Math.max(0, currentHealth - finalDamage);
    
    await this.update({
      'system.derived.health.value': newHealth
    });
    
    // Show damage message
    ChatMessage.create({
      speaker: ChatMessage.getSpeaker({ actor: this }),
      content: `${this.name} takes ${finalDamage} damage (${damage} reduced by ${toughness.mod} toughness). Health: ${newHealth}/${this.system.derived.health.max}`
    });
    
    return finalDamage;
  }

  /**
   * Bulk import character data from CSV
   */
  static async bulkImportFromCSV(csvData, options = {}) {
    const results = {
      success: [],
      errors: []
    };
    
    try {
      const lines = csvData.split('\n');
      const headers = lines[0].split(',').map(h => h.trim());
      
      for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',').map(v => v.trim());
        if (values.length < headers.length) continue;
        
        const characterData = {};
        headers.forEach((header, index) => {
          characterData[header] = values[index];
        });
        
        try {
          const actor = await Actor.create({
            name: characterData.name || `Character ${i}`,
            type: 'character',
            system: {
              abilities: {
                vitality: { value: parseInt(characterData.vitality) || 5 },
                endurance: { value: parseInt(characterData.endurance) || 5 },
                strength: { value: parseInt(characterData.strength) || 5 },
                dexterity: { value: parseInt(characterData.dexterity) || 5 },
                toughness: { value: parseInt(characterData.toughness) || 5 },
                intelligence: { value: parseInt(characterData.intelligence) || 5 },
                willpower: { value: parseInt(characterData.willpower) || 5 },
                wisdom: { value: parseInt(characterData.wisdom) || 5 },
                perception: { value: parseInt(characterData.perception) || 5 }
              },
              attributes: {
                race: {
                  name: characterData.race || 'Human',
                  level: parseInt(characterData.raceLevel) || 1
                },
                class: {
                  name: characterData.class || '',
                  level: parseInt(characterData.classLevel) || 0
                },
                profession: {
                  name: characterData.profession || '',
                  level: parseInt(characterData.professionLevel) || 0
                }
              }
            }
          });
          
          results.success.push(actor.name);
        } catch (error) {
          results.errors.push(`Row ${i}: ${error.message}`);
        }
      }
    } catch (error) {
      results.errors.push(`CSV Parse Error: ${error.message}`);
    }
    
    return results;
  }
}