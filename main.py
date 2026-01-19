import pygame
from settings import WIDTH, HEIGHT, FPS
from player import Player
from camera import Camera
from level0 import Level0
from level1 import Level1
from level2 import Level2
from choice_textbox import ChoiceTextBox
from password_textbox import PasswordTextBox
from weapon import Weapon

INTERACT_KEY = pygame.K_e
NPC_PROMPT_DELAY = 1000  # ms

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)

# ---------- START ----------
current_level = Level0()
player = Player(current_level.spawn_pos)
camera = Camera(WIDTH, HEIGHT)

# ---------- LEVEL 0 DOOR ----------
door_choice = None
door_used = False

DOOR_DIALOGUE = [
    "There is a strange mark in the wall.",
    "It looks like a vulnerability.",
    "Exploit it?"
]

# ---------- NPC PROMPTS ----------
npc_dialogue = None
npc_choice_box = None
npc_triggered = False
npc_prompt_count = 0
npc_prompt_pending = False
npc_prompt_timer = 0

NPC_PROMPTS = [
    ["Hiya Kiddo!", "You seem kinda lost but I can show you the way out!"],
    ["Come on now kid, don't be shy!", "I ain't gonna lay a finger on ya.","I'm only here to help."],
    ["You need to come with me.", "Or you're going to be trapped here like the others.", "I'm not going to hurt you."]
]

NPC_CHOICE_TEXT = [
    "You just need to follow me."
]

# ---------- WEAPON ----------
weapon_obtained = False
weapon_dialogue = None
password_box = None

WEAPON_DIALOGUE = [
    "The remnants of an old antivirus lie here.",
    "You obtained a weapon."
]

# ---------- COMBAT (DIALOGUE-BASED) ----------
current_enemy = None
combat_choice = None
combat_message = None
combat_active = False
combat_active = False
awaiting_attack_password = False
password_mode = None

# ---------- DEATH ----------
player_dead = False
death_message = None

# ---------- HELPERS ----------
def get_player_damage(player):
    if player.weapon:
        return player.weapon.damage
    return 5

def draw_hp_bar(screen, x, y, w, h, hp, max_hp):
    ratio = max(0, hp / max_hp)
    red = int(255 * (1 - ratio))
    green = int(255 * ratio)
    color = (red, green, 0)

    pygame.draw.rect(screen, (40, 40, 40), (x, y, w, h))
    pygame.draw.rect(screen, color, (x, y, int(w * ratio), h))
    pygame.draw.rect(screen, (255, 255, 255), (x, y, w, h), 2)

def draw_xp_bar(screen, x, y, w, h, xp, max_xp):
    ratio = min(1.0, max(0, xp / max_xp))
    color = (0, 200, 255)  # Cyan/Blue

    pygame.draw.rect(screen, (40, 40, 40), (x, y, w, h))
    pygame.draw.rect(screen, color, (x, y, int(w * ratio), h))
    pygame.draw.rect(screen, (255, 255, 255), (x, y, w, h), 2)

