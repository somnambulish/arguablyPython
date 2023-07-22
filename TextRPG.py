import re, openai, random, json


openai.api_key = 'OPEN_AI_API_TOKEN'

############### CHARACTER AND MONSTER COMBAT MODULE START###############################

class Character():
    def __init__(self, name, level, health, max_health, attack, defense, evasion, experience, gold):
        self.name = name
        self.level = level
        self.health = health
        self.max_health = max_health
        self.attack_level = attack
        self.defense_level = defense
        self.evasion_level = evasion
        self.experience = experience
        self.gold = gold
        self.kill_count = {}
        self.crit_chance = 0.1      # 10% crit chance
        self.bag = {'Health Potion': 5}

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

    def defend(self, damage):
        damage_reduction = self.defense_level / 100
        damage_taken = max(int(damage * (1 - damage_reduction)), 0)
        self.health -= damage_taken
        print(f"{self.name} takes {damage_taken} damage.")

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
            print(f'Experienced needed for the next level: {experience_required - self.experience}')

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

    def list_contents(self):
        print("You have the following in your bag:")
        for item, quanity in self.bag.items():
            print(f'{item}: {quanity}')

    # helth
    def use_item(self, item_name):
        if item_name not in self.bag:
            print(f'You do not have any {item_name}')
        else:
            if item_name == 'Health Potion':
                if self.health == self.max_health:
                    print("Your health is already full.")
                else:
                    if self.bag['Health Potion'] > 0:
                        self.health += 20               # increase health by 20
                        self.health = min(self.health, self.max_health) # cap max health
                        self.bag['Health Potion'] -= 1        # decrease health pots in inventory
                        print(f'You used a health potion. Your health is now {self.health}/{self.max_health}.')
                    else:
                        print("You do not have any health potions left.")
            else:
                print(f'Cannot use {item_name}')


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
        print(f"{self.name} takes {damage_taken} damage.")



    @property
    def enemy_type(self):
        return self.__class__.__name__


# enemies defined here

class GiantRat(Enemy):
    max_health = 7
    evasion_level = 0
    level = 1
    def __init__(self):
        super().__init__("Giant Rat", 7, 3, 0, 10, random.randint(2, 3)) # name, health, attack, defense, experience, gold


class HumanBandit(Enemy):
    max_health = 25
    evasion_level = 0.1
    level = 1
    def __init__(self):
        super().__init__("Bandit", 25, 10, 10, 15, random.randint(5, 10)) # name, health, attack, defense, experience, gold


class Goblin(Enemy):
    max_health = 20
    evasion_level = 0.1
    level = 1
    def __init__(self):
        super().__init__("Goblin", 20, 5, 5, 5, random.randint(7, 13)) # name, health, attack, defense, experience, gold


class GoblinBrute(Enemy):
    max_health = 30
    evasion_level = 0.1
    level = 1
    def __init__(self):
        super().__init__("Goblin Brute", 30, 10, 5, 20, random.randint(13, 18)) # name, health, attack, defense, experience, gold


class RogueDwarf(Enemy):
    max_health = 10
    evasion_level = 0
    level = 1
    def __init__(self):
        super().__init__("Rogue Dwarf", 10, 5, 30, 20, random.randint(5, 12)) # name, health, attack, defense, experience, gold


class Skulldyr(Enemy):
    max_health = 15
    evasion_level = 0
    level = 1
    def __init__(self):
        super().__init__("Skulldyr", 15, 25, 0, 20, random.randint(20, 30)) # name, health, attack, defense, experience, gold


class BasiliskHatchling(Enemy):
    max_health = 10
    evasion_level = 0.25
    level = 1
    def __init__(self):
        super().__init__("Basilisk Hatchling", 10, 15, 5, 15, random.randint(10, 15)) # name, health, attack, defense, experience, gold


class GiantEvilMushroom(Enemy):
    max_health = 50
    evasion_level = 0
    level = 1
    def __init__(self):
        super().__init__("Giant Evil Mushroom", 50, 5, 25, 75, random.randint(5, 10)) # name, health, attack, defense, experience, gold


