// module/data-models.mjs
import { HTMLField, NumberField, SchemaField, StringField, ArrayField, ObjectField } from foundry.data.fields;

// Base character data model
export class CharacterDataModel extends foundry.abstract.TypeDataModel {
  static defineSchema() {
    return {
      // Core Abilities (9 stats from your game)
      abilities: new SchemaField({
        vitality: new SchemaField({
          value: new NumberField({ required: true, initial: 5, min: 1, integer: true }),
          mod: new NumberField({ required: true, initial: -11, integer: true })
        }),
        endurance: new SchemaField({
          value: new NumberField({ required: true, initial: 5, min: 1, integer: true }),
          mod: new NumberField({ required: true, initial: -11, integer: true })
        }),
        strength: new SchemaField({
          value: new NumberField({ required: true, initial: 5, min: 1, integer: true }),
          mod: new NumberField({ required: true, initial: -11, integer: true })
        }),
        dexterity: new SchemaField({
          value: new NumberField({ required: true, initial: 5, min: 1, integer: true }),
          mod: new NumberField({ required: true, initial: -11, integer: true })
        }),
        toughness: new SchemaField({
          value: new NumberField({ required: true, initial: 5, min: 1, integer: true }),
          mod: new NumberField({ required: true, initial: -11, integer: true })
        }),
        intelligence: new SchemaField({
          value: new NumberField({ required: true, initial: 5, min: 1, integer: true }),
          mod: new NumberField({ required: true, initial: -11, integer: true })
        }),
        willpower: new SchemaField({
          value: new NumberField({ required: true, initial: 5, min: 1, integer: true }),
          mod: new NumberField({ required: true, initial: -11, integer: true })
        }),
        wisdom: new SchemaField({
          value: new NumberField({ required: true, initial: 5, min: 1, integer: true }),
          mod: new NumberField({ required: true, initial: -11, integer: true })
        }),
        perception: new SchemaField({
          value: new NumberField({ required: true, initial: 5, min: 1, integer: true }),
          mod: new NumberField({ required: true, initial: -11, integer: true })
        })
      }),

      // Character Progression
      attributes: new SchemaField({
        // Race progression
        race: new SchemaField({
          name: new StringField({ required: true, initial: "Human" }),
          level: new NumberField({ required: true, initial: 1, min: 1, integer: true }),
          rank: new StringField({ required: true, initial: "G" })
        }),
        
        // Class progression
        class: new SchemaField({
          name: new StringField({ required: true, initial: "" }),
          level: new NumberField({ required: true, initial: 0, min: 0, integer: true }),
          tier: new NumberField({ required: true, initial: 1, min: 1, max: 4, integer: true })
        }),
        
        // Profession progression
        profession: new SchemaField({
          name: new StringField({ required: true, initial: "" }),
          level: new NumberField({ required: true, initial: 0, min: 0, integer: true })
        }),

        // Free points available for allocation
        freePoints: new NumberField({ required: true, initial: 0, min: 0, integer: true })
      }),

      // Derived Stats
      derived: new SchemaField({
        health: new SchemaField({
          value: new NumberField({ required: true, initial: 10, min: 0, integer: true }),
          max: new NumberField({ required: true, initial: 10, min: 0, integer: true })
        }),
        mana: new SchemaField({
          value: new NumberField({ required: true, initial: 10, min: 0, integer: true }),
          max: new NumberField({ required: true, initial: 10, min: 0, integer: true })
        }),
        defense: new NumberField({ required: true, initial: 0, integer: true }),
        initiative: new NumberField({ required: true, initial: 0, integer: true })
      }),

      // Combat stats
      combat: new SchemaField({
        toHitBonus: new NumberField({ required: true, initial: 0, integer: true }),
        damageBonus: new NumberField({ required: true, initial: 0, integer: true }),
        standardDamage: new StringField({ required: true, initial: "2d6" }),
        finesseDamage: new StringField({ required: true, initial: "2d6" })
      }),

      // Character details
      details: new SchemaField({
        biography: new HTMLField({ required: true, blank: true }),
        appearance: new HTMLField({ required: true, blank: true }),
        notes: new HTMLField({ required: true, blank: true })
      })
    };
  }

