import pygame
from settings import WIDTH, HEIGHT, FPS
from player import Player
from camera import Camera
from level0 import Level0
from level1 import Level1
from choice_textbox import ChoiceTextBox
from password_textbox import PasswordTextBox
from weapon import Weapon

INTERACT_KEY = pygame.K_e
NPC_PROMPT_DELAY = 2000  # ms

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
    ["Hey.", "You really shouldn't be here."],
    ["You're still here.", "This place isn't safe."],
    ["Last warning.", "Trust me, or stay trapped forever."]
]

NPC_CHOICE_TEXT = [
    "I can show you the way out.",
    "Will you follow me?"
]

# ---------- WEAPON ----------
weapon_obtained = False
weapon_dialogue = None
password_box = None
password_mode = None  # "weapon" or "attack"

WEAPON_DIALOGUE = [
    "The remnants of an old antivirus lie here.",
    "You obtained a weapon."
]

# ---------- COMBAT ----------
current_enemy = None
combat_choice = None
combat_message = None
combat_active = False

# ---------- DEATH ----------
player_dead = False
death_message = None

# ---------- HELPERS ----------
def draw_hp_bar(screen, x, y, w, h, hp, max_hp):
    ratio = max(0, hp / max_hp)
    red = int(255 * (1 - ratio))
    green = int(255 * ratio)
    color = (red, green, 0)

    pygame.draw.rect(screen, (40, 40, 40), (x, y, w, h))
    pygame.draw.rect(screen, color, (x, y, int(w * ratio), h))
    pygame.draw.rect(screen, (255, 255, 255), (x, y, w, h), 2)

# ---------- MAIN LOOP ----------
running = True
while running:
    clock.tick(FPS)
    now = pygame.time.get_ticks()
    keys = pygame.key.get_pressed()

    # ---------- EVENTS ----------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ---- DOOR CHOICE ----
        if door_choice and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                door_choice.move_selection("left")
            elif event.key == pygame.K_d:
                door_choice.move_selection("right")
            elif event.key == INTERACT_KEY:
                if door_choice.next_page():
                    result = door_choice.confirm()
                    door_choice = None
                    door_used = True
                    if result == "Yes":
                        current_level = Level1()
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
                            ["You trusted the wrong entity.", "You died."],
                            ["Respawn"],
                            font
                        )
                    else:
                        npc_prompt_pending = True
                        npc_prompt_timer = now

        # ---- COMBAT MESSAGE ----
        elif combat_message and event.type == pygame.KEYDOWN:
            if event.key == INTERACT_KEY:
                if combat_message.next_page():
                    combat_message = None
                    if combat_active:
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
                        password_box = PasswordTextBox(
                            "Enter weapon password:",
                            font
                        )
                        password_mode = "attack"
                    else:
                        dmg = current_enemy.damage // 2
                        player.hp -= dmg
                        combat_message = ChoiceTextBox(
                            ["You defend yourself.",
                             f"You took {dmg} damage."],
                            ["OK"],
                            font
                        )

        # ONLY THE PASSWORD / COMBAT RESOLUTION BLOCK IS CHANGED
# Everything else remains exactly as in your last working version

        elif password_box and event.type == pygame.KEYDOWN:
            entered = password_box.handle_event(event)
            if entered is not None:

                # --- WEAPON SETUP ---
                if password_mode == "weapon":
                    player.equip_weapon(Weapon(entered))
                    weapon_obtained = True

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
                        ["Your processes have terminated.", "You died."],
                        ["Respawn"],
                        font
                    )

            # --- ENEMY DEAD ---
                elif current_enemy.hp <= 0:
                    combat_active = False
                    current_level.enemies.remove(current_enemy)
                    combat_message = ChoiceTextBox(
                        ["Enemy terminated."],
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


        # ---- DEATH ----
        elif death_message and event.type == pygame.KEYDOWN:
            if event.key == INTERACT_KEY and death_message.next_page():
                player_dead = False
                death_message = None
                player = Player(current_level.spawn_pos)
                camera.reset()

    # ---------- NPC TIMED PROMPTS ----------
    if npc_prompt_pending and now - npc_prompt_timer >= NPC_PROMPT_DELAY:
        npc_dialogue = ChoiceTextBox(
            NPC_PROMPTS[npc_prompt_count],
            ["OK"],
            font
        )
        npc_prompt_count += 1
        npc_prompt_pending = False

    # ---------- UPDATE ----------
    allow_update = not player_dead

    # Only block UPDATE with modals in Level 1
    if isinstance(current_level, Level1) and not npc_triggered and not npc_dialogue:
        allow_update = allow_update and not any([
            door_choice, npc_dialogue, npc_choice_box,
            weapon_dialogue, password_box,
            combat_choice, combat_message, death_message
        ])

    if allow_update:
        prev_rect = player.rect.copy()
        prev_hitbox = player.hitbox.copy()

        player.update(keys)

        # ---- LEVEL 0 DOOR ----
        if isinstance(current_level, Level0) and current_level.door and not door_used:
            if player.hitbox.colliderect(current_level.door.inflate(10, 10)):
                if keys[INTERACT_KEY]:
                    door_choice = ChoiceTextBox(
                        DOOR_DIALOGUE,
                        ["Yes", "No"],
                        font
                    )

        # ---- ENEMY TRIGGER (LEVEL 1 ONLY) ----
        if isinstance(current_level, Level1) and not combat_active:
            for enemy in current_level.enemies:
                if player.hitbox.colliderect(enemy.trigger_rect):
                    current_enemy = enemy
                    combat_active = True
                    combat_message = ChoiceTextBox(
                        ["A hostile process attacks!"],
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

    for box in [
        door_choice, npc_dialogue, npc_choice_box,
        weapon_dialogue, password_box,
        combat_message, combat_choice, death_message
    ]:
        if box:
            box.draw(screen)

    pygame.display.flip()

pygame.quit()
