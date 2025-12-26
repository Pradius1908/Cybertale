import pygame
from settings import WIDTH, HEIGHT, FPS
from player import Player
from Level1 import Level1
from camera import Camera
from textbox import TextBox
from choice_textbox import ChoiceTextBox

# ---------- CONSTANTS ----------
INTERACT_KEY = pygame.K_e
INTERACT_DISTANCE = 20

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# ---------- LOAD GAME OBJECTS ----------
level = Level1()
player = Player(level.spawn_pos)
camera = Camera(WIDTH, HEIGHT)

font = pygame.font.Font(None, 24)

# ---------- INTRO TEXTBOX ----------
textbox = TextBox(
    [
        "You find yourself trapped in a strange cell.",
        "Last thing you remember, you were playing a game you downloaded off a shady website.",
	"You must find a way out."
    ],
    font
)
show_textbox = True

# ---------- CHOICE STATE ----------
active_choice_box = None
pending_door = None

running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ===== INTRO TEXTBOX =====
        if show_textbox:
            if event.type == pygame.KEYDOWN and event.key == INTERACT_KEY:
                textbox.next_page()
                if not textbox.visible:
                    show_textbox = False

        # ===== CHOICE TEXTBOX =====
        elif active_choice_box:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    active_choice_box.move_selection("left")

                elif event.key == pygame.K_d:
                    active_choice_box.move_selection("right")

                elif event.key == INTERACT_KEY:
                    ready = active_choice_box.next_page()

                    if ready:
                        result = active_choice_box.confirm()

                        if result == "Yes":
                            pending_door.open()
                            # later: teleport player here

                        # If "No", do nothing (remain trapped)

                        active_choice_box = None
                        pending_door = None

        # ===== DOOR INTERACTION (OPEN CHOICE BOX) =====
        elif event.type == pygame.KEYDOWN and event.key == INTERACT_KEY:
            for door in level.doors:
                if not door.is_open:
                    expanded_rect = door.rect.inflate(
                        INTERACT_DISTANCE * 2,
                        INTERACT_DISTANCE * 2
                    )

                    if player.hitbox.colliderect(expanded_rect):
                        active_choice_box = ChoiceTextBox(
                            [
                                "There is a strange mark in this wall.",
                                "It appears to be a vulnerability.",
                                "Exploit the vulnerability?"
                            ],
                            ["Yes", "No"],
                            font
                        )
                        pending_door = door
                        break

    keys = pygame.key.get_pressed()

    # ===== PLAYER UPDATE (PAUSED IF UI ACTIVE) =====
    if not show_textbox and active_choice_box is None:
        prev_x = player.rect.x
        prev_y = player.rect.y
        prev_hx = player.hitbox.x
        prev_hy = player.hitbox.y

        player.update(keys)

        # ===== COLLISION =====
        for wall in level.get_solid_walls():
            if player.hitbox.colliderect(wall):
                player.rect.x = prev_x
                player.rect.y = prev_y
                player.hitbox.x = prev_hx
                player.hitbox.y = prev_hy
                break

    # ===== CAMERA =====
    camera.update(player.rect, level.pixel_width, level.pixel_height)

    # ===== DRAW =====
    screen.fill((30, 30, 30))
    level.draw(screen, camera)
    player.draw(screen, camera)

    # ===== UI DRAW (SCREEN SPACE) =====
    if show_textbox:
        textbox.draw(screen)

    if active_choice_box:
        active_choice_box.draw(screen)

    # DEBUG: visualize hitbox (remove later)
    pygame.draw.rect(
        screen,
        (0, 255, 0),
        camera.apply(player.hitbox),
        1
    )

    pygame.display.flip()

pygame.quit()