  // Data preparation method called after schema validation
  prepareDerivedData() {
    // Calculate ability modifiers using Aspects of Power formula
    for (let [key, ability] of Object.entries(this.abilities)) {
      ability.mod = Math.floor((ability.value - 50) / 3);
    }

    // Calculate race rank based on level
    if (this.attributes.race.level <= 9) {
      this.attributes.race.rank = "G";
    } else if (this.attributes.race.level <= 24) {
      this.attributes.race.rank = "F";
    } else if (this.attributes.race.level <= 99) {
      this.attributes.race.rank = "E";
    } else if (this.attributes.race.level <= 199) {
      this.attributes.race.rank = "D";
    } else {
      this.attributes.race.rank = "C";
    }

    // Calculate derived stats
    this.derived.health.max = this.abilities.vitality.value + this.abilities.vitality.mod;
    this.derived.mana.max = this.abilities.intelligence.value + this.abilities.intelligence.mod;
    
    // Combat calculations
    this.derived.defense = Math.round(this.abilities.dexterity.mod + this.abilities.strength.mod * 0.3);
    this.derived.initiative = this.abilities.perception.mod;
    
    // Ensure current values don't exceed max
    this.derived.health.value = Math.min(this.derived.health.value, this.derived.health.max);
    this.derived.mana.value = Math.min(this.derived.mana.value, this.derived.mana.max);
  }
}

// Familiar/Monster simplified data model
export class CreatureDataModel extends foundry.abstract.TypeDataModel {
  static defineSchema() {
    return {
      abilities: new SchemaField({
        vitality: new SchemaField({
          value: new NumberField({ required: true, initial: 5, min: 1, integer: true }),
          mod: new NumberField({ required: true, initial: -11, integer: true })
        }),
        endurance: new SchemaField({
          value: new NumberField({ required: true, initial: 5, min: 1, integer: true }),
          mod: new NumberField({ required: true, initial: -11, integer: true })
        }),
        strength: new SchemaField({
          value: new NumberField({ required: true, initial: 5, min: 1, integer: true }),
          mod: new NumberField({ required: true, initial: -11, integer: true })
        }),
        dexterity: new SchemaField({
          value: new NumberField({ required: true, initial: 5, min: 1, integer: true }),
          mod: new NumberField({ required: true, initial: -11, integer: true })
        }),
        toughness: new SchemaField({
          value: new NumberField({ required: true, initial: 5, min: 1, integer: true }),
          mod: new NumberField({ required: true, initial: -11, integer: true })
        }),
        intelligence: new SchemaField({
          value: new NumberField({ required: true, initial: 5, min: 1, integer: true }),
          mod: new NumberField({ required: true, initial: -11, integer: true })
        }),
        willpower: new SchemaField({
          value: new NumberField({ required: true, initial: 5, min: 1, integer: true }),
          mod: new NumberField({ required: true, initial: -11, integer: true })
        }),
        wisdom: new SchemaField({
          value: new NumberField({ required: true, initial: 5, min: 1, integer: true }),
          mod: new NumberField({ required: true, initial: -11, integer: true })
        }),
        perception: new SchemaField({
          value: new NumberField({ required: true, initial: 5, min: 1, integer: true }),
          mod: new NumberField({ required: true, initial: -11, integer: true })
        })
      }),

      // Only race levels for creatures
      attributes: new SchemaField({
        race: new SchemaField({
          name: new StringField({ required: true, initial: "Beast" }),
          level: new NumberField({ required: true, initial: 1, min: 1, integer: true }),
          rank: new StringField({ required: true, initial: "G" })
        })
      }),

      derived: new SchemaField({
        health: new SchemaField({
          value: new NumberField({ required: true, initial: 10, min: 0, integer: true }),
          max: new NumberField({ required: true, initial: 10, min: 0, integer: true })
        }),
        defense: new NumberField({ required: true, initial: 0, integer: true })
      }),

      details: new SchemaField({
        description: new HTMLField({ required: true, blank: true }),
        behavior: new HTMLField({ required: true, blank: true })
      })
    };
  }

