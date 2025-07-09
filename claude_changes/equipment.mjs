// module/systems/equipment.mjs

/**
 * Equipment management and active effects system
 */
export class EquipmentSystem {
  
  /**
   * Initialize equipment system hooks
   */
  static initialize() {
    Hooks.on("updateItem", this._onItemUpdate.bind(this));
    Hooks.on("createItem", this._onItemCreate.bind(this));
    Hooks.on("deleteItem", this._onItemDelete.bind(this));
  }

  /**
   * Handle item updates (especially equipment state changes)
   */
  static _onItemUpdate(item, updateData, options, userId) {
    if (!item.parent || item.parent.type !== 'character') return;
    
    // Handle equipment state changes
    if (updateData.system?.equipped !== undefined) {
      this._handleEquipmentChange(item, updateData.system.equipped.value);
    }
    
    // Handle item property changes that affect stats
    if (updateData.system?.damage || updateData.system?.defense || updateData.system?.bonuses) {
      item.parent.prepareData(); // Recalculate derived stats
    }
  }

  /**
   * Handle new item creation
   */
  static _onItemCreate(item, options, userId) {
    if (!item.parent || item.parent.type !== 'character') return;
    
    // Auto-equip if specified
    if (options.autoEquip && this._canEquipItem(item)) {
      this._equipItem(item);
    }
  }

  /**
   * Handle item deletion
   */
  static _onItemDelete(item, options, userId) {
    if (!item.parent || item.parent.type !== 'character') return;
    
    // Remove any active effects from this item
    this._removeItemEffects(item);
  }

  /**
   * Handle equipment state changes
   */
  static _handleEquipmentChange(item, equipped) {
    const actor = item.parent;
    
    if (equipped) {
      this._equipItem(item);
    } else {
      this._unequipItem(item);
    }
    
    // Recalculate actor stats
    actor.prepareData();
  }

  /**
   * Equip an item and apply its effects
   */
  static async _equipItem(item) {
    const actor = item.parent;
    
    // Check if item can be equipped
    if (!this._canEquipItem(item)) {
      ui.notifications.warn(`Cannot equip ${item.name}`);
      return false;
    }
    
    // Unequip conflicting items
    await this._unequipConflictingItems(item);
    
    // Apply equipment effects
    await this._applyEquipmentEffects(item);
    
    // Update equipment state
    await item.update({ 'system.equipped.value': true });
    
    ui.notifications.info(`Equipped ${item.name}`);
    return true;
  }

  /**
   * Unequip an item and remove its effects
   */
  static async _unequipItem(item) {
    // Remove equipment effects
    await this._removeItemEffects(item);
    
    // Update equipment state
    await item.update({ 'system.equipped.value': false });
    
    ui.notifications.info(`Unequipped ${item.name}`);
  }

  /**
   * Check if an item can be equipped
   */
  static _canEquipItem(item) {
    // Check if item has equipment slot
    if (!item.system.equipped) return false;
    
    // Check actor requirements (could add level, stat requirements, etc.)
    const actor = item.parent;
    
    // Example: Check if actor meets stat requirements
    if (item.system.requirements) {
      for (let [stat, required] of Object.entries(item.system.requirements)) {
        if (actor.system.abilities[stat]?.value < required) {
          return false;
        }
      }
    }
    
    return true;
  }

  /**
   * Unequip items that conflict with the new item
   */
  static async _unequipConflictingItems(newItem) {
    const actor = newItem.parent;
    const newSlot = newItem.system.equipped.slot;
    
    // Define slot conflicts
    const slotConflicts = {
      'weapon': ['weapon', 'twohand'],
      'twohand': ['weapon', 'shield', 'twohand'],
      'shield': ['twohand'],
      'armor': ['armor'],
      'helmet': ['helmet'],
      'gloves': ['gloves'],
      'boots': ['boots'],
      'ring': [], // Multiple rings allowed
      'amulet': ['amulet']
    };
    
    const conflictingSlots = slotConflicts[newSlot] || [newSlot];
    
    // Find and unequip conflicting items
    for (let item of actor.items) {
      if (item.id === newItem.id) continue;
      if (!item.system.equipped?.value) continue;
      
      const itemSlot = item.system.equipped.slot;
      if (conflictingSlots.includes(itemSlot)) {
        await this._unequipItem(item);
      }
    }
  }