class Orc(Enemy):
    max_health = 40
    evasion_level = 0.1
    level = 1
    def __init__(self):
        super().__init__("Orc", 40, 10, 15, 25, random.randint(10, 25)) # name, health, attack, defense, experience, gold


############### CHARACTER AND MONSTER COMBAT MODULE END###############################
############### WORLD TRAVEL SYSTEM START#############################################

class World:
    def __init__(self, name, exits=None, directions=None, possible_enemies=None):
        self.name = name
        self.exits = exits or {}
        self.directions = directions
        self.possible_enemies = possible_enemies

    def enter(self, player):
        player = None
        pass


class Square(World):
    def __init__(self):
        exits = {
            "west quarter": "west quarter",
            "south quarter": "south quarter"
        }
        directions = "west quarter\nsouth quarter\n"
        super().__init__("square", exits, directions, possible_enemies=None)

    def enter(self, player=None):

        print("entered Square.")


class WestQuarter(World):
    def __init__(self):
        exits = {
            "square": "square",
            "tavern": "tavern",
            "forest": "forest"

        }
        directions = "square\ntavern\nforest\n"
        possible_enemies = [GiantRat, HumanBandit]
        super().__init__("west quarter", exits, directions, possible_enemies=possible_enemies)

    def enter(self, player=None):
        # additional functionality specific
        print("entered West Quarter.")


class Tavern(World):
    tavern_description = None

    def __init__(self):
        exits = {
            "west quarter": "west quarter",
            "inn": "inn"
        }
        directions = "west quarter\n inn\n"
        super().__init__("tavern", exits, directions, possible_enemies=None)
        self.should_leave = False # sets flag for staying in enter() until flag is changed

    def enter(self, player):

        if Tavern.tavern_description is not None:
            print(Tavern.tavern_description)

        else:
            system_prompt = "You are the game master for a dungeons and dragons campaign. Give a very brief " \
                            "description of the location based on the provided text."
            prompt = "I have just entered a tavern in a town, describe it to me"
            Tavern.tavern_description = exposition(system_prompt, prompt)
            print(Tavern.tavern_description)
        # additional functionality specific

        while not self.should_leave:  # keeps you in the tavern_actions if statement until 'leave' is entered
            print("The following options are available in the tavern:\n'look around'\n'order a drink'\n"
                  "`order food`\n'help'\n"
                  "'leave'\n")
            tavern_actions = input("What do you want to do in the tavern?\n")

            if tavern_actions.lower() == 'look around':
                print("You notice a few patrons scattered around the tavern. There also appears to be a lone barkeep "
                      "behind the counter.")

            elif tavern_actions.lower() == 'order a drink' or tavern_actions.lower() == 'drink':
                if player.gold >= 5:
                    if player.health < player.max_health:
                        player.gold -= 5                                            # pays 5 gold for a drink
                        player.health = min(player.health + 10, player.max_health)  # 10+ to health to not exceed max
                        print(f'{player.name} buys a drink and recovers 10 health.')
                    else:
                        print(f'{self.name} is already at full health.')
                else:
                    print(f'{player.name} does not have enough for a drink. ')

            elif tavern_actions.lower() == 'order food' or tavern_actions.lower() == 'food':
                if player.gold >= 10:
                    if player.health < player.max_health:
                        player.gold -= 10                                            # pays 10 gold for a drink
                        player.health = min(player.health + 25, player.max_health)  # 25+ to health to not exceed max
                        print(f'{player.name} buys some food and recovers 25 health.')
                    else:
                        print(f'{self.name} is already at full health.')
                else:
                    print(f'{player.name} does not have enough for a drink. ')

            elif tavern_actions.lower() == 'help':
                print("In the tavern:\n`look around`\n`leave`\n")

            elif tavern_actions.lower() == 'leave':
                print("You step out of the tavern, walking back into the West Quarter\n")
                self.should_leave = True # change flag to leave method

            else:
                print("That was not a valid command.")


class Inn(World):
    def __init__(self):
        exits = {
            "tavern": "tavern"

        }
        directions = "tavern"
        super().__init__("inn", exits, directions, possible_enemies=None)

    def enter(self, player=None):
        # additional functionality specific
        print("entered Inn.")


