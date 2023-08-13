import re, openai, random, json, traceback, sys, time

#TODO: Add quest details to save file.


openai.api_key = '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'

############### CHARACTER AND MONSTER COMBAT MODULE START###############################
class Character:
    def __init__(self, name, level, health, max_health, attack, defense, evasion, experience, gold):
        self.name = name
        self.level = level
        self.health = health
        self.max_health = max_health    # 50 health
        self.attack_level = attack  # default 10 attack, and defense
        self.defense_level = defense
        self.evasion_level = evasion  # 10% dodge chance
        self.experience = experience
        self.gold = gold
        self.kill_count = {}
        self.crit_chance = 0.1      # 10% crit chance
        self.bag = []                               # inventory for character
        self.equipped_gear = {"Head": None,   # store gear here
                              "Chest": None,
                              "Legs": None,
                              "Boots": None,
                              "Right Hand": None,
                              "Left Hand": None}
        self.equipped_gear_attributes = {}
        #potion buffs
        self.active_potion = None
        self.fight_count = 0
        self.potion_duration = 0
        # quest tracker
        self.quest = None
        self.quest_location = None
        self.quest_target = None
        self.quest_quantity = 0
        self.quest_current_quantity = 0
        self.quest_reward = 0

    def attack(self, enemy):
        if self.crit_chance >= random.random() > enemy.evasion_level:  #crit check
            attack_power = self.attack_level * 1.5 # full attack by 50% crit
            print(f'{self.name} dealt a critical hit!')
            enemy.defend(attack_power)
        elif random.random() > enemy.evasion_level:
            attack_power = random.randint(self.attack_level // 2, self.attack_level) # calculate damage done, scales to attack level
            enemy.defend(attack_power)
        else:
            print(f'{enemy.name} evades the attack from {self.name}!')

    def defend(self, damage):
        damage_reduction = self.defense_level / 100
        damage_taken = max(int(damage * (1 - damage_reduction)), 0)
        self.health -= damage_taken
        print(f"You were hit by the enemy, taking {damage_taken} damage.")
        #print(f"{self.name} takes {damage_taken} damage.")

    def defeat(self, enemy):
        enemy_type = enemy.enemy_type
        if enemy_type in self.kill_count:
            self.kill_count[enemy_type] += 1
        else:
            self.kill_count[enemy_type] = 1

        self.experience += enemy.experience
        self.gold += enemy.gold

        experience_required = self.level * 100
        if self.experience >= experience_required:
            self.level_up()
        else:
            print(f'Experience needed for the next level: {experience_required - self.experience}')

    def level_up(self):
        self.level += 1
        print(f'Congratulations! {self.name} leveled up to level {self.level}.')
        print('1. Attack')
        print('2. Defense')
        print('3. Health')
        print('4. Evasion')
        choice = input(f'What skill do you want to level?\n')

        if choice == '1' or choice.lower() == 'attack':
            self.attack_level += 5
        elif choice == '2' or choice.lower() == 'defense':
            self.defense_level += 5
        elif choice == '3' or choice.lower() == 'health':
            self.max_health += 5
        elif choice == '4' or choice.lower() == 'evasion':
            self.evasion_level += .025
        else:
            print('Not a valid choice. Try again.')
            self.level_up()
        self.health = self.max_health       # refresh health after leveling up
        self.experience = 0                 # sets exp to zero for the next level.

    def list_inventory(self, action):
        if not self.bag:
            print("Your inventory is empty.")
        elif action == 'all':
            print("You have the following items in your inventory:")
            for item in self.bag:
                item_name = item['item_name']
                item_quantity = item['quantity']
                print(f'{item_name} | {item["type"]} | {item_quantity}')

        elif action == 'onbody':
            if not self.equipped_gear:
                print("You do not have any gear equipped.")
            else:
                print("You have the following equipped:")
                for item_slot, item in self.equipped_gear.items():
                    if item is not None:
                        item_name = item['item_name']
                        print(f'{item_slot}: {item_name}')
                    else:
                        print(f'{item_slot}: None')

        elif action == 'equip':
            print("You have the following equippable items in your inventory:")
            for item in self.bag:
                if item['equippable'] == 'true':
                    print(f"{item['item_name']} | Slot: {item['slot']}")

        elif action == 'consumable':
            for item in self.bag:
                if item['slot'] == 'consumable':
                    item_name = item['item_name']
                    item_quantity = item['quantity']
                    print(f'{item_name}: {item_quantity}')

    def inspect_item(self, item_name):
        if not self.bag:
            print("Your inventory is empty.")
        else:
            for item in self.bag:
                if item['item_name'] == item_name:
                    print(f"=====================")
                    print(f'Item Name: {item_name} \nItem Type: {item["type"]} \nItem Slot: {item["slot"]}')
                    print(f'Description: {item["description"]}')
                    print(f'Rarity: {item["rarity"]} ')
                    print(f"Value: {item['price']}")
                    print(f"=====================")
                    print(f"Item Stats:")
                    if item["attack"] > 0:
                        print(f'Attack : {item["attack"]} ')
                    if item["defense"] > 0:
                        print(f'Defense: {item["defense"]}')
                    if item["max_health"] > 0:
                        print(f'Health : {item["max_health"]}')
                    if item["evasion"] > 0:
                        print(f'Evasion: {item["evasion"] * 100}%')
                    print(f"=====================")
                    break

            else:
                print(f"{item_name} is not in your inventory.")
                return

    def list_equipped_gear(self):
        if not self.equipped_gear:
            print("You do not have any gear equipped.")
        else:
            print("You have the following equipped:")
            for item_slot, item in self.equipped_gear.items():
                if item is not None:
                    item_name = item['item_name']
                    print(f'{item_slot}: {item_name}')
                else:
                    print(f'{item_slot}: None')
    # helth
    def use_item(self, item_name):
        #### equip, sell item.
            for item in self.bag:
                if item['item_name'] == item_name:
                    # code to use health potion
                    if item['type'] == 'potion' and item['duration'] == 0:
                        if item['item_name'] == item_name and item['quantity'] > 0:
                            self.health += item['max_health']
                            self.health = min(self.health, self.max_health)
                            item['quantity'] -= 1
                            print(f"You used a {item['item_name']}. Your health is now {self.health}/{self.max_health}.")
                        if item['item_name'] == item_name and item['quantity'] == 0:
                            print(f"You ran out of {item['item_name']}.")
                            self.bag.remove(item)
                            break

                    # code to use runes
                    elif item['type'] == 'rune' and item['duration'] > 0:
                        if self.active_potion is not None:
                            print(f"You already have an active rune.")
                        else:
                            if item['quantity'] > 0:
                                self.active_potion = item['item_name']
                                self.attack_level += item['attack']
                                self.defense_level += item['defense']
                                self.max_health += item['max_health']
                                self.evasion_level += item['evasion']
                                self.potion_duration += item['duration']
                                item['quantity'] -= 1
                                if item['attack'] > 0:
                                    print(f"You consumed a {item['item_name']}. Your attack level is increased by {item['attack']} for {item['duration']} fights.")
                                if item['defense'] > 0:
                                    print(f"You consumed a {item['item_name']}. Your defense level is increased by {item['defense']} for {item['duration']} fights.")
                                if item['max_health'] > 0:
                                    print(f"You consumed a {item['item_name']}. Your max health level is increased by {item['max_health']} for {item['duration']} fights.")
                                if item['evasion'] > 0:
                                    print(f"You consumed a {item['item_name']}. Your evasion level is increased by {item['evasion']} for {item['duration']} fights.")
                            if item['quantity'] == 0:
                                print(f"You ran out of {item['item_name']}.")
                                self.bag.remove(item)
                                break

                    else:
                        print('That is not a valid item.')

    def buy_item(self, item_name, quantity):
        with open('item_list.json') as file:
            items_data = json.load(file)

        for item in items_data['item']:
            if item['item_name'] == item_name:
                if item['sellable']:
                    if self.gold >= item['price'] * quantity:
                        self.gold -= item['price'] * quantity

                        found_item = False
                        for backpack_item in self.bag:
                            if backpack_item['item_name'] == item_name:
                                backpack_item['quantity'] += quantity
                                found_item = True
                                break

                        if not found_item:
                            self.bag.append(item)
                            for backpack_item in self.bag:
                                if backpack_item['item_name'] == item_name:
                                    backpack_item['quantity'] += quantity - 1
                                    break

                        if quantity > 1:
                            print(f"You bought {quantity} {item['item_name']}s for {item['price'] * quantity} gold.")
                        else:
                            print(f"You bought {quantity} {item['item_name']} for {item['price'] * quantity} gold.")
                    else:
                        print("You don't have enough gold to buy this item.")
                else:
                    print("This item cannot be sold.")
                break
        else:
            print("Item not found.")

    def equip_gear(self):
        if not self.bag:
            return
        else:
            item_name = input("Enter the name of the item you want to equip:\n")
            item = next((item for item in self.bag if item['item_name'] == item_name), None)

            if item is None:
                print("Item not found in bag.")
                return

            if item['equippable'] != "true":
                print(f"{item['item_name']} is not equippable.")
            elif item['slot'] not in self.equipped_gear:
                print(f"{item['item_name']} cannot be equipped in this slot.")
            else:
                if self.equipped_gear[item['slot']] is not None:
                    self.remove_equipment(self.equipped_gear[item['slot']])
                self.equipped_gear[item['slot']] = item
                self.attack_level += item['attack']
                self.defense_level += item['defense']
                self.max_health += item['max_health']
                self.evasion_level += item['evasion']
                self.bag.remove(item)
                print(f"{item['item_name']} was equipped.")
                self.calculate_equipped_gear_attributes()

    def remove_equipment(self, slot):

        if not self.equipped_gear:
            print("You are not wearing any gear.")

        else:
            if all(slot_value is None for slot_value in self.equipped_gear.values()):
                print("You are not wearing any gear.")
                return

            slot = input("What slot do you want to remove an item from?\n")
            if slot not in self.equipped_gear:
                print(f"No item equipped in {slot} slot.")
                return

            equipped_item = self.equipped_gear[slot]
            if equipped_item is None:
                print(f"No item equipped in {slot} slot.")
                return

            self.attack_level -= equipped_item['attack']
            self.defense_level -= equipped_item['defense']
            self.max_health -= equipped_item['max_health']
            self.evasion_level -= equipped_item['evasion']
            self.bag.append(equipped_item)
            self.equipped_gear[slot] = None
            print(f"Removed {equipped_item['item_name']} from {slot} slot.")
            self.calculate_equipped_gear_attributes()

    def calculate_equipped_gear_attributes(self):
        self.equipped_gear_attributes = {
            'attack': sum([item['attack'] if item else 0 for item in self.equipped_gear.values()]),
            'defense': sum([item['defense'] if item else 0 for item in self.equipped_gear.values()]),
            'max_health': sum([item['max_health'] if item else 0 for item in self.equipped_gear.values()]),
            'evasion': sum([item['evasion'] if item else 0 for item in self.equipped_gear.values()])
        }

    def is_alive(self):
        return self.health > 0


class Enemy(Character):
    def __init__(self, name, health, attack, defense, experience, gold):
        super().__init__(name, self.level, health, self.max_health, attack, defense, self.evasion_level, experience, gold)
        self.crit_chance = 0.1 # 10% crit chance

    def attack(self, enemy):
        if self.crit_chance >= random.random() > enemy.evasion_level:  #crit check
            attack_power = random.randint(self.attack_level // 2, self.attack_level) * 1.5 # normal attack by 50% crit
            print(f'{self.name} dealt a critical hit!')
            enemy.defend(attack_power)
        elif random.random() > enemy.evasion_level:
            attack_power = random.randint(self.attack_level // 2, self.attack_level) # calculate damage done, scales to attack level
            enemy.defend(attack_power)
        else:
            print(f'{enemy.name} evades the attack from {self.name}!')

    def retaliation(self, enemy):  #calculates damage done to player when they retreat from a fight
        crit_chance = 0.1 # 10% crit chance
        if random.random() <= crit_chance: #crit check
            attack_power = random.randint(0, self.attack_level // 2) * 1.5 # normal attack by 50% crit
            print(f'{self.name} dealt {attack_power} damage, a critical hit!')
            enemy.defend(attack_power)
        else:
            attack_power = random.randint(0, self.attack_level // 2) # calculate damage done, scales to attack level
        enemy.defend(attack_power)

    def defend(self, damage):
        damage_reduction = self.defense_level / 100
        damage_taken = max(int(damage * (1 - damage_reduction)), 0)
        self.health -= damage_taken
        print(f"You attack the {self.name}, dealing {damage_taken} damage.")

        #print(f"{self.name} takes {damage_taken} damage.")

    # quest kill check
    #def kill(self, character):
        #character.kill_count[self.enemy_type] == character.kill_count.get(self.enemy_type, 0) + 1


    @property
    def enemy_type(self):
        return self.__class__.__name__

# enemies defined here

######################################
# Level 1
######################################

class GiantRat(Enemy):
    max_health = 7
    evasion_level = 0.1
    level = 1
    # giant rat
    def __init__(self):
        super().__init__("Giant Rat", 7, 3, 0, 15, random.randint(8, 12)) # name, health, attack, defense, experience, gold

class Wolf(Enemy):
    max_health = 5
    evasion_level = 0.25
    level = 2
    # low level wolf, high evasion
    def __init__(self):
        super().__init__("Wolf", 5, 7, 0, 25, random.randint(10, 15)) # name, health, attack, defense, experience, gold

class HumanBandit(Enemy):
    max_health = 25
    evasion_level = 0.1
    level = 3
    # average level 3
    def __init__(self):
        super().__init__("Human Bandit", 25, 10, 10, 35, random.randint(8, 12)) # name, health, attack, defense, experience, gold

######################################
# Level 5
######################################

class BasiliskHatchling(Enemy):
    max_health = 10
    evasion_level = 0.25
    level = 3
    # high hitting lower level enemy with decent exp
    def __init__(self):
        super().__init__("Basilisk Hatchling", 10, 15, 10, 45, random.randint(20, 30)) # name, health, attack, defense, experience, gold

class RogueDwarf(Enemy):
    max_health = 10
    evasion_level = 0.1
    level = 4
    # Average low level enemy with good defense
    def __init__(self):
        super().__init__("Rogue Dwarf", 25, 10, 30, 40, random.randint(15, 25)) # name, health, attack, defense, experience, gold

class Goblin(Enemy):
    max_health = 20
    evasion_level = 0.1
    level = 5
    # average level 5 with decent gold drop
    def __init__(self):
        super().__init__("Goblin", 30, 15, 15, 55, random.randint(25, 35)) # name, health, attack, defense, experience, gold


class GiantEvilMushroom(Enemy):
    max_health = 50
    evasion_level = 0
    level = 5
    # very tanky level 5 with low damage output, good experience
    def __init__(self):
        super().__init__("Giant Evil Mushroom", 50, 10, 35, 100, random.randint(10, 20)) # name, health, attack, defense, experience, gold

class Orc(Enemy):
    max_health = 40
    evasion_level = 0.1
    level = 5
    # level 5 enemy with high health, decent damage
    def __init__(self):
        super().__init__("Orc", 50, 20, 15, 60, random.randint(15, 25)) # name, health, attack, defense, experience, gold

######################################
# Level 10
######################################

class Skulldyr(Enemy):
    max_health = 50
    evasion_level = 0
    level = 10
    # hard hitting level 10 enemy
    def __init__(self):
        super().__init__("Skulldyr", 40, 60, 10, 250, random.randint(85, 125)) # name, health, attack, defense, experience, gold

class GoblinBrute(Enemy):
    max_health = 55
    evasion_level = 0.2
    level = 10
    # average level 10, drops good gold
    def __init__(self):
        super().__init__("Goblin Brute", 65, 20, 25, 150, random.randint(100, 150)) # name, health, attack, defense, experience, gold


############### CHARACTER AND MONSTER COMBAT MODULE END###############################
############### WORLD TRAVEL SYSTEM START#############################################

class World:
    def __init__(self, name, exits=None, directions=None, level=None, possible_enemies=None, possible_wood=None, possible_metal=None):
        self.name = name
        self.exits = exits or {}
        self.directions = directions
        self.level = level
        self.possible_enemies = possible_enemies
        self.possible_wood = possible_wood
        self.possible_metal = possible_metal

    def enter(self, player):
        self.player = player
        pass

class Square(World):
    def __init__(self):
        exits = {
            "main street": "main street",
            "west": "main street",
        }
        directions = "west: main street"
        level = "Ilion Safe Zone"
        super().__init__("town square", exits, directions, level, possible_enemies=None, possible_metal=None,
                         possible_wood=None)
    def enter(self, player=None):

        print("You've entered the town square.")


class MainStreet(World):
    def __init__(self):
        exits = {
            "town square": "town square",
            "east": "town square",
            "tavern": "tavern",
            "south": "tavern",
            "forest": "forest",
            "west": "forest",
            "market": "market",
            "north": "market",
            "south east": "inn"

        }
        directions = "east: town square\nsouth: tavern\nsouth east: inn\nwest: forest\nnorth: market\n"
        level = "Ilion Safe Zone"
        super().__init__("main street", exits, directions, level, possible_enemies=None, possible_metal=None,
                         possible_wood=None)

    def enter(self, player=None):
        # additional functionality specific
        print("entered West Quarter.")


class Tavern(World):
    tavern_description = None

    def __init__(self):
        exits = {
            "main street": "main street",

        }
        directions = "main street\n"
        level = "Ilion Safe Zone"
        super().__init__("tavern", exits, directions, level, possible_enemies=None, possible_metal=None,
                         possible_wood=None)
        self.should_leave = False # sets flag for staying in enter() until flag is changed

    def enter(self, player):

        if Tavern.tavern_description is not None:
            print(Tavern.tavern_description)

        else:
            system_prompt = "You are the game master for a dungeons and dragons campaign. Give a very brief " \
                            "description of the location based on the provided text."
            prompt = "I have just entered a tavern in a town, describe it to me"
            #Tavern.tavern_description = exposition(system_prompt, prompt)
            #print(Tavern.tavern_description)
        # additional functionality specific

        while not self.should_leave:  # keeps you in the tavern_actions if statement until 'leave' is entered
            print("The following options are available in the tavern:\n'look around'\n'order a drink'\n"
                  "`order food`\n'help'\n"
                  "'leave'\n")
            tavern_actions = input("What do you want to do in the tavern?\n")

            if tavern_actions.lower() == 'look around':
                print("You notice a few patrons scattered around the tavern. There also appears to be a lone barkeep "
                      "behind the counter.")

            elif tavern_actions.lower() in ['order a drink', 'drink']:
                if player.gold >= 5:
                    if player.health < player.max_health:
                        player.gold -= 5                                            # pays 5 gold for a drink
                        player.health = min(player.health + 25, player.max_health)  # 10+ to health to not exceed max
                        print(f'{player.name} buys a drink and recovers 25 health.')
                    else:
                        print(f'{player.name} is already at full health.')
                else:
                    print(f'{player.name} does not have enough for a drink. ')

            elif tavern_actions.lower() in ['order food', 'food']:
                if player.gold >= 10:
                    if player.health < player.max_health:
                        player.gold -= 10                                            # pays 10 gold for a drink
                        player.health = min(player.health + 40, player.max_health)  # 25+ to health to not exceed max
                        print(f'{player.name} buys some food and recovers 40 health.')
                    else:
                        print(f'{self.name} is already at full health.')
                else:
                    print(f'{player.name} does not have enough for a drink. ')

            elif tavern_actions.lower() == 'leave':
                print("You step out of the tavern, walking back into the main street.\n")
                self.should_leave = True # change flag to leave method

            else:
                print("That was not a valid command.")



class Inn(World):
    # safe zone, no combat
    def __init__(self):
        exits = {
            "tavern": "tavern",
            "west": "tavern",
            "main street": "main street",
            "north": "main street"

        }
        directions = "west: tavern\nnorth: main street"
        level = "Ilion Safe Zone"

        super().__init__("inn", exits, directions, level, possible_enemies=None, possible_metal=None,
                         possible_wood=None)

    def enter(self, player=None):
        # additional functionality specific
        print("entered Inn.")

class Market(World):
    market_description = None

    def __init__(self):
        exits = {
            "main street": "main street"
        }
        directions = "main street\n"
        level = "Ilion Safe Zone"
        super().__init__("market", exits, directions, level, possible_enemies=None, possible_metal=None,
                         possible_wood=None)
        self.should_leave = False # sets flag for staying in enter() until flag is changed

    def enter(self, player):
        # additional functionality specific
        if Market.market_description is not None:
            print(Market.market_description)

        else:
            system_prompt = "You are the game master for a dungeons and dragons campaign. Give a very brief " \
                            "description of the location based on the provided text."
            prompt = "I have just entered a market in a town, describe it to me"
            #Market.market_description = exposition(system_prompt, prompt)
            #print(Market.market_description)
            print("PLACEHOLDER Market Text PLACEHOLDER")



        # additional functionality specific

        while not self.should_leave:  # keeps you in the market if statement until 'leave' is entered
            print("From the market, you can enter the following commands:")
            print("|   gear    | - Highland Defense - Sells common and uncommon armor.")
            print("|  potions  | - He'brews Apothecary Inventory - Sells Health Potions.")
            print("|   runes   | - Runes2Go - Sells runes to increase player stats temporarily.")
            print("|  weapons  | - Occam's Razor - Sells common and uncommon weapons.")
            print("| sell item | - Ariel's Acquisitions - Sell unwanted items and loot.")
            print("|   leave   | - Leave the market and return to the main street.")
            print("========================================================")
            market_actions = input("What do you do in the market?\n")

            # ARMOR
            if market_actions.lower() in ['buy gear', 'gear', 'equipment']:
                print("You notice a sign on a storefront labeled \"Highland Defense\" and walk inside.")
                print("______________________________")
                print("Highland Defense Inventory:")
                print(f"You have {player.gold} gold.")
                with open('item_list.json') as file:
                    items_data = json.load(file)
                continue_buying = True
                while continue_buying:

                    for item in items_data['item']:
                        if item['type'] in ['armor'] and item['rarity'] in ['common', 'uncommon']:
                            print(f"{item['item_name']}: {item['price']} gold. | Defense: {item['defense']} | Health: "
                                  f"{item['max_health']} | Evasion: {item['evasion'] * 100}% |")
                    print("______________________________")
                    print(f"You have {player.gold} gold.")

                    highland_armory = input("What do you want to buy?\n")
                    if highland_armory.lower() == "leave":
                        print("You leave the shop, returning to the market.")
                        continue_buying = False
                        continue

                    for item in items_data['item']:
                        if item['item_name'] == highland_armory:
                            highland_armory_quantity = int(input(f"How many {highland_armory}'s do you want?\n"))
                            player.buy_item(highland_armory, highland_armory_quantity)
                            current_room = Market()
                            save_game(player, current_room)

                            buy_again = input(f"Do you want to buy more armor?\n")
                            if buy_again.lower() in ['yes', 'y']:
                                continue_buying = True
                                break
                            else:
                                print("You leave the shop, entering the market.")
                                continue_buying = False
                                break
                    else:
                        print("You cannot buy that item here.")
                        print("To leave the shop, type 'leave'")
                        print("______________________________")
                        continue
            # WEAPONS
            elif market_actions.lower() in ['buy weapon', 'weapons', 'weapon']:
                print("After looking around the market, you walk into a shop called \"Occam\'s Razor\".")
                print("______________________________")
                print("Occam's Razor Inventory:")

                with open('item_list.json') as file:
                    items_data = json.load(file)

                continue_buying = True
                while continue_buying:

                    for item in items_data['item']:
                        if item['type'] in ['weapon'] and item['rarity'] in ['common', 'uncommon']:
                            print(f"{item['item_name']}: {item['price']} gold. | Attack: {item['attack']} | Evasion: "
                                  f"{item['evasion'] * 100}%")

                    print("______________________________")
                    print(f"You have {player.gold} gold.")

                    occams_razor = input("What do you want to buy?\n")

                    for item in items_data['item']:
                        if item['item_name'] == occams_razor:
                            occams_razor_quantity = int(input(f"How many {occams_razor}'s do you want?\n"))
                            player.buy_item(occams_razor, occams_razor_quantity)
                            current_room = Market()
                            save_game(player, current_room)

                            buy_again = input(f"Do you want to any more weapons?\n")
                            if buy_again.lower() in ['yes', 'y']:
                                continue_buying = True
                                break
                            else:
                                print("After buying some gear, you leave the shop.")
                                continue_buying = False
                                break

                    else:
                        print("You cannot buy that item here.")
                        print("To leave the shop, type 'leave'")
                        print("______________________________")
                        continue_buying = False
                        continue
            # RUNES
            elif market_actions.lower() in ['buy rune', 'rune', 'runes']:
                print("After looking around the market, you walk into \"Runes2Go\".")
                print("______________________________")
                print("Runes2Go Inventory:")

                with open('item_list.json') as file:
                    items_data = json.load(file)

                continue_buying = True
                while continue_buying:

                    for item in items_data['item']:
                        if item['type'] in ['rune'] and item['rarity'] in ['common', 'uncommon']:
                            if item['attack'] > 0:
                                print(f"Price: {item['price']} | Item: {item['item_name']}: {item['description']}")
                            if item['defense'] > 0:
                                print(f"Price: {item['price']} | Item: {item['item_name']}: {item['description']}")
                            if item['max_health'] > 0:
                                print(f"Price: {item['price']} | Item: {item['item_name']}: {item['description']}")
                            if item['evasion'] > 0:
                                print(f"Price: {item['price']} | Item: {item['item_name']}: {item['description']}")

                    print("______________________________")
                    print(f"You have {player.gold} gold.")
                    runes2go = input("What do you want to buy?\n")
                    if runes2go.lower() == "leave":
                        print("You leave the shop, returning to the market.")
                        continue_buying = False
                        continue

                    for item in items_data['item']:
                        if item['item_name'] == runes2go:
                            runes2go_quantity = int(input(f"How many {runes2go}'s do you want?\n"))
                            player.buy_item(runes2go, runes2go_quantity)
                            current_room = Market()
                            save_game(player, current_room)

                            buy_again = input(f"Do you want to any more runes?\n")
                            if buy_again.lower() in ['yes', 'y']:
                                continue_buying = True
                                break
                            else:
                                print("You turn around and walk back into the market.")
                                continue_buying = False
                                break

                    else:
                        print("You cannot buy that item here.")
                        print("To leave the shop, type 'leave'")
                        print("______________________________")
                        continue_buying = False
                        continue
            # POTIONS AND BUFFS
            elif market_actions.lower() in ['buy potions', 'potions']:
                print("After looking around the market, you find a merchant with a large supply of "
                      "health potions.")
                print("______________________________")
                print("He'brews Apothecary Inventory:")
                with open('item_list.json') as file:
                    items_data = json.load(file)
                print(f"You have {player.gold} gold.")
                for item in items_data['item']:
                    if item['slot'] == 'consumable' and item['type'] == 'potion':
                        print(f"{item['item_name']}: {item['price']} gold - Heal Amount: {item['max_health']}")
                continue_buying = True
                while continue_buying:

                    potion_size = input("What do you want to buy?\n")
                    if potion_size.lower() == "leave":
                        print("You leave the shop, returning to the market.")
                        continue_buying = False
                        continue

                    for item in items_data['item']:
                        if item['item_name'] == potion_size:
                            potion_quantity = int(input(f"How many {potion_size}'s do you want?\n"))
                            player.buy_item(potion_size, potion_quantity)
                            current_room = Market()
                            save_game(player, current_room)

                            buy_again = input(f"Do you want to any more potions?\n")
                            if buy_again.lower() in ['yes', 'y']:
                                continue_buying = True
                                break
                            else:
                                print("You turn around and walk back into the market.")
                                continue_buying = False
                                break

                    else:
                        print("You cannot buy that item here.")
                        print("To leave the shop, type 'leave'")
                        print("______________________________")
                        continue_buying = False
                        continue

            # SELL JUNK HERE
            elif market_actions.lower() in ['sell', 'junk', 'sell junk']:
                print("You walk into the market, and find a merchant that deals in buying used items.")
                print("______________________________")
                print("Welcome to Ariel's Acquisitions!")
                print("Here's my offer for what is in your inventory:")
                print("______________________________")
                continue_selling = True
                while continue_selling:
                    inventory_empty = True
                    print(f"You have {player.gold} gold.")
                    for item in player.bag:
                        if item['sellable'] == 'true':
                            item_quantity = item['quantity']
                            item_name = item['item_name']
                            item_price = item['price']
                            print(f"{item_name} | Quantity: {item_quantity} | {(item_price) * item_quantity} Gold total ({item_price} each).")
                            inventory_empty = False

                    if inventory_empty:
                        print("You do not have any items to sell. You turn around and leave the shop, entering the market.")
                        break

                    selling_item = input("What do you want to sell?\n")
                    found_item = False
                    for item in player.bag:
                        if item['sellable'] == 'true' and item['item_name'] == selling_item:
                            found_item = True
                            player.gold += int(item['price'] * item['quantity'])
                            print(f"You sell all your {item['item_name']} for {(item['price']) * item['quantity']} gold.")
                            player.bag.remove(item)
                            current_room = Market()
                            save_game(player, current_room)
                            if player.bag is None:
                                break

                    if not found_item:
                        print("That was not a valid item in your inventory. Try typing another item.")

                    keep_selling = input(f"Do you want to continue selling items?\n")
                    if keep_selling.lower() not in ['yes', 'y']:
                        continue_selling = False

            elif market_actions.lower() == 'leave':
                print("You leave the market, walking back into the main street.\n")
                self.should_leave = True # change flag to leave method
            else:
                print("From the market, you can enter the following commands:")
                print("| equipment | - Highland Defense - Sells common and uncommon armor.")
                print("|  potions  | - He'brews Apothecary Inventory - Sells Health Potions.")
                print("|  weapons  | - Occam's Razor - Sells common and uncommon weapons.")
                print("|   sell    | - Ariel's Acquisitions - Sell unwanted items and loot.")
                print("|   leave   | - Leave the market and return to the main street.")

class Forest(World):
    forest_description = None
    def __init__(self):
        exits = {
            "main street": "main street",
            "east": "main street",
            "cross roads": "cross roads",
            "west": "cross roads"

        }
        directions = "east: main street\nwest: cross roads"
        possible_enemies = [GiantRat]
        possible_wood = ["Pine Log"]
        possible_metal = ["Stone"]
        level = "Level 1 Zone"
        super().__init__("forest", exits, directions, level, possible_enemies=possible_enemies, possible_metal=possible_metal,
                         possible_wood=possible_wood)
    def enter(self, player):
        # additional functionality specific
        pass

class CrossRoads(World):
    def __init__(self):
        exits = {
            "forest": "forest",
            "east": "forest",
            "wilderness": "wilderness",
            "west": "wilderness",
            "old ruins": "old ruins",
            "south": "old ruins"
        }
        directions = "west: wilderness\neast: forest\nsouth: old ruins"
        possible_enemies = [GiantRat]
        possible_wood = ["Pine Log", "Oak Log"]
        possible_metal = ["Stone", "Marble"]
        level = "Level 3 Zone"


        super().__init__("cross roads", exits, directions, level, possible_enemies=possible_enemies, possible_metal=possible_metal,
                         possible_wood=possible_wood)
    def enter(self, player):
        pass

class Wilderness(World):
    def __init__(self):
        exits = {
            "cross roads": "cross roads",
            "east": "cross roads",

        }
        directions = "east: cross roads"
        possible_enemies = [GiantRat]
        possible_wood = ["Pine Log", "Oak Log"]
        possible_metal = ["Stone", "Marble"]
        level = "Level 5 Zone"


        super().__init__("wilderness", exits, directions, level, possible_enemies=possible_enemies, possible_metal=possible_metal,
                         possible_wood=possible_wood)
    def enter(self, player):
        pass

class OldRuins(World):
    def __init__(self):
        exits = {
            "cross roads": "cross roads",
            "hellas keep": "hellas keep"
        }
        directions = "North: cross roads\nSouth: hellas keep"
        possible_enemies = [GiantRat]
        possible_wood = ["Pine Log"]
        possible_metal = ["Stone", "Marble"]
        level = "Level 5 Zone"


        super().__init__("old ruins", exits, directions, level, possible_enemies=possible_enemies, possible_metal=possible_metal,
                         possible_wood=possible_wood)
    def enter(self, player):
        pass

class HellasKeep(World):
    def __init__(self):
        exits = {
            "old ruins": "old ruins"
        }
        directions = "North: old ruins"
        possible_enemies = [GiantRat]
        possible_wood = ["Pine Log, Oak Log"]
        possible_metal = ["Stone", "Marble", "Hematite"]
        level = "Level 5 Zone"


        super().__init__("old ruins", exits, directions, level, possible_enemies=possible_enemies, possible_metal=possible_metal,
                         possible_wood=possible_wood)
    def enter(self, player):
        pass

############### WORLD TRAVEL SYSTEM END#############################################

### HELP FUNCTION FOR GAME COMMANDS ###
def help():
    print("This game works by entering commands when prompted. Certain commands are available in specific areas.\n"
          " For example, entering 'buy a drink' in the Tavern will regenerate 10 health for your character. \n"
          "Main commands can be entered from generally any location, with few exceptions (One being the tavern).\n"
          "The following are the main commands to help you play the game:\n\n"
          "=============================================== NAVIGATION ===============================================\n"
          "|  `directions`  | -get a description of your current location and potential connections for where to go.\n"
          "|  `go LOCATION` | -move to a new location (so long as it's next to your current location)\n\n"
          "================================================ CHARACTER ===============================================\n"
          "|  `inventory`   | -view contents of your inventory. Can also use 'inv' and 'items'.\n"
          "|    `stats`     | -pull your character stats and progression.\n"
          "|    `save`      | -manual save of the game. The game automatically saves after combat.\n\n"
          "=============================================== INTERACTION ==============================================\n"
          "|    `equip`     | -equip any items that you have in your inventory.\n"
          "|   `harvest`    | -harvest resources depending on what is available in each area.\n"
          "|   `unequip`    | -unequip any items on your character. Can also use 'remove'.\n"
          "|   `inspect`    | -inspect items in inventory for stats and more information.\n"
          "|    `fight`     | -look for an enemy to fight. Certain enemies only spawn in specific areas of the world.\n"
          "|     `use`      | -use any potions you have in your inventory. Can also use 'consumables'.\n")
    return


### OPEN AI INTEGRATION FOR PROMPTS ###
def exposition(system_prompt, prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": system_prompt}, {"role": "system", "content": prompt}],
        temperature=0.1,
        max_tokens=300,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
    )
    output = response['choices'][0]['message']['content']
    return output


### SET RARITY RATES FOR ENEMIES ###

##### SAVE GAME FUNCTION #####


def save_game(player, current_room):
    game_data = {
        "player_name": player.name,
        "player_level": player.level,
        "player_health": player.health,
        "player_max_health": player.max_health,
        "player_attack": player.attack_level,
        "player_defense": player.defense_level,
        "player_evasion": player.evasion_level,
        "player_experience": player.experience,
        "player_gold": player.gold,
        "kill_stats": player.kill_count,
        "player_backpack": player.bag,
        "player_equipped_items": player.equipped_gear,
        "current_room": current_room.name,
        "active_potion": player.active_potion,
        "fight_count": player.fight_count,
        "active_quest": player.quest,
        "quest_location": player.quest_location,
        "quest_target": player.quest_target,
        "quest_quantity": player.quest_quantity,
        "quest_current_quantity": player.quest_current_quantity,
        "quest_reward": player.quest_reward
        # to add inventory options here eventually so those are saved
    }
    with open("save_game1.json", "w") as f:
        json.dump(game_data, f, indent=4)
    print("Game Saved.")


def load_game(rooms):
    try:
        with open("save_game1.json", "r") as f:
            game_data = json.load(f)
        player_name = game_data["player_name"]
        player_level = game_data["player_level"]
        player_health = game_data["player_health"]
        player_max_health = game_data["player_max_health"]
        player_attack = game_data["player_attack"]
        player_defense = game_data["player_defense"]
        player_evasion = game_data["player_evasion"]
        player_experience = game_data["player_experience"]
        player_gold = game_data["player_gold"]
        player_backpack = game_data["player_backpack"]
        player_equipped_items = game_data["player_equipped_items"]
        current_room_name = game_data["current_room"]
        current_room = rooms[current_room_name]
        kill_stats = game_data["kill_stats"]
        player_active_potion = game_data["active_potion"]
        player_fight_count = game_data["fight_count"]
        player_active_quest = game_data["active_quest"]
        player_quest_location = game_data["quest_location"]
        player_quest_target = game_data["quest_target"]
        player_quest_quantity = game_data["quest_quantity"]
        player_quest_current_quantity = game_data["quest_current_quantity"]
        player_quest_reward = game_data["quest_reward"]

        player = Character(player_name, player_level, player_health, player_max_health, player_attack, player_defense, player_evasion,
                           player_experience, player_gold)
        player.kill_count = kill_stats
        player.bag = player_backpack
        player.equipped_gear = player_equipped_items
        player.fight_count = player_fight_count
        player.active_potion = player_active_potion
        player.quest = player_active_quest
        player.quest_location = player_quest_location
        player.quest_target = player_quest_target
        player.quest_quantity = player_quest_quantity
        player.quest_current_quantity = player_quest_current_quantity
        player.quest_reward = player_quest_reward

        print("Game Loaded.")
        return player, current_room
    except FileNotFoundError:
        print("Save file not found. Starting a new game.")
        return None, rooms["main street"]

def log_exception(exc_type, exc_value, exc_traceback):
    traceback_text = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    with open("crash_log.txt", "w") as log_file:
        log_file.write(traceback_text)

sys.excepthook = log_exception

def game():

    ####### ROOM DIRECTORY #######
    global has_consumables
    rooms = {
        "town square": Square(),
        "main street": MainStreet(),
        "tavern": Tavern(),
        "inn": Inn(),
        "market": Market(),
        "forest": Forest(),
        "cross roads": CrossRoads(),
        "wilderness": Wilderness(),
        "old ruins": OldRuins(),
        "hellas keep": HellasKeep()
    }

    ######### START CHARACTER STATS #############
    player_level = 1
    player_health = 50       # default health
    player_max_health = 50
    player_attack = 10       # default attack
    player_defense = 10      # default defense
    player_evasion = 0.1     # evasion level
    player_experience = 0
    player_gold = 0
    # pass above values to character class for the character
    ######### END CHARACTER STATS #############




    ######################   M A I N    G A M E    L O O P    #######################################################

    ### Game Initialization ###
    player, current_room = load_game(rooms)
    if player is None:
        player_name = input("Enter your character's name:\n")
        player = Character(player_name, player_level, player_health, player_max_health, player_attack, player_defense,
                           player_evasion, player_experience, player_gold)
        print("New game started.")
        print(help())

    # Enter game intro via chatgpt here.

    while True:
        if not player.is_alive():
            restart = input(f"{player.name} is dead. Do you want to restart? (y/n)\n")
            if restart.lower() == 'y' or restart.lower() == 'yes':
                player_name = input(f"Enter your new character's name:\n")
                player.name = player_name
                player.level = player_level
                player.health = player_health
                player.attack = player_attack
                player.defense = player_defense
                player.experience = player_experience
                player.gold = player_gold
                player.kill_count = {}
                # Reset current room
                current_room = rooms["town square"]
                # overwrite save
                save_game(player, current_room)
                continue

            else:
                break

        # checks to see if potion duration (1 use per fight) is exceeded by fights.
        if player.fight_count >= player.potion_duration:
            item_name = player.active_potion
            with open('item_list.json') as file:
                items_data = json.load(file)

            for item in items_data['item']:
                if item['item_name'] == item_name:
                    player.attack_level -= item['attack']
                    player.defense_level -= item['defense']
                    player.max_health -= item['max_health']
                    player.evasion_level -= item['evasion']
                    print(f"{item['item_name']} has worn off and your stats have gone back to normal.")
                    player.active_potion = None
                    player.fight_count = 0
                    continue

        print("========================================================")
        print("Your current location:", current_room.name)
        experience_required = player.level * 100

        # tavern instance for getting food, drink, and quests(soonTM)
        if isinstance(current_room, Tavern):
            current_room.enter(player)

            if current_room.should_leave: # statement to handle where you go after you leave a method if statement
                current_room.should_leave = False
                save_game(player, current_room)
                current_room = rooms[current_room.exits["main street"]]

        # market instance for buying items
        if isinstance(current_room, Market):
            current_room.enter(player)

            if current_room.should_leave: # statement to handle where you go after you leave a method if statement
                current_room.should_leave = False
                save_game(player, current_room)
                current_room = rooms[current_room.exits["main street"]]

        action = input("What do you want to do?\n")
        if action.lower() == "help":
            help()

        elif action.lower().startswith("go"):
            direction = re.sub("go ", "", action)
            if direction.lower() in current_room.exits:
                print(f"You leave the {current_room.name}, heading towards the {direction.lower()}.")
                current_room = rooms[current_room.exits[direction.lower()]]
                time.sleep(1)
                print("...")
                time.sleep(1)
                print("...")
                time.sleep(1)
                print("...")

                print(f"You enter the {current_room.name}.")
                print(f"|~ {current_room.level} ~|")
                print("------------------------")
                print(f"From the {current_room.name} you can go to the following locations:\n{current_room.directions}")

            else:
                print(f"You can't go this way. You can go to the following locations from your current location:")
                print(current_room.directions)

        elif action.lower() == 'directions':
            print(f'From the {current_room.name} you can go to the following locations:\n{current_room.directions}')

        elif action.lower() == 'harvest':
            harvest(player, current_room, action)

        elif action.lower() == 'fight':
            fight(player, current_room, action)

        elif action.lower() == 'save':
            save_game(player, current_room)

        elif action.lower() == 'stats':
            player.calculate_equipped_gear_attributes()
            print("|========================================|")
            print(f"Character Stats for {player.name}")
            print(f'Name:           | {player.name}')
            print(f'Level:          | {player.level}')
            print(f'Experience:     | {player.experience} / {experience_required}')
            print(f'Health:         | {player.health} / {player.max_health} (+{player.equipped_gear_attributes["max_health"]} item bonus)')
            print(f'Attack:         | {player.attack_level} (+{player.equipped_gear_attributes["attack"]} item bonus)')
            print(f'Defense:        | {player.defense_level} (+{player.equipped_gear_attributes["defense"]} item bonus)')
            print(f'Evasion:        | {round(player.evasion_level * 100, 2)}% ({player.equipped_gear_attributes["evasion"] * 100}% item bonus)')
            print(f"Active Rune:    | {player.active_potion}: {player.fight_count} / 3 charges used.")
            print(f'Gold:           | {player.gold}')
            print(f'Total Kills:    | {player.kill_count}')
            print("|========================================|")

        elif action.lower() in ['inventory', 'inv']:
            print("|========================================|")
            print(f"Equipped Items for {player.name}")
            player.list_inventory('onbody')
            print("|----------------------------------------|")
            print(f"Inventory for {player.name}")
            player.list_inventory('all')
            print("|========================================|")

        elif action.lower() in ['inspect']:
            print("|========================================|")
            player.list_inventory('all')
            inspect_item = input(f"What item do you want to inspect?\n")
            player.inspect_item(inspect_item)
            print("|========================================|")

        elif action.lower() in ['equip']:
            print("|========================================|")
            player.list_inventory('equip')
            player.equip_gear()
            print("|========================================|")

        elif action.lower() in ['remove', 'unequip']:
            print("|========================================|")
            player.remove_equipment(slot=None)
            print("|========================================|")

        elif action.lower() == 'journal':
            pass

        elif action.lower() == 'quest':
            if player.quest is None:
                quest(player, current_room, action)
            else:

                print(f"Active Quest:\n{player.quest}")
                print(player.quest_current_quantity)
                print(player.quest_quantity)
                abandon_quest = input(f"Do you want to abandon this quest?\n")
                if abandon_quest in ['yes', 'y']:
                    player.quest = None

                    print(f"Your quest was abandoned.")


        elif action.lower() in ['use', 'consumable', 'consumables']:
            print("|========================================|")
            has_consumables = False
            for item in player.bag:
                if item['slot'] == 'consumable':
                    has_consumables = True
                    break
            if has_consumables:
                print(f"You have the following consumables in your inventory:")
                player.list_inventory('consumable')
                print("|========================================|")
                what_use = input("What item do you want to use?\n")
                player.use_item(what_use)
            else:
                print(f"You do not have any consumable items.")
                print("|========================================|")

        else:
            print("That was not a valid command.")
            print("If you are lost or need help, type 'help'.")

    ######################   M A I N    G A M E    L O O P    #######################################################

def quest(player, current_room, action):
    if current_room.name == 'town square':
        quest_type = random.choice(['collect', 'combat'])
        # estasblish the areas in which quests can be generated for
        randomLocation = random.choice([Forest(), CrossRoads(), Wilderness(), OldRuins(), HellasKeep()])
        if quest_type == 'collect':
            if player.quest is None:
                random_chance = random.random()
                if random_chance <= 0.5:
                    if randomLocation.possible_wood:
                        randomLocationWood = random.choice(randomLocation.possible_wood)
                        materialquant = (random.randint(3, 5) * player.level)
                        matpayout = materialquant * random.randint(8, 12)
                        quest = f"Collect {materialquant} {randomLocationWood} in the {randomLocation.name}. Reward: {matpayout} gold."
                        print(quest)
                        accept_quest = input("Do you want to accept this quest?\n")
                        if accept_quest.lower() in ['yes', 'y']:
                            player.quest = quest
                        else:
                            pass

                else:
                    if randomLocation.possible_metal:
                        randomLocationMetal = random.choice(randomLocation.possible_metal)
                        materialquant = (random.randint(2, 4) * player.level)
                        matpayout = materialquant * random.randint(10, 14)
                        quest = f"Collect {materialquant} {randomLocationMetal} in the {randomLocation.name}. Reward: {matpayout} gold."
                        print(quest)
                        accept_quest = input("Do you want to accept this quest?\n")
                        if accept_quest.lower() in ['yes', 'y']:
                            player.quest = quest
                        else:
                            pass

        elif quest_type == 'combat':
            if player.quest is None:

                valid_enemies = [
                    enemy for enemy in randomLocation.possible_enemies if enemy.level >= player.level - 3 and enemy.level
                                                                          <= player.level + 3]
                if len(valid_enemies) > 0:
                    randomLocationEnemy = random.choice(valid_enemies)
                    enemyquant = (random.randint(3, 5) * player.level // 2)
                    reward = enemyquant * (random.randint(5, 8) * (randomLocationEnemy().level * 5))
                    quest = f"Kill {enemyquant} {randomLocationEnemy().name} in the {randomLocation.name}. Reward: {reward} gold."
                    print(quest)
                    accept_quest = input("Do you want to accept this quest?\n")
                    if accept_quest.lower() in ['yes', 'y']:
                        player.quest = quest
                        player.quest_location = randomLocation.name
                        player.quest_target = randomLocationEnemy().name
                        player.quest_quantity = enemyquant
                        player.quest_reward = reward
                        print(player.quest)
                        print(player.quest_location)
                        print(player.quest_target)
                        print(player.quest_current_quantity)
                        print(player.quest_quantity)
                    else:
                        pass


            else:
                print(f"You can only have one active quest at a time.")

    else:
        print("There are no quests available in this area. Try another location.")
        if player.quest is None:
            print(f"You do not have any active quests. Try going to the town square to find one.")

def harvest(player, current_room, action):
    if action.lower() == 'harvest':
        harvesting = True
    else:
        harvesting = False
    with open('item_list.json') as file:
        items_data = json.load(file)

    while harvesting:
        print("You can try to look for the following materials:")
        print("1. Wood")
        print("2. Metal")
        print("3. Nevermind")

        harvest_type = input("What resource do you want to look for?\n")

        if harvest_type.lower() in ['wood'] or harvest_type == '1':
            randomitem = random.choice(current_room.possible_wood)
            if not randomitem:
                print(f"You cannot harvest {randomitem} in this area.")
                return
            # checks the 'room' to see if there are any resoruces available, then randomly picks one.
            for item in items_data['item']:
                if item['item_name'] == randomitem:
                    counter = 0
                    time.sleep(1)
                    print(f"You find a tree! You start swinging your axe...")
                    while counter < 10:
                        time.sleep(2)
                        print(f"You chop at the {item['material']} tree and place the {randomitem} in your inventory.")
                        player.experience += (4 * player.level)
                        print(f"You gain {4 * player.level} experience for harvesting.")
                        random_number = random.random()
                        if random_number < (0.01 + (player.level / 100)):
                            print(f"As you are harvesting, you hear rustling behind you.")
                            fight(player, current_room, 'fight')
                        found_item = False

                        for backpack_item in player.bag:
                            if backpack_item['item_name'] == randomitem:
                                backpack_item['quantity'] += 1
                                player.update_progress(item.type)
                                print(f"You now have {backpack_item['quantity']} {backpack_item['item_name']}")
                                counter += 1
                                found_item = True
                                continue

                        if not found_item:
                            player.bag.append(item)
                            for backpack_item in player.bag:
                                if backpack_item['item_name'] == randomitem:
                                    print(f"You now have {backpack_item['quantity']} {backpack_item['item_name']}")
                                    counter += 1
                                    continue

        elif harvest_type.lower() in ['metal'] or harvest_type == '2':
            randomitem = random.choice(current_room.possible_metal)
            if not randomitem:
                print(f"You cannot harvest {randomitem} in this area.")
                return
            for item in items_data['item']:
                if item['item_name'] == randomitem:
                    counter = 0
                    time.sleep(1)
                    print(f"You find a large rock! You start swinging your pickaxe...")
                    while counter < 10:
                        time.sleep(2)
                        print(f"You find a piece of {randomitem} and place it in your inventory.")
                        player.experience += (4 * player.level)
                        print(f"You gain {4 * player.level} experience for harvesting.")
                        random_number = random.random()
                        if random_number < (0.01 + (player.level / 100)):
                            print(f"As you are harvesting, you hear rustling behind you.")
                            fight(player, current_room, 'fight')
                        found_item = False
                        for backpack_item in player.bag:
                            if backpack_item['item_name'] == randomitem:
                                backpack_item['quantity'] += 1
                                player.update_progress(item.type)
                                print(f"You now have {backpack_item['quantity']} {backpack_item['item_name']}")
                                found_item = True
                                counter += 1
                                continue

                        if not found_item:
                            player.bag.append(item)
                            for backpack_item in player.bag:
                                if backpack_item['item_name'] == randomitem:
                                    print(f"You now have {backpack_item['quantity']} {backpack_item['item_name']}")
                                    counter += 1
                                    continue

        else:
            print("You stop looking for resources.")
            harvesting = False

def fight(player, current_room, action):
    if action.lower() == 'fight':
        in_combat = True
    else:
        in_combat = False

    # combat code start
    while in_combat:
        enemy_pool = current_room.possible_enemies
        # exception if no enemies in the room
        if not enemy_pool:
            print("There are no enemies in the nearby area. Try another location.")
            return
        enemy_type = random.choice(enemy_pool)
        enemy = enemy_type()

        print(f"You see a {enemy.name} approach!")
        time.sleep(1)

        while player.is_alive() and enemy.health > 0:
            print("========================================================")
            # roll for initiative
            playerroll = random.randint(1, 20)
            enemyroll = random.randint(1,20)
            if playerroll > enemyroll:
                time.sleep(1)
                print(f"You get to attack first.")
                time.sleep(1)
                print(f"You prepare your attack!")
                time.sleep(1)
                player.attack(enemy)
                time.sleep(1)
                enemy.attack(player)
                time.sleep(1)
                print("~~~~~~~~~~~~~~~~~~~~~~~~")
                print(f"{player.name}'s health: {player.health}.")
                print(f"{enemy.name}'s health: {enemy.health}.")
                print("~~~~~~~~~~~~~~~~~~~~~~~~")

            else:
                time.sleep(1)
                print(f"The {enemy.name} gets to attack first.")
                time.sleep(1)
                print(f"{enemy.name} is preparing their attack!")
                time.sleep(1)
                enemy.attack(player)
                time.sleep(1)
                player.attack(enemy)
                time.sleep(1)
                print("~~~~~~~~~~~~~~~~~~~~~~~~")
                print(f"{player.name}'s health: {player.health}.")
                print(f"{enemy.name}'s health: {enemy.health}.")
                print("~~~~~~~~~~~~~~~~~~~~~~~~")

            if enemy.health <= 0:
                print(f'{enemy.name} was defeated. You win!')
                print("========================================================")
                # get enemy xp and gold
                player.defeat(enemy)
                if player.quest is not None:
                    if enemy.name == player.quest_target and player.quest_location == current_room.name:
                        player.quest_current_quantity += 1
                        if player.quest_current_quantity >= player.quest_quantity:
                            print(f"You have completed the following quest:\n{player.quest}")
                            player.gold += player.quest_reward
                            player.quest = None
                            player.quest_location = None
                            player.quest_target = None
                            player.quest_current_quantity = 0
                            player.quest_quantity = 0
                            player.quest_reward = 0


                print(f"You've earned {enemy.experience} experience and {enemy.gold} gold.")
                if player.active_potion is not None:
                    if player.fight_count > 1:
                        player.fight_count += 1
                        print(f"You used {player.fight_count} charges.")
                    else:
                        player.fight_count += 1
                        print(f"You used {player.fight_count} charge.")
                    print("========================================================")



                save_game(player, current_room)
                in_combat = False
                break

            if player.health <= 0:
                break

            continue_fight = input("The fight continues. What do you do: [fight] [item] [run]\n")
            if continue_fight.lower() in ['fight', 'continue', 'c']:
                continue

            elif continue_fight.lower() in ['use', 'item']:
                print("|========================================|")
                has_consumables = False
                for item in player.bag:
                    if item['slot'] == 'consumable':
                        has_consumables = True
                        break
                if has_consumables:
                    print(f"You have the following consumables in your inventory:")
                    player.list_inventory('consumable')
                    print("|========================================|")
                    what_use = input("What item do you want to use?\n")
                    player.use_item(what_use)
                else:
                    print(f"You do not have any consumable items.")
                    print("|========================================|")

            elif continue_fight.lower() in ['run', 'flee']:
                # retaliation damage if you flee is applied
                enemy.retaliation(player)
                print(f"You run from the fight, taking damage as you flee!")
                print(f"{player.name}'s health: {player.health}.")
                if player.active_potion is not None:
                    if player.fight_count > 1:
                        player.fight_count += 1
                        print(f"You used {player.fight_count} charges.")
                    else:
                        player.fight_count += 1
                        print(f"You used {player.fight_count} charge.")
                in_combat = False
                break

            else:
                print(f"You continue the fight.")
                continue


        if enemy.health > 0 and not player.is_alive():
            print(f'{player.name} has been defeated. Game over!')
            break

        if not player.is_alive():
            print(f'{player.name} has died!')
            break

game()