  prepareDerivedData() {
    // Same ability mod calculation
    for (let [key, ability] of Object.entries(this.abilities)) {
      ability.mod = Math.floor((ability.value - 50) / 3);
    }

    // Calculate race rank
    if (this.attributes.race.level <= 9) {
      this.attributes.race.rank = "G";
    } else if (this.attributes.race.level <= 24) {
      this.attributes.race.rank = "F";
    } else if (this.attributes.race.level <= 99) {
      this.attributes.race.rank = "E";
    } else if (this.attributes.race.level <= 199) {
      this.attributes.race.rank = "D";
    } else {
      this.attributes.race.rank = "C";
    }

    // Simplified derived stats
    this.derived.health.max = this.abilities.vitality.value + this.abilities.vitality.mod;
    this.derived.defense = Math.round(this.abilities.dexterity.mod + this.abilities.strength.mod * 0.3);
    this.derived.health.value = Math.min(this.derived.health.value, this.derived.health.max);
  }
}

// Item data models for different item types
export class WeaponDataModel extends foundry.abstract.TypeDataModel {
  static defineSchema() {
    return {
      description: new HTMLField({ required: true, blank: true }),
      
      // Weapon properties
      weaponType: new StringField({ 
        required: true, 
        initial: "melee",
        choices: ["melee", "ranged", "thrown", "finesse"]
      }),
      
      // Damage and bonuses
      damage: new SchemaField({
        formula: new StringField({ required: true, initial: "2d6" }),
        type: new StringField({ required: true, initial: "standard" }),
        bonus: new NumberField({ required: true, initial: 0, integer: true })
      }),
      
      // Attack bonuses
      attack: new SchemaField({
        bonus: new NumberField({ required: true, initial: 0, integer: true }),
        ability: new StringField({ required: true, initial: "strength" })
      }),
      
      // Equipment state
      equipped: new SchemaField({
        value: new NumberField({ required: true, initial: false }),
        slot: new StringField({ required: true, initial: "weapon" })
      }),
      
      // Weight and value
      physical: new SchemaField({
        weight: new NumberField({ required: true, initial: 1, min: 0 }),
        value: new NumberField({ required: true, initial: 0, min: 0 }),
        quantity: new NumberField({ required: true, initial: 1, min: 0, integer: true })
      })
    };
  }
}

export class ArmorDataModel extends foundry.abstract.TypeDataModel {
  static defineSchema() {
    return {
      description: new HTMLField({ required: true, blank: true }),
      
      // Armor properties
      armorType: new StringField({ 
        required: true, 
        initial: "light",
        choices: ["light", "medium", "heavy", "shield"]
      }),
      
      // Defense bonuses
      defense: new SchemaField({
        value: new NumberField({ required: true, initial: 0, integer: true }),
        maxDex: new NumberField({ required: true, initial: 10, integer: true })
      }),
      
      // Equipment state
      equipped: new SchemaField({
        value: new NumberField({ required: true, initial: false }),
        slot: new StringField({ required: true, initial: "armor" })
      }),
      
      physical: new SchemaField({
        weight: new NumberField({ required: true, initial: 1, min: 0 }),
        value: new NumberField({ required: true, initial: 0, min: 0 }),
        quantity: new NumberField({ required: true, initial: 1, min: 0, integer: true })
      })
    };
  }
}

export class AbilityDataModel extends foundry.abstract.TypeDataModel {
  static defineSchema() {
    return {
      description: new HTMLField({ required: true, blank: true }),
      
      // Ability mechanics
      activation: new SchemaField({
        type: new StringField({ required: true, initial: "action" }),
        cost: new NumberField({ required: true, initial: 1, min: 0, integer: true }),
        condition: new StringField({ required: true, initial: "" })
      }),
      
      // Resource usage
      uses: new SchemaField({
        value: new NumberField({ required: true, initial: 0, min: 0, integer: true }),
        max: new NumberField({ required: true, initial: 0, min: 0, integer: true }),
        per: new StringField({ required: true, initial: "day" })
      }),
      
      // Source information
      source: new SchemaField({
        type: new StringField({ required: true, initial: "class" }),
        level: new NumberField({ required: true, initial: 1, min: 1, integer: true }),
        class: new StringField({ required: true, initial: "" })
      })
    };
  }
}