class SouthQuarter(World):
    def __init__(self):
        exits = {
            "square": "square",
            "inn": "inn"

        }
        directions = "square\ninn"
        possible_enemies = [GiantRat, HumanBandit]
        super().__init__("south quarter", exits, directions, possible_enemies)

    def enter(self, player=None):
        # additional functionality specific
        print("entered south quarter.")


class Market(World):
    def __init__(self):
        exits = {
            "south quarter": "south quarter",
            #"east quarter": "east quarter"

        }
        directions = "south quarter\n"
        possible_enemies = [HumanBandit, GiantRat, RogueDwarf]
        super().__init__("market", exits, directions, possible_enemies=possible_enemies)

    def enter(self, player=None):
        # additional functionality specific
        print("entered Market.")


class Forest(World):
    def __init__(self):
        exits = {
            "west quarter": "west quarter",

        }
        directions = "west quarter\n"
        possible_enemies = [Goblin, HumanBandit, GoblinBrute, RogueDwarf, Skulldyr, BasiliskHatchling,
                            GiantEvilMushroom, Orc]
        super().__init__("forest", exits, directions, possible_enemies=possible_enemies)

    def enter(self, player=None):
        # additional functionality specific
        print("entered forest.")

############### WORLD TRAVEL SYSTEM END#############################################

### HELP FUNCTION FOR GAME COMMANDS ###
def help():
    print("This game works by entering commands when prompted. Certain commands are available in specific areas."
          "For example, entering 'buy a drink' in the Tavern will regenerate 10 health for your character. "
          "Main commands can be entered from generally any location, with few exceptions (One being the tavern)."
          "The following are the main commands to help you navigate the world:\n\n"
          "|     `save`     | -saves the progress made by the player. The game automatically saves after combat.\n"
          "|  `directions`  | -get a description of your current location and potential connections for where to go.\n"
          "|  `go tavern`   | -move to the tavern from your current location (or any valid connection)\n"
          "|    `fight`     | -look for an enemy to fight. Certain enemies only spawn in specific areas of the world.\n"
          "")
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
def gen_enemy_pool():
    # spawn rates for enemies defined in class
    enemy_pool = []
    spawn_rates = {
        # rates: 50, common; 30, uncommon, 15, rare; 4, epic; 1, legendary
        GiantRat: 50,       # its a rat thats giant
        HumanBandit: 50,
        Goblin: 50,  # common normal. no attributes
        GoblinBrute: 50,  # common normal. higher damage resist
        RogueDwarf: 50,
        Skulldyr: 50,       # common undead. no attributes
        BasiliskHatchling: 50,
        GiantEvilMushroom: 50,
        Orc: 50
    }
    for enemy_type, spawn_rate, in spawn_rates.items():
        enemy_pool.extend([enemy_type] * spawn_rate)
    return enemy_pool

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
        "current_room": current_room.name
        # to add inventory options here eventually so those are saved
    }
    with open("game_save.json", "w") as f:
        json.dump(game_data, f)
    print("Game Saved.")


def load_game(rooms):
    try:
        with open("game_save.json", "r") as f:
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
        current_room_name = game_data["current_room"]
        current_room = rooms[current_room_name]
        kill_stats = game_data["kill_stats"]

        # reminder to add kill_count

        player = Character(player_name, player_level, player_health, player_max_health, player_attack, player_defense, player_evasion,
                           player_experience, player_gold)
        player.kill_count = kill_stats

        print("Game Loaded.")
        return player, current_room
    except FileNotFoundError:
        print("Save file not found. Starting a new game.")
        return None, rooms["square"]