  /**
   * Apply equipment effects to the actor
   */
  static async _applyEquipmentEffects(item) {
    const actor = item.parent;
    const effects = [];
    
    // Weapon effects
    if (item.type === 'weapon') {
      effects.push(...this._createWeaponEffects(item));
    }
    
    // Armor effects
    if (item.type === 'armor') {
      effects.push(...this._createArmorEffects(item));
    }
    
    // Accessory effects (rings, amulets, etc.)
    if (item.type === 'accessory') {
      effects.push(...this._createAccessoryEffects(item));
    }
    
    // Apply custom item effects
    if (item.system.customEffects) {
      effects.push(...item.system.customEffects);
    }
    
    // Create active effects on the actor
    if (effects.length > 0) {
      await actor.createEmbeddedDocuments("ActiveEffect", effects);
    }
  }

  /**
   * Create weapon-specific active effects
   */
  static _createWeaponEffects(weapon) {
    const effects = [];
    const system = weapon.system;
    
    // Attack bonus effect
    if (system.attack?.bonus) {
      effects.push({
        name: `${weapon.name} - Attack Bonus`,
        icon: weapon.img,
        origin: weapon.uuid,
        disabled: false,
        changes: [{
          key: "system.combat.toHitBonus",
          mode: 2, // ADD
          value: system.attack.bonus,
          priority: 20
        }],
        flags: {
          aspectsofpower: {
            itemSource: weapon.id,
            effectType: "equipment"
          }
        }
      });
    }
    
    // Damage bonus effect
    if (system.damage?.bonus) {
      effects.push({
        name: `${weapon.name} - Damage Bonus`,
        icon: weapon.img,
        origin: weapon.uuid,
        disabled: false,
        changes: [{
          key: "system.combat.damageBonus",
          mode: 2, // ADD
          value: system.damage.bonus,
          priority: 20
        }],
        flags: {
          aspectsofpower: {
            itemSource: weapon.id,
            effectType: "equipment"
          }
        }
      });
    }
    
    // Stat bonuses from magical weapons
    if (system.statBonuses) {
      for (let [stat, bonus] of Object.entries(system.statBonuses)) {
        effects.push({
          name: `${weapon.name} - ${stat.charAt(0).toUpperCase() + stat.slice(1)} Bonus`,
          icon: weapon.img,
          origin: weapon.uuid,
          disabled: false,
          changes: [{
            key: `system.abilities.${stat}.value`,
            mode: 2, // ADD
            value: bonus,
            priority: 20
          }],
          flags: {
            aspectsofpower: {
              itemSource: weapon.id,
              effectType: "equipment"
            }
          }
        });
      }
    }
    
    return effects;
  }

  /**
   * Create armor-specific active effects
   */
  static _createArmorEffects(armor) {
    const effects = [];
    const system = armor.system;
    
    // Defense bonus effect
    if (system.defense?.value) {
      effects.push({
        name: `${armor.name} - Defense`,
        icon: armor.img,
        origin: armor.uuid,
        disabled: false,
        changes: [{
          key: "system.derived.defense",
          mode: 2, // ADD
          value: system.defense.value,
          priority: 20
        }],
        flags: {
          aspectsofpower: {
            itemSource: armor.id,
            effectType: "equipment"
          }
        }
      });
    }
    
    // Stat bonuses from magical armor
    if (system.statBonuses) {
      for (let [stat, bonus] of Object.entries(system.statBonuses)) {
        effects.push({
          name: `${armor.name} - ${stat.charAt(0).toUpperCase() + stat.slice(1)} Bonus`,
          icon: armor.img,
          origin: armor.uuid,
          disabled: false,
          changes: [{
            key: `system.abilities.${stat}.value`,
            mode: 2, // ADD
            value: bonus,
            priority: 20
          }],
          flags: {
            aspectsofpower: {
              itemSource: armor.id,
              effectType: "equipment"
            }
          }
        });
      }
    }
    
    // Special armor properties
    if (system.properties) {
      for (let property of system.properties) {
        switch (property) {
          case 'fire_resistance':
            effects.push({
              name: `${armor.name} - Fire Resistance`,
              icon: armor.img,
              origin: armor.uuid,
              disabled: false,
              changes: [{
                key: "system.resistances.fire",
                mode: 2,
                value: 5,
                priority: 20
              }]
            });
            break;
          case 'spell_protection':
            effects.push({
              name: `${armor.name} - Spell Protection`,
              icon: armor.img,
              origin: armor.uuid,
              disabled: false,
              changes: [{
                key: "system.combat.spellDefense",
                mode: 2,
                value: 2,
                priority: 20
              }]
            });
            break;
        }
      }
    }
    
    return effects;
  }

