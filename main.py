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
from save_manager import SaveManager

INTERACT_KEY = pygame.K_e
NPC_PROMPT_DELAY = 1000  # ms

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)

# ---------- START ----------
# We delay Level creation until "New Game" or "Continue"
current_level = None
player = None
camera = None

game_state = "TITLE"
title_menu = ChoiceTextBox(
    ["CYBERTALE", "Select an option:"],
    ["New Game", "Continue", "Exit"],
    font
)

# Temp init for menu drawing if needed, but we'll handle it in loop
camera = Camera(WIDTH, HEIGHT) # Needed for sizing? No, Title uses screen coords.

# ---------- LEVEL 0 DOOR ----------

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

# ---------- TROJAN ----------
trojan_dialogue = None
trojan_choice = None
trojan_stage = 0  # 0: First offer, 1: Second offer, 2: Done
trojan_expecting_choice = False

TROJAN_OFFER_1 = [
    "Psst... over here.",
    "I can optimize your weapon's drivers.",
    "Just 10 XP. Small price for power."
]

TROJAN_OFFER_2 = [
    "Nice doing business.",
    "I've got a kernel-level exploit for you.",
    "20 XP. It'll make you unstoppable."
]

# ---------- COMBAT (DIALOGUE-BASED) ----------
current_enemies = []
combat_target = None
combat_choice = None
combat_message = None
combat_active = False
player_backfire = False
awaiting_attack_password = False
password_mode = None

# ---------- DEATH ----------
player_dead = False
death_message = None

# ---------- END SCREEN ----------
end_dialogue = None
last_battle_time = 0

# ---------- HELPERS ----------
def get_player_damage(player):
    dmg = player.base_attack
    if player.weapon:
        dmg += player.weapon.damage
    return dmg

def draw_hp_bar(screen, x, y, w, h, hp, max_hp):
    ratio = max(0, hp / max_hp)
    red = int(255 * (1 - ratio))
    green = int(255 * ratio)
    color = (red, green, 0)

    pygame.draw.rect(screen, (40, 40, 40), (x, y, w, h))
    pygame.draw.rect(screen, color, (x, y, int(w * ratio), h))
    pygame.draw.rect(screen, (255, 255, 255), (x, y, w, h), 2)

def draw_xp_bar(screen, x, y, w, h, xp, max_xp=100):
    ratio = (xp % 100) / 100.0
    color = (0, 200, 255)  # Cyan/Blue

    pygame.draw.rect(screen, (40, 40, 40), (x, y, w, h))
    pygame.draw.rect(screen, color, (x, y, int(w * ratio), h))
    pygame.draw.rect(screen, (255, 255, 255), (x, y, w, h), 2)
    
    # Draw Level Text
    lvl_text = font.render(f"Lvl {player.level}", True, (255, 255, 255))
    screen.blit(lvl_text, (x + w + 10, y - 2))