# ---------- MAIN LOOP ----------
running = True
while running:
    clock.tick(FPS)
    now = pygame.time.get_ticks()

    # ---------- EVENTS ----------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ---- DOOR ----
        if door_choice and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                door_choice.move_selection("left")
            elif event.key == pygame.K_d:
                door_choice.move_selection("right")
            elif event.key == INTERACT_KEY:
                if door_choice.next_page():
                    result = door_choice.confirm()
                    door_choice = None
                    
                    if result == "Yes":
                        if isinstance(current_level, Level0):
                            current_level = Level1()
                            player = Player(current_level.spawn_pos)
                            camera.reset()
                            door_used = True
                        elif isinstance(current_level, Level1):
                            current_level = Level2()
                            player = Player(current_level.spawn_pos)
                            camera.reset()

        # ---- NPC DIALOGUE ----
        elif npc_dialogue and event.type == pygame.KEYDOWN:
            if event.key == INTERACT_KEY:
                if npc_dialogue.next_page():
                    npc_dialogue = None
                    npc_choice_box = ChoiceTextBox(
                        NPC_CHOICE_TEXT,
                        ["Yes", "No"],
                        font
                    )

        # ---- NPC CHOICE ----
        elif npc_choice_box and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                npc_choice_box.move_selection("left")
            elif event.key == pygame.K_d:
                npc_choice_box.move_selection("right")
            elif event.key == INTERACT_KEY:
                if npc_choice_box.next_page():
                    result = npc_choice_box.confirm()
                    npc_choice_box = None

                    if result == "Yes":
                        player_dead = True
                        death_message = ChoiceTextBox(
                            ["You trusted the wrong entity.", "You crumble into garbage data."],
                            ["Respawn"],
                            font
                        )
                    else:
                        if npc_prompt_count < len(NPC_PROMPTS):
                            npc_prompt_pending = True
                            npc_prompt_timer = now

        # ---- COMBAT MESSAGE ----
        elif combat_message and event.type == pygame.KEYDOWN:
            if event.key == INTERACT_KEY:
                if combat_message.next_page():
                    combat_message = None
                    if combat_active and current_enemy:
                        combat_choice = ChoiceTextBox(
                            ["Choose your action:"],
                            ["Attack", "Defend"],
                            font
                        )

        # ---- COMBAT CHOICE ----
        elif combat_choice and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                combat_choice.move_selection("left")
            elif event.key == pygame.K_d:
                combat_choice.move_selection("right")
            elif event.key == INTERACT_KEY:
                 if combat_choice.next_page():
                     action = combat_choice.confirm()
                     combat_choice = None

                     if action == "Attack":
                         if player.weapon:
                                password_box = PasswordTextBox(
                                    "Enter weapon password:",
                                    font
                                )
                                awaiting_attack_password = True
                                password_mode = "attack"
                                log = []
                         else:
                             combat_active = False
                             current_enemy = None
                             player_dead = True
                             death_message = ChoiceTextBox(
                                 ["Fatal Error: Weapon module missing.", "You crumble into garbage data."],
                                 ["Respawn"],
                                 font
                             )

                     elif action == "Defend":
                         dmg = current_enemy.damage // 2
                         player.hp -= dmg
                         combat_message = ChoiceTextBox(
                             ["You defend yourself.",
                              f"You took {dmg} damage."],
                             ["OK"],
                             font
                         )

                         if player.hp <= 0:
                             combat_active = False
                             current_enemy = None
                             player_dead = True
                             death_message = ChoiceTextBox(
                                 ["You crumble into garbage data."],
                                 ["Respawn"],
                                 font
                             )



        # ---- DEATH ----
        elif death_message and event.type == pygame.KEYDOWN:
            if event.key == INTERACT_KEY:
                if death_message.next_page():
                    player_dead = False
                    death_message = None
                    player = Player(current_level.spawn_pos)
                    camera.reset()

                    npc_triggered = False
                    npc_prompt_count = 0
                    npc_prompt_pending = False

                    weapon_dialogue = None
                    password_box = None

        # ---- WEAPON ----
        elif weapon_dialogue and event.type == pygame.KEYDOWN:
            if event.key == INTERACT_KEY:
                if weapon_dialogue.next_page():
                    weapon_dialogue = None
                    password_box = PasswordTextBox(
                        "Set a password for the weapon:",
                        font
                    )
                    password_mode = "weapon"

        # ---- PASSWORD ----
        elif password_box and event.type == pygame.KEYDOWN:
            entered = password_box.handle_event(event)
            if entered is not None:

                # --- WEAPON SETUP ---
                if password_mode == "weapon":
                    player.equip_weapon(Weapon(entered))
                    weapon_obtained = True
                    current_level.weapon_visible = False

                # --- ATTACK RESOLUTION ---
                elif password_mode == "attack":
                    log = []

                    if entered == player.weapon.password:
                        dmg = player.weapon.damage
                        current_enemy.hp -= dmg
                        log.append("Password accepted.")
                        log.append(f"You dealt {dmg} damage.")
                    else:
                        log.append("Password rejected.")
                        log.append("Your attack failed.")

                    # Enemy retaliates if alive
                    if current_enemy.hp > 0:
                        player.hp -= current_enemy.damage
                        log.append(f"You took {current_enemy.damage} damage.")

                    # --- PLAYER DEAD ---
                    if player.hp <= 0:
                        combat_active = False
                        current_enemy = None
                        player_dead = True
                        death_message = ChoiceTextBox(
                            ["You crumble into garbage data."],
                            ["Respawn"],
                            font
                        )

                    # --- ENEMY DEAD ---
                    elif current_enemy.hp <= 0:
                        combat_active = False
                        player.xp += current_enemy.xp_reward
                        current_level.enemies.remove(current_enemy)
                        combat_message = ChoiceTextBox(
                            ["Enemy terminated.", current_enemy.lore, f"XP Gained: {current_enemy.xp_reward}"],
                            ["OK"],
                            font
                        )
                        current_enemy = None

                    # --- COMBAT CONTINUES ---
                    else:
                        combat_active = True  # 🔑 IMPORTANT
                        combat_message = ChoiceTextBox(log, ["OK"], font)

                password_box = None
                password_mode = None


    # ---------- NPC TIMED PROMPTS ----------
    if npc_prompt_pending and now - npc_prompt_timer >= NPC_PROMPT_DELAY:
        if npc_prompt_count < len(NPC_PROMPTS):
            npc_dialogue = ChoiceTextBox(
                NPC_PROMPTS[npc_prompt_count],
                ["OK"],
                font
            )
            npc_prompt_count += 1
        npc_prompt_pending = False

    # ---------- UPDATE ----------
    if not player_dead and not any([
        door_choice, npc_dialogue, npc_choice_box,
        weapon_dialogue, password_box,
        combat_choice, combat_message, death_message
    ]):
        prev_rect = player.rect.copy()
        prev_hitbox = player.hitbox.copy()

        player.update(pygame.key.get_pressed())

        # ---- LEVEL 0 DOOR ----
        if isinstance(current_level, Level0) and current_level.door and not door_used:
            if player.hitbox.colliderect(current_level.door.inflate(10, 10)):
                if pygame.key.get_pressed()[INTERACT_KEY]:
                    door_choice = ChoiceTextBox(DOOR_DIALOGUE, ["Yes", "No"], font)

        # ---- LEVEL 1 EXIT (TO LEVEL 2) ----
        if isinstance(current_level, Level1) and current_level.exit_rect:
            if player.hitbox.colliderect(current_level.exit_rect.inflate(10, 10)):
                if pygame.key.get_pressed()[INTERACT_KEY] and not door_choice:
                    door_choice = ChoiceTextBox(["Proceed to next level?"], ["Yes", "No"], font)

        # ---- NPC INITIAL TRIGGER ----
        if isinstance(current_level, Level1) and not npc_triggered:
            for trig in current_level.npc_triggers:
                if player.hitbox.colliderect(trig):
                    npc_dialogue = ChoiceTextBox(
                        NPC_PROMPTS[0],
                        ["OK"],
                        font
                    )
                    npc_triggered = True
                    npc_prompt_count = 1
                    break

        # ---- ENEMY TRIGGER ----
        if isinstance(current_level, Level1) and not combat_active:
            for enemy in current_level.enemies:
                if player.hitbox.colliderect(enemy.trigger_rect):
                    current_enemy = enemy
                    combat_active = True
                    combat_message = ChoiceTextBox(
                        [f"{enemy.type.capitalize()}: {enemy.dialogue}"],
                        ["OK"],
                        font
                    )
                    break

        # ---- WEAPON ----
        if isinstance(current_level, Level1) and not weapon_obtained and not weapon_dialogue and not password_box:
            for trig in current_level.weapon_triggers:
                if player.hitbox.colliderect(trig):
                    # Do not set weapon_obtained yet
                    # Do not hide weapon yet
                    weapon_dialogue = ChoiceTextBox(
                        WEAPON_DIALOGUE,
                        ["OK"],
                        font
                    )
                    break

        # ---- COLLISION ----
        for solid in current_level.get_solid_walls():
            if player.hitbox.colliderect(solid):
                player.rect = prev_rect
                player.hitbox = prev_hitbox
                break

    # ---------- CAMERA ----------
    camera.update(
        player.rect,
        current_level.pixel_width,
        current_level.pixel_height
    )

    # ---------- DRAW ----------
    screen.fill((20, 20, 20))
    current_level.draw(screen, camera)
    player.draw(screen, camera)

    draw_hp_bar(screen, 20, 20, 200, 20, player.hp, player.max_hp)
    # XP Bar (Below HP)
    draw_xp_bar(screen, 20, 50, 200, 10, player.xp, 100)

    if combat_active and current_enemy:
        # Enemy HP Bar (Top Right)
        draw_hp_bar(
            screen,
            WIDTH - 220, 20,
            200, 20,
            current_enemy.hp,
            current_enemy.max_hp
        )

    for box in [
        door_choice, npc_dialogue, npc_choice_box,
        weapon_dialogue, password_box,
        combat_message, combat_choice,
        death_message
    ]:
        if box:
            box.draw(screen)

    pygame.display.flip()

pygame.quit()