  /**
   * Create accessory-specific active effects
   */
  static _createAccessoryEffects(accessory) {
    const effects = [];
    const system = accessory.system;
    
    // Stat bonuses from accessories
    if (system.statBonuses) {
      for (let [stat, bonus] of Object.entries(system.statBonuses)) {
        effects.push({
          name: `${accessory.name} - ${stat.charAt(0).toUpperCase() + stat.slice(1)} Bonus`,
          icon: accessory.img,
          origin: accessory.uuid,
          disabled: false,
          changes: [{
            key: `system.abilities.${stat}.value`,
            mode: 2, // ADD
            value: bonus,
            priority: 20
          }],
          flags: {
            aspectsofpower: {
              itemSource: accessory.id,
              effectType: "equipment"
            }
          }
        });
      }
    }
    
    // Special accessory effects
    if (system.specialEffects) {
      for (let effect of system.specialEffects) {
        effects.push({
          name: `${accessory.name} - ${effect.name}`,
          icon: accessory.img,
          origin: accessory.uuid,
          disabled: false,
          changes: effect.changes || [],
          flags: {
            aspectsofpower: {
              itemSource: accessory.id,
              effectType: "equipment",
              customEffect: true
            }
          }
        });
      }
    }
    
    return effects;
  }

  /**
   * Remove all active effects from a specific item
   */
  static async _removeItemEffects(item) {
    const actor = item.parent;
    
    // Find effects created by this item
    const effectsToRemove = actor.effects.filter(effect => 
      effect.flags?.aspectsofpower?.itemSource === item.id
    );
    
    // Remove the effects
    if (effectsToRemove.length > 0) {
      const effectIds = effectsToRemove.map(e => e.id);
      await actor.deleteEmbeddedDocuments("ActiveEffect", effectIds);
    }
  }

  /**
   * Get all equipment slots and their current items
   */
  static getEquipmentSlots(actor) {
    const slots = {
      weapon: null,
      shield: null,
      armor: null,
      helmet: null,
      gloves: null,
      boots: null,
      rings: [],
      amulet: null,
      belt: null,
      cloak: null
    };
    
    for (let item of actor.items) {
      if (!item.system.equipped?.value) continue;
      
      const slot = item.system.equipped.slot;
      
      if (slot === 'ring') {
        slots.rings.push(item);
      } else if (slots.hasOwnProperty(slot)) {
        slots[slot] = item;
      }
    }
    
    return slots;
  }

  /**
   * Auto-equip best available gear
   */
  static async autoEquipBestGear(actor) {
    const unequippedItems = actor.items.filter(item => 
      item.system.equipped && !item.system.equipped.value
    );
    
    // Sort by item value/power level
    const sortedItems = unequippedItems.sort((a, b) => {
      const aValue = this._calculateItemPower(a);
      const bValue = this._calculateItemPower(b);
      return bValue - aValue;
    });
    
    const equipped = [];
    const failed = [];
    
    for (let item of sortedItems) {
      try {
        const success = await this._equipItem(item);
        if (success) {
          equipped.push(item.name);
        } else {
          failed.push(item.name);
        }
      } catch (error) {
        failed.push(item.name);
      }
    }
    
    ui.notifications.info(`Auto-equipped: ${equipped.join(', ')}`);
    if (failed.length > 0) {
      ui.notifications.warn(`Failed to equip: ${failed.join(', ')}`);
    }
  }