# ---------- MAIN LOOP ----------
running = True
while running:
    clock.tick(FPS)
    now = pygame.time.get_ticks()

    # ---------- EVENTS ----------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ---- TITLE SCREEN ----
        if game_state == "TITLE":
            if title_menu and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    title_menu.move_selection("left")
                elif event.key == pygame.K_d:
                    title_menu.move_selection("right")
                elif event.key == INTERACT_KEY:
                    if title_menu.next_page():
                        choice = title_menu.confirm()
                        
                        if choice == "New Game":
                            current_level = Level0()
                            player = Player(current_level.spawn_pos)
                            camera = Camera(WIDTH, HEIGHT)
                            game_state = "PLAYING"
                            # Reset flags
                            door_used = False
                            weapon_obtained = False
                            
                        elif choice == "Continue":
                            data = SaveManager.load_game()
                            if data:
                                idx = data.get("level_index", 0)
                                if idx == 0: current_level = Level0()
                                elif idx == 1: current_level = Level1()
                                elif idx == 2: current_level = Level2()
                                else: current_level = Level0()
                                
                                player = Player(current_level.spawn_pos)
                                player.load_data(data["player"])
                                camera = Camera(WIDTH, HEIGHT)
                                game_state = "PLAYING"
                                
                                # Restore logic flags if needed?
                                # Simplified: If level > 0, assume door used.
                                if idx > 0: door_used = True
                                if player.weapon: weapon_obtained = True
                                if idx >= 2: weapon_obtained = True # Force if in Lvl2
                            else:
                                # No save found, maybe flash text?
                                # For now, just treat as New Game or do nothing?
                                # Let's restart menu text to say "No Save".
                                title_menu = ChoiceTextBox(["No Save Data found.", "Select option:"], ["New Game", "Exit"], font)

                        elif choice == "Exit":
                            running = False
            continue # Skip other events if in TITLE

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
                            player.teleport(current_level.spawn_pos)
                            camera.reset()
                            door_used = True
                            SaveManager.save_game(player, 1)
                        elif isinstance(current_level, Level1):
                            current_level = Level2()
                            player.teleport(current_level.spawn_pos)
                            camera.reset()
                            SaveManager.save_game(player, 2)

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
                            ["Fatal Error. Respawn?"],
                            ["Yes"],
                            font
                        )
                    else:
                        if npc_prompt_count < len(NPC_PROMPTS):
                            npc_prompt_pending = True
                            npc_prompt_timer = now
        
        # ---- TROJAN DIALOGUE ----
        elif trojan_dialogue and event.type == pygame.KEYDOWN:
            if event.key == INTERACT_KEY:
                if trojan_dialogue.next_page():
                    trojan_dialogue = None
                    # Only open choice if we were expecting one (i.e. not closing a success/error message)
                    if trojan_expecting_choice:
                        trojan_choice = ChoiceTextBox(
                            ["Accept the upgrade?"],
                            ["Yes", "No"],
                            font
                        )
                        trojan_expecting_choice = False # Consumed

        # ---- TROJAN CHOICE ----
        elif trojan_choice and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                trojan_choice.move_selection("left")
            elif event.key == pygame.K_d:
                trojan_choice.move_selection("right")
            elif event.key == INTERACT_KEY:
                if trojan_choice.next_page():
                    result = trojan_choice.confirm()
                    trojan_choice = None
                    
                    if result == "Yes":
                        cost = 10 if trojan_stage == 0 else 20
                        if player.xp >= cost:
                            player.xp -= cost
                            if trojan_stage == 0:
                                # First Offer: Damage Nerf
                                if player.weapon:
                                    player.weapon.damage_modifier = 0.5
                                    print("Weapon damage reduced by 50%")
                                trojan_stage = 1
                                trojan_dialogue = ChoiceTextBox([" optimization_complete.exe executed."], ["OK"], font) # User feedback
                            elif trojan_stage == 1:
                                # Second Offer: Jamming
                                if player.weapon:
                                    player.weapon.jam_chance = 0.3
                                    print("Weapon jam chance set to 30%")
                                trojan_stage = 2
                                trojan_dialogue = ChoiceTextBox([" kernel_patch.dll installed."], ["OK"], font) # User feedback
                        else:
                            # Not enough XP
                             trojan_dialogue = ChoiceTextBox([f"Error: Insufficient resources. Need {cost} XP."], ["OK"], font)
                    else:
                        # Refused
                        pass

        # ---- COMBAT MESSAGE ----
        elif combat_message and event.type == pygame.KEYDOWN:
            if event.key == INTERACT_KEY:
                if combat_message.next_page():
                    combat_message = None
                    if combat_active and current_enemies:
                        combat_choice = ChoiceTextBox(
                            ["Choose your action:"],
                            ["Attack", "Defend"],
                            font
                        )
                    # Victory Condition (Combat ended)
                    elif not combat_active:
                         last_battle_time = now # Set cooldown when box closes
                    pass

        # ---- TARGET SELECTION (Reuse Combat Choice) ----
        elif password_mode == "target_selection" and combat_choice and event.type == pygame.KEYDOWN:
             if event.key == pygame.K_a:
                combat_choice.move_selection("left")
             elif event.key == pygame.K_d:
                combat_choice.move_selection("right")
             elif event.key == INTERACT_KEY:
                 if combat_choice.next_page():
                     pick = combat_choice.confirm() # Returns name string, e.g. "worm_tier3"
                     # Find index
                     idx = 0
                     for i, e in enumerate(current_enemies):
                         if e.type == pick:
                             idx = i
                             break
                     combat_target = current_enemies[idx]
                     combat_choice = None
                     password_mode = None
                     
                     # Now go to password
                     password_box = PasswordTextBox("Enter weapon password:", font)
                     awaiting_attack_password = True
                     password_mode = "attack"
                     log = []

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
                         # Check for Jamming
                         jammed = False
                         import random
                         if player.weapon and random.random() < player.weapon.jam_chance:
                             jammed = True
                        
                         if jammed:
                             # Calc Enemy Retaliation immediately for jamming
                             total_dmg = 0
                             log = ["ERROR: Weapon driver failure.", "Attack aborted."]
                             for enemy in current_enemies:
                                 total_dmg += enemy.damage
                                 # Backfire chance check (only if worm hits you?) 
                                 # User said "when worms deal damage... can make weapon backfire"
                                 # We'll set the flag for NEXT turn.
                                 if hasattr(enemy, "backfire_chance") and random.random() < enemy.backfire_chance:
                                     player_backfire = True
                                     log.append(f"WARNING: {enemy.type} corrupted your drivers!")

                             player.hp -= total_dmg
                             if total_dmg > 0:
                                log.append(f"You took {total_dmg} damage.")
                             
                             combat_message = ChoiceTextBox(log, ["OK"], font)
                             
                             if player.hp <= 0:
                                 combat_active = False
                                 current_enemies = []
                                 player_dead = True
                                 current_enemies = []
                                 player_dead = True
                                 player.image = player.sprites["dead"]
                                 combat_message = None # Clear priority message
                                 death_message = ChoiceTextBox(
                                     ["SYSTEM FAILURE. Respawn?"],
                                     ["Yes"],
                                     font
                                 ) 

                         elif player.weapon:
                                # Target Selection if multiple
                                if len(current_enemies) > 1:
                                    # Create a simple choice box for targets? 
                                    # ChoiceTextBox supports text options.
                                    # We'll map selection index to enemy index.
                                    # Assuming max 2 enemies for now (Tag Battle).
                                    target_names = [e.type for e in current_enemies]
                                    # We need a way to know WHICH was picked. 
                                    # Temporarily hijack combat_choice for targeting? Or new box?
                                    # Let's use a new state: combat_target_selection
                                    pass # Implemented via nested state or simplify?
                                    # SIMPLIFY: Just target [0] for now or use specific logic?
                                    # User requested "fight off a virus and a worm".
                                    # I should implement targeting.
                                    # Let's skip PasswordBox for a second and show TargetBox
                                    combat_choice = ChoiceTextBox(["Select Target:"], target_names, font)
                                    password_mode = "target_selection" # Valid hack?
                                else:
                                    combat_target = current_enemies[0]
                                    password_box = PasswordTextBox("Enter weapon password:", font)
                                    awaiting_attack_password = True
                                    password_mode = "attack"
                                    log = []

                         else:
                             combat_active = False
                             current_enemies = []
                             current_enemies = []
                             player_dead = True
                             player.image = player.sprites["dead"]
                             death_message = ChoiceTextBox(
                                 ["Fatal Error: No Weapon. Respawn?"],
                                 ["Yes"],
                                 font
                             )

                     elif action == "Defend":
                         total_dmg = 0
                         for enemy in current_enemies:
                             total_dmg += enemy.damage
                         
                         dmg = max(0, total_dmg - player.base_defense)
                         dmg = dmg // 2
                         player.hp -= dmg
                         combat_message = ChoiceTextBox(
                             ["You defend yourself.",
                              f"You took {dmg} damage."],
                             ["OK"],
                             font
                         )

                         if player.hp <= 0:
                             combat_active = False
                             current_enemies = []
                             current_enemies = []
                             player_dead = True
                             player.image = player.sprites["dead"]
                             combat_message = None # Clear priority message
                             death_message = ChoiceTextBox(
                                 ["SYSTEM FAILURE. Respawn?"],
                                 ["Yes"],
                                 font
                             )

        # ---- DYING MESSAGE / END DIALOGUE ----
        elif end_dialogue and event.type == pygame.KEYDOWN:
            if event.key == INTERACT_KEY:
                if end_dialogue.next_page():
                    # Quit Game or return to title
                    end_dialogue = None
                    running = False # Simply quit for now as requested

        # ---- DEATH ----
        elif death_message and event.type == pygame.KEYDOWN:
            if event.key == INTERACT_KEY:
                if death_message.next_page():
                    # Check confirmation to ensure intentional input
                    choice = death_message.confirm()
                    if choice == "Yes":
                        # Execute Respawn
                        death_message = None
                        combat_active = False 
                        current_enemies = [] 
                        player.hp = player.max_hp # Reset HP First
                        player_dead = False # Then revive
                        player.image = player.sprites["down"] # Reset sprite
                        
                        player.teleport(current_level.spawn_pos)
                        camera.reset()
                        
                        # Reset all enemies HP and Alive status
                        if current_level and hasattr(current_level, "enemies"):
                            for e in current_level.enemies:
                                e.hp = e.max_hp
                                e.alive = True

                        npc_triggered = False
                        npc_prompt_count = 0
                        npc_prompt_pending = False

                        weapon_dialogue = None
                        password_box = None
                        
                        trojan_stage = 0

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
                    
                    # BACKFIRE CHECK
                    backfire_triggered = False
                    if player_backfire:
                        import random
                        if random.random() < 0.6: # 60% chance to backfire
                             backfire_triggered = True
                             raw_dmg = player.weapon.damage + player.base_attack
                             dmg = int(raw_dmg * 0.5) # Reduced to 50% as per user request
                             player.hp -= dmg
                             log.append("CRITICAL ERROR: Attack Backfired!")
                             log.append(f"You hit yourself for {dmg} damage.")
                             player_backfire = False
                        else:
                             log.append("System stabilized. Backfire avoided.")
                             player_backfire = False

                    if not backfire_triggered:
                        if entered == player.weapon.password:
                            dmg = player.weapon.damage + player.base_attack
                            if combat_target in current_enemies:
                                combat_target.hp -= dmg
                                log.append("Password accepted.")
                                log.append(f"You dealt {dmg} damage to {combat_target.type}.")
                        else:
                            log.append("Password rejected.")
                            log.append("Your attack failed.")

                    # Enemies retaliate
                    total_dmg = 0
                    import random
                    for enemy in current_enemies:
                        if enemy.hp > 0:
                            # --- VIRUS COOLDOWN MECHANIC ---
                            if enemy.type == "VIRUS":
                                if enemy.recharging:
                                    log.append("VIRUS is compiling shaders... (Recharging)")
                                    enemy.recharging = False
                                    continue # Skip attack this turn
                                else:
                                    enemy.recharging = True # Will recharge next turn
                            
                            total_dmg += enemy.damage
                            if not backfire_triggered and hasattr(enemy, "backfire_chance") and random.random() < enemy.backfire_chance:
                                player_backfire = True
                                log.append(f"WARNING: {enemy.type} corrupted drivers!")

                    if total_dmg > 0:
                        total_dmg = max(0, total_dmg - player.base_defense)
                        player.hp -= total_dmg
                        log.append(f"You took {total_dmg} damage.")

                    # --- PLAYER DEAD ---
                    if player.hp <= 0:
                        combat_active = False
                        current_enemies = []
                        player_dead = True
                        player.image = player.sprites["dead"]
                        combat_message = None # Clear priority message
                        death_message = ChoiceTextBox(
                            ["SYSTEM FAILURE. Respawn?"],
                            ["Yes"],
                            font
                        )

                    # --- ENEMIES UPDATE ---
                    # Remove dead enemies
                    alive_enemies = []
                    xp_gain = 0
                    for enemy in current_enemies:
                        if enemy.hp <= 0:
                            # Grant XP immediately
                            player.gain_xp(enemy.xp_reward)
                            log.append(f"{enemy.type} terminated.")
                            log.append(f"Gained {enemy.xp_reward} XP.")
                            
                            # Show Lore
                            if hasattr(enemy, "lore") and enemy.lore:
                                log.append(f"DATA: {enemy.lore}")
                            
                            # Restore 50% HP
                            heal_amount = int(player.max_hp * 0.5)
                            old_hp = player.hp
                            player.hp = min(player.max_hp, player.hp + heal_amount)
                            actual_heal = player.hp - old_hp
                            log.append(f"System Optimized. Recovered {actual_heal} HP.")
                            
                            
                            # DO NOT REMOVE - Logic Update
                            # Instead of resetting HP logic from before:
                            # We mark as dead so they disappear.
                            enemy.alive = False
                        else:
                            alive_enemies.append(enemy)
                    
                    current_enemies = alive_enemies

                    if not current_enemies:
                        # VICTORY
                        combat_active = False
                        
                        # Show logs if present (Enemy terminated, XP gained, etc.)
                        if log:
                            combat_message = ChoiceTextBox(log, ["OK"], font)
                        else:
                            # No logs, just end immediately (rare)
                            last_battle_time = pygame.time.get_ticks() 
                            combat_message = None
                    else:
                        combat_active = True
                        combat_message = ChoiceTextBox(log, ["OK"], font)

                password_box = None
                password_mode = None

        # ---- INTERACTION (KEYDOWN) ----
        elif event.type == pygame.KEYDOWN and event.key == INTERACT_KEY:
            if not any([door_choice, npc_dialogue, npc_choice_box, weapon_dialogue, password_box, combat_choice, combat_message, death_message, trojan_dialogue, trojan_choice]):
                
                # ---- LEVEL 0 DOOR ----
                if isinstance(current_level, Level0) and current_level.door and not door_used:
                    if player.hitbox.colliderect(current_level.door.inflate(10, 10)):
                        door_choice = ChoiceTextBox(DOOR_DIALOGUE, ["Yes", "No"], font)

                # ---- LEVEL 1 EXIT ----
                if isinstance(current_level, Level1) and current_level.exit_rect:
                    if player.hitbox.colliderect(current_level.exit_rect.inflate(10, 10)):
                        door_choice = ChoiceTextBox(["Proceed to next level?"], ["Yes", "No"], font)

                # ---- LEVEL 2 TROJAN ----
                if isinstance(current_level, Level2) and hasattr(current_level, "trojan_rect"):
                    if player.hitbox.colliderect(current_level.trojan_rect.inflate(10, 10)):
                         if trojan_stage < 2:
                            txt = TROJAN_OFFER_1 if trojan_stage == 0 else TROJAN_OFFER_2
                            trojan_dialogue = ChoiceTextBox(txt, ["OK"], font)
                            trojan_expecting_choice = True
                         else:
                            trojan_dialogue = ChoiceTextBox(["I have nothing more for you.", "Good luck."], ["OK"], font)
                
                # ---- LEVEL 2 END SCREEN ----
                if isinstance(current_level, Level2) and current_level.door:
                     if player.hitbox.colliderect(current_level.door.inflate(10, 10)):
                         end_dialogue = ChoiceTextBox(
                             ["To Be Continued...", "Thanks for Playing!"],
                             ["OK"],
                             font
                         )


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
    if game_state == "PLAYING" and not player_dead and not any([
        door_choice, npc_dialogue, npc_choice_box,
        weapon_dialogue, password_box,
        combat_choice, combat_message, death_message,
        trojan_dialogue, trojan_choice, end_dialogue
    ]):
        prev_rect = player.rect.copy()
        prev_hitbox = player.hitbox.copy()

        player.update(pygame.key.get_pressed())

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
        if (isinstance(current_level, Level1) or isinstance(current_level, Level2)) and not combat_active:
            # Check cooldown to prevent instant re-trigger after victory
            if now - last_battle_time > 2000:
                # Normal Enemy Triggers
                for enemy in current_level.enemies:
                    # If enemy is tagged, they are part of tag battle, don't trigger individually?
                    # Assume tagged enemies don't have individual triggers or rely on tag object.
                    if enemy.alive and not enemy.tag and player.hitbox.colliderect(enemy.trigger_rect):
                        current_enemies = [enemy]
                        combat_active = True
                        combat_message = ChoiceTextBox(
                            [f"{enemy.type.capitalize()}: {enemy.dialogue}"],
                            ["OK"],
                            font
                        )
                        break
                
                # Tag Battle Trigger (Level 2)
                if isinstance(current_level, Level2) and current_level.tag_trigger:
                    if player.hitbox.colliderect(current_level.tag_trigger):
                        # Find tagged enemies
                        tagged_enemies = [e for e in current_level.enemies if e.tag and e.alive]
                        if tagged_enemies:
                            current_enemies = tagged_enemies
                            combat_active = True
                            combat_message = ChoiceTextBox(
                                ["AMBUSH DETECTED.", "Multiple threads engaging."],
                                ["OK"],
                                font
                            )
                            # Do NOT remove trigger if we want re-battles?
                            # But tag trigger is a specific zone.
                            # If we leave it, they can fight the ambush again.
                        else:
                            # If no enemies left (shouldn't happen with reset), maybe just remove trigger
                            # But if enemies are reset, we can keep trigger.
                            pass

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
    if game_state == "PLAYING" and camera:
        camera.update(
            player.rect,
            current_level.pixel_width,
            current_level.pixel_height
        )

    # ---------- DRAW ----------
    screen.fill((20, 20, 20))
    
    if game_state == "TITLE":
        if title_menu:
            title_menu.draw(screen)
    else:
        # Check for End Game Blackout
        if end_dialogue:
             screen.fill((0, 0, 0))
             # Don't draw level or player
        else:
            if current_level:
                current_level.draw(screen, camera)
            if player:
                player.draw(screen, camera)

            draw_hp_bar(screen, 20, 20, 200, 20, player.hp, player.max_hp)
            # XP Bar (Below HP)
            draw_xp_bar(screen, 20, 50, 200, 10, player.xp)

        if combat_active and current_enemies:
            # Enemy HP Bars (Top Right)
            y_offset = 20
            for i, enemy in enumerate(current_enemies):
                txt = f"{enemy.type} ({enemy.hp}/{enemy.max_hp})"
                # Draw name
                name_surf = font.render(txt, True, (255, 80, 80))
                screen.blit(name_surf, (WIDTH - 220, y_offset - 20))
                
                draw_hp_bar(
                    screen,
                    WIDTH - 220, y_offset,
                    200, 20,
                    enemy.hp,
                    enemy.max_hp
                )
                y_offset += 60

    for box in [
        door_choice, npc_dialogue, npc_choice_box,
        weapon_dialogue, password_box,
        combat_message, combat_choice,
        death_message,
        trojan_dialogue, trojan_choice, end_dialogue
    ]:
        if box:
            box.draw(screen)

    pygame.display.flip()

pygame.quit()