def game():

    ####### ROOM DIRECTORY #######
    rooms = {
        "square": Square(),
        "west quarter": WestQuarter(),
        "tavern": Tavern(),
        "inn": Inn(),
        "south quarter": SouthQuarter(),
        "market": Market(),
        "forest": Forest()
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
        player = Character(player_name, player_level, player_health, player_max_health, player_attack, player_defense, player_evasion,
                           player_experience, player_gold)
        print("New game started. ")


    # Enter game intro via chatgpt here.

    while True:
        if not player.is_alive():
            restart = input(f"{player.name} is dead. Do you want to restart? (y/n)\n")
            player_name = input(f"Enter your new character's name:\n")
            if restart.lower() == 'y' or restart.lower() == 'yes':
                player.name = player_name
                player.level = player_level
                player.health = player_health
                player.attack = player_attack
                player.defense = player_defense
                player.experience = player_experience
                player.gold = player_gold
                player.kill_count = {}
                # Reset current room
                current_room = rooms["square"]
                # overwrite save
                save_game(player, current_room)
                continue

            else:
                break

        print("========================================================")
        print("Current Location:", current_room.name)
        experience_required = player.level * 100
        # trigger actions based on locations (questing, buying items, etc)
        if isinstance(current_room, Tavern):
            current_room.enter(player)

            if current_room.should_leave: # statement to handle where you go after you leave a method if statement
                current_room.should_leave = False
                save_game(player, current_room)
                current_room = rooms[current_room.exits["west quarter"]]

        action = input("What do you want to do?\n")
        if action.lower() == "help":
            help()

        elif action.lower().startswith("go"):
            direction = re.sub("go ", "", action)
            if direction in current_room.exits:
                print(f"You leave the {current_room.name}")
                current_room = rooms[current_room.exits[direction]]

            else:
                print("You can't go this way. Try typing 'directions' for help. ")

        elif action.lower() == 'directions':
            print(f'From the {current_room.name} you can go to the following locations:\n{current_room.directions}')

        elif action.lower() == 'look around':
            pass
            # get details from the room if they exist

        elif action.lower() == 'fight':
            fight(player, current_room, action)

        elif action.lower() == 'save':
            save_game(player, current_room)

        elif action.lower() == 'stats':
            print(f'Name:           | {player.name}')
            print(f'Level:          | {player.level}')
            print(f'Experience:     | {player.experience} / {experience_required}')
            print(f'Health:         | {player.health} / {player.max_health}')
            print(f'Attack:         | {player.attack_level}')
            print(f'Defense:        | {player.defense_level}')
            print(f'Evasion:        | {player.evasion_level * 100}%')
            print(f'Gold:           | {player.gold}')
            print(f'Total Kills:    | {player.kill_count}')

        elif action.lower() == 'inventory':
            player.list_contents()

        else:
            print("That was not a valid command.")
            help()



    ######################   M A I N    G A M E    L O O P    #######################################################
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

        print(f"You see a {enemy.name}!")

        combat_choice = input(f"Do you want to fight the {enemy.name}?(y/n)\n")

        if combat_choice == "y":
            while player.is_alive() and enemy.health > 0:
                print("========================================================")
                player.attack(enemy)
                enemy.attack(player)
                print(f"{enemy.name}'s health: {enemy.health}.")
                print(f"{player.name}'s health: {player.health}.")

                if enemy.health <= 0:
                    print(f'{enemy.name} was defeated. You win!')
                    # get enemy xp and gold
                    player.defeat(enemy)
                    print(f"You've earned {enemy.experience} experience and {enemy.gold} gold.")
                    save_game(player, current_room)
                    in_combat = False
                    break

                if player.health <= 0:
                    break

                continue_fight = input("The fight rages on. Do you [Continue], [Use] an item, or [Run] away?\n")
                if continue_fight.lower().startswith('c'):
                    continue

                elif continue_fight.lower().startswith('u'):
                    player.list_contents()
                    item_choice = input(f'What item would you like to use?\n')

                    if item_choice.lower().startswith('h'):
                        player.use_item('Health Potion')
                        continue

                    else:
                        print(f'You do not have any {item_choice}.')
                    break

                else:
                    # retaliation damage if you flee is applied
                    enemy.retaliation(player)
                    print(f"You run from the fight, taking damage as you flee!")
                    print(f"{player.name}'s health: {player.health}.")
                    in_combat = False
                    break

            if enemy.health > 0 and not player.is_alive():
                print(f'{player.name} has been defeated. Game over!')
                break

            if not player.is_alive():
                print(f'{player.name} has died!')
                break

        else:
            in_combat = False


game()