  /**
   * Calculate item power level for comparison
   */
  static _calculateItemPower(item) {
    let power = 0;
    const system = item.system;
    
    // Base power from item value
    power += system.physical?.value || 0;
    
    // Power from combat bonuses
    if (item.type === 'weapon') {
      power += (system.attack?.bonus || 0) * 10;
      power += (system.damage?.bonus || 0) * 8;
    }
    
    if (item.type === 'armor') {
      power += (system.defense?.value || 0) * 12;
    }
    
    // Power from stat bonuses
    if (system.statBonuses) {
      for (let bonus of Object.values(system.statBonuses)) {
        power += bonus * 15;
      }
    }
    
    return power;
  }

  /**
   * Create equipment from template
   */
  static async createEquipmentFromTemplate(actor, template) {
    const equipmentData = {
      ...template,
      name: template.name,
      type: template.type,
      system: {
        ...template.system,
        equipped: {
          value: false,
          slot: template.system.slot || template.type
        }
      }
    };
    
    const items = await actor.createEmbeddedDocuments("Item", [equipmentData]);
    return items[0];
  }

  /**
   * Bulk equip/unequip items
   */
  static async bulkEquipItems(actor, itemIds, equip = true) {
    const results = {
      success: [],
      failed: []
    };
    
    for (let itemId of itemIds) {
      const item = actor.items.get(itemId);
      if (!item) {
        results.failed.push({ id: itemId, error: "Item not found" });
        continue;
      }
      
      try {
        if (equip) {
          const success = await this._equipItem(item);
          if (success) {
            results.success.push(item.name);
          } else {
            results.failed.push({ id: itemId, error: "Cannot equip" });
          }
        } else {
          await this._unequipItem(item);
          results.success.push(item.name);
        }
      } catch (error) {
        results.failed.push({ id: itemId, error: error.message });
      }
    }
    
    return results;
  }

  /**
   * Repair all equipped items
   */
  static async repairAllEquipment(actor) {
    const equippedItems = actor.items.filter(item => 
      item.system.equipped?.value && item.system.durability
    );
    
    const updates = [];
    
    for (let item of equippedItems) {
      if (item.system.durability.value < item.system.durability.max) {
        updates.push({
          _id: item.id,
          'system.durability.value': item.system.durability.max
        });
      }
    }
    
    if (updates.length > 0) {
      await actor.updateEmbeddedDocuments("Item", updates);
      ui.notifications.info(`Repaired ${updates.length} items.`);
    } else {
      ui.notifications.info("All equipment is already in perfect condition.");
    }
  }

  /**
   * Get equipment summary for display
   */
  static getEquipmentSummary(actor) {
    const slots = this.getEquipmentSlots(actor);
    const summary = {
      totalDefense: 0,
      totalAttackBonus: 0,
      totalDamageBonus: 0,
      statBonuses: {},
      specialEffects: []
    };
    
    // Calculate totals from all equipped items
    for (let item of actor.items) {
      if (!item.system.equipped?.value) continue;
      
      // Defense bonuses
      if (item.type === 'armor' && item.system.defense?.value) {
        summary.totalDefense += item.system.defense.value;
      }
      
      // Combat bonuses
      if (item.type === 'weapon') {
        summary.totalAttackBonus += item.system.attack?.bonus || 0;
        summary.totalDamageBonus += item.system.damage?.bonus || 0;
      }
      
      // Stat bonuses
      if (item.system.statBonuses) {
        for (let [stat, bonus] of Object.entries(item.system.statBonuses)) {
          summary.statBonuses[stat] = (summary.statBonuses[stat] || 0) + bonus;
        }
      }
      
      // Special effects
      if (item.system.specialEffects) {
        summary.specialEffects.push(...item.system.specialEffects.map(e => ({
          ...e,
          source: item.name
        })));
      }
    }
    
    return summary;
  }
}