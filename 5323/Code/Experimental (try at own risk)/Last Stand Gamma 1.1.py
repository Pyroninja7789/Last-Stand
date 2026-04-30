#5323 Gamma 1.0

#Importations
import os
import pygame 
import random
import sys
import time
import threading
from fastapi import background
import platform
import subprocess
from pygame.locals import (
    MOUSEBUTTONUP,
    MOUSEBUTTONDOWN,
    RLEACCEL,
    K_RETURN,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_w,
    K_a,
    K_s,
    K_d,
    K_1,
    K_2,
    K_3,
    K_4,
    K_5,
    K_6,
    K_7,
    K_8,
    K_9,
    K_0,
    K_SPACE,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

def get_display_info():
    sys_name = platform.system()
    
    if sys_name == "Windows":
        import ctypes
        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32  # FIXED: GetDeviceCaps is in gdi32.dll
        
        user32.SetProcessDPIAware()

        hdc = user32.GetDC(0)
        dpi = gdi32.GetDeviceCaps(hdc, 88)    # FIXED: gdi32.GetDeviceCaps
        user32.ReleaseDC(0, hdc)
        scaling = dpi / 96
        
        import pyautogui
        width, height = pyautogui.size()
        print(width, height)
        
    elif sys_name == "Darwin":  # macOS
        
        from AppKit import NSScreen
        width = 1920
        height = 1080
        scaling = 100.0
        try:
            screen = NSScreen.mainScreen()
            logical_size = screen.frame().size
            backing_scale = screen.backingScaleFactor()
            scaling = backing_scale
        except ImportError:
            pass

        import pyautogui 
        width, height = pyautogui.size()
        print(width, height)

        
    else:  # Linux (no tkinter needed)

        try:
            with open('/sys/class/graphics/fb0/virtual_size', 'r') as f:
                width, height = map(int, f.read().strip().split(','))
            scaling = 100

        except:
            width, height = 1920, 1080
        
        # Get scaling/DPI (xrdb Xresources)
        scaling = 1.0
        try:
            dpi_result = subprocess.check_output(['xrdb', '-query']).decode()
            for line in dpi_result.splitlines():
                if 'Xft.dpi' in line:
                    dpi = float(line.split(':')[1])
                    scaling = dpi / 96
                    break
        except:
            pass
        
        # Physical pixels = logical × scaling
        phys_width = int(width * scaling)
        phys_height = int(height * scaling)
    
    return {
        'width': width,
        'height': height,
        'scaling': scaling * 100
    }

info = get_display_info()
width = info['width']
height = info['height']
scaling = info['scaling']


SCREEN_HEIGHT = height * scaling / 100
SCREEN_WIDTH = width * scaling / 100


print(SCREEN_WIDTH, SCREEN_HEIGHT)

#variables
hz = 24
placeholder = "" #can be changed with no effect
stop_music = False
menu_choice = ""
settings_choice = ""
sprite_timer = 100
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
storage_file = os.path.join(BASE_DIR, "TextFolders", "Storage.txt")
background_image = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Background1.png")), (SCREEN_WIDTH, SCREEN_HEIGHT))
background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Menu1.png")), (SCREEN_WIDTH, SCREEN_HEIGHT))
menu_in_use = 1
global enemy_multiplier
enemy_multiplier = 1

#Accounts
def get_storage_data():
    global name1, name2, name3, name4, name5
    global password1, password2, password3, password4, password5
    global score1, score2, score3, score4, score5
    with open(storage_file, "r") as f:
        lines = f.readlines()

    name1, password1, score1 = lines[0].strip().split("|")
    name2, password2, score2 = lines[1].strip().split("|")
    name3, password3, score3 = lines[2].strip().split("|")
    name4, password4, score4 = lines[3].strip().split("|")
    name5, password5, score5 = lines[4].strip().split("|")

    score1 = int(score1)
    score2 = int(score2)
    score3 = int(score3)
    score4 = int(score4)
    score5 = int(score5)

    """
    print(f"Name: {name1}, Password: {password1}, Score: {score1}")
    print(f"Name: {name2}, Password: {password2}, Score: {score2}")
    print(f"Name: {name3}, Password: {password3}, Score: {score3}")
    print(f"Name: {name4}, Password: {password4}, Score: {score4}")
    print(f"Name: {name5}, Password: {password5}, Score: {score5}")
    """

    global name0, password0, score0
    name0 = "Not Logged In"
    password0 = ""
    score0 = 0

    global logged_in
    logged_in = False

#Menu
def menu(BASE_DIR):
    #ESSENTIAL CODE DO NOT TOUCH
    global SCREEN_HEIGHT, SCREEN_WIDTH
    global background_image1
    pygame.init()
    pygame.joystick.init()
    clock = pygame.time.Clock()
    running = True
    #variables
    hz = 24
    placeholder = "" #can be changed with no effect
    menu_choice = ""
    settings_choice = ""
    sprite_timer = 100
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
    background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Menu1.png")), (SCREEN_WIDTH, SCREEN_HEIGHT))
    menu_in_use = 0

    #Create the screen object
    #The size is determined by the constant WIDTH and HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.RESIZABLE) 
    pygame.display.set_caption("Last Stand")
    
    class Menu(pygame.sprite.Sprite):
        def __init__(self):
            super(Menu, self).__init__()
            self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

        def update(self, pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR):
            if menu_in_use == 0:
                menu_in_use = 1

            if pressed_keys[K_UP] and menu_in_use > 1:
                menu_in_use -= 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", f"Menu{menu_in_use}.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            if pressed_keys[K_DOWN] and menu_in_use < 6:
                menu_in_use += 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", f"Menu{menu_in_use}.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            
            #========================  Redirect to next function  =====================#
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 1:
                start_confirm(BASE_DIR)
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 2: #settings
                settings(BASE_DIR)
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 3: #tutorial/controls
                tutorial(BASE_DIR)
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 4: #leaderboard
                leaderboard(BASE_DIR)
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 5: #account (sign in)
                accounts(BASE_DIR)
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 6: #credits
                credits(BASE_DIR)
            return menu_in_use, sprite_timer, background_image1, 

    Menu1 = Menu()

    #GAME LOOP ITSELF
    while running:
        true = True
        for event in pygame.event.get():
            if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                quit_game(BASE_DIR)

            pressed_keys = pygame.key.get_pressed()
            menu_in_use, sprite_timer, background_image1,  = Menu1.update(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                
        
        #Cirtical Screen Stuff
        screen.blit(Menu1.surf, Menu1.rect)        
        pygame.display.flip()
        clock.tick(10)

    pygame.quit()
    sys.exit()

#Start Confirmation
def start_confirm(BASE_DIR):
    #ESSENTIAL CODE DO NOT TOUCH
    global SCREEN_HEIGHT, SCREEN_WIDTH
    global background_image1
    pygame.init()
    pygame.joystick.init()
    clock = pygame.time.Clock()
    running = True
    #variables
    hz = 24
    placeholder = "" #can be changed with no effect
    menu_choice = ""
    settings_choice = ""
    sprite_timer = 100
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
    background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Start_confirm-2.png.png")), (SCREEN_WIDTH, SCREEN_HEIGHT))
    menu_in_use = 1

    #Create the screen object
    #The size is determined by the constant WIDTH and HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.RESIZABLE) 
    pygame.display.set_caption("Last Stand")
    
    class Menu(pygame.sprite.Sprite):
        def __init__(self):
            super(Menu, self).__init__()
            self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

        def update(self, pressed_keys, menu_in_use, sprite_timer, background_image1, ):

            if pressed_keys[K_UP]:
                menu_in_use = 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Start_confirm-2.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            if pressed_keys[K_DOWN]:
                menu_in_use = 2
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Start_confirm-3.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            
            #========================  Redirect to next function  =====================#
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 1: #game
                global enemy_multiplier 
                if score0 == 8670:
                    enemy_multiplier = 10
                    boss()
                elif score0 == 6670:
                    enemy_multiplier = 10
                    boss()
                elif score0 == 4870:
                    enemy_multiplier = 10
                    game5()
                elif score0 == 4270:
                    enemy_multiplier = 10
                    game4()
                elif score0 == 3870:
                    enemy_multiplier = 10
                    game3()
                elif score0 == 3670:
                    enemy_multiplier = 10
                    game2()
                elif score0 == 3570:
                    enemy_multiplier = 10
                    game1()
                elif score0 == 2770:
                    enemy_multiplier = 4
                    boss()
                elif score0 == 2370:
                    enemy_multiplier = 4
                    game6()
                elif score0 == 2040:
                    enemy_multiplier = 4
                    game5()
                elif score0 == 1810:
                    enemy_multiplier = 4
                    game4()
                elif score0 == 1650:
                    enemy_multiplier = 4
                    game3()
                elif score0 == 1570:
                    enemy_multiplier = 4
                    game2()
                elif score0 == 1530:
                    enemy_multiplier = 4
                    game1()
                elif score0 == 1130:
                    enemy_multiplier = 2
                    boss()
                elif score0 == 930:
                    enemy_multiplier = 2
                    game6()
                elif score0 == 770:
                    enemy_multiplier = 2
                    game5()
                elif score0 == 650:
                    enemy_multiplier = 2
                    game4()
                elif score0 == 570:
                    enemy_multiplier = 2
                    game3()
                elif score0 == 530:
                    enemy_multiplier = 2
                    game2()
                elif score0 == 510:
                    enemy_multiplier = 2
                    game1()
                elif score0 == 310:
                    enemy_multiplier = 1
                    boss()
                elif score0 == 210:
                    enemy_multiplier = 1
                    game6()
                elif score0 == 130:
                    enemy_multiplier = 1
                    game5()
                elif score0 == 70:
                    enemy_multiplier = 1
                    game4()
                elif score0 == 30:
                    enemy_multiplier = 1
                    game3()
                elif score0 == 10:
                    enemy_multiplier = 1
                    game2()
                else:
                    enemy_multiplier = 1
                    game1()
                print(score0)
                print(enemy_multiplier)
                
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 2: #menu
                menu(BASE_DIR)
            return menu_in_use, sprite_timer, background_image1, 

    Menu1 = Menu()

    time.sleep(0.5)

    #GAME LOOP ITSELF
    while running:
        true = True
        for event in pygame.event.get():
            pressed_keys = pygame.key.get_pressed()
            menu_in_use, sprite_timer, background_image1,  = Menu1.update(pressed_keys, menu_in_use, sprite_timer, background_image1, )
             
        
        #Cirtical Screen Stuff
        screen.blit(Menu1.surf, Menu1.rect)        
        pygame.display.flip()
        clock.tick(10)

    pygame.quit()
    sys.exit()


#Menu
def dificulty(BASE_DIR): # This is not in use because icba to fix it rn
    #ESSENTIAL CODE DO NOT TOUCH
    global SCREEN_HEIGHT, SCREEN_WIDTH
    global background_image1
    pygame.init()
    pygame.joystick.init()
    clock = pygame.time.Clock()
    running = True
    #variables
    hz = 24
    placeholder = "" #can be changed with no effect
    menu_choice = ""
    settings_choice = ""
    menu_in_use = 1
    sprite_timer = 100
    global score0

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if score0 >= 5370: #imposible
        background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", "Level_select_imp-1.png.png")), (SCREEN_WIDTH, SCREEN_HEIGHT))
    elif score0 >= 1530: #hard
        background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", "Level_select_hard-1.png.png")), (SCREEN_WIDTH, SCREEN_HEIGHT))
    elif score0 >= 510: #medium
        background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", "Level_select_medium-1.png.png")), (SCREEN_WIDTH, SCREEN_HEIGHT))
    else: #easy 
        background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", "Level_select_easy-1.png.png")), (SCREEN_WIDTH, SCREEN_HEIGHT))

    #Create the screen object
    #The size is determined by the constant WIDTH and HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.RESIZABLE) 
    pygame.display.set_caption("Last Stand")

    global enemy_multiplier
    enemy_multiplier = 0

    
    class Menu(pygame.sprite.Sprite):
        def __init__(self):
            super(Menu, self).__init__()
            self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

        def update_imp(self, pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR, enemy_multiplier):
            
            if menu_in_use == 0:
                menu_in_use = 1

            if pressed_keys[K_UP] and menu_in_use > 1:
                menu_in_use -= 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_imp-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            if pressed_keys[K_DOWN] and menu_in_use < 5:
                menu_in_use += 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_imp-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            
            #========================  Redirect to next function  =====================#
            pressed_keys = pygame.key.get_pressed()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 1: #easy
                enemy_multiplier = 1
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 2: #medium
                enemy_multiplier = 2        
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 3: #hard
                enemy_multiplier = 4
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 4: #imposible
                enemy_multiplier = 10
                
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 5: #go back
                menu(BASE_DIR)
            
            return menu_in_use, sprite_timer, background_image1, enemy_multiplier

        def update_hard(self, pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR, enemy_multiplier):
            
            if menu_in_use == 0:
                menu_in_use = 1

            if pressed_keys[K_UP] and menu_in_use > 1:
                menu_in_use -= 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_hard-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            if pressed_keys[K_DOWN] and menu_in_use < 4:
                menu_in_use += 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_hard-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            
            #========================  Redirect to next function  =====================#
            pressed_keys = pygame.key.get_pressed()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 1: #easy
                enemy_multiplier = 1
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 2: #medium
                enemy_multiplier = 2        
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 3: #hard
                enemy_multiplier = 4
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 4:  #go back
                menu(BASE_DIR)
            
            return menu_in_use, sprite_timer, background_image1, enemy_multiplier

        def update_medium(self, pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR, enemy_multiplier):
            
            if menu_in_use == 0:
                menu_in_use = 1

            if pressed_keys[K_UP] and menu_in_use > 1:
                menu_in_use -= 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_medium-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            if pressed_keys[K_DOWN] and menu_in_use < 3:
                menu_in_use += 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_medium-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            
            #========================  Redirect to next function  =====================#
            pressed_keys = pygame.key.get_pressed()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 1: #easy
                enemy_multiplier = 1
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 2: #medium
                enemy_multiplier = 2        
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 3: #go back
                menu(BASE_DIR)
            
            return menu_in_use, sprite_timer, background_image1, enemy_multiplier

        def update_easy(self, pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR, enemy_multiplier):
            
            if menu_in_use == 0:
                menu_in_use = 1

            if pressed_keys[K_UP] and menu_in_use > 1:
                menu_in_use -= 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_easy-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            if pressed_keys[K_DOWN] and menu_in_use < 5:
                menu_in_use += 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_easy-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            
            #========================  Redirect to next function  =====================#
            pressed_keys = pygame.key.get_pressed()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 1: #easy
                enemy_multiplier = 1
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 2: #go back
                menu(BASE_DIR)
            
            return menu_in_use, sprite_timer, background_image1, enemy_multiplier

    Menu1 = Menu()


    #GAME LOOP ITSELF
    while running:
        true = True
        for event in pygame.event.get():
            
            if   score0 > 3430: #imposible
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1, enemy_multiplier = Menu1.update_imp(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR, enemy_multiplier)
            elif score0 > 1430: #hard
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1, enemy_multiplier = Menu1.update_hard(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR, enemy_multiplier)
            elif score0 > 510: #medium
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1, enemy_multiplier = Menu1.update_medium(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR, enemy_multiplier)
            else: #easy
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1, enemy_multiplier = Menu1.update_easy(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR, enemy_multiplier)

            if enemy_multiplier != 0:
                print(enemy_multiplier, "hello")
                



                if score0 >= 23698:
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1  = Menu1.update_9(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 13698:
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_8(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 10698:
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_7(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 10198:
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_6(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 9948:
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_5(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 9848:
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_4(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 9798:
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_3(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 9768:
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_2(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 9758:
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_1(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                
                elif score0 >= 5758:
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_9(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 4958:
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_8(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 4558:
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_7(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 4358:
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_6(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 4258:
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_5(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 4218:
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_4(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 4198:
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_3(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 4186:
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_2(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 4182: 
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_1(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                
                elif score0 >= 2182: 
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_9(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 1782: 
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_8(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 1582: 
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_7(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 1482: 
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_6(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 1432: 
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_5(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 1412: 
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_4(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 1402: 
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_3(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 1396: 
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_2(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 1394: 
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_1(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                
                elif score0 >= 394: 
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_9(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 194: 
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_8(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 94: 
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_7(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 44: 
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_6(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 19: 
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_5(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 9: 
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_4(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 4: 
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_3(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 1: 
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_2(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
                elif score0 >= 0: 
                    pressed_keys = pygame.key.get_pressed()
                    menu_in_use, sprite_timer, background_image1,  = Menu1.update_1(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)

                game5()

        #Cirtical Screen Stuff
        screen.blit(Menu1.surf, Menu1.rect)        
        pygame.display.flip()
        clock.tick(10)

    pygame.quit()
    sys.exit()

#Menu
def level(BASE_DIR): # This is also not in use because i also cba to fix it rn
    #ESSENTIAL CODE DO NOT TOUCH
    global SCREEN_HEIGHT, SCREEN_WIDTH
    global background_image1
    pygame.init()
    pygame.joystick.init()
    clock = pygame.time.Clock()
    running = True
    #variables
    hz = 24
    placeholder = "" #can be changed with no effect
    menu_choice = ""
    settings_choice = ""
    sprite_timer = 100
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
    background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", "Level_select_9-1.png.png")), (SCREEN_WIDTH, SCREEN_HEIGHT))
    menu_in_use = 0

    #Create the screen object
    #The size is determined by the constant WIDTH and HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.RESIZABLE) 
    pygame.display.set_caption("Last Stand")

    global enemy_multiplier
    enemy_multiplier = 1
    
    class Menu(pygame.sprite.Sprite):
        def __init__(self):
            super(Menu, self).__init__()
            self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

        def update_9(self, pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR):
            if menu_in_use == 0:
                menu_in_use = 1

            elif pressed_keys[K_UP] and menu_in_use == 3:
                menu_in_use = 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_9-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            elif pressed_keys[K_UP] and menu_in_use == 4:
                menu_in_use = 2
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_9-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            elif pressed_keys[K_UP] and menu_in_use == 5:
                menu_in_use = 3
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_9-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            elif pressed_keys[K_UP] and menu_in_use == 6:
                menu_in_use = 4
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_9-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            elif pressed_keys[K_UP] and menu_in_use == 7:
                menu_in_use = 5
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_9-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            elif pressed_keys[K_UP] and menu_in_use == 8:
                menu_in_use = 7
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_9-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            if pressed_keys[K_DOWN] and menu_in_use == 7:
                menu_in_use = 8
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_9-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))#
            
            elif pressed_keys[K_DOWN] and menu_in_use == 6:
                menu_in_use = 7
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_9-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            
            elif pressed_keys[K_DOWN] and menu_in_use == 5:
                menu_in_use = 7
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_9-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            elif pressed_keys[K_DOWN] and menu_in_use == 4:
                menu_in_use = 6
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_9-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            elif pressed_keys[K_DOWN] and menu_in_use == 3:
                menu_in_use = 5
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_9-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            elif pressed_keys[K_DOWN] and menu_in_use == 2:
                menu_in_use = 4
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_9-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            elif pressed_keys[K_DOWN] and menu_in_use == 1:
                menu_in_use == 3
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_9-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))






            



            if pressed_keys[K_LEFT] and menu_in_use == 2:
                menu_in_use == 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_9-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            
            if pressed_keys[K_LEFT] and menu_in_use == 4:
                menu_in_use == 3
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_9-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            
            if pressed_keys[K_LEFT] and menu_in_use == 6:
                menu_in_use == 5
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_9-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))



            if pressed_keys[K_RIGHT] and menu_in_use == 1:
                menu_in_use == 2
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_9-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            
            if pressed_keys[K_RIGHT] and menu_in_use == 3:
                menu_in_use == 4
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_9-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            
            if pressed_keys[K_RIGHT] and menu_in_use == 5:
                menu_in_use == 6
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_9-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            
            #========================  Redirect to next function  =====================#
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 1: #1
                game1()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 2: #2
                game2()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 3: #3
                game3()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 4: #4
                game4()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 5: #5
                game5()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 6: #6
                game6()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 7: #7
                boss()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 8: #go back
                menu(BASE_DIR)

            return menu_in_use, sprite_timer, background_image1,

        def update_6(self, pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR):
            if menu_in_use == 0:
                menu_in_use = 1

            if pressed_keys[K_UP] and menu_in_use > 1:
                menu_in_use -= 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_6-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            if pressed_keys[K_DOWN] and menu_in_use < 7:
                menu_in_use += 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_6-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            
            #========================  Redirect to next function  =====================#
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 1: #1
                game1()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 2: #2
                game2()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 3: #3
                game3()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 4: #4
                game4()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 5: #5
                game5()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 6: #6
                game6()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 7: #go back
                menu(BASE_DIR)
            return menu_in_use, sprite_timer, background_image1

        def update_5(self, pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR):
            if menu_in_use == 0:
                menu_in_use = 1

            if pressed_keys[K_UP] and menu_in_use > 1:
                menu_in_use -= 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_5-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            if pressed_keys[K_DOWN] and menu_in_use < 6:
                menu_in_use += 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_5-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            
            #========================  Redirect to next function  =====================#
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 1: #1
                game1()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 2: #2
                game2()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 3: #3
                game3()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 4: #4
                game4()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 5: #5
                game5()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 6: #go back
                menu(BASE_DIR)
            return menu_in_use, sprite_timer, background_image1

        def update_4(self, pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR):
            if menu_in_use == 0:
                menu_in_use = 1

            if pressed_keys[K_UP] and menu_in_use > 1:
                menu_in_use -= 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_4-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            if pressed_keys[K_DOWN] and menu_in_use < 5:
                menu_in_use += 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_4-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            
            #========================  Redirect to next function  =====================#
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 1: #1
                game1()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 2: #2
                game2()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 3: #3
                game3()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 4: #4
                game4()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 5: #go back
                menu(BASE_DIR)
            return menu_in_use, sprite_timer, background_image1

        def update_3(self, pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR):
            if menu_in_use == 0:
                menu_in_use = 1

            if pressed_keys[K_UP] and menu_in_use > 1:
                menu_in_use -= 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_3-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            if pressed_keys[K_DOWN] and menu_in_use < 4:
                menu_in_use += 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_3-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            
            #========================  Redirect to next function  =====================#
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 1: #1
                game1()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 2: #2
                game2()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 3: #3
                game3()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 4: #go back
                menu(BASE_DIR)
            return menu_in_use, sprite_timer, background_image1

        def update_2(self, pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR):
            if menu_in_use == 0:
                menu_in_use = 1

            if pressed_keys[K_UP] and menu_in_use > 1:
                menu_in_use -= 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_2-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            if pressed_keys[K_DOWN] and menu_in_use < 3:
                menu_in_use += 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_2-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            
            #========================  Redirect to next function  =====================#
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 1: #1
                game1()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 2: #2
                game2()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 3: #go back
                menu(BASE_DIR)
            return menu_in_use, sprite_timer, background_image1
    
        def update_1(self, pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR):
            if menu_in_use == 0:
                menu_in_use = 1

            if pressed_keys[K_UP] and menu_in_use > 1:
                menu_in_use -= 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_1-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            if pressed_keys[K_DOWN] and menu_in_use < 2:
                menu_in_use += 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level select", f"Level_select_1-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            
            #========================  Redirect to next function  =====================#
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 1: #1
                game1()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 2: #go back
                menu(BASE_DIR)
            return menu_in_use, sprite_timer, background_image1
    
    
    Menu1 = Menu()

    #GAME LOOP ITSELF
    while running:
        true = True
        for event in pygame.event.get():
            if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                quit_game(BASE_DIR)
            
            elif score0 >= 23698:
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1  = Menu1.update_9(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 13698:
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_8(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 10698:
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_7(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 10198:
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_6(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 9948:
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_5(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 9848:
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_4(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 9798:
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_3(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 9768:
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_2(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 9758:
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_1(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            
            elif score0 >= 5758:
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_9(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 4958:
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_8(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 4558:
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_7(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 4358:
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_6(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 4258:
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_5(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 4218:
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_4(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 4198:
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_3(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 4186:
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_2(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 4182: 
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_1(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            
            elif score0 >= 2182: 
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_9(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 1782: 
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_8(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 1582: 
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_7(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 1482: 
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_6(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 1432: 
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_5(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 1412: 
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_4(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 1402: 
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_3(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 1396: 
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_2(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 1394: 
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_1(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            
            elif score0 >= 394: 
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_9(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 194: 
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_8(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 94: 
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_7(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 44: 
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_6(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 19: 
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_5(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 9: 
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_4(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 4: 
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_3(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 1: 
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_2(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            elif score0 >= 0: 
                pressed_keys = pygame.key.get_pressed()
                menu_in_use, sprite_timer, background_image1,  = Menu1.update_1(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
            
        #Cirtical Screen Stuff
        screen.blit(Menu1.surf, Menu1.rect)        
        pygame.display.flip()
        clock.tick(10)

    pygame.quit()
    sys.exit()
 
#Settings
def settings(BASE_DIR): # This needs to be fixed (have it do stuff)
    #ESSENTIAL CODE DO NOT TOUCH
    global SCREEN_HEIGHT, SCREEN_WIDTH
    global background_image1
    pygame.init()
    pygame.joystick.init()
    clock = pygame.time.Clock()
    running = True
    #variables
    hz = 24
    placeholder = "" #can be changed with no effect
    menu_choice = ""
    settings_choice = ""
    sprite_timer = 100
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
    background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Settings-2.png.png")), (SCREEN_WIDTH, SCREEN_HEIGHT))
    menu_in_use = 2

    #Create the screen object
    #The size is determined by the constant WIDTH and HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.RESIZABLE) 
    pygame.display.set_caption("Last Stand")
    
    class Menu(pygame.sprite.Sprite):
        def __init__(self):
            super(Menu, self).__init__()
            self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

        def update(self, pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR):

            if pressed_keys[K_UP] and menu_in_use > 2:
                menu_in_use -= 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", f"Settings-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            if pressed_keys[K_DOWN] and menu_in_use < 4:
                menu_in_use += 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", f"Settings-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            
            #========================  Redirect to next function  =====================#
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 2: #audio
                audio(BASE_DIR)
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 3: #music
                music(BASE_DIR)
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 4: #menu
                menu(BASE_DIR)
            return menu_in_use, sprite_timer, background_image1, 

    Menu1 = Menu()

    #GAME LOOP ITSELF
    while running:
        true = True
        for event in pygame.event.get():
            pressed_keys = pygame.key.get_pressed()
            menu_in_use, sprite_timer, background_image1,  = Menu1.update(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
             
        
        #Cirtical Screen Stuff
        screen.blit(Menu1.surf, Menu1.rect)        
        pygame.display.flip()
        clock.tick(10)

    pygame.quit()
    sys.exit()

#Audio
def audio(BASE_DIR): # This is also not in use because i also cba to fix it rn
    #ESSENTIAL CODE DO NOT TOUCH
    global SCREEN_HEIGHT, SCREEN_WIDTH
    global background_image1
    pygame.init()
    pygame.joystick.init()
    clock = pygame.time.Clock()
    running = True
    #variables
    hz = 24
    placeholder = "" #can be changed with no effect
    menu_choice = ""
    settings_choice = ""
    sprite_timer = 100
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
    background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Settings-error-1.png.png")), (SCREEN_WIDTH, SCREEN_HEIGHT))
    menu_in_use = 2

    #Create the screen object
    #The size is determined by the constant WIDTH and HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.RESIZABLE) 
    pygame.display.set_caption("Last Stand")
    
    class Menu(pygame.sprite.Sprite):
        def __init__(self):
            super(Menu, self).__init__()
            self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

        def update(self, pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR):

            
            #========================  Redirect to next function  =====================#
            if event.type == KEYDOWN and pressed_keys[K_RETURN]: #settings
                settings(BASE_DIR)
            return menu_in_use, sprite_timer, background_image1, 

    Menu1 = Menu()

    #GAME LOOP ITSELF
    while running:
        true = True
        for event in pygame.event.get():
            pressed_keys = pygame.key.get_pressed()
            menu_in_use, sprite_timer, background_image1,  = Menu1.update(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
             
        
        #Cirtical Screen Stuff
        screen.blit(Menu1.surf, Menu1.rect)        
        pygame.display.flip()
        clock.tick(10)

    pygame.quit()
    sys.exit()

#Music
def music(BASE_DIR): # This is also not in use because i also cba to fix it rn
    #ESSENTIAL CODE DO NOT TOUCH
    global SCREEN_HEIGHT, SCREEN_WIDTH
    global background_image1
    pygame.init()
    pygame.joystick.init()
    clock = pygame.time.Clock()
    running = True
    #variables
    hz = 24
    placeholder = "" #can be changed with no effect
    menu_choice = ""
    settings_choice = ""
    sprite_timer = 100
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
    background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Settings-error-2.png.png")), (SCREEN_WIDTH, SCREEN_HEIGHT))
    menu_in_use = 2

    #Create the screen object
    #The size is determined by the constant WIDTH and HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.RESIZABLE) 
    pygame.display.set_caption("Last Stand")
    
    class Menu(pygame.sprite.Sprite):
        def __init__(self):
            super(Menu, self).__init__()
            self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

        def update(self, pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR):

            
            #========================  Redirect to next function  =====================#
            if event.type == KEYDOWN and pressed_keys[K_RETURN]: #settings
                settings(BASE_DIR)
            return menu_in_use, sprite_timer, background_image1, 

    Menu1 = Menu()

    #GAME LOOP ITSELF
    while running:
        true = True
        for event in pygame.event.get():
            pressed_keys = pygame.key.get_pressed()
            menu_in_use, sprite_timer, background_image1,  = Menu1.update(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
             
        
        #Cirtical Screen Stuff
        screen.blit(Menu1.surf, Menu1.rect)        
        pygame.display.flip()
        clock.tick(10)

    pygame.quit()
    sys.exit()

#Tutorial
def tutorial(BASE_DIR):
    #ESSENTIAL CODE DO NOT TOUCH
    global SCREEN_HEIGHT, SCREEN_WIDTH
    global background_image1
    pygame.init()
    pygame.joystick.init()
    clock = pygame.time.Clock()
    running = True
    #variables
    hz = 24
    placeholder = "" #can be changed with no effect
    menu_choice = ""
    settings_choice = ""
    sprite_timer = 0
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
    background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Tutorial-1.png.png")), (SCREEN_WIDTH, SCREEN_HEIGHT))
    menu_in_use = 1

    #Create the screen object
    #The size is determined by the constant WIDTH and HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.RESIZABLE) 
    pygame.display.set_caption("Last Stand")
    
    class Menu(pygame.sprite.Sprite):
        def __init__(self):
            super(Menu, self).__init__()
            self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

        def update(self, pressed_keys, menu_in_use, sprite_timer, background_image1, ):
            
            sprite_timer += 1

            if sprite_timer == 5:
                menu_in_use = 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Tutorial-1.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            if sprite_timer == 10:
                sprite_timer = 0
                menu_in_use = 2
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Tutorial-2.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            return menu_in_use, sprite_timer, background_image1, 

    Menu1 = Menu()

    time.sleep(0.5)

    #GAME LOOP ITSELF
    while running:
        true = True
        for event in pygame.event.get():
            pressed_keys = pygame.key.get_pressed()
            if pressed_keys[K_ESCAPE]: #menu
                menu(BASE_DIR)
            
        pressed_keys = pygame.key.get_pressed()
        menu_in_use, sprite_timer, background_image1,  = Menu1.update(pressed_keys, menu_in_use, sprite_timer, background_image1, )
            
        
        #Cirtical Screen Stuff
        screen.blit(Menu1.surf, Menu1.rect)        
        pygame.display.flip()
        clock.tick(10)

    pygame.quit()
    sys.exit()

#Leaderboard
def leaderboard(BASE_DIR):
    #ESSENTIAL CODE DO NOT TOUCH
    global SCREEN_WIDTH, SCREEN_HEIGHT
    global background_image1
    pygame.init()
    pygame.joystick.init()
    clock = pygame.time.Clock()
    running = True
    #variables
    hz = 24
    placeholder = "" #can be changed with no effect
    menu_choice = ""
    settings_choice = ""
    sprite_timer = 0
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
    background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "leaderboard-1.png.png")), (SCREEN_WIDTH, SCREEN_HEIGHT))
    menu_in_use = 1

    #Create the screen object
    #The size is determined by the constant WIDTH and HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.RESIZABLE) 
    pygame.display.set_caption("Last Stand")
    
    class Menu(pygame.sprite.Sprite):
        def __init__(self):
            super(Menu, self).__init__()
            self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

    Menu1 = Menu()

    textfont = pygame.font.SysFont("spacemono", 85) 


    time.sleep(0.5)

    #GAME LOOP ITSELF
    while running:
        true = True
        for event in pygame.event.get():
            pressed_keys = pygame.key.get_pressed()
            if pressed_keys[K_RETURN]: #menu
                menu(BASE_DIR)
        
        name1_printed = textfont.render(f" {name1}", 1, (255,255,255))  
        score1_printed = textfont.render(f" {score1}", 1, (255,255,255))

        name2_printed = textfont.render(f" {name2}", 1, (255,255,255))  
        score2_printed = textfont.render(f" {score2}", 1, (255,255,255))

        name3_printed = textfont.render(f" {name3}", 1, (255,255,255))  
        score3_printed = textfont.render(f" {score3}", 1, (255,255,255))

        name4_printed = textfont.render(f" {name4}", 1, (255,255,255))  
        score4_printed = textfont.render(f" {score4}", 1, (255,255,255))

        name5_printed = textfont.render(f" {name5}", 1, (255,255,255))  
        score5_printed = textfont.render(f" {score5}", 1, (255,255,255))  

        name0_printed = textfont.render(f" {name0}", 1, (255,255,255))  
        score0_printed = textfont.render(f" {score0}", 1, (255,255,255))  

        #Cirtical Screen Stuff
        screen.blit(Menu1.surf, Menu1.rect)
        screen.blit(name1_printed,  (SCREEN_WIDTH / 2.7, SCREEN_HEIGHT / 3.27))       
        screen.blit(score1_printed, (SCREEN_WIDTH / 1.65, SCREEN_HEIGHT / 3.27))        
        screen.blit(name2_printed,  (SCREEN_WIDTH / 2.7, SCREEN_HEIGHT / 2.83))        
        screen.blit(score2_printed, (SCREEN_WIDTH / 1.65, SCREEN_HEIGHT / 2.83))        
        screen.blit(name3_printed,  (SCREEN_WIDTH / 2.7, SCREEN_HEIGHT / 2.49))        
        screen.blit(score3_printed, (SCREEN_WIDTH / 1.65, SCREEN_HEIGHT / 2.49))        
        screen.blit(name4_printed,  (SCREEN_WIDTH / 2.7, SCREEN_HEIGHT / 2.22))        
        screen.blit(score4_printed, (SCREEN_WIDTH / 1.65, SCREEN_HEIGHT / 2.22))        
        screen.blit(name5_printed,  (SCREEN_WIDTH / 2.7, SCREEN_HEIGHT / 2.00))        
        screen.blit(score5_printed, (SCREEN_WIDTH / 1.65, SCREEN_HEIGHT / 2.00))          
        screen.blit(name0_printed,  (SCREEN_WIDTH / 2.7, SCREEN_HEIGHT / 1.68))        
        screen.blit(score0_printed, (SCREEN_WIDTH / 1.65, SCREEN_HEIGHT / 1.68))     
        pygame.display.flip()
        clock.tick(10)

    pygame.quit()
    sys.exit()

#Accounts
def accounts(BASE_DIR):
    #ESSENTIAL CODE DO NOT TOUCH
    global SCREEN_WIDTH, SCREEN_HEIGHT
    global background_image1
    pygame.init()
    pygame.joystick.init()
    clock = pygame.time.Clock()
    running = True
    #variables
    hz = 24
    placeholder = "" #can be changed with no effect
    menu_choice = ""
    settings_choice = ""
    sprite_timer = 100
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
    background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Accounts-2.png.png")), (SCREEN_WIDTH, SCREEN_HEIGHT))
    menu_in_use = 1
    details_sent = False

    #Create the screen object
    #The size is determined by the constant WIDTH and HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.RESIZABLE) 
    pygame.display.set_caption("Last Stand")
    
    class Menu(pygame.sprite.Sprite):
        def __init__(self):
            super(Menu, self).__init__()
            self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2) 

    Menu1 = Menu()

    textfont = pygame.font.SysFont("spacemono", 85) 
    name = ""
    name_entered = False
    password = ""
    password_entered = False
    menu_in_use = 1
    background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Accounts-1.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    Menu1.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

    #GAME LOOP ITSELF
    while running:
        true = True
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if name_entered == False:
                    if event.key == pygame.K_BACKSPACE:
                        password = password[:-1]
                    elif event.key == pygame.K_RETURN:
                        name_entered = True
                        menu_in_use = 2
                        background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Accounts-2.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                        Menu1.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                    else:
                        name += event.unicode

                elif password_entered == False:
                    if event.key == pygame.K_BACKSPACE:
                        password = password[:-1]
                    elif event.key == pygame.K_RETURN:
                        password_entered = True
                        menu_in_use = 3
                        background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Accounts-3.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                        Menu1.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                    else:
                        password += event.unicode

                else:
                    pressed_keys = pygame.key.get_pressed()
                    if pressed_keys[K_UP] and menu_in_use > 3:
                        menu_in_use -= 1
                        background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", f"Accounts-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                        Menu1.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

                    if pressed_keys[K_DOWN] and menu_in_use < 5:
                        menu_in_use += 1
                        background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", f"Accounts-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                        Menu1.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                    
                    #========================  Redirect to next function  =====================#
                    global name0
                    global password0
                    global score0
                    global logged_in 
                    if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 3: #sign up
                        if len(name) > 0 and len(password) > 0:
                            if name != name1 and name != name2 and name != name3 and name != name4 and name != name5:
                                name0 = name 
                                password0 = password
                                score0 = 0
                                logged_in = True
                        menu(BASE_DIR)
                    if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 4: #sign in    
                        name0 = name
                        password0 = password
                        score0 = 0
                        if name0 == name1:
                            if password0 == password1:
                                score0 = int(score1)
                                logged_in = True
                        if name0 == name2:
                            if password0 == password2:
                                score0 = int(score2)
                                logged_in = True
                        if name0 == name3: 
                            if password0 == password3:
                                score0 = int(score3)
                                logged_in = True
                        if name0 == name4:
                            if password0 == password4:
                                score0 = int(score4)
                                logged_in = True
                        if name0 == name5: 
                            if password0 == password5:
                                score0 = int(score5)
                                logged_in = True
                        menu(BASE_DIR)


                    if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 5: #menu
                        menu(BASE_DIR)

        pressed_keys = pygame.key.get_pressed()
        Menu1.update(name_entered, password_entered, pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)

        name_printed = textfont.render(f" {name}", 1, (255,255,255))  
        password_printed = textfont.render(f" {password}", 1, (255,255,255))  

        #Cirtical Screen Stuff
        screen.blit(Menu1.surf, Menu1.rect) 
        screen.blit(name_printed, (SCREEN_WIDTH / 1.8, SCREEN_HEIGHT / 3.85))
        screen.blit(password_printed, (SCREEN_WIDTH / 1.8, SCREEN_HEIGHT / 3.27))

        pygame.display.flip()
        clock.tick(10)

    pygame.quit()
    sys.exit()

#Credits
def credits(BASE_DIR):
    #ESSENTIAL CODE DO NOT TOUCH
    global SCREEN_HEIGHT, SCREEN_WIDTH
    global background_image1
    pygame.init()
    pygame.joystick.init()
    clock = pygame.time.Clock()
    running = True
    #variables
    hz = 24
    placeholder = "" #can be changed with no effect
    menu_choice = ""
    settings_choice = ""
    sprite_timer = 100
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
    background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Credits-1.png.png")), (SCREEN_WIDTH, SCREEN_HEIGHT))
    menu_in_use = 1
    details_sent = False

    #Create the screen object
    #The size is determined by the constant WIDTH and HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.RESIZABLE) 
    pygame.display.set_caption("Last Stand")
    
    class Menu(pygame.sprite.Sprite):
        def __init__(self):
            super(Menu, self).__init__()
            self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

        def update(self, pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR):

            if pressed_keys[K_LEFT] and menu_in_use == 5:
                menu_in_use -= 2
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", f"Credits-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            elif pressed_keys[K_LEFT] and menu_in_use > 1:
                menu_in_use -= 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", f"Credits-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            if pressed_keys[K_RIGHT] and menu_in_use == 3:
                menu_in_use += 2
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", f"Credits-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            elif pressed_keys[K_RIGHT] and menu_in_use < 7:
                menu_in_use += 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", f"Credits-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            if pressed_keys[K_ESCAPE] and menu_in_use == 7:
                menu(BASE_DIR)
            
            return menu_in_use, sprite_timer, background_image1, 

    Menu1 = Menu()

    #GAME LOOP ITSELF
    while running:
        true = True
        for event in pygame.event.get():            
            pressed_keys = pygame.key.get_pressed()
            menu_in_use, sprite_timer, background_image1,  = Menu1.update(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
             
        
        #Cirtical Screen Stuff
        screen.blit(Menu1.surf, Menu1.rect)        
        pygame.display.flip()
        clock.tick(10)

    pygame.quit()
    sys.exit()

#Quit game
def quit_game(BASE_DIR):
    #ESSENTIAL CODE DO NOT TOUCH
    global SCREEN_HEIGHT, SCREEN_WIDTH
    global background_image1
    pygame.init()
    pygame.joystick.init()
    clock = pygame.time.Clock()
    running = True
    #variables
    hz = 24
    placeholder = "" #can be changed with no effect
    menu_choice = ""
    settings_choice = ""
    sprite_timer = 100
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
    background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Quit-1.png.png")), (SCREEN_WIDTH, SCREEN_HEIGHT))
    menu_in_use = 1
    details_sent = False

    #Create the screen object
    #The size is determined by the constant WIDTH and HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.RESIZABLE) 
    pygame.display.set_caption("Last Stand")
    
    class Menu(pygame.sprite.Sprite):
        def __init__(self):
            super(Menu, self).__init__()
            self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

        def update(self, pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR):

            if pressed_keys[K_UP]:
                menu_in_use = 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", f"Quit-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            if pressed_keys[K_DOWN]:
                menu_in_use = 2 
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", f"Quit-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 1:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 2:
                menu(BASE_DIR)
            
            return menu_in_use, sprite_timer, background_image1, 

    Menu1 = Menu()

    #GAME LOOP ITSELF
    while running:
        true = True
        for event in pygame.event.get():            
            pressed_keys = pygame.key.get_pressed()
            menu_in_use, sprite_timer, background_image1,  = Menu1.update(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
             
        
        #Cirtical Screen Stuff
        screen.blit(Menu1.surf, Menu1.rect)        
        pygame.display.flip()
        clock.tick(10)

    pygame.quit()
    sys.exit()


#Quit game
def game_to_menu(BASE_DIR):
    #ESSENTIAL CODE DO NOT TOUCH
    global SCREEN_HEIGHT, SCREEN_WIDTH
    global background_image1, running
    pygame.init()
    pygame.joystick.init()
    clock = pygame.time.Clock()
    running = True
    #variables
    hz = 24
    placeholder = "" #can be changed with no effect
    menu_choice = ""
    settings_choice = ""
    sprite_timer = 100
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
    background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Quit_game-1.png.png")), (SCREEN_WIDTH, SCREEN_HEIGHT))
    menu_in_use = 1
    run = True
    details_sent = False

    #Create the screen object
    #The size is determined by the constant WIDTH and HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.RESIZABLE) 
    pygame.display.set_caption("Last Stand")
    
    class Menu(pygame.sprite.Sprite):
        def __init__(self):
            super(Menu, self).__init__()
            self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

        def update(self, pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR):

            if pressed_keys[K_UP]:
                menu_in_use = 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", f"Quit_game-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            if pressed_keys[K_DOWN]:
                menu_in_use = 2 
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", f"Quit_game-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            return menu_in_use, sprite_timer, background_image1

    Menu1 = Menu()

    #GAME LOOP ITSELF
    while running:
        for event in pygame.event.get():            
            pressed_keys = pygame.key.get_pressed()
            menu_in_use, sprite_timer, background_image1,  = Menu1.update(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)

        pressed_keys = pygame.key.get_pressed()
        if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 1:
            menu(BASE_DIR)
        if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 2:
            running = False     
        
        #Cirtical Screen Stuff
        screen.blit(Menu1.surf, Menu1.rect)        
        pygame.display.flip()
        clock.tick(10)

#Game
def game1():
    #Game Settings
    global SCREEN_HEIGHT, SCREEN_HEIGHT
    player_speed =  SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    enemy_speed =   SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    bullet_speed =  SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    missile_speed = SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    bomb_speed =    SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    global enemy_multiplier, score0
    print(enemy_multiplier)

    enemy_strength = enemy_multiplier * 1

    #Setting Up Window and Sprites values
    WHITE = (255, 255, 255)
    sprite_gap_to_border = SCREEN_HEIGHT / 9.6
    sprite_gap_to_right = SCREEN_WIDTH / 3.95
    sprite_gap_to_left = SCREEN_WIDTH / 3.95
    player_size_w = SCREEN_WIDTH / 14.2
    player_size_h = SCREEN_HEIGHT / 5
    enemy_size_w = SCREEN_WIDTH / 17.78
    enemy_size_h = SCREEN_HEIGHT / 12.86
    bullet_size_w = SCREEN_WIDTH / 64
    bullet_size_h = SCREEN_HEIGHT / 13.58
    missile_size_w = SCREEN_WIDTH / 51.2
    missile_size_h = SCREEN_HEIGHT / 6.55
    bomb_size_w = SCREEN_WIDTH / 47
    bomb_size_h = SCREEN_HEIGHT / 10.9

    player_health = 15 +80
    enemy1_health = 1 * enemy_multiplier
    player_bullet_damage = 10
    player_missile_damage = 15
    player_bomb_damage = 35
    enemy1_bullet_damage = 1 * enemy_multiplier

    #Globilisation
    global enemy_time
    global LorR_Enemy
    global LorR_Calc
    global sprite_timer
    global bullet1_shot
    global bullet2_shot
    global missile_shot
    global bomb_shot
    global bullet1
    global bullet2
    global enemy_bullet1_shot
    global enemy_bullet2_shot
    global enemy_missile_shot
    global enemy_bomb_shot
    global enemy_bullet1
    global enemy_bullet2


    enemy_time = random.randint(45, 50) 
    LorR_Enemy = random.choice([1, 100])
    LorR_Calc = random.randint(0, 100)
    sprite_timer = 100

    #ESSENTIAL CODE DO NOT TOUCH
    pygame.init()
    clock = pygame.time.Clock()
    running = True
    bullet1_shot = False
    bullet2_shot = False 
    missile_shot = False
    bomb_shot = False
    enemy_bullet1_shot = False
    enemy_bullet2_shot = False 
    enemy_missile_shot = False
    enemy_bomb_shot = False
    explode_true = False
    deadP = True


    #Create the screen object
    #The size is determined by the constant WIDTH and HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.RESIZABLE)
    textfont = pygame.font.SysFont("monospace", 50) 
    pygame.display.set_caption("Last Stand")

    class Player(pygame.sprite.Sprite):
        def __init__(self):
            super(Player, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame1.png")).convert(),
                (player_size_w, player_size_h))
            self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT - player_size_h/2 - sprite_gap_to_border)

        # Move the sprite based on user keypresses
        def update(self, pressed_keys):

            global enemy_time, LorR_Enemy, LorR_Calc, sprite_timer

            if sprite_timer == 100:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame1.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            
            elif sprite_timer == 80:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame2.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            
            elif sprite_timer == 60:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame3.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            
            elif sprite_timer == 40:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame4.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)

            elif sprite_timer == 20:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame5.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)

            if pressed_keys[K_w]:
                self.rect.move_ip(0, -player_speed)
            if pressed_keys[K_s]:
                self.rect.move_ip(0, player_speed)
            if pressed_keys[K_a]:
                self.rect.move_ip(-player_speed, 0)
            if pressed_keys[K_d]:
                self.rect.move_ip(player_speed, 0)
            
            # Keep player on the screen
            if self.rect.left < sprite_gap_to_left:
                self.rect.left = sprite_gap_to_left
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH

            if self.rect.top <= SCREEN_HEIGHT - player_size_h*1.5 - sprite_gap_to_border*2:
                self.rect.top = SCREEN_HEIGHT - player_size_h*1.5 - sprite_gap_to_border*2
            if self.rect.bottom >= SCREEN_HEIGHT-5:
                self.rect.bottom = SCREEN_HEIGHT-5

    class Bullet(pygame.sprite.Sprite):

        def __init__(self):
            super(Bullet, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame1.png")).convert(),
                (bullet_size_w, bullet_size_h))
            self.surf.set_colorkey((255, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (player.rect.x  + player_size_h/2, player.rect.y + bullet_size_h/2)   

        def update(self):
            
            global sprite_timer, bullet1_shot, bullet2_shot

            if sprite_timer == 100:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame1.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            elif sprite_timer == 80:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame2.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            elif sprite_timer == 60:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame3.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            elif sprite_timer == 40:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame4.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            elif sprite_timer == 20:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame5.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if bullet1_shot == True:
                bullet1.rect.move_ip(0, -bullet_speed)
            if bullet1_shot == False:
                bullet1.rect.x = (player.rect.x+33)
                bullet1.rect.y = (player.rect.y)
                bullet1.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if bullet1.rect.bottom <= 0:
                bullet1_shot = False

            if bullet2_shot == True:
                bullet2.rect.move_ip(0, -bullet_speed)
            if bullet2_shot == False:
                bullet2.rect.x = (player.rect.x+33)
                bullet2.rect.y = (player.rect.y)
                bullet2.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if bullet2.rect.bottom <= 0:
                bullet2_shot = False
    class Missile(pygame.sprite.Sprite):

        def __init__(self):
            super(Missile, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame1.png")).convert(),
                (missile_size_w, missile_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (player.rect.x  + player_size_h/2, player.rect.y + missile_size_h/2)   

        def update(self):
            
            global sprite_timer, missile_shot

            if missile_shot == True:
                missile1.rect.move_ip(0, -missile_speed)

                if sprite_timer == 100:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame1.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame2.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame3.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame4.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame5.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if missile_shot == False:
                missile1.rect.x = (player.rect.x + 30)
                missile1.rect.y = (player.rect.y)
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (missile_size_w, missile_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if missile1.rect.bottom <= 0:
                missile_shot = False
    class Bomb(pygame.sprite.Sprite):

        def __init__(self):
            super(Bomb, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame1.png")).convert(),
                (bomb_size_w, bomb_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (player.rect.x  + player_size_h/2, player.rect.y + bomb_size_h/2)   

        def update(self):
            
            global sprite_timer, bomb_shot

            if bomb_shot == True:
                bomb1.rect.move_ip(0, -bomb_speed)

                if sprite_timer == 100:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame1.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                if sprite_timer == 80:
                    self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame1.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                if sprite_timer == 60:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame3.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                if sprite_timer == 40:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame4.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                if sprite_timer == 20:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame5.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if bomb_shot == False:
                bomb1.rect.x = (player.rect.x + 32)
                bomb1.rect.top = (player.rect.top)

                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (missile_size_w, missile_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if bomb1.rect.bottom <= 0:
                bomb_shot = False

    class Enemy(pygame.sprite.Sprite):

        def __init__(self):
            super(Enemy, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 1", "1", "Frame1.png")).convert(),
                (enemy_size_w, enemy_size_h))
            self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, enemy_size_h/2 + sprite_gap_to_border)

        def update(self):
            
            global enemy_time, LorR_Enemy, LorR_Calc, sprite_timer

            if sprite_timer == 100:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 1", "1", "Frame1.png")).convert(),
                    (enemy_size_w, enemy_size_h))
                self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            
            elif sprite_timer == 75:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 1", "1", "Frame2.png")).convert(),
                    (enemy_size_w, enemy_size_h))
                self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            
            elif sprite_timer == 50:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 1", "1", "Frame3.png")).convert(),
                    (enemy_size_w, enemy_size_h))
                self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            
            elif sprite_timer == 25:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 1", "1", "Frame4.png")).convert(),
                    (enemy_size_w, enemy_size_h))
                self.surf.set_colorkey((255, 0, 255), RLEACCEL)

            

            #Enemy Movement
            if enemy_time > 0:
                enemy_time -= 1

                #timer runs out
                if LorR_Enemy >= LorR_Calc:  
                    self.rect.move_ip(-enemy_speed, 0)   #left
                elif LorR_Enemy < LorR_Calc: 
                    self.rect.move_ip(enemy_speed, 0)   #right

            else:
                #Reset
                enemy_time = random.randint(25, 30)
                LorR_Enemy = (enemy1.rect.x - 241.5) / 1437 * 100
                
                #1920 - 483 = 1437

                LorR_Calc = random.randint(0, 100) 
                
            # Keep enemy on the screen
            if self.rect.left < sprite_gap_to_left:
                self.rect.left = sprite_gap_to_left
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH

            if self.rect.top <= 0:
                self.rect.top = 0
            if self.rect.bottom >= SCREEN_HEIGHT:
                self.rect.bottom = SCREEN_HEIGHT

    class Enemy_Bullet(pygame.sprite.Sprite):

        def __init__(self):
            super(Enemy_Bullet, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (bullet_size_w, bullet_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.x = (enemy1.rect.x+25)
            self.rect.y = (enemy1.rect.y)

        def update(self):
            
            global sprite_timer, enemy_bullet1_shot, enemy_bullet2_shot
            
            if enemy_bullet1.rect.top >= SCREEN_HEIGHT:
                enemy_bullet1_shot = False
                enemy_bullet1.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                enemy_bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if enemy_bullet2.rect.top >= SCREEN_HEIGHT:
                enemy_bullet2_shot = False
                enemy_bullet2.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                enemy_bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)

            if enemy_bullet1_shot == True:
                enemy_bullet1.rect.move_ip(0, +bullet_speed)
                if sprite_timer == 100:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame1.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame2.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame3.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame4.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame5.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)
            if enemy_bullet2_shot == True:
                enemy_bullet2.rect.move_ip(0, +bullet_speed)
                if sprite_timer == 100:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame1.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame2.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame3.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame4.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame5.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if enemy_bullet1_shot == False:
                enemy_bullet1.rect.x = (enemy1.rect.x+25)
                enemy_bullet1.rect.y = (enemy1.rect.y)   
                enemy_bullet1.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                enemy_bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)      
            if enemy_bullet2_shot == False:
                enemy_bullet2.rect.x = (enemy1.rect.x+25)
                enemy_bullet2.rect.y = (enemy1.rect.y)  
                enemy_bullet2.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                enemy_bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)           

    class Explode(pygame.sprite.Sprite):

        def __init__(self):
            super(Explode, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH, SCREEN_HEIGHT)   

        def update(self):
            
            global sprite_timer, explode_true

            explode_sleep = 0.05

            bullet1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            bullet2.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)
            missile1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            missile1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            bomb1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            bomb1.surf.set_colorkey((0, 255, 255), RLEACCEL)

            enemy_bullet1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            enemy_bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            enemy_bullet2.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            enemy_bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)




            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-1.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-2.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-3.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-4.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-5.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-6.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-7.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-8.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-9.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-10.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-11.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-12.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-13.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-14.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            if deadP == True:
                player.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (150, 150))
                player.surf.set_colorkey((0, 255, 255), RLEACCEL)
            elif deadP == False:
                enemy1.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (150, 150))
                enemy1.surf.set_colorkey((0, 255, 255), RLEACCEL)

            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-15.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-16.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-17.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-18.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-19.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-20.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-21.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-22.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-23.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-24.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
    class Game_over(pygame.sprite.Sprite):

        def __init__(self):
            super(Game_over, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)    

        def update(self):

            explode_sleep = 0.05
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over--1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(1.2)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-0.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(0.14)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over--1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(0.7)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-0.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(1.2)

            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-2.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-3.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-4.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-5.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-6.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-7.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-8.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-9.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-10.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-11.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-12.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-13.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-14.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-15.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-16.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-17.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-18.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-19.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-20.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-21.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()

            menu(BASE_DIR)   
    class Success(pygame.sprite.Sprite):

        def __init__(self):
            super(Success, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)    

        def update(self):

            explode_sleep = 0.05
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(1.2)

            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-2.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-3.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-4.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-5.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-6.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-7.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-8.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-9.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-10.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-11.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-12.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-13.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-14.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-15.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-16.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-17.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-18.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-19.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-20.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-21.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-22.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-23.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-24.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-25.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-26.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()

            menu(BASE_DIR)   


    """    """

    explode1 = Explode()
    game_over = Game_over()
    success = Success()
    #space = Space()

    # Instantiate sprites
    player = Player()

    bullet1 = Bullet()
    bullet2 = Bullet()
    missile1 = Missile()
    bomb1 = Bomb()

    enemy1 = Enemy()

    enemy_bullet1 = Enemy_Bullet()
    enemy_bullet2 = Enemy_Bullet()

    #Groups
    players = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    missiles = pygame.sprite.Group()
    bombs = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()

    players.add(player
                )
    enemies.add(enemy1,
                )
    bullets.add(bullet1,
                bullet2
                )
    missiles.add(missile1
                 )
    bombs.add(bomb1
              )
    enemy_bullets.add(enemy_bullet1,
                enemy_bullet2
                )
    all_sprites.add(
                    bullet1,
                    bullet2,
                    missile1,
                    bomb1, 
                    enemy_bullet1,
                    enemy_bullet2,
                    player, 
                    enemy1,
                    explode1,
                    game_over,
                    success
                    )
    
    bullet_delay_time = 0
    bullet_delay_base = 20
    missile_delay_time = 0
    missile_delay_base = 75
    bomb_delay_time = 0
    bomb_delay_base = 75

    enemy_bullet_delay_time = 0
    enemy_bullet_delay_base = 20
    enemy_missile_delay_time = 0
    enemy_missile_delay_base = 75
    enemy_bomb_delay_time = 0
    enemy_bomb_delay_base = 75

    def bullets_updating():
        bullet1.update()
        bullet2.update()

    #GAME LOOP ITSELF
    while running:
        true = True
        for event in pygame.event.get():            
            if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                game_to_menu(BASE_DIR)

        # Get all the keys currently pressed
        pressed_keys = pygame.key.get_pressed()
        Thread1 = threading.Thread(player.update(pressed_keys))
        Thread2 = threading.Thread(enemy1.update())
        Thread3 = threading.Thread(target = bullets_updating)
        Thread5 = threading.Thread(missile1.update())
        Thread6 = threading.Thread(bomb1.update())
        Thread7 = threading.Thread(enemy_bullet1.update())
        Thread8 = threading.Thread(enemy_bullet2.update())

        Thread1.start()
        Thread2.start()
        Thread3.start()
        Thread5.start()
        Thread6.start()
        Thread7.start()
        Thread8.start()

        
        if sprite_timer == 0:
            sprite_timer = 100 
        else:
            sprite_timer -= 5

        #Kills player bullets
        if pygame.sprite.spritecollideany(bullet1, enemies):
            bullet1_shot = False
            enemy1_health -= player_bullet_damage
        if pygame.sprite.spritecollideany(bullet2, enemies):
            bullet2_shot = False
            enemy1_health -= player_bullet_damage
        if pygame.sprite.spritecollideany(missile1, enemies):
            missile_shot = False
            enemy1_health -= player_missile_damage
        if pygame.sprite.spritecollideany(bomb1, enemies):
            bomb_shot = False
            enemy1_health -= player_bomb_damage
        #Kills enemy bullets
        if pygame.sprite.spritecollideany(enemy_bullet1, players):
            enemy_bullet1_shot = False
            player_health -= enemy1_bullet_damage
        if pygame.sprite.spritecollideany(enemy_bullet2, players):
            enemy_bullet2_shot = False
            player_health -= enemy1_bullet_damage
    
        #Kills player
        if player_health <= 0:
            player.kill()
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            explode1.rect.center = player.rect.center
            deadP = True
            explode1.update()
            time.sleep(1.5)
            game_over.update()
            score0 += 10 * enemy_multiplier
            next_level(BASE_DIR)
        
        #kills enemy
        if enemy1_health <= 0:
            if pygame.sprite.spritecollideany(enemy1, bullets):
                enemy1.kill()
                screen.blit(background_image, (0, 0))
                for entity in all_sprites:
                    screen.blit(entity.surf, entity.rect)
                pygame.display.flip()
                explode1.rect.center = enemy1.rect.center
                deadP = False
                explode1.update()
                time.sleep(1.5)
                success.update()
                score0 += enemy_strength
                menu(BASE_DIR)
            if pygame.sprite.spritecollideany(enemy1, missiles):
                enemy1.kill()
                screen.blit(background_image, (0, 0))
                for entity in all_sprites:
                    screen.blit(entity.surf, entity.rect)
                pygame.display.flip()
                explode1.rect.center = enemy1.rect.center
                deadP = False
                explode1.update()
                time.sleep(1.5)
                success.update()
                score0 += enemy_strength
                menu(BASE_DIR)
            if pygame.sprite.spritecollideany(enemy1, bombs):
                enemy1.kill()
                screen.blit(background_image, (0, 0))
                for entity in all_sprites:
                    screen.blit(entity.surf, entity.rect)
                pygame.display.flip()
                explode1.rect.center = enemy1.rect.center
                deadP = False
                explode1.update()
                time.sleep(1.5)
                success.update()
                score0 += enemy_strength
                menu(BASE_DIR)

        enemy_bullet_chance = random.randint(1,50)
        enemy_missile_chance = random.randint(1,50)
        enemy_bomb_chance = random.randint(1,50)

        if enemy_bullet_chance == 5:
            if enemy_bullet_delay_time <= 0:
                if enemy_bullet1_shot == False:
                    enemy_bullet1_shot = True
                    enemy_bullet_delay_time = enemy_bullet_delay_base
                elif enemy_bullet1_shot and enemy_bullet2_shot == False:
                    enemy_bullet2_shot = True
                    enemy_bullet_delay_time = enemy_bullet_delay_base

        if enemy_missile_chance == 5:
            if enemy_missile_delay_time <= 0:
                if enemy_missile_shot == False:
                    enemy_missile_shot = True
                    enemy_missile_delay_time = enemy_missile_delay_base

        if enemy_bomb_chance == 5:
            if enemy_bomb_delay_time <= 0:
                if enemy_bomb_shot == False:
                    enemy_bomb_shot = True
                    enemy_bomb_delay_time = enemy_bomb_delay_base
        

        enemy_bullet_delay_time -= 2
        enemy_missile_delay_time -= 2
        enemy_bomb_delay_time -= 2

        pressed_keys = pygame.key.get_pressed()
        mouse_button = pygame.mouse.get_pressed()

        if mouse_button[0]:
            if bullet_delay_time <= 0:
                if bullet1_shot == False:
                    bullet1_shot = True
                    bullet_delay_time = bullet_delay_base
                elif bullet1_shot and bullet2_shot == False:
                    bullet2_shot = True
                    bullet_delay_time = bullet_delay_base

        if mouse_button[2]:
            if missile_delay_time <= 0:
                if missile_shot == False:
                    missile_shot = True
                    missile_delay_time = missile_delay_base

        if pressed_keys[K_SPACE]:
            if bomb_delay_time <= 0:
                if bomb_shot == False:
                    bomb_shot = True
                    bomb_delay_time = bomb_delay_base
        
        bullet_delay_time -= 2
        missile_delay_time -= 2
        bomb_delay_time -= 2

        Health_Player = textfont.render(f" {player_health}", 1, (255,255,255))
        Health_Enemy = textfont.render(f" {enemy1_health}", 1, (255,255,255))

        
        #space.update() idk if i like this or if it can be made to be perfect in near future

        Thread1.join()
        Thread2.join()
        Thread3.join()
        Thread5.join()
        Thread6.join()
        Thread7.join()
        Thread8.join()

        #Cirtical Screen Stuff
        screen.blit(background_image, (0, 0))
        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)
        screen.blit(Health_Player, (60, 175))
        screen.blit(Health_Enemy, (60, 500))
        pygame.display.flip()
        clock.tick(hz)

    pygame.quit()
    sys.exit()
def game2():
    #Game Settings
    global SCREEN_HEIGHT, SCREEN_HEIGHT
    player_speed =  SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    enemy_speed =   SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    bullet_speed =  SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    missile_speed = SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    bomb_speed =    SCREEN_HEIGHT * SCREEN_WIDTH / 120000

    enemy_strength = enemy_multiplier * 1

    #Setting Up Window and Sprites values
    WHITE = (255, 255, 255)
    sprite_gap_to_border = SCREEN_HEIGHT / 9.6
    sprite_gap_to_right = SCREEN_WIDTH / 3.95
    sprite_gap_to_left = SCREEN_WIDTH / 3.95
    player_size_w = SCREEN_WIDTH / 14.2
    player_size_h = SCREEN_HEIGHT / 5
    enemy_size_w = 80 #20 18 = 
    enemy_size_h = 44
     #11 14 = 
    bullet_size_w = SCREEN_WIDTH / 64
    bullet_size_h = SCREEN_HEIGHT / 13.58
    missile_size_w = SCREEN_WIDTH / 51.2
    missile_size_h = SCREEN_HEIGHT / 6.55
    bomb_size_w = SCREEN_WIDTH / 47
    bomb_size_h = SCREEN_HEIGHT / 10.9

    player_health = 15 +80
    enemy1_health = 3 * enemy_multiplier
    player_bullet_damage = 10
    player_missile_damage = 15
    player_bomb_damage = 35
    enemy1_bullet_damage = 2 * enemy_multiplier

    #Globilisation
    global enemy_time
    global LorR_Enemy
    global LorR_Calc
    global sprite_timer
    global bullet1_shot
    global bullet2_shot
    global missile_shot
    global bomb_shot
    global bullet1
    global bullet2
    global enemy_bullet1_shot
    global enemy_bullet2_shot
    global enemy_missile_shot
    global enemy_bomb_shot
    global enemy_bullet1
    global enemy_bullet2


    enemy_time = random.randint(45, 50) 
    LorR_Enemy = random.choice([1, 100])
    LorR_Calc = random.randint(0, 100)
    sprite_timer = 100

    #ESSENTIAL CODE DO NOT TOUCH
    pygame.init()
    clock = pygame.time.Clock()
    running = True
    bullet1_shot = False
    bullet2_shot = False 
    missile_shot = False
    bomb_shot = False
    enemy_bullet1_shot = False
    enemy_bullet2_shot = False 
    enemy_missile_shot = False
    enemy_bomb_shot = False
    explode_true = False
    deadP = True


    #Create the screen object
    #The size is determined by the constant WIDTH and HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.RESIZABLE)
    textfont = pygame.font.SysFont("monospace", 50) 
    pygame.display.set_caption("Last Stand")


    class Player(pygame.sprite.Sprite):
        def __init__(self):
            super(Player, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame1.png")).convert(),
                (player_size_w, player_size_h))
            self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT - player_size_h/2 - sprite_gap_to_border)

        # Move the sprite based on user keypresses
        def update(self, pressed_keys):

            global enemy_time, LorR_Enemy, LorR_Calc, sprite_timer

            if sprite_timer == 100:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame1.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            
            elif sprite_timer == 80:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame2.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            
            elif sprite_timer == 60:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame3.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            
            elif sprite_timer == 40:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame4.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)

            elif sprite_timer == 20:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame5.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)

            if pressed_keys[K_w]:
                self.rect.move_ip(0, -player_speed)
            if pressed_keys[K_s]:
                self.rect.move_ip(0, player_speed)
            if pressed_keys[K_a]:
                self.rect.move_ip(-player_speed, 0)
            if pressed_keys[K_d]:
                self.rect.move_ip(player_speed, 0)
            
            # Keep player on the screen
            if self.rect.left < sprite_gap_to_left:
                self.rect.left = sprite_gap_to_left
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH

            if self.rect.top <= SCREEN_HEIGHT - player_size_h*1.5 - sprite_gap_to_border*2:
                self.rect.top = SCREEN_HEIGHT - player_size_h*1.5 - sprite_gap_to_border*2
            if self.rect.bottom >= SCREEN_HEIGHT-5:
                self.rect.bottom = SCREEN_HEIGHT-5

    class Bullet(pygame.sprite.Sprite):

        def __init__(self):
            super(Bullet, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame1.png")).convert(),
                (bullet_size_w, bullet_size_h))
            self.surf.set_colorkey((255, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (player.rect.x  + player_size_h/2, player.rect.y + bullet_size_h/2)   

        def update(self):
            
            global sprite_timer, bullet1_shot, bullet2_shot

            if sprite_timer == 100:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame1.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            elif sprite_timer == 80:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame2.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            elif sprite_timer == 60:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame3.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            elif sprite_timer == 40:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame4.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            elif sprite_timer == 20:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame5.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if bullet1_shot == True:
                bullet1.rect.move_ip(0, -bullet_speed)
            if bullet1_shot == False:
                bullet1.rect.x = (player.rect.x+33)
                bullet1.rect.y = (player.rect.y)
                bullet1.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if bullet1.rect.bottom <= 0:
                bullet1_shot = False

            if bullet2_shot == True:
                bullet2.rect.move_ip(0, -bullet_speed)
            if bullet2_shot == False:
                bullet2.rect.x = (player.rect.x+33)
                bullet2.rect.y = (player.rect.y)
                bullet2.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if bullet2.rect.bottom <= 0:
                bullet2_shot = False
    class Missile(pygame.sprite.Sprite):

        def __init__(self):
            super(Missile, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame1.png")).convert(),
                (missile_size_w, missile_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (player.rect.x  + player_size_h/2, player.rect.y + missile_size_h/2)   

        def update(self):
            
            global sprite_timer, missile_shot

            if missile_shot == True:
                missile1.rect.move_ip(0, -missile_speed)

                if sprite_timer == 100:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame1.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame2.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame3.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame4.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame5.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if missile_shot == False:
                missile1.rect.x = (player.rect.x + 30)
                missile1.rect.y = (player.rect.y)
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (missile_size_w, missile_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if missile1.rect.bottom <= 0:
                missile_shot = False
    class Bomb(pygame.sprite.Sprite):

        def __init__(self):
            super(Bomb, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame1.png")).convert(),
                (bomb_size_w, bomb_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (player.rect.x  + player_size_h/2, player.rect.y + bomb_size_h/2)   

        def update(self):
            
            global sprite_timer, bomb_shot

            if bomb_shot == True:
                bomb1.rect.move_ip(0, -bomb_speed)

                if sprite_timer == 100:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame1.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                if sprite_timer == 80:
                    self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame1.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                if sprite_timer == 60:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame3.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                if sprite_timer == 40:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame4.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                if sprite_timer == 20:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame5.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if bomb_shot == False:
                bomb1.rect.x = (player.rect.x + 32)
                bomb1.rect.top = (player.rect.top)

                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (missile_size_w, missile_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if bomb1.rect.bottom <= 0:
                bomb_shot = False

    class Enemy(pygame.sprite.Sprite):

        def __init__(self):
            super(Enemy, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 1", "2", "Frame1.png")).convert(),
                (enemy_size_w, enemy_size_h))
            self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, enemy_size_h/2 + sprite_gap_to_border)

        def update(self):
            
            global enemy_time, LorR_Enemy, LorR_Calc, sprite_timer

            if sprite_timer == 100:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 1", "2", "Frame1.png")).convert(),
                    (enemy_size_w, enemy_size_h))
                self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            
            elif sprite_timer == 75:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 1", "2", "Frame2.png")).convert(),
                    (enemy_size_w, enemy_size_h))
                self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            
            elif sprite_timer == 50:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 1", "2", "Frame3.png")).convert(),
                    (enemy_size_w, enemy_size_h))
                self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            
            elif sprite_timer == 25:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 1", "2", "Frame4.png")).convert(),
                    (enemy_size_w, enemy_size_h))
                self.surf.set_colorkey((255, 0, 255), RLEACCEL)

            

            #Enemy Movement
            if enemy_time > 0:
                enemy_time -= 1

                #timer runs out
                if LorR_Enemy >= LorR_Calc:  
                    self.rect.move_ip(-enemy_speed, 0)   #left
                elif LorR_Enemy < LorR_Calc: 
                    self.rect.move_ip(enemy_speed, 0)   #right

            else:
                #Reset
                enemy_time = random.randint(25, 30)
                LorR_Enemy = (enemy1.rect.x - 241.5) / 1437 * 100
                
                #1920 - 483 = 1437

                LorR_Calc = random.randint(0, 100) 
                
            # Keep enemy on the screen
            if self.rect.left < sprite_gap_to_left:
                self.rect.left = sprite_gap_to_left
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH

            if self.rect.top <= 0:
                self.rect.top = 0
            if self.rect.bottom >= SCREEN_HEIGHT:
                self.rect.bottom = SCREEN_HEIGHT

    class Enemy_Bullet(pygame.sprite.Sprite):

        def __init__(self):
            super(Enemy_Bullet, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (bullet_size_w, bullet_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.x = (enemy1.rect.x+25)
            self.rect.y = (enemy1.rect.y)

        def update(self):
            
            global sprite_timer, enemy_bullet1_shot, enemy_bullet2_shot
            
            if enemy_bullet1.rect.top >= SCREEN_HEIGHT:
                enemy_bullet1_shot = False
                enemy_bullet1.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                enemy_bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if enemy_bullet2.rect.top >= SCREEN_HEIGHT:
                enemy_bullet2_shot = False
                enemy_bullet2.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                enemy_bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)

            if enemy_bullet1_shot == True:
                enemy_bullet1.rect.move_ip(0, +bullet_speed)
                if sprite_timer == 100:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame1.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame2.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame3.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame4.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame5.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)
            if enemy_bullet2_shot == True:
                enemy_bullet2.rect.move_ip(0, +bullet_speed)
                if sprite_timer == 100:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame1.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame2.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame3.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame4.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame5.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if enemy_bullet1_shot == False:
                enemy_bullet1.rect.x = (enemy1.rect.x+25)
                enemy_bullet1.rect.y = (enemy1.rect.y)   
                enemy_bullet1.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                enemy_bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)      
            if enemy_bullet2_shot == False:
                enemy_bullet2.rect.x = (enemy1.rect.x+25)
                enemy_bullet2.rect.y = (enemy1.rect.y)  
                enemy_bullet2.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                enemy_bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)           
    
    class Explode(pygame.sprite.Sprite):

        def __init__(self):
            super(Explode, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH, SCREEN_HEIGHT)   

        def update(self):
            
            global sprite_timer, explode_true

            explode_sleep = 0.05

            bullet1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            bullet2.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)
            missile1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            missile1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            bomb1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            bomb1.surf.set_colorkey((0, 255, 255), RLEACCEL)

            enemy_bullet1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            enemy_bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            enemy_bullet2.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            enemy_bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)


            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-1.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-2.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-3.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-4.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-5.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-6.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-7.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-8.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-9.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-10.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-11.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-12.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-13.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-14.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            if deadP == True:
                player.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (150, 150))
                player.surf.set_colorkey((0, 255, 255), RLEACCEL)
            elif deadP == False:
                enemy1.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (150, 150))
                enemy1.surf.set_colorkey((0, 255, 255), RLEACCEL)

            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-15.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-16.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-17.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-18.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-19.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-20.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-21.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-22.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-23.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-24.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
    class Game_over(pygame.sprite.Sprite):

        def __init__(self):
            super(Game_over, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)    

        def update(self):

            explode_sleep = 0.05
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over--1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(1.2)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-0.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(0.14)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over--1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(0.7)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-0.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(1.2)

            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-2.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-3.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-4.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-5.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-6.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-7.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-8.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-9.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-10.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-11.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-12.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-13.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-14.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-15.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-16.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-17.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-18.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-19.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-20.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-21.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()

            menu(BASE_DIR)   
    class Success(pygame.sprite.Sprite):

        def __init__(self):
            super(Success, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)    

        def update(self):

            explode_sleep = 0.05
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(1.2)

            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-2.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-3.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-4.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-5.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-6.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-7.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-8.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-9.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-10.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-11.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-12.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-13.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-14.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-15.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-16.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-17.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-18.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-19.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-20.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-21.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-22.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-23.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-24.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-25.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-26.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()

            menu(BASE_DIR)   


    explode1 = Explode()
    game_over = Game_over()
    success = Success()

    # Instantiate sprites
    player = Player()

    bullet1 = Bullet()
    bullet2 = Bullet()
    missile1 = Missile()
    bomb1 = Bomb()

    enemy1 = Enemy()

    enemy_bullet1 = Enemy_Bullet()
    enemy_bullet2 = Enemy_Bullet()

    #Groups
    players = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    missiles = pygame.sprite.Group()
    bombs = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()

    players.add(player
                )
    enemies.add(enemy1,
                )
    bullets.add(bullet1,
                bullet2
                )
    missiles.add(missile1
                 )
    bombs.add(bomb1
              )
    enemy_bullets.add(enemy_bullet1,
                enemy_bullet2
                )
    all_sprites.add(bullet1,
                    bullet2,
                    missile1,
                    bomb1, 
                    enemy_bullet1,
                    enemy_bullet2,
                    player, 
                    enemy1,
                    explode1,
                    game_over,
                    success
                    )
    
    bullet_delay_time = 0
    bullet_delay_base = 20
    missile_delay_time = 0
    missile_delay_base = 75
    bomb_delay_time = 0
    bomb_delay_base = 75

    enemy_bullet_delay_time = 0
    enemy_bullet_delay_base = 20

    def bullets_updating():
        bullet1.update()
        bullet2.update()

    #GAME LOOP ITSELF
    while running:
        true = True
        for event in pygame.event.get():            
            if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                game_to_menu(BASE_DIR)

        # Get all the keys currently pressed
        pressed_keys = pygame.key.get_pressed()
        Thread1 = threading.Thread(player.update(pressed_keys))
        Thread2 = threading.Thread(enemy1.update())
        Thread3 = threading.Thread(target = bullets_updating)
        Thread5 = threading.Thread(missile1.update())
        Thread6 = threading.Thread(bomb1.update())
        Thread7 = threading.Thread(enemy_bullet1.update())
        Thread8 = threading.Thread(enemy_bullet2.update())

        Thread1.start()
        Thread2.start()
        Thread3.start()
        Thread5.start()
        Thread6.start()
        Thread7.start()
        Thread8.start()

        
        if sprite_timer == 0:
            sprite_timer = 100 
        else:
            sprite_timer -= 5

        #Kills player bullets
        if pygame.sprite.spritecollideany(bullet1, enemies):
            bullet1_shot = False
            enemy1_health -= player_bullet_damage
        if pygame.sprite.spritecollideany(bullet2, enemies):
            bullet2_shot = False
            enemy1_health -= player_bullet_damage
        if pygame.sprite.spritecollideany(missile1, enemies):
            missile_shot = False
            enemy1_health -= player_missile_damage
        if pygame.sprite.spritecollideany(bomb1, enemies):
            bomb_shot = False
            enemy1_health -= player_bomb_damage
        #Kills enemy bullets
        if pygame.sprite.spritecollideany(enemy_bullet1, players):
            enemy_bullet1_shot = False
            player_health -= enemy1_bullet_damage
        if pygame.sprite.spritecollideany(enemy_bullet2, players):
            enemy_bullet2_shot = False
            player_health -= enemy1_bullet_damage
    
        #Kills player
        if player_health <= 0:
            player.kill()
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            explode1.rect.center = player.rect.center
            deadP = True
            explode1.update()
            time.sleep(1.5)
            game_over.update()
            score0 += 20 * enemy_multiplier
            next_level(BASE_DIR)
        
        #kills enemy
        if enemy1_health <= 0:
            if pygame.sprite.spritecollideany(enemy1, bullets):
                enemy1.kill()
                screen.blit(background_image, (0, 0))
                for entity in all_sprites:
                    screen.blit(entity.surf, entity.rect)
                pygame.display.flip()
                explode1.rect.center = enemy1.rect.center
                deadP = False
                explode1.update()
                time.sleep(1.5)
                success.update()
                score0 += enemy_strength
                menu(BASE_DIR)
            if pygame.sprite.spritecollideany(enemy1, missiles):
                enemy1.kill()
                screen.blit(background_image, (0, 0))
                for entity in all_sprites:
                    screen.blit(entity.surf, entity.rect)
                pygame.display.flip()
                explode1.rect.center = enemy1.rect.center
                deadP = False
                explode1.update()
                time.sleep(1.5)
                success.update()
                score0 += enemy_strength
                menu(BASE_DIR)
            if pygame.sprite.spritecollideany(enemy1, bombs):
                enemy1.kill()
                screen.blit(background_image, (0, 0))
                for entity in all_sprites:
                    screen.blit(entity.surf, entity.rect)
                pygame.display.flip()
                explode1.rect.center = enemy1.rect.center
                deadP = False
                explode1.update()
                time.sleep(1.5)
                success.update()
                score0 += enemy_strength
                menu(BASE_DIR)

        enemy_bullet_chance = random.randint(1,50)
        enemy_missile_chance = random.randint(1,50)
        enemy_bomb_chance = random.randint(1,50)

        if enemy_bullet_chance == 5:
            if enemy_bullet_delay_time <= 0:
                if enemy_bullet1_shot == False:
                    enemy_bullet1_shot = True
                    enemy_bullet_delay_time = enemy_bullet_delay_base
                elif enemy_bullet1_shot and enemy_bullet2_shot == False:
                    enemy_bullet2_shot = True
                    enemy_bullet_delay_time = enemy_bullet_delay_base

        

        enemy_bullet_delay_time -= 2

        pressed_keys = pygame.key.get_pressed()
        mouse_button = pygame.mouse.get_pressed()

        if mouse_button[0]:
            if bullet_delay_time <= 0:
                if bullet1_shot == False:
                    bullet1_shot = True
                    bullet_delay_time = bullet_delay_base
                elif bullet1_shot and bullet2_shot == False:
                    bullet2_shot = True
                    bullet_delay_time = bullet_delay_base

        if mouse_button[2]:
            if missile_delay_time <= 0:
                if missile_shot == False:
                    missile_shot = True
                    missile_delay_time = missile_delay_base

        if pressed_keys[K_SPACE]:
            if bomb_delay_time <= 0:
                if bomb_shot == False:
                    bomb_shot = True
                    bomb_delay_time = bomb_delay_base
        
        bullet_delay_time -= 2
        missile_delay_time -= 2
        bomb_delay_time -= 2

        Health_Player = textfont.render(f" {player_health}", 1, (255,255,255))
        Health_Enemy = textfont.render(f" {enemy1_health}", 1, (255,255,255))

        
        #space.update() idk if i like this or if it can be made to be perfect in near future

        Thread1.join()
        Thread2.join()
        Thread3.join()
        Thread5.join()
        Thread6.join()
        Thread7.join()
        Thread8.join()

        #Cirtical Screen Stuff
        screen.blit(background_image, (0, 0))
        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)
        screen.blit(Health_Player, (60, 175))
        screen.blit(Health_Enemy, (60, 500))
        pygame.display.flip()
        clock.tick(hz)

    pygame.quit()
    sys.exit()
def game3():
    #Game Settings
    global SCREEN_HEIGHT, SCREEN_HEIGHT
    player_speed =  SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    enemy_speed =   SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    bullet_speed =  SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    missile_speed = SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    bomb_speed =    SCREEN_HEIGHT * SCREEN_WIDTH / 120000

    enemy_strength = enemy_multiplier * 1

    #Setting Up Window and Sprites values
    WHITE = (255, 255, 255)
    sprite_gap_to_border = SCREEN_HEIGHT / 9.6
    sprite_gap_to_right = SCREEN_WIDTH / 3.95
    sprite_gap_to_left = SCREEN_WIDTH / 3.95
    player_size_w = SCREEN_WIDTH / 14.2
    player_size_h = SCREEN_HEIGHT / 5
    enemy_size_w = 14*5.5
    enemy_size_h = 24*5.5
    bullet_size_w = SCREEN_WIDTH / 64
    bullet_size_h = SCREEN_HEIGHT / 13.58
    missile_size_w = SCREEN_WIDTH / 51.2
    missile_size_h = SCREEN_HEIGHT / 6.55
    bomb_size_w = SCREEN_WIDTH / 47
    bomb_size_h = SCREEN_HEIGHT / 10.9

    player_health = 15 +80
    enemy1_health = 5 * enemy_multiplier
    player_bullet_damage = 10
    player_missile_damage = 15
    player_bomb_damage = 35
    enemy1_bullet_damage = 3 * enemy_multiplier
    enemy1_missile_damage = 5 * enemy_multiplier 

    #Globilisation
    global enemy_time
    global LorR_Enemy
    global LorR_Calc
    global sprite_timer
    global bullet1_shot
    global bullet2_shot
    global missile_shot
    global bomb_shot
    global bullet1
    global bullet2
    global enemy_bullet1_shot
    global enemy_bullet2_shot
    global enemy_missile_shot
    global enemy_bullet1
    global enemy_bullet2


    enemy_time = random.randint(45, 50) 
    LorR_Enemy = random.choice([1, 100])
    LorR_Calc = random.randint(0, 100)
    sprite_timer = 100

    #ESSENTIAL CODE DO NOT TOUCH
    pygame.init()
    clock = pygame.time.Clock()
    running = True
    bullet1_shot = False
    bullet2_shot = False 
    missile_shot = False
    bomb_shot = False
    enemy_bullet1_shot = False
    enemy_bullet2_shot = False 
    enemy_missile_shot = False
    explode_true = False
    deadP = True


    #Create the screen object
    #The size is determined by the constant WIDTH and HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.RESIZABLE)
    textfont = pygame.font.SysFont("monospace", 50) 
    pygame.display.set_caption("Last Stand")

    class Player(pygame.sprite.Sprite):
        def __init__(self):
            super(Player, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame1.png")).convert(),
                (player_size_w, player_size_h))
            self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT - player_size_h/2 - sprite_gap_to_border)

        # Move the sprite based on user keypresses
        def update(self, pressed_keys):

            global enemy_time, LorR_Enemy, LorR_Calc, sprite_timer

            if sprite_timer == 100:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame1.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            
            elif sprite_timer == 80:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame2.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            
            elif sprite_timer == 60:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame3.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            
            elif sprite_timer == 40:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame4.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)

            elif sprite_timer == 20:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame5.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)

            if pressed_keys[K_w]:
                self.rect.move_ip(0, -player_speed)
            if pressed_keys[K_s]:
                self.rect.move_ip(0, player_speed)
            if pressed_keys[K_a]:
                self.rect.move_ip(-player_speed, 0)
            if pressed_keys[K_d]:
                self.rect.move_ip(player_speed, 0)
            
            # Keep player on the screen
            if self.rect.left < sprite_gap_to_left:
                self.rect.left = sprite_gap_to_left
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH

            if self.rect.top <= SCREEN_HEIGHT - player_size_h*1.5 - sprite_gap_to_border*2:
                self.rect.top = SCREEN_HEIGHT - player_size_h*1.5 - sprite_gap_to_border*2
            if self.rect.bottom >= SCREEN_HEIGHT-5:
                self.rect.bottom = SCREEN_HEIGHT-5

    class Bullet(pygame.sprite.Sprite):

        def __init__(self):
            super(Bullet, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame1.png")).convert(),
                (bullet_size_w, bullet_size_h))
            self.surf.set_colorkey((255, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (player.rect.x  + player_size_h/2, player.rect.y + bullet_size_h/2)   

        def update(self):
            
            global sprite_timer, bullet1_shot, bullet2_shot

            if sprite_timer == 100:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame1.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            elif sprite_timer == 80:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame2.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            elif sprite_timer == 60:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame3.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            elif sprite_timer == 40:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame4.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            elif sprite_timer == 20:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame5.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if bullet1_shot == True:
                bullet1.rect.move_ip(0, -bullet_speed)
            if bullet1_shot == False:
                bullet1.rect.x = (player.rect.x+33)
                bullet1.rect.y = (player.rect.y)
                bullet1.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if bullet1.rect.bottom <= 0:
                bullet1_shot = False

            if bullet2_shot == True:
                bullet2.rect.move_ip(0, -bullet_speed)
            if bullet2_shot == False:
                bullet2.rect.x = (player.rect.x+33)
                bullet2.rect.y = (player.rect.y)
                bullet2.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if bullet2.rect.bottom <= 0:
                bullet2_shot = False
    class Missile(pygame.sprite.Sprite):

        def __init__(self):
            super(Missile, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame1.png")).convert(),
                (missile_size_w, missile_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (player.rect.x  + player_size_h/2, player.rect.y + missile_size_h/2)   

        def update(self):
            
            global sprite_timer, missile_shot

            if missile_shot == True:
                missile1.rect.move_ip(0, -missile_speed)

                if sprite_timer == 100:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame1.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame2.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame3.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame4.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame5.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if missile_shot == False:
                missile1.rect.x = (player.rect.x + 30)
                missile1.rect.y = (player.rect.y)
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (missile_size_w, missile_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if missile1.rect.bottom <= 0:
                missile_shot = False
    class Bomb(pygame.sprite.Sprite):

        def __init__(self):
            super(Bomb, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame1.png")).convert(),
                (bomb_size_w, bomb_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (player.rect.x  + player_size_h/2, player.rect.y + bomb_size_h/2)   

        def update(self):
            
            global sprite_timer, bomb_shot

            if bomb_shot == True:
                bomb1.rect.move_ip(0, -bomb_speed)

                if sprite_timer == 100:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame1.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                if sprite_timer == 80:
                    self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame1.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                if sprite_timer == 60:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame3.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                if sprite_timer == 40:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame4.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                if sprite_timer == 20:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame5.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if bomb_shot == False:
                bomb1.rect.x = (player.rect.x + 32)
                bomb1.rect.top = (player.rect.top)

                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (missile_size_w, missile_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if bomb1.rect.bottom <= 0:
                bomb_shot = False

    class Enemy(pygame.sprite.Sprite):

        def __init__(self):
            super(Enemy, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 2", "3", "Frame1.png")).convert(),
                (enemy_size_w, enemy_size_h))
            self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, enemy_size_h/2 + sprite_gap_to_border)

        def update(self):
            
            global enemy_time, LorR_Enemy, LorR_Calc, sprite_timer

            if sprite_timer == 100:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 2", "3", "Frame1.png")).convert(),
                    (enemy_size_w, enemy_size_h))
                self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            
            elif sprite_timer == 75:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 2", "3", "Frame2.png")).convert(),
                    (enemy_size_w, enemy_size_h))
                self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            
            elif sprite_timer == 50:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 2", "3", "Frame3.png")).convert(),
                    (enemy_size_w, enemy_size_h))
                self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            
            elif sprite_timer == 25:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 2", "3", "Frame4.png")).convert(),
                    (enemy_size_w, enemy_size_h))
                self.surf.set_colorkey((255, 0, 255), RLEACCEL)

            

            #Enemy Movement
            if enemy_time > 0:
                enemy_time -= 1

                #timer runs out
                if LorR_Enemy >= LorR_Calc:  
                    self.rect.move_ip(-enemy_speed, 0)   #left
                elif LorR_Enemy < LorR_Calc: 
                    self.rect.move_ip(enemy_speed, 0)   #right

            else:
                #Reset
                enemy_time = random.randint(25, 30)
                LorR_Enemy = (enemy1.rect.x - 241.5) / 1437 * 100
                
                #1920 - 483 = 1437

                LorR_Calc = random.randint(0, 100) 
                
            # Keep enemy on the screen
            if self.rect.left < sprite_gap_to_left:
                self.rect.left = sprite_gap_to_left
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH

            if self.rect.top <= 0:
                self.rect.top = 0
            if self.rect.bottom >= SCREEN_HEIGHT:
                self.rect.bottom = SCREEN_HEIGHT

    class Enemy_Bullet(pygame.sprite.Sprite):

        def __init__(self):
            super(Enemy_Bullet, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (bullet_size_w, bullet_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.x = (enemy1.rect.x+25)
            self.rect.y = (enemy1.rect.y)

        def update(self):
            
            global sprite_timer, enemy_bullet1_shot, enemy_bullet2_shot
            
            if enemy_bullet1.rect.top >= SCREEN_HEIGHT:
                enemy_bullet1_shot = False
                enemy_bullet1.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                enemy_bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if enemy_bullet2.rect.top >= SCREEN_HEIGHT:
                enemy_bullet2_shot = False
                enemy_bullet2.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                enemy_bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)

            if enemy_bullet1_shot == True:
                enemy_bullet1.rect.move_ip(0, +bullet_speed)
                if sprite_timer == 100:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame1.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame2.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame3.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame4.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame5.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)
            if enemy_bullet2_shot == True:
                enemy_bullet2.rect.move_ip(0, +bullet_speed)
                if sprite_timer == 100:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame1.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame2.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame3.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame4.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame5.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if enemy_bullet1_shot == False:
                enemy_bullet1.rect.x = (enemy1.rect.x+25)
                enemy_bullet1.rect.y = (enemy1.rect.y)   
                enemy_bullet1.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                enemy_bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)      
            if enemy_bullet2_shot == False:
                enemy_bullet2.rect.x = (enemy1.rect.x+25)
                enemy_bullet2.rect.y = (enemy1.rect.y)  
                enemy_bullet2.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                enemy_bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)           
    class Enemy_Missile(pygame.sprite.Sprite):

        def __init__(self):
            super(Enemy_Missile, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (missile_size_w, missile_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.x = (enemy1.rect.x + 24)
            self.rect.bottom = (enemy1.rect.top)     

        def update(self):
            
            global sprite_timer, enemy_missile_shot

            if enemy_missile_shot == True:
                enemy_missile1.rect.move_ip(0, +missile_speed)

                if sprite_timer == 100:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Missiles", "Frame1.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Missiles", "Frame2.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Missiles", "Frame3.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Missiles", "Frame4.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Missiles", "Frame5.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if enemy_missile_shot == False:
                enemy_missile1.rect.x = (enemy1.rect.x + 24)
                enemy_missile1.rect.bottom = (enemy1.rect.top)
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (missile_size_w, missile_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
                
            if enemy_missile1.rect.top >= SCREEN_HEIGHT:
                enemy_missile_shot = False
    
    class Explode(pygame.sprite.Sprite):

        def __init__(self):
            super(Explode, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH, SCREEN_HEIGHT)   

        def update(self):
            
            global sprite_timer, explode_true

            explode_sleep = 0.05

            bullet1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            bullet2.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)
            missile1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            missile1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            bomb1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            bomb1.surf.set_colorkey((0, 255, 255), RLEACCEL)

            enemy_bullet1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            enemy_bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            enemy_bullet2.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            enemy_bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)
            enemy_missile1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            enemy_missile1.surf.set_colorkey((0, 255, 255), RLEACCEL)


            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-1.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-2.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-3.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-4.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-5.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-6.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-7.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-8.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-9.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-10.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-11.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-12.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-13.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-14.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            if deadP == True:
                player.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (150, 150))
                player.surf.set_colorkey((0, 255, 255), RLEACCEL)
            elif deadP == False:
                enemy1.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (150, 150))
                enemy1.surf.set_colorkey((0, 255, 255), RLEACCEL)

            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-15.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-16.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-17.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-18.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-19.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-20.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-21.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-22.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-23.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-24.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
    class Game_over(pygame.sprite.Sprite):

        def __init__(self):
            super(Game_over, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)    

        def update(self):

            explode_sleep = 0.05
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over--1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(1.2)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-0.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(0.14)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over--1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(0.7)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-0.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(1.2)

            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-2.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-3.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-4.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-5.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-6.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-7.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-8.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-9.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-10.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-11.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-12.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-13.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-14.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-15.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-16.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-17.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-18.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-19.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-20.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-21.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()

            menu(BASE_DIR)   
    class Success(pygame.sprite.Sprite):

        def __init__(self):
            super(Success, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)    

        def update(self):

            explode_sleep = 0.05
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(1.2)

            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-2.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-3.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-4.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-5.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-6.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-7.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-8.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-9.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-10.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-11.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-12.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-13.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-14.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-15.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-16.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-17.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-18.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-19.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-20.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-21.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-22.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-23.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-24.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-25.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-26.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()

            menu(BASE_DIR)   


    explode1 = Explode()
    game_over = Game_over()
    success = Success()

    # Instantiate sprites
    player = Player()

    bullet1 = Bullet()
    bullet2 = Bullet()
    missile1 = Missile()
    bomb1 = Bomb()

    enemy1 = Enemy()

    enemy_bullet1 = Enemy_Bullet()
    enemy_bullet2 = Enemy_Bullet()
    enemy_missile1 = Enemy_Missile()

    #Groups
    players = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    missiles = pygame.sprite.Group()
    bombs = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    enemy_missiles = pygame.sprite.Group()
    enemy_bombs = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()

    players.add(player
                )
    enemies.add(enemy1,
                )
    bullets.add(bullet1,
                bullet2
                )
    missiles.add(missile1
                 )
    bombs.add(bomb1
              )
    enemy_bullets.add(enemy_bullet1,
                enemy_bullet2
                )
    enemy_missiles.add(enemy_missile1
                 )
    all_sprites.add(bullet1,
                    bullet2,
                    missile1,
                    bomb1, 
                    enemy_bullet1,
                    enemy_bullet2,
                    enemy_missile1,
                    player, 
                    enemy1,
                    explode1,
                    game_over,
                    success
                    )
    
    bullet_delay_time = 0
    bullet_delay_base = 20
    missile_delay_time = 0
    missile_delay_base = 75
    bomb_delay_time = 0
    bomb_delay_base = 75

    enemy_bullet_delay_time = 0
    enemy_bullet_delay_base = 20
    enemy_missile_delay_time = 0
    enemy_missile_delay_base = 75

    def bullets_updating():
        bullet1.update()
        bullet2.update()

    #GAME LOOP ITSELF
    while running:
        true = True
        for event in pygame.event.get():            
            if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                game_to_menu(BASE_DIR)

        # Get all the keys currently pressed
        pressed_keys = pygame.key.get_pressed()
        Thread1 = threading.Thread(player.update(pressed_keys))
        Thread2 = threading.Thread(enemy1.update())
        Thread3 = threading.Thread(target = bullets_updating)
        Thread5 = threading.Thread(missile1.update())
        Thread6 = threading.Thread(bomb1.update())
        Thread7 = threading.Thread(enemy_bullet1.update())
        Thread8 = threading.Thread(enemy_bullet2.update())
        Thread9 = threading.Thread(enemy_missile1.update())

        Thread1.start()
        Thread2.start()
        Thread3.start()
        Thread5.start()
        Thread6.start()
        Thread7.start()
        Thread8.start()
        Thread9.start()

        
        if sprite_timer == 0:
            sprite_timer = 100 
        else:
            sprite_timer -= 5

        #Kills player bullets
        if pygame.sprite.spritecollideany(bullet1, enemies):
            bullet1_shot = False
            enemy1_health -= player_bullet_damage
        if pygame.sprite.spritecollideany(bullet2, enemies):
            bullet2_shot = False
            enemy1_health -= player_bullet_damage
        if pygame.sprite.spritecollideany(missile1, enemies):
            missile_shot = False
            enemy1_health -= player_missile_damage
        if pygame.sprite.spritecollideany(bomb1, enemies):
            bomb_shot = False
            enemy1_health -= player_bomb_damage
        #Kills enemy bullets
        if pygame.sprite.spritecollideany(enemy_bullet1, players):
            enemy_bullet1_shot = False
            player_health -= enemy1_bullet_damage
        if pygame.sprite.spritecollideany(enemy_bullet2, players):
            enemy_bullet2_shot = False
            player_health -= enemy1_bullet_damage
        if pygame.sprite.spritecollideany(enemy_missile1, players):
            enemy_missile_shot = False
            player_health -= enemy1_missile_damage
        
    
        #Kills player
        if player_health <= 0:
            player.kill()
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            explode1.rect.center = player.rect.center
            deadP = True
            explode1.update()
            time.sleep(1.5)
            game_over.update()
            score0 += 40 * enemy_multiplier
            next_level(BASE_DIR)            
        
        #kills enemy
        if enemy1_health <= 0:
            if pygame.sprite.spritecollideany(enemy1, bullets):
                enemy1.kill()
                screen.blit(background_image, (0, 0))
                for entity in all_sprites:
                    screen.blit(entity.surf, entity.rect)
                pygame.display.flip()
                explode1.rect.center = enemy1.rect.center
                deadP = False
                explode1.update()
                time.sleep(1.5)
                success.update()
                score0 += enemy_strength
                menu(BASE_DIR)
            if pygame.sprite.spritecollideany(enemy1, missiles):
                enemy1.kill()
                screen.blit(background_image, (0, 0))
                for entity in all_sprites:
                    screen.blit(entity.surf, entity.rect)
                pygame.display.flip()
                explode1.rect.center = enemy1.rect.center
                deadP = False
                explode1.update()
                time.sleep(1.5)
                success.update()
                score0 += enemy_strength
                menu(BASE_DIR)
            if pygame.sprite.spritecollideany(enemy1, bombs):
                enemy1.kill()
                screen.blit(background_image, (0, 0))
                for entity in all_sprites:
                    screen.blit(entity.surf, entity.rect)
                pygame.display.flip()
                explode1.rect.center = enemy1.rect.center
                deadP = False
                explode1.update()
                time.sleep(1.5)
                success.update()
                score0 += enemy_strength
                menu(BASE_DIR)

        enemy_bullet_chance = random.randint(1,50)
        enemy_missile_chance = random.randint(1,50)

        if enemy_bullet_chance == 5:
            if enemy_bullet_delay_time <= 0:
                if enemy_bullet1_shot == False:
                    enemy_bullet1_shot = True
                    enemy_bullet_delay_time = enemy_bullet_delay_base
                elif enemy_bullet1_shot and enemy_bullet2_shot == False:
                    enemy_bullet2_shot = True
                    enemy_bullet_delay_time = enemy_bullet_delay_base

        if enemy_missile_chance == 5:
            if enemy_missile_delay_time <= 0:
                if enemy_missile_shot == False:
                    enemy_missile_shot = True
                    enemy_missile_delay_time = enemy_missile_delay_base


        enemy_bullet_delay_time -= 2
        enemy_missile_delay_time -= 2

        pressed_keys = pygame.key.get_pressed()
        mouse_button = pygame.mouse.get_pressed()

        if mouse_button[0]:
            if bullet_delay_time <= 0:
                if bullet1_shot == False:
                    bullet1_shot = True
                    bullet_delay_time = bullet_delay_base
                elif bullet1_shot and bullet2_shot == False:
                    bullet2_shot = True
                    bullet_delay_time = bullet_delay_base

        if mouse_button[2]:
            if missile_delay_time <= 0:
                if missile_shot == False:
                    missile_shot = True
                    missile_delay_time = missile_delay_base

        if pressed_keys[K_SPACE]:
            if bomb_delay_time <= 0:
                if bomb_shot == False:
                    bomb_shot = True
                    bomb_delay_time = bomb_delay_base
        
        bullet_delay_time -= 2
        missile_delay_time -= 2
        bomb_delay_time -= 2

        Health_Player = textfont.render(f" {player_health}", 1, (255,255,255))
        Health_Enemy = textfont.render(f" {enemy1_health}", 1, (255,255,255))

        
        #space.update() idk if i like this or if it can be made to be perfect in near future

        Thread1.join()
        Thread2.join()
        Thread3.join()
        Thread5.join()
        Thread6.join()
        Thread7.join()
        Thread8.join()
        Thread9.join()

        #Cirtical Screen Stuff
        screen.blit(background_image, (0, 0))
        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)
        screen.blit(Health_Player, (60, 175))
        screen.blit(Health_Enemy, (60, 500))
        pygame.display.flip()
        clock.tick(hz)

    pygame.quit()
    sys.exit()
def game4():
    #Game Settings
    global SCREEN_HEIGHT, SCREEN_HEIGHT
    player_speed =  SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    enemy_speed =   SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    bullet_speed =  SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    missile_speed = SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    bomb_speed =    SCREEN_HEIGHT * SCREEN_WIDTH / 120000

    enemy_strength = enemy_multiplier * 1

    #Setting Up Window and Sprites values
    WHITE = (255, 255, 255)
    sprite_gap_to_border = SCREEN_HEIGHT / 9.6
    sprite_gap_to_right = SCREEN_WIDTH / 3.95
    sprite_gap_to_left = SCREEN_WIDTH / 3.95
    player_size_w = SCREEN_WIDTH / 14.2
    player_size_h = SCREEN_HEIGHT / 5
    enemy_size_w = 5.5*26
    enemy_size_h = 5.5*15
    bullet_size_w = SCREEN_WIDTH / 64
    bullet_size_h = SCREEN_HEIGHT / 13.58
    missile_size_w = SCREEN_WIDTH / 51.2
    missile_size_h = SCREEN_HEIGHT / 6.55
    bomb_size_w = SCREEN_WIDTH / 47
    bomb_size_h = SCREEN_HEIGHT / 10.9

    player_health = 15 +80
    enemy1_health = 10 * enemy_multiplier
    player_bullet_damage = 10
    player_missile_damage = 15
    player_bomb_damage = 35
    enemy1_bullet_damage = 5 * enemy_multiplier
    enemy1_missile_damage = 10 * enemy_multiplier 

    #Globilisation
    global enemy_time
    global LorR_Enemy
    global LorR_Calc
    global sprite_timer
    global bullet1_shot
    global bullet2_shot
    global missile_shot
    global bomb_shot
    global bullet1
    global bullet2
    global enemy_bullet1_shot
    global enemy_bullet2_shot
    global enemy_missile_shot
    global enemy_bullet1
    global enemy_bullet2


    enemy_time = random.randint(45, 50) 
    LorR_Enemy = random.choice([1, 100])
    LorR_Calc = random.randint(0, 100)
    sprite_timer = 100

    #ESSENTIAL CODE DO NOT TOUCH
    pygame.init()
    clock = pygame.time.Clock()
    running = True
    bullet1_shot = False
    bullet2_shot = False 
    missile_shot = False
    bomb_shot = False
    enemy_bullet1_shot = False
    enemy_bullet2_shot = False 
    enemy_missile_shot = False
    enemy_bomb_shot = False
    explode_true = False
    deadP = True


    #Create the screen object
    #The size is determined by the constant WIDTH and HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.RESIZABLE)
    textfont = pygame.font.SysFont("monospace", 50) 
    pygame.display.set_caption("Last Stand")


    class Player(pygame.sprite.Sprite):
        def __init__(self):
            super(Player, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame1.png")).convert(),
                (player_size_w, player_size_h))
            self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT - player_size_h/2 - sprite_gap_to_border)

        # Move the sprite based on user keypresses
        def update(self, pressed_keys):

            global enemy_time, LorR_Enemy, LorR_Calc, sprite_timer

            if sprite_timer == 100:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame1.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            
            elif sprite_timer == 80:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame2.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            
            elif sprite_timer == 60:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame3.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            
            elif sprite_timer == 40:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame4.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)

            elif sprite_timer == 20:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame5.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)

            if pressed_keys[K_w]:
                self.rect.move_ip(0, -player_speed)
            if pressed_keys[K_s]:
                self.rect.move_ip(0, player_speed)
            if pressed_keys[K_a]:
                self.rect.move_ip(-player_speed, 0)
            if pressed_keys[K_d]:
                self.rect.move_ip(player_speed, 0)
            
            # Keep player on the screen
            if self.rect.left < sprite_gap_to_left:
                self.rect.left = sprite_gap_to_left
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH

            if self.rect.top <= SCREEN_HEIGHT - player_size_h*1.5 - sprite_gap_to_border*2:
                self.rect.top = SCREEN_HEIGHT - player_size_h*1.5 - sprite_gap_to_border*2
            if self.rect.bottom >= SCREEN_HEIGHT-5:
                self.rect.bottom = SCREEN_HEIGHT-5

    class Bullet(pygame.sprite.Sprite):

        def __init__(self):
            super(Bullet, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame1.png")).convert(),
                (bullet_size_w, bullet_size_h))
            self.surf.set_colorkey((255, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (player.rect.x  + player_size_h/2, player.rect.y + bullet_size_h/2)   

        def update(self):
            
            global sprite_timer, bullet1_shot, bullet2_shot

            if sprite_timer == 100:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame1.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            elif sprite_timer == 80:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame2.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            elif sprite_timer == 60:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame3.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            elif sprite_timer == 40:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame4.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            elif sprite_timer == 20:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame5.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if bullet1_shot == True:
                bullet1.rect.move_ip(0, -bullet_speed)
            if bullet1_shot == False:
                bullet1.rect.x = (player.rect.x+33)
                bullet1.rect.y = (player.rect.y)
                bullet1.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if bullet1.rect.bottom <= 0:
                bullet1_shot = False

            if bullet2_shot == True:
                bullet2.rect.move_ip(0, -bullet_speed)
            if bullet2_shot == False:
                bullet2.rect.x = (player.rect.x+33)
                bullet2.rect.y = (player.rect.y)
                bullet2.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if bullet2.rect.bottom <= 0:
                bullet2_shot = False
    class Missile(pygame.sprite.Sprite):

        def __init__(self):
            super(Missile, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame1.png")).convert(),
                (missile_size_w, missile_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (player.rect.x  + player_size_h/2, player.rect.y + missile_size_h/2)   

        def update(self):
            
            global sprite_timer, missile_shot

            if missile_shot == True:
                missile1.rect.move_ip(0, -missile_speed)

                if sprite_timer == 100:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame1.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame2.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame3.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame4.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame5.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if missile_shot == False:
                missile1.rect.x = (player.rect.x + 30)
                missile1.rect.y = (player.rect.y)
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (missile_size_w, missile_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if missile1.rect.bottom <= 0:
                missile_shot = False
    class Bomb(pygame.sprite.Sprite):

        def __init__(self):
            super(Bomb, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame1.png")).convert(),
                (bomb_size_w, bomb_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (player.rect.x  + player_size_h/2, player.rect.y + bomb_size_h/2)   

        def update(self):
            
            global sprite_timer, bomb_shot

            if bomb_shot == True:
                bomb1.rect.move_ip(0, -bomb_speed)

                if sprite_timer == 100:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame1.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                if sprite_timer == 80:
                    self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame1.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                if sprite_timer == 60:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame3.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                if sprite_timer == 40:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame4.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                if sprite_timer == 20:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame5.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if bomb_shot == False:
                bomb1.rect.x = (player.rect.x + 32)
                bomb1.rect.top = (player.rect.top)

                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (missile_size_w, missile_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if bomb1.rect.bottom <= 0:
                bomb_shot = False

    class Enemy(pygame.sprite.Sprite):

        def __init__(self):
            super(Enemy, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 2", "4", "Frame1.png")).convert(),
                (enemy_size_w, enemy_size_h))
            self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, enemy_size_h/2 + sprite_gap_to_border)

        def update(self):
            
            global enemy_time, LorR_Enemy, LorR_Calc, sprite_timer

            if sprite_timer == 100:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 2", "4", "Frame1.png")).convert(),
                    (enemy_size_w, enemy_size_h))
                self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            
            elif sprite_timer == 75:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 2", "4", "Frame2.png")).convert(),
                    (enemy_size_w, enemy_size_h))
                self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            
            elif sprite_timer == 50:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 2", "4", "Frame3.png")).convert(),
                    (enemy_size_w, enemy_size_h))
                self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            
            elif sprite_timer == 25:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 2", "4", "Frame4.png")).convert(),
                    (enemy_size_w, enemy_size_h))
                self.surf.set_colorkey((255, 0, 255), RLEACCEL)

            

            #Enemy Movement
            if enemy_time > 0:
                enemy_time -= 1

                #timer runs out
                if LorR_Enemy >= LorR_Calc:  
                    self.rect.move_ip(-enemy_speed, 0)   #left
                elif LorR_Enemy < LorR_Calc: 
                    self.rect.move_ip(enemy_speed, 0)   #right

            else:
                #Reset
                enemy_time = random.randint(25, 30)
                LorR_Enemy = (enemy1.rect.x - 241.5) / 1437 * 100
                
                #1920 - 483 = 1437

                LorR_Calc = random.randint(0, 100) 
                
            # Keep enemy on the screen
            if self.rect.left < sprite_gap_to_left:
                self.rect.left = sprite_gap_to_left
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH

            if self.rect.top <= 0:
                self.rect.top = 0
            if self.rect.bottom >= SCREEN_HEIGHT:
                self.rect.bottom = SCREEN_HEIGHT

    class Enemy_Bullet(pygame.sprite.Sprite):

        def __init__(self):
            super(Enemy_Bullet, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (bullet_size_w, bullet_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.x = (enemy1.rect.x+25)
            self.rect.y = (enemy1.rect.y)

        def update(self):
            
            global sprite_timer, enemy_bullet1_shot, enemy_bullet2_shot
            
            if enemy_bullet1.rect.top >= SCREEN_HEIGHT:
                enemy_bullet1_shot = False
                enemy_bullet1.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                enemy_bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if enemy_bullet2.rect.top >= SCREEN_HEIGHT:
                enemy_bullet2_shot = False
                enemy_bullet2.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                enemy_bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)

            if enemy_bullet1_shot == True:
                enemy_bullet1.rect.move_ip(0, +bullet_speed)
                if sprite_timer == 100:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame1.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame2.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame3.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame4.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame5.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)
            if enemy_bullet2_shot == True:
                enemy_bullet2.rect.move_ip(0, +bullet_speed)
                if sprite_timer == 100:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame1.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame2.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame3.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame4.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame5.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if enemy_bullet1_shot == False:
                enemy_bullet1.rect.x = (enemy1.rect.x+25)
                enemy_bullet1.rect.y = (enemy1.rect.y)   
                enemy_bullet1.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                enemy_bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)      
            if enemy_bullet2_shot == False:
                enemy_bullet2.rect.x = (enemy1.rect.x+25)
                enemy_bullet2.rect.y = (enemy1.rect.y)  
                enemy_bullet2.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                enemy_bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)           
    class Enemy_Missile(pygame.sprite.Sprite):

        def __init__(self):
            super(Enemy_Missile, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (missile_size_w, missile_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.x = (enemy1.rect.x + 24)
            self.rect.bottom = (enemy1.rect.top)     

        def update(self):
            
            global sprite_timer, enemy_missile_shot

            if enemy_missile_shot == True:
                enemy_missile1.rect.move_ip(0, +missile_speed)

                if sprite_timer == 100:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Missiles", "Frame1.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Missiles", "Frame2.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Missiles", "Frame3.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Missiles", "Frame4.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Missiles", "Frame5.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if enemy_missile_shot == False:
                enemy_missile1.rect.x = (enemy1.rect.x + 24)
                enemy_missile1.rect.bottom = (enemy1.rect.top)
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (missile_size_w, missile_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
                
            if enemy_missile1.rect.top >= SCREEN_HEIGHT:
                enemy_missile_shot = False
    
    class Explode(pygame.sprite.Sprite):

        def __init__(self):
            super(Explode, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH, SCREEN_HEIGHT)   

        def update(self):
            
            global sprite_timer, explode_true

            explode_sleep = 0.05

            bullet1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            bullet2.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)
            missile1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            missile1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            bomb1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            bomb1.surf.set_colorkey((0, 255, 255), RLEACCEL)

            enemy_bullet1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            enemy_bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            enemy_bullet2.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            enemy_bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)
            enemy_missile1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            enemy_missile1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            


            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-1.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-2.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-3.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-4.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-5.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-6.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-7.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-8.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-9.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-10.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-11.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-12.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-13.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-14.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            if deadP == True:
                player.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (150, 150))
                player.surf.set_colorkey((0, 255, 255), RLEACCEL)
            elif deadP == False:
                enemy1.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (150, 150))
                enemy1.surf.set_colorkey((0, 255, 255), RLEACCEL)

            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-15.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-16.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-17.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-18.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-19.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-20.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-21.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-22.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-23.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-24.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
    class Game_over(pygame.sprite.Sprite):

        def __init__(self):
            super(Game_over, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)    

        def update(self):

            explode_sleep = 0.05
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over--1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(1.2)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-0.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(0.14)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over--1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(0.7)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-0.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(1.2)

            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-2.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-3.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-4.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-5.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-6.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-7.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-8.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-9.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-10.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-11.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-12.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-13.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-14.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-15.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-16.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-17.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-18.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-19.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-20.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-21.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()

            menu(BASE_DIR)   
    class Success(pygame.sprite.Sprite):

        def __init__(self):
            super(Success, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)    

        def update(self):

            explode_sleep = 0.05
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(1.2)

            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-2.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-3.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-4.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-5.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-6.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-7.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-8.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-9.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-10.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-11.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-12.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-13.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-14.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-15.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-16.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-17.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-18.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-19.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-20.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-21.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-22.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-23.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-24.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-25.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-26.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()

            menu(BASE_DIR)   


    explode1 = Explode()
    game_over = Game_over()
    success = Success()

    # Instantiate sprites
    player = Player()

    bullet1 = Bullet()
    bullet2 = Bullet()
    missile1 = Missile()
    bomb1 = Bomb()

    enemy1 = Enemy()

    enemy_bullet1 = Enemy_Bullet()
    enemy_bullet2 = Enemy_Bullet()
    enemy_missile1 = Enemy_Missile()

    #Groups
    players = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    missiles = pygame.sprite.Group()
    bombs = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    enemy_missiles = pygame.sprite.Group()
    enemy_bombs = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()

    players.add(player
                )
    enemies.add(enemy1,
                )
    bullets.add(bullet1,
                bullet2
                )
    missiles.add(missile1
                 )
    bombs.add(bomb1
              )
    enemy_bullets.add(enemy_bullet1,
                enemy_bullet2
                )
    enemy_missiles.add(enemy_missile1
                 )
    all_sprites.add(bullet1,
                    bullet2,
                    missile1,
                    bomb1, 
                    enemy_bullet1,
                    enemy_bullet2,
                    enemy_missile1,
                    player, 
                    enemy1,
                    explode1,
                    game_over,
                    success
                    )
    
    bullet_delay_time = 0
    bullet_delay_base = 20
    missile_delay_time = 0
    missile_delay_base = 75
    bomb_delay_time = 0
    bomb_delay_base = 75

    enemy_bullet_delay_time = 0
    enemy_bullet_delay_base = 20
    enemy_missile_delay_time = 0
    enemy_missile_delay_base = 75
    enemy_bomb_delay_time = 0
    enemy_bomb_delay_base = 75

    def bullets_updating():
        bullet1.update()
        bullet2.update()

    #GAME LOOP ITSELF
    while running:
        true = True
        for event in pygame.event.get():            
            if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                game_to_menu(BASE_DIR)

        # Get all the keys currently pressed
        pressed_keys = pygame.key.get_pressed()
        Thread1 = threading.Thread(player.update(pressed_keys))
        Thread2 = threading.Thread(enemy1.update())
        Thread3 = threading.Thread(target = bullets_updating)
        Thread5 = threading.Thread(missile1.update())
        Thread6 = threading.Thread(bomb1.update())
        Thread7 = threading.Thread(enemy_bullet1.update())
        Thread8 = threading.Thread(enemy_bullet2.update())
        Thread9 = threading.Thread(enemy_missile1.update())

        Thread1.start()
        Thread2.start()
        Thread3.start()
        Thread5.start()
        Thread6.start()
        Thread7.start()
        Thread8.start()
        Thread9.start()

        
        if sprite_timer == 0:
            sprite_timer = 100 
        else:
            sprite_timer -= 5

        #Kills player bullets
        if pygame.sprite.spritecollideany(bullet1, enemies):
            bullet1_shot = False
            enemy1_health -= player_bullet_damage
        if pygame.sprite.spritecollideany(bullet2, enemies):
            bullet2_shot = False
            enemy1_health -= player_bullet_damage
        if pygame.sprite.spritecollideany(missile1, enemies):
            missile_shot = False
            enemy1_health -= player_missile_damage
        if pygame.sprite.spritecollideany(bomb1, enemies):
            bomb_shot = False
            enemy1_health -= player_bomb_damage
        #Kills enemy bullets
        if pygame.sprite.spritecollideany(enemy_bullet1, players):
            enemy_bullet1_shot = False
            player_health -= enemy1_bullet_damage
        if pygame.sprite.spritecollideany(enemy_bullet2, players):
            enemy_bullet2_shot = False
            player_health -= enemy1_bullet_damage
        if pygame.sprite.spritecollideany(enemy_missile1, players):
            enemy_missile_shot = False
            player_health -= enemy1_missile_damage
    
        #Kills player
        if player_health <= 0:
            player.kill()
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            explode1.rect.center = player.rect.center
            deadP = True
            explode1.update()
            time.sleep(1.5)
            game_over.update()
            score0 += 60 * enemy_multiplier
            next_level(BASE_DIR)        
        #kills enemy
        if enemy1_health <= 0:
            if pygame.sprite.spritecollideany(enemy1, bullets):
                enemy1.kill()
                screen.blit(background_image, (0, 0))
                for entity in all_sprites:
                    screen.blit(entity.surf, entity.rect)
                pygame.display.flip()
                explode1.rect.center = enemy1.rect.center
                deadP = False
                explode1.update()
                time.sleep(1.5)
                success.update()
                score0 += enemy_strength
                menu(BASE_DIR)
            if pygame.sprite.spritecollideany(enemy1, missiles):
                enemy1.kill()
                screen.blit(background_image, (0, 0))
                for entity in all_sprites:
                    screen.blit(entity.surf, entity.rect)
                pygame.display.flip()
                explode1.rect.center = enemy1.rect.center
                deadP = False
                explode1.update()
                time.sleep(1.5)
                success.update()
                score0 += enemy_strength
                menu(BASE_DIR)
            if pygame.sprite.spritecollideany(enemy1, bombs):
                enemy1.kill()
                screen.blit(background_image, (0, 0))
                for entity in all_sprites:
                    screen.blit(entity.surf, entity.rect)
                pygame.display.flip()
                explode1.rect.center = enemy1.rect.center
                deadP = False
                explode1.update()
                time.sleep(1.5)
                success.update()
                score0 += enemy_strength
                menu(BASE_DIR)

        enemy_bullet_chance = random.randint(1,50)
        enemy_missile_chance = random.randint(1,50)

        if enemy_bullet_chance == 5:
            if enemy_bullet_delay_time <= 0:
                if enemy_bullet1_shot == False:
                    enemy_bullet1_shot = True
                    enemy_bullet_delay_time = enemy_bullet_delay_base
                elif enemy_bullet1_shot and enemy_bullet2_shot == False:
                    enemy_bullet2_shot = True
                    enemy_bullet_delay_time = enemy_bullet_delay_base

        if enemy_missile_chance == 5:
            if enemy_missile_delay_time <= 0:
                if enemy_missile_shot == False:
                    enemy_missile_shot = True
                    enemy_missile_delay_time = enemy_missile_delay_base


        enemy_bullet_delay_time -= 2
        enemy_missile_delay_time -= 2

        pressed_keys = pygame.key.get_pressed()
        mouse_button = pygame.mouse.get_pressed()

        if mouse_button[0]:
            if bullet_delay_time <= 0:
                if bullet1_shot == False:
                    bullet1_shot = True
                    bullet_delay_time = bullet_delay_base
                elif bullet1_shot and bullet2_shot == False:
                    bullet2_shot = True
                    bullet_delay_time = bullet_delay_base

        if mouse_button[2]:
            if missile_delay_time <= 0:
                if missile_shot == False:
                    missile_shot = True
                    missile_delay_time = missile_delay_base

        if pressed_keys[K_SPACE]:
            if bomb_delay_time <= 0:
                if bomb_shot == False:
                    bomb_shot = True
                    bomb_delay_time = bomb_delay_base
        
        bullet_delay_time -= 2
        missile_delay_time -= 2
        bomb_delay_time -= 2

        Health_Player = textfont.render(f" {player_health}", 1, (255,255,255))
        Health_Enemy = textfont.render(f" {enemy1_health}", 1, (255,255,255))

        
        #space.update() idk if i like this or if it can be made to be perfect in near future

        Thread1.join()
        Thread2.join()
        Thread3.join()
        Thread5.join()
        Thread6.join()
        Thread7.join()
        Thread8.join()
        Thread9.join()

        #Cirtical Screen Stuff
        screen.blit(background_image, (0, 0))
        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)
        screen.blit(Health_Player, (60, 175))
        screen.blit(Health_Enemy, (60, 500))
        pygame.display.flip()
        clock.tick(hz)

    pygame.quit()
    sys.exit()
def game5():
    #Game Settings
    global SCREEN_HEIGHT, SCREEN_HEIGHT
    player_speed =  SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    enemy_speed =   SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    bullet_speed =  SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    missile_speed = SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    bomb_speed =    SCREEN_HEIGHT * SCREEN_WIDTH / 120000

    enemy_strength = enemy_multiplier * 1

    #Setting Up Window and Sprites values
    WHITE = (255, 255, 255)
    sprite_gap_to_border = SCREEN_HEIGHT / 9.6
    sprite_gap_to_right = SCREEN_WIDTH / 3.95
    sprite_gap_to_left = SCREEN_WIDTH / 3.95
    player_size_w = SCREEN_WIDTH / 14.2
    player_size_h = SCREEN_HEIGHT / 5
    enemy_size_w = 7*24
    enemy_size_h = 7*14
    bullet_size_w = SCREEN_WIDTH / 64
    bullet_size_h = SCREEN_HEIGHT / 13.58
    missile_size_w = SCREEN_WIDTH / 51.2
    missile_size_h = SCREEN_HEIGHT / 6.55
    bomb_size_w = SCREEN_WIDTH / 47
    bomb_size_h = SCREEN_HEIGHT / 10.9

    player_health = 15 +80
    enemy1_health = 25 * enemy_multiplier
    player_bullet_damage = 10
    player_missile_damage = 15
    player_bomb_damage = 35
    enemy1_bullet_damage = 7 * enemy_multiplier
    enemy1_missile_damage = 12 * enemy_multiplier 
    enemy1_bomb_damage = 25 * enemy_multiplier

    #Globilisation
    global enemy_time
    global LorR_Enemy
    global LorR_Calc
    global sprite_timer
    global bullet1_shot
    global bullet2_shot
    global missile_shot
    global bomb_shot
    global bullet1
    global bullet2
    global enemy_bullet1_shot
    global enemy_bullet2_shot
    global enemy_missile_shot
    global enemy_bomb_shot
    global enemy_bullet1
    global enemy_bullet2


    enemy_time = random.randint(45, 50) 
    LorR_Enemy = random.choice([1, 100])
    LorR_Calc = random.randint(0, 100)
    sprite_timer = 100

    #ESSENTIAL CODE DO NOT TOUCH
    pygame.init()
    clock = pygame.time.Clock()
    running = True
    bullet1_shot = False
    bullet2_shot = False 
    missile_shot = False
    bomb_shot = False
    enemy_bullet1_shot = False
    enemy_bullet2_shot = False 
    enemy_missile_shot = False
    enemy_bomb_shot = False
    explode_true = False
    deadP = True


    #Create the screen object
    #The size is determined by the constant WIDTH and HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.RESIZABLE)
    textfont = pygame.font.SysFont("monospace", 50) 
    pygame.display.set_caption("Last Stand")

    class Player(pygame.sprite.Sprite):
        def __init__(self):
            super(Player, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame1.png")).convert(),
                (player_size_w, player_size_h))
            self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT - player_size_h/2 - sprite_gap_to_border)

        # Move the sprite based on user keypresses
        def update(self, pressed_keys):

            global enemy_time, LorR_Enemy, LorR_Calc, sprite_timer

            if sprite_timer == 100:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame1.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            
            elif sprite_timer == 80:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame2.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            
            elif sprite_timer == 60:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame3.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            
            elif sprite_timer == 40:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame4.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)

            elif sprite_timer == 20:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame5.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)

            if pressed_keys[K_w]:
                self.rect.move_ip(0, -player_speed)
            if pressed_keys[K_s]:
                self.rect.move_ip(0, player_speed)
            if pressed_keys[K_a]:
                self.rect.move_ip(-player_speed, 0)
            if pressed_keys[K_d]:
                self.rect.move_ip(player_speed, 0)
            
            # Keep player on the screen
            if self.rect.left < sprite_gap_to_left:
                self.rect.left = sprite_gap_to_left
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH

            if self.rect.top <= SCREEN_HEIGHT - player_size_h*1.5 - sprite_gap_to_border*2:
                self.rect.top = SCREEN_HEIGHT - player_size_h*1.5 - sprite_gap_to_border*2
            if self.rect.bottom >= SCREEN_HEIGHT-5:
                self.rect.bottom = SCREEN_HEIGHT-5

    class Bullet(pygame.sprite.Sprite):

        def __init__(self):
            super(Bullet, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame1.png")).convert(),
                (bullet_size_w, bullet_size_h))
            self.surf.set_colorkey((255, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (player.rect.x  + player_size_h/2, player.rect.y + bullet_size_h/2)   

        def update(self):
            
            global sprite_timer, bullet1_shot, bullet2_shot

            if sprite_timer == 100:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame1.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            elif sprite_timer == 80:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame2.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            elif sprite_timer == 60:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame3.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            elif sprite_timer == 40:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame4.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            elif sprite_timer == 20:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame5.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if bullet1_shot == True:
                bullet1.rect.move_ip(0, -bullet_speed)
            if bullet1_shot == False:
                bullet1.rect.x = (player.rect.x+33)
                bullet1.rect.y = (player.rect.y)
                bullet1.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if bullet1.rect.bottom <= 0:
                bullet1_shot = False

            if bullet2_shot == True:
                bullet2.rect.move_ip(0, -bullet_speed)
            if bullet2_shot == False:
                bullet2.rect.x = (player.rect.x+33)
                bullet2.rect.y = (player.rect.y)
                bullet2.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if bullet2.rect.bottom <= 0:
                bullet2_shot = False
    class Missile(pygame.sprite.Sprite):

        def __init__(self):
            super(Missile, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame1.png")).convert(),
                (missile_size_w, missile_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (player.rect.x  + player_size_h/2, player.rect.y + missile_size_h/2)   

        def update(self):
            
            global sprite_timer, missile_shot

            if missile_shot == True:
                missile1.rect.move_ip(0, -missile_speed)

                if sprite_timer == 100:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame1.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame2.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame3.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame4.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame5.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if missile_shot == False:
                missile1.rect.x = (player.rect.x + 30)
                missile1.rect.y = (player.rect.y)
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (missile_size_w, missile_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if missile1.rect.bottom <= 0:
                missile_shot = False
    class Bomb(pygame.sprite.Sprite):

        def __init__(self):
            super(Bomb, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame1.png")).convert(),
                (bomb_size_w, bomb_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (player.rect.x  + player_size_h/2, player.rect.y + bomb_size_h/2)   

        def update(self):
            
            global sprite_timer, bomb_shot

            if bomb_shot == True:
                bomb1.rect.move_ip(0, -bomb_speed)

                if sprite_timer == 100:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame1.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                if sprite_timer == 80:
                    self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame1.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                if sprite_timer == 60:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame3.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                if sprite_timer == 40:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame4.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                if sprite_timer == 20:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame5.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if bomb_shot == False:
                bomb1.rect.x = (player.rect.x + 32)
                bomb1.rect.top = (player.rect.top)

                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (missile_size_w, missile_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if bomb1.rect.bottom <= 0:
                bomb_shot = False

    class Enemy(pygame.sprite.Sprite):

        def __init__(self):
            super(Enemy, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 3", "5", "Frame1.png")).convert(),
                (enemy_size_w, enemy_size_h))
            self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, enemy_size_h/2 + sprite_gap_to_border)

        def update(self):
            
            global enemy_time, LorR_Enemy, LorR_Calc, sprite_timer

            if sprite_timer == 100:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 3", "5", "Frame1.png")).convert(),
                    (enemy_size_w, enemy_size_h))
                self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            
            elif sprite_timer == 75:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 3", "5", "Frame2.png")).convert(),
                    (enemy_size_w, enemy_size_h))
                self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            
            elif sprite_timer == 50:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 3", "5", "Frame3.png")).convert(),
                    (enemy_size_w, enemy_size_h))
                self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            
            elif sprite_timer == 25:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 3", "5", "Frame4.png")).convert(),
                    (enemy_size_w, enemy_size_h))
                self.surf.set_colorkey((255, 0, 255), RLEACCEL)

            

            #Enemy Movement
            if enemy_time > 0:
                enemy_time -= 1

                #timer runs out
                if LorR_Enemy >= LorR_Calc:  
                    self.rect.move_ip(-enemy_speed, 0)   #left
                elif LorR_Enemy < LorR_Calc: 
                    self.rect.move_ip(enemy_speed, 0)   #right

            else:
                #Reset
                enemy_time = random.randint(25, 30)
                LorR_Enemy = (enemy1.rect.x - 241.5) / 1437 * 100
                
                #1920 - 483 = 1437

                LorR_Calc = random.randint(0, 100) 
                
            # Keep enemy on the screen
            if self.rect.left < sprite_gap_to_left:
                self.rect.left = sprite_gap_to_left
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH

            if self.rect.top <= 0:
                self.rect.top = 0
            if self.rect.bottom >= SCREEN_HEIGHT:
                self.rect.bottom = SCREEN_HEIGHT

    class Enemy_Bullet(pygame.sprite.Sprite):

        def __init__(self):
            super(Enemy_Bullet, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (bullet_size_w, bullet_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.x = (enemy1.rect.x+25)
            self.rect.y = (enemy1.rect.y)

        def update(self):
            
            global sprite_timer, enemy_bullet1_shot, enemy_bullet2_shot
            
            if enemy_bullet1.rect.top >= SCREEN_HEIGHT:
                enemy_bullet1_shot = False
                enemy_bullet1.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                enemy_bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if enemy_bullet2.rect.top >= SCREEN_HEIGHT:
                enemy_bullet2_shot = False
                enemy_bullet2.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                enemy_bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)

            if enemy_bullet1_shot == True:
                enemy_bullet1.rect.move_ip(0, +bullet_speed)
                if sprite_timer == 100:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame1.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame2.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame3.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame4.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame5.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)
            if enemy_bullet2_shot == True:
                enemy_bullet2.rect.move_ip(0, +bullet_speed)
                if sprite_timer == 100:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame1.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame2.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame3.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame4.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame5.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if enemy_bullet1_shot == False:
                enemy_bullet1.rect.x = (enemy1.rect.x+25)
                enemy_bullet1.rect.y = (enemy1.rect.y)   
                enemy_bullet1.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                enemy_bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)      
            if enemy_bullet2_shot == False:
                enemy_bullet2.rect.x = (enemy1.rect.x+25)
                enemy_bullet2.rect.y = (enemy1.rect.y)  
                enemy_bullet2.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                enemy_bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)           
    class Enemy_Missile(pygame.sprite.Sprite):

        def __init__(self):
            super(Enemy_Missile, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (missile_size_w, missile_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.x = (enemy1.rect.x + 24)
            self.rect.bottom = (enemy1.rect.top)     

        def update(self):
            
            global sprite_timer, enemy_missile_shot

            if enemy_missile_shot == True:
                enemy_missile1.rect.move_ip(0, +missile_speed)

                if sprite_timer == 100:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Missiles", "Frame1.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Missiles", "Frame2.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Missiles", "Frame3.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Missiles", "Frame4.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Missiles", "Frame5.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if enemy_missile_shot == False:
                enemy_missile1.rect.x = (enemy1.rect.x + 24)
                enemy_missile1.rect.bottom = (enemy1.rect.top)
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (missile_size_w, missile_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
                
            if enemy_missile1.rect.top >= SCREEN_HEIGHT:
                enemy_missile_shot = False
    class Enemy_Bomb(pygame.sprite.Sprite):

        def __init__(self):
            super(Enemy_Bomb, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (bomb_size_w, bomb_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.x = (enemy1.rect.x + 24)
            self.rect.top = (enemy1.rect.bottom)

        def update(self):
            
            global sprite_timer, enemy_bomb_shot

            if enemy_bomb_shot == True:
                enemy_bomb1.rect.move_ip(0, +bomb_speed)

                if sprite_timer == 100:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bombs", "Frame1.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bombs", "Frame2.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bombs", "Frame3.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bombs", "Frame4.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bombs", "Frame5.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if enemy_bomb_shot == False:
                enemy_bomb1.rect.x = (enemy1.rect.x + 24)
                enemy_bomb1.rect.top = (enemy1.rect.bottom)

                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons","SetAs'00FFFF'.png")).convert(),
                    (bomb_size_w, bomb_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if enemy_bomb1.rect.top >= SCREEN_HEIGHT:
                enemy_bomb_shot = False

    class Explode(pygame.sprite.Sprite):

        def __init__(self):
            super(Explode, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH, SCREEN_HEIGHT)   

        def update(self):
            
            global sprite_timer, explode_true

            explode_sleep = 0.05

            bullet1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            bullet2.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)
            missile1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            missile1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            bomb1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            bomb1.surf.set_colorkey((0, 255, 255), RLEACCEL)

            enemy_bullet1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            enemy_bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            enemy_bullet2.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            enemy_bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)
            enemy_missile1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            enemy_missile1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            enemy_bomb1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            enemy_bomb1.surf.set_colorkey((0, 255, 255), RLEACCEL)




            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-1.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-2.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-3.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-4.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-5.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-6.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-7.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-8.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-9.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-10.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-11.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-12.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-13.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-14.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            if deadP == True:
                player.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (150, 150))
                player.surf.set_colorkey((0, 255, 255), RLEACCEL)
            elif deadP == False:
                enemy1.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (150, 150))
                enemy1.surf.set_colorkey((0, 255, 255), RLEACCEL)

            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-15.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-16.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-17.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-18.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-19.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-20.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-21.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-22.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-23.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-24.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
    class Game_over(pygame.sprite.Sprite):

        def __init__(self):
            super(Game_over, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)    

        def update(self):

            explode_sleep = 0.05
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over--1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(1.2)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-0.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(0.14)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over--1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(0.7)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-0.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(1.2)

            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-2.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-3.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-4.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-5.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-6.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-7.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-8.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-9.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-10.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-11.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-12.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-13.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-14.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-15.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-16.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-17.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-18.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-19.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-20.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-21.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()

            menu(BASE_DIR)   
    class Success(pygame.sprite.Sprite):

        def __init__(self):
            super(Success, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)    

        def update(self):

            explode_sleep = 0.05
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(1.2)

            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-2.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-3.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-4.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-5.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-6.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-7.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-8.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-9.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-10.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-11.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-12.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-13.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-14.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-15.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-16.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-17.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-18.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-19.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-20.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-21.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-22.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-23.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-24.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-25.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-26.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()

            menu(BASE_DIR)   


    explode1 = Explode()
    game_over = Game_over()
    success = Success()

    # Instantiate sprites
    player = Player()

    bullet1 = Bullet()
    bullet2 = Bullet()
    missile1 = Missile()
    bomb1 = Bomb()

    enemy1 = Enemy()

    enemy_bullet1 = Enemy_Bullet()
    enemy_bullet2 = Enemy_Bullet()
    enemy_missile1 = Enemy_Missile()
    enemy_bomb1 = Enemy_Bomb()

    #Groups
    players = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    missiles = pygame.sprite.Group()
    bombs = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    enemy_missiles = pygame.sprite.Group()
    enemy_bombs = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()

    players.add(player
                )
    enemies.add(enemy1,
                )
    bullets.add(bullet1,
                bullet2
                )
    missiles.add(missile1
                 )
    bombs.add(bomb1
              )
    enemy_bullets.add(enemy_bullet1,
                enemy_bullet2
                )
    enemy_missiles.add(enemy_missile1
                 )
    enemy_bombs.add(enemy_bomb1
              )
    all_sprites.add(bullet1,
                    bullet2,
                    missile1,
                    bomb1, 
                    enemy_bullet1,
                    enemy_bullet2,
                    enemy_missile1,
                    enemy_bomb1,
                    player, 
                    enemy1,
                    explode1,
                    game_over,
                    success
                    )
    
    bullet_delay_time = 0
    bullet_delay_base = 20
    missile_delay_time = 0
    missile_delay_base = 75
    bomb_delay_time = 0
    bomb_delay_base = 75

    enemy_bullet_delay_time = 0
    enemy_bullet_delay_base = 20
    enemy_missile_delay_time = 0
    enemy_missile_delay_base = 75
    enemy_bomb_delay_time = 0
    enemy_bomb_delay_base = 75

    def bullets_updating():
        bullet1.update()
        bullet2.update()

    #GAME LOOP ITSELF
    while running:
        true = True
        for event in pygame.event.get():            
            if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                game_to_menu(BASE_DIR)

        # Get all the keys currently pressed
        pressed_keys = pygame.key.get_pressed()
        Thread1 = threading.Thread(player.update(pressed_keys))
        Thread2 = threading.Thread(enemy1.update())
        Thread3 = threading.Thread(target = bullets_updating)
        Thread5 = threading.Thread(missile1.update())
        Thread6 = threading.Thread(bomb1.update())
        Thread7 = threading.Thread(enemy_bullet1.update())
        Thread8 = threading.Thread(enemy_bullet2.update())
        Thread9 = threading.Thread(enemy_missile1.update())
        Thread10 = threading.Thread(enemy_bomb1.update())

        Thread1.start()
        Thread2.start()
        Thread3.start()
        Thread5.start()
        Thread6.start()
        Thread7.start()
        Thread8.start()
        Thread9.start()
        Thread10.start()

        
        if sprite_timer == 0:
            sprite_timer = 100 
        else:
            sprite_timer -= 5

        #Kills player bullets
        if pygame.sprite.spritecollideany(bullet1, enemies):
            bullet1_shot = False
            enemy1_health -= player_bullet_damage
        if pygame.sprite.spritecollideany(bullet2, enemies):
            bullet2_shot = False
            enemy1_health -= player_bullet_damage
        if pygame.sprite.spritecollideany(missile1, enemies):
            missile_shot = False
            enemy1_health -= player_missile_damage
        if pygame.sprite.spritecollideany(bomb1, enemies):
            bomb_shot = False
            enemy1_health -= player_bomb_damage
        #Kills enemy bullets
        if pygame.sprite.spritecollideany(enemy_bullet1, players):
            enemy_bullet1_shot = False
            player_health -= enemy1_bullet_damage
        if pygame.sprite.spritecollideany(enemy_bullet2, players):
            enemy_bullet2_shot = False
            player_health -= enemy1_bullet_damage
        if pygame.sprite.spritecollideany(enemy_missile1, players):
            enemy_missile_shot = False
            player_health -= enemy1_missile_damage
        if pygame.sprite.spritecollideany(enemy_bomb1, players):
            enemy_bomb_shot = False
            player_health -= enemy1_bomb_damage
    
        #Kills player
        if player_health <= 0:
            player.kill()
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            explode1.rect.center = player.rect.center
            deadP = True
            explode1.update()
            time.sleep(1.5)
            game_over.update()
            score0 += 80 * enemy_multiplier
            next_level(BASE_DIR)        
        #kills enemy
        if enemy1_health <= 0:
            if pygame.sprite.spritecollideany(enemy1, bullets):
                enemy1.kill()
                screen.blit(background_image, (0, 0))
                for entity in all_sprites:
                    screen.blit(entity.surf, entity.rect)
                pygame.display.flip()
                explode1.rect.center = enemy1.rect.center
                deadP = False
                explode1.update()
                time.sleep(1.5)
                success.update()
                score0 += enemy_strength
                menu(BASE_DIR)
            if pygame.sprite.spritecollideany(enemy1, missiles):
                enemy1.kill()
                screen.blit(background_image, (0, 0))
                for entity in all_sprites:
                    screen.blit(entity.surf, entity.rect)
                pygame.display.flip()
                explode1.rect.center = enemy1.rect.center
                deadP = False
                explode1.update()
                time.sleep(1.5)
                success.update()
                score0 += enemy_strength
                menu(BASE_DIR)
            if pygame.sprite.spritecollideany(enemy1, bombs):
                enemy1.kill()
                screen.blit(background_image, (0, 0))
                for entity in all_sprites:
                    screen.blit(entity.surf, entity.rect)
                pygame.display.flip()
                explode1.rect.center = enemy1.rect.center
                deadP = False
                explode1.update()
                time.sleep(1.5)
                success.update()
                score0 += enemy_strength
                menu(BASE_DIR)

        enemy_bullet_chance = random.randint(1,50)
        enemy_missile_chance = random.randint(1,50)
        enemy_bomb_chance = random.randint(1,50)

        if enemy_bullet_chance == 5:
            if enemy_bullet_delay_time <= 0:
                if enemy_bullet1_shot == False:
                    enemy_bullet1_shot = True
                    enemy_bullet_delay_time = enemy_bullet_delay_base
                elif enemy_bullet1_shot and enemy_bullet2_shot == False:
                    enemy_bullet2_shot = True
                    enemy_bullet_delay_time = enemy_bullet_delay_base

        if enemy_missile_chance == 5:
            if enemy_missile_delay_time <= 0:
                if enemy_missile_shot == False:
                    enemy_missile_shot = True
                    enemy_missile_delay_time = enemy_missile_delay_base

        if enemy_bomb_chance == 5:
            if enemy_bomb_delay_time <= 0:
                if enemy_bomb_shot == False:
                    enemy_bomb_shot = True
                    enemy_bomb_delay_time = enemy_bomb_delay_base
        

        enemy_bullet_delay_time -= 2
        enemy_missile_delay_time -= 2
        enemy_bomb_delay_time -= 2

        pressed_keys = pygame.key.get_pressed()
        mouse_button = pygame.mouse.get_pressed()

        if mouse_button[0]:
            if bullet_delay_time <= 0:
                if bullet1_shot == False:
                    bullet1_shot = True
                    bullet_delay_time = bullet_delay_base
                elif bullet1_shot and bullet2_shot == False:
                    bullet2_shot = True
                    bullet_delay_time = bullet_delay_base

        if mouse_button[2]:
            if missile_delay_time <= 0:
                if missile_shot == False:
                    missile_shot = True
                    missile_delay_time = missile_delay_base

        if pressed_keys[K_SPACE]:
            if bomb_delay_time <= 0:
                if bomb_shot == False:
                    bomb_shot = True
                    bomb_delay_time = bomb_delay_base
        
        bullet_delay_time -= 2
        missile_delay_time -= 2
        bomb_delay_time -= 2

        Health_Player = textfont.render(f" {player_health}", 1, (255,255,255))
        Health_Enemy = textfont.render(f" {enemy1_health}", 1, (255,255,255))

        
        #space.update() idk if i like this or if it can be made to be perfect in near future

        Thread1.join()
        Thread2.join()
        Thread3.join()
        Thread5.join()
        Thread6.join()
        Thread7.join()
        Thread8.join()
        Thread9.join()
        Thread10.join()

        #Cirtical Screen Stuff
        screen.blit(background_image, (0, 0))
        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)
        screen.blit(Health_Player, (60, 175))
        screen.blit(Health_Enemy, (60, 500))
        pygame.display.flip()
        clock.tick(hz)

    pygame.quit()
    sys.exit()
def game6():
    #Game Settings
    global SCREEN_HEIGHT, SCREEN_HEIGHT
    player_speed =  SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    enemy_speed =   SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    bullet_speed =  SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    missile_speed = SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    bomb_speed =    SCREEN_HEIGHT * SCREEN_WIDTH / 120000

    enemy_strength = enemy_multiplier * 1

    #Setting Up Window and Sprites values
    WHITE = (255, 255, 255)
    sprite_gap_to_border = SCREEN_HEIGHT / 9.6
    sprite_gap_to_right = SCREEN_WIDTH / 3.95
    sprite_gap_to_left = SCREEN_WIDTH / 3.95
    player_size_w = SCREEN_WIDTH / 14.2
    player_size_h = SCREEN_HEIGHT / 5
    enemy_size_w = 7*26
    enemy_size_h = 7*15
    bullet_size_w = SCREEN_WIDTH / 64
    bullet_size_h = SCREEN_HEIGHT / 13.58
    missile_size_w = SCREEN_WIDTH / 51.2
    missile_size_h = SCREEN_HEIGHT / 6.55
    bomb_size_w = SCREEN_WIDTH / 47
    bomb_size_h = SCREEN_HEIGHT / 10.9

    player_health = 15 +80
    enemy1_health = 50 * enemy_multiplier
    player_bullet_damage = 10
    player_missile_damage = 15
    player_bomb_damage = 35
    enemy1_bullet_damage = 8 * enemy_multiplier
    enemy1_missile_damage = 15 * enemy_multiplier 
    enemy1_bomb_damage = 30 * enemy_multiplier

    #Globilisation
    global enemy_time
    global LorR_Enemy
    global LorR_Calc
    global sprite_timer
    global bullet1_shot
    global bullet2_shot
    global missile_shot
    global bomb_shot
    global bullet1
    global bullet2
    global enemy_bullet1_shot
    global enemy_bullet2_shot
    global enemy_missile_shot
    global enemy_bomb_shot
    global enemy_bullet1
    global enemy_bullet2


    enemy_time = random.randint(45, 50) 
    LorR_Enemy = random.choice([1, 100])
    LorR_Calc = random.randint(0, 100)
    sprite_timer = 100

    #ESSENTIAL CODE DO NOT TOUCH
    pygame.init()
    clock = pygame.time.Clock()
    running = True
    bullet1_shot = False
    bullet2_shot = False 
    missile_shot = False
    bomb_shot = False
    enemy_bullet1_shot = False
    enemy_bullet2_shot = False 
    enemy_missile_shot = False
    enemy_bomb_shot = False
    explode_true = False
    deadP = True


    #Create the screen object
    #The size is determined by the constant WIDTH and HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.RESIZABLE)
    textfont = pygame.font.SysFont("monospace", 50) 
    pygame.display.set_caption("Last Stand")


    class Player(pygame.sprite.Sprite):
        def __init__(self):
            super(Player, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame1.png")).convert(),
                (player_size_w, player_size_h))
            self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT - player_size_h/2 - sprite_gap_to_border)

        # Move the sprite based on user keypresses
        def update(self, pressed_keys):

            global enemy_time, LorR_Enemy, LorR_Calc, sprite_timer

            if sprite_timer == 100:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame1.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            
            elif sprite_timer == 80:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame2.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            
            elif sprite_timer == 60:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame3.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            
            elif sprite_timer == 40:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame4.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)

            elif sprite_timer == 20:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame5.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)

            if pressed_keys[K_w]:
                self.rect.move_ip(0, -player_speed)
            if pressed_keys[K_s]:
                self.rect.move_ip(0, player_speed)
            if pressed_keys[K_a]:
                self.rect.move_ip(-player_speed, 0)
            if pressed_keys[K_d]:
                self.rect.move_ip(player_speed, 0)
            
            # Keep player on the screen
            if self.rect.left < sprite_gap_to_left:
                self.rect.left = sprite_gap_to_left
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH

            if self.rect.top <= SCREEN_HEIGHT - player_size_h*1.5 - sprite_gap_to_border*2:
                self.rect.top = SCREEN_HEIGHT - player_size_h*1.5 - sprite_gap_to_border*2
            if self.rect.bottom >= SCREEN_HEIGHT-5:
                self.rect.bottom = SCREEN_HEIGHT-5

    class Bullet(pygame.sprite.Sprite):

        def __init__(self):
            super(Bullet, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame1.png")).convert(),
                (bullet_size_w, bullet_size_h))
            self.surf.set_colorkey((255, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (player.rect.x  + player_size_h/2, player.rect.y + bullet_size_h/2)   

        def update(self):
            
            global sprite_timer, bullet1_shot, bullet2_shot

            if sprite_timer == 100:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame1.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            elif sprite_timer == 80:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame2.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            elif sprite_timer == 60:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame3.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            elif sprite_timer == 40:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame4.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            elif sprite_timer == 20:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame5.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if bullet1_shot == True:
                bullet1.rect.move_ip(0, -bullet_speed)
            if bullet1_shot == False:
                bullet1.rect.x = (player.rect.x+33)
                bullet1.rect.y = (player.rect.y)
                bullet1.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if bullet1.rect.bottom <= 0:
                bullet1_shot = False

            if bullet2_shot == True:
                bullet2.rect.move_ip(0, -bullet_speed)
            if bullet2_shot == False:
                bullet2.rect.x = (player.rect.x+33)
                bullet2.rect.y = (player.rect.y)
                bullet2.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if bullet2.rect.bottom <= 0:
                bullet2_shot = False
    class Missile(pygame.sprite.Sprite):

        def __init__(self):
            super(Missile, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame1.png")).convert(),
                (missile_size_w, missile_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (player.rect.x  + player_size_h/2, player.rect.y + missile_size_h/2)   

        def update(self):
            
            global sprite_timer, missile_shot

            if missile_shot == True:
                missile1.rect.move_ip(0, -missile_speed)

                if sprite_timer == 100:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame1.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame2.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame3.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame4.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame5.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if missile_shot == False:
                missile1.rect.x = (player.rect.x + 30)
                missile1.rect.y = (player.rect.y)
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (missile_size_w, missile_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if missile1.rect.bottom <= 0:
                missile_shot = False
    class Bomb(pygame.sprite.Sprite):

        def __init__(self):
            super(Bomb, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame1.png")).convert(),
                (bomb_size_w, bomb_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (player.rect.x  + player_size_h/2, player.rect.y + bomb_size_h/2)   

        def update(self):
            
            global sprite_timer, bomb_shot

            if bomb_shot == True:
                bomb1.rect.move_ip(0, -bomb_speed)

                if sprite_timer == 100:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame1.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                if sprite_timer == 80:
                    self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame1.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                if sprite_timer == 60:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame3.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                if sprite_timer == 40:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame4.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                if sprite_timer == 20:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame5.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if bomb_shot == False:
                bomb1.rect.x = (player.rect.x + 32)
                bomb1.rect.top = (player.rect.top)

                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (missile_size_w, missile_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if bomb1.rect.bottom <= 0:
                bomb_shot = False

    class Enemy(pygame.sprite.Sprite):

        def __init__(self):
            super(Enemy, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 3", "6", "Frame1.png")).convert(),
                (enemy_size_w, enemy_size_h))
            self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, enemy_size_h/2 + sprite_gap_to_border)

        def update(self):
            
            global enemy_time, LorR_Enemy, LorR_Calc, sprite_timer

            if sprite_timer == 100:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 3", "6", "Frame1.png")).convert(),
                    (enemy_size_w, enemy_size_h))
                self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            
            elif sprite_timer == 75:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 3", "6", "Frame2.png")).convert(),
                    (enemy_size_w, enemy_size_h))
                self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            
            elif sprite_timer == 50:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 3", "6", "Frame3.png")).convert(),
                    (enemy_size_w, enemy_size_h))
                self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            
            elif sprite_timer == 25:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 3", "6", "Frame4.png")).convert(),
                    (enemy_size_w, enemy_size_h))
                self.surf.set_colorkey((255, 0, 255), RLEACCEL)

            

            #Enemy Movement
            if enemy_time > 0:
                enemy_time -= 1

                #timer runs out
                if LorR_Enemy >= LorR_Calc:  
                    self.rect.move_ip(-enemy_speed, 0)   #left
                elif LorR_Enemy < LorR_Calc: 
                    self.rect.move_ip(enemy_speed, 0)   #right

            else:
                #Reset
                enemy_time = random.randint(25, 30)
                LorR_Enemy = (enemy1.rect.x - 241.5) / 1437 * 100
                
                #1920 - 483 = 1437

                LorR_Calc = random.randint(0, 100) 
                
            # Keep enemy on the screen
            if self.rect.left < sprite_gap_to_left:
                self.rect.left = sprite_gap_to_left
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH

            if self.rect.top <= 0:
                self.rect.top = 0
            if self.rect.bottom >= SCREEN_HEIGHT:
                self.rect.bottom = SCREEN_HEIGHT

    class Enemy_Bullet(pygame.sprite.Sprite):

        def __init__(self):
            super(Enemy_Bullet, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (bullet_size_w, bullet_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.x = (enemy1.rect.x+25)
            self.rect.y = (enemy1.rect.y)

        def update(self):
            
            global sprite_timer, enemy_bullet1_shot, enemy_bullet2_shot
            
            if enemy_bullet1.rect.top >= SCREEN_HEIGHT:
                enemy_bullet1_shot = False
                enemy_bullet1.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                enemy_bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if enemy_bullet2.rect.top >= SCREEN_HEIGHT:
                enemy_bullet2_shot = False
                enemy_bullet2.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                enemy_bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)

            if enemy_bullet1_shot == True:
                enemy_bullet1.rect.move_ip(0, +bullet_speed)
                if sprite_timer == 100:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame1.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame2.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame3.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame4.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame5.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)
            if enemy_bullet2_shot == True:
                enemy_bullet2.rect.move_ip(0, +bullet_speed)
                if sprite_timer == 100:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame1.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame2.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame3.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame4.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame5.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if enemy_bullet1_shot == False:
                enemy_bullet1.rect.x = (enemy1.rect.x+25)
                enemy_bullet1.rect.y = (enemy1.rect.y)   
                enemy_bullet1.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                enemy_bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)      
            if enemy_bullet2_shot == False:
                enemy_bullet2.rect.x = (enemy1.rect.x+25)
                enemy_bullet2.rect.y = (enemy1.rect.y)  
                enemy_bullet2.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                enemy_bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)           
    class Enemy_Missile(pygame.sprite.Sprite):

        def __init__(self):
            super(Enemy_Missile, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (missile_size_w, missile_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.x = (enemy1.rect.x + 24)
            self.rect.bottom = (enemy1.rect.top)     

        def update(self):
            
            global sprite_timer, enemy_missile_shot

            if enemy_missile_shot == True:
                enemy_missile1.rect.move_ip(0, +missile_speed)

                if sprite_timer == 100:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Missiles", "Frame1.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Missiles", "Frame2.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Missiles", "Frame3.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Missiles", "Frame4.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Missiles", "Frame5.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if enemy_missile_shot == False:
                enemy_missile1.rect.x = (enemy1.rect.x + 24)
                enemy_missile1.rect.bottom = (enemy1.rect.top)
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (missile_size_w, missile_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
                
            if enemy_missile1.rect.top >= SCREEN_HEIGHT:
                enemy_missile_shot = False
    class Enemy_Bomb(pygame.sprite.Sprite):

        def __init__(self):
            super(Enemy_Bomb, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (bomb_size_w, bomb_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.x = (enemy1.rect.x + 24)
            self.rect.top = (enemy1.rect.bottom)

        def update(self):
            
            global sprite_timer, enemy_bomb_shot

            if enemy_bomb_shot == True:
                enemy_bomb1.rect.move_ip(0, +bomb_speed)

                if sprite_timer == 100:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bombs", "Frame1.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bombs", "Frame2.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bombs", "Frame3.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bombs", "Frame4.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bombs", "Frame5.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if enemy_bomb_shot == False:
                enemy_bomb1.rect.x = (enemy1.rect.x + 24)
                enemy_bomb1.rect.top = (enemy1.rect.bottom)

                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons","SetAs'00FFFF'.png")).convert(),
                    (bomb_size_w, bomb_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if enemy_bomb1.rect.top >= SCREEN_HEIGHT:
                enemy_bomb_shot = False

    class Explode(pygame.sprite.Sprite):

        def __init__(self):
            super(Explode, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH, SCREEN_HEIGHT)   

        def update(self):
            
            global sprite_timer, explode_true

            explode_sleep = 0.05

            bullet1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            bullet2.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)
            missile1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            missile1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            bomb1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            bomb1.surf.set_colorkey((0, 255, 255), RLEACCEL)

            enemy_bullet1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            enemy_bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            enemy_bullet2.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            enemy_bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)
            enemy_missile1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            enemy_missile1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            enemy_bomb1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            enemy_bomb1.surf.set_colorkey((0, 255, 255), RLEACCEL)




            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-1.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-2.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-3.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-4.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-5.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-6.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-7.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-8.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-9.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-10.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-11.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-12.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-13.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-14.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            if deadP == True:
                player.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (150, 150))
                player.surf.set_colorkey((0, 255, 255), RLEACCEL)
            elif deadP == False:
                enemy1.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (150, 150))
                enemy1.surf.set_colorkey((0, 255, 255), RLEACCEL)

            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-15.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-16.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-17.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-18.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-19.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-20.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-21.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-22.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-23.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-24.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
    class Game_over(pygame.sprite.Sprite):

        def __init__(self):
            super(Game_over, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)    

        def update(self):

            explode_sleep = 0.05
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over--1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(1.2)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-0.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(0.14)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over--1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(0.7)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-0.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(1.2)

            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-2.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-3.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-4.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-5.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-6.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-7.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-8.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-9.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-10.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-11.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-12.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-13.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-14.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-15.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-16.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-17.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-18.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-19.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-20.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-21.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()

            menu(BASE_DIR)   
    class Success(pygame.sprite.Sprite):

        def __init__(self):
            super(Success, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)    

        def update(self):

            explode_sleep = 0.05
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(1.2)

            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-2.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-3.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-4.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-5.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-6.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-7.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-8.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-9.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-10.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-11.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-12.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-13.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-14.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-15.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-16.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-17.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-18.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-19.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-20.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-21.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-22.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-23.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-24.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-25.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-26.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()

            menu(BASE_DIR)   


    explode1 = Explode()
    game_over = Game_over()
    success = Success()

    # Instantiate sprites
    player = Player()

    bullet1 = Bullet()
    bullet2 = Bullet()
    missile1 = Missile()
    bomb1 = Bomb()

    enemy1 = Enemy()

    enemy_bullet1 = Enemy_Bullet()
    enemy_bullet2 = Enemy_Bullet()
    enemy_missile1 = Enemy_Missile()
    enemy_bomb1 = Enemy_Bomb()

    #Groups
    players = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    missiles = pygame.sprite.Group()
    bombs = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    enemy_missiles = pygame.sprite.Group()
    enemy_bombs = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()

    players.add(player
                )
    enemies.add(enemy1,
                )
    bullets.add(bullet1,
                bullet2
                )
    missiles.add(missile1
                 )
    bombs.add(bomb1
              )
    enemy_bullets.add(enemy_bullet1,
                enemy_bullet2
                )
    enemy_missiles.add(enemy_missile1
                 )
    enemy_bombs.add(enemy_bomb1
              )
    all_sprites.add(bullet1,
                    bullet2,
                    missile1,
                    bomb1, 
                    enemy_bullet1,
                    enemy_bullet2,
                    enemy_missile1,
                    enemy_bomb1,
                    player, 
                    enemy1,
                    explode1,
                    game_over,
                    success
                    )
    
    bullet_delay_time = 0
    bullet_delay_base = 20
    missile_delay_time = 0
    missile_delay_base = 75
    bomb_delay_time = 0
    bomb_delay_base = 75

    enemy_bullet_delay_time = 0
    enemy_bullet_delay_base = 20
    enemy_missile_delay_time = 0
    enemy_missile_delay_base = 75
    enemy_bomb_delay_time = 0
    enemy_bomb_delay_base = 75

    def bullets_updating():
        bullet1.update()
        bullet2.update()

    #GAME LOOP ITSELF
    while running:
        true = True
        for event in pygame.event.get():            
            if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                game_to_menu(BASE_DIR)

        # Get all the keys currently pressed
        pressed_keys = pygame.key.get_pressed()
        Thread1 = threading.Thread(player.update(pressed_keys))
        Thread2 = threading.Thread(enemy1.update())
        Thread3 = threading.Thread(target = bullets_updating)
        Thread5 = threading.Thread(missile1.update())
        Thread6 = threading.Thread(bomb1.update())
        Thread7 = threading.Thread(enemy_bullet1.update())
        Thread8 = threading.Thread(enemy_bullet2.update())
        Thread9 = threading.Thread(enemy_missile1.update())
        Thread10 = threading.Thread(enemy_bomb1.update())

        Thread1.start()
        Thread2.start()
        Thread3.start()
        Thread5.start()
        Thread6.start()
        Thread7.start()
        Thread8.start()
        Thread9.start()
        Thread10.start()

        
        if sprite_timer == 0:
            sprite_timer = 100 
        else:
            sprite_timer -= 5

        #Kills player bullets
        if pygame.sprite.spritecollideany(bullet1, enemies):
            bullet1_shot = False
            enemy1_health -= player_bullet_damage
        if pygame.sprite.spritecollideany(bullet2, enemies):
            bullet2_shot = False
            enemy1_health -= player_bullet_damage
        if pygame.sprite.spritecollideany(missile1, enemies):
            missile_shot = False
            enemy1_health -= player_missile_damage
        if pygame.sprite.spritecollideany(bomb1, enemies):
            bomb_shot = False
            enemy1_health -= player_bomb_damage
        #Kills enemy bullets
        if pygame.sprite.spritecollideany(enemy_bullet1, players):
            enemy_bullet1_shot = False
            player_health -= enemy1_bullet_damage
        if pygame.sprite.spritecollideany(enemy_bullet2, players):
            enemy_bullet2_shot = False
            player_health -= enemy1_bullet_damage
        if pygame.sprite.spritecollideany(enemy_missile1, players):
            enemy_missile_shot = False
            player_health -= enemy1_missile_damage
        if pygame.sprite.spritecollideany(enemy_bomb1, players):
            enemy_bomb_shot = False
            player_health -= enemy1_bomb_damage
    
        #Kills player
        if player_health <= 0:
            player.kill()
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            explode1.rect.center = player.rect.center
            deadP = True
            explode1.update()
            time.sleep(1.5)
            game_over.update()
            score0 += 100 * enemy_multiplier
            next_level(BASE_DIR)        
        #kills enemy
        if enemy1_health <= 0:
            if pygame.sprite.spritecollideany(enemy1, bullets):
                enemy1.kill()
                screen.blit(background_image, (0, 0))
                for entity in all_sprites:
                    screen.blit(entity.surf, entity.rect)
                pygame.display.flip()
                explode1.rect.center = enemy1.rect.center
                deadP = False
                explode1.update()
                time.sleep(1.5)
                success.update()
                score0 += enemy_strength
                menu(BASE_DIR)
            if pygame.sprite.spritecollideany(enemy1, missiles):
                enemy1.kill()
                screen.blit(background_image, (0, 0))
                for entity in all_sprites:
                    screen.blit(entity.surf, entity.rect)
                pygame.display.flip()
                explode1.rect.center = enemy1.rect.center
                deadP = False
                explode1.update()
                time.sleep(1.5)
                success.update()
                score0 += enemy_strength
                menu(BASE_DIR)
            if pygame.sprite.spritecollideany(enemy1, bombs):
                enemy1.kill()
                screen.blit(background_image, (0, 0))
                for entity in all_sprites:
                    screen.blit(entity.surf, entity.rect)
                pygame.display.flip()
                explode1.rect.center = enemy1.rect.center
                deadP = False
                explode1.update()
                time.sleep(1.5)
                success.update()
                score0 += enemy_strength
                menu(BASE_DIR)

        enemy_bullet_chance = random.randint(1,50)
        enemy_missile_chance = random.randint(1,50)
        enemy_bomb_chance = random.randint(1,50)

        if enemy_bullet_chance == 5:
            if enemy_bullet_delay_time <= 0:
                if enemy_bullet1_shot == False:
                    enemy_bullet1_shot = True
                    enemy_bullet_delay_time = enemy_bullet_delay_base
                elif enemy_bullet1_shot and enemy_bullet2_shot == False:
                    enemy_bullet2_shot = True
                    enemy_bullet_delay_time = enemy_bullet_delay_base

        if enemy_missile_chance == 5:
            if enemy_missile_delay_time <= 0:
                if enemy_missile_shot == False:
                    enemy_missile_shot = True
                    enemy_missile_delay_time = enemy_missile_delay_base

        if enemy_bomb_chance == 5:
            if enemy_bomb_delay_time <= 0:
                if enemy_bomb_shot == False:
                    enemy_bomb_shot = True
                    enemy_bomb_delay_time = enemy_bomb_delay_base
        

        enemy_bullet_delay_time -= 2
        enemy_missile_delay_time -= 2
        enemy_bomb_delay_time -= 2

        pressed_keys = pygame.key.get_pressed()
        mouse_button = pygame.mouse.get_pressed()

        if mouse_button[0]:
            if bullet_delay_time <= 0:
                if bullet1_shot == False:
                    bullet1_shot = True
                    bullet_delay_time = bullet_delay_base
                elif bullet1_shot and bullet2_shot == False:
                    bullet2_shot = True
                    bullet_delay_time = bullet_delay_base

        if mouse_button[2]:
            if missile_delay_time <= 0:
                if missile_shot == False:
                    missile_shot = True
                    missile_delay_time = missile_delay_base

        if pressed_keys[K_SPACE]:
            if bomb_delay_time <= 0:
                if bomb_shot == False:
                    bomb_shot = True
                    bomb_delay_time = bomb_delay_base
        
        bullet_delay_time -= 2
        missile_delay_time -= 2
        bomb_delay_time -= 2

        Health_Player = textfont.render(f" {player_health}", 1, (255,255,255))
        Health_Enemy = textfont.render(f" {enemy1_health}", 1, (255,255,255))

        
        #space.update() idk if i like this or if it can be made to be perfect in near future

        Thread1.join()
        Thread2.join()
        Thread3.join()
        Thread5.join()
        Thread6.join()
        Thread7.join()
        Thread8.join()
        Thread9.join()
        Thread10.join()

        #Cirtical Screen Stuff
        screen.blit(background_image, (0, 0))
        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)
        screen.blit(Health_Player, (60, 175))
        screen.blit(Health_Enemy, (60, 500))
        pygame.display.flip()
        clock.tick(hz)

    pygame.quit()
    sys.exit()
def boss():
    #Game Settings
    global SCREEN_HEIGHT, SCREEN_HEIGHT
    player_speed =  SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    enemy_speed =   SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    bullet_speed =  SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    missile_speed = SCREEN_HEIGHT * SCREEN_WIDTH / 120000
    bomb_speed =    SCREEN_HEIGHT * SCREEN_WIDTH / 120000

    enemy_strength = enemy_multiplier * 1

    #Setting Up Window and Sprites values
    WHITE = (255, 255, 255)
    sprite_gap_to_border = SCREEN_HEIGHT / 9.6
    sprite_gap_to_right = SCREEN_WIDTH / 3.95
    sprite_gap_to_left = SCREEN_WIDTH / 3.95
    player_size_w = SCREEN_WIDTH / 14.2
    player_size_h = SCREEN_HEIGHT / 5
    enemy_size_w = 10*1 # pixel size
    enemy_size_h = 10*1 # pixel size
    bullet_size_w = SCREEN_WIDTH / 64
    bullet_size_h = SCREEN_HEIGHT / 13.58
    missile_size_w = SCREEN_WIDTH / 51.2
    missile_size_h = SCREEN_HEIGHT / 6.55
    bomb_size_w = SCREEN_WIDTH / 47
    bomb_size_h = SCREEN_HEIGHT / 10.9

    player_health = 15 +80
    enemy1_health = 1000 * enemy_multiplier
    player_bullet_damage = 10
    player_missile_damage = 15
    player_bomb_damage = 35
    enemy1_bullet_damage = 25 * enemy_multiplier
    enemy1_missile_damage = 30 * enemy_multiplier 
    enemy1_bomb_damage = 55 * enemy_multiplier

    #Globilisation
    global enemy_time
    global LorR_Enemy
    global LorR_Calc
    global sprite_timer
    global bullet1_shot
    global bullet2_shot
    global missile_shot
    global bomb_shot
    global bullet1
    global bullet2
    global enemy_bullet1_shot
    global enemy_bullet2_shot
    global enemy_missile_shot
    global enemy_bomb_shot
    global enemy_bullet1
    global enemy_bullet2


    enemy_time = random.randint(45, 50) 
    LorR_Enemy = random.choice([1, 100])
    LorR_Calc = random.randint(0, 100)
    sprite_timer = 100

    #ESSENTIAL CODE DO NOT TOUCH
    pygame.init()
    clock = pygame.time.Clock()
    running = True
    bullet1_shot = False
    bullet2_shot = False 
    missile_shot = False
    bomb_shot = False
    enemy_bullet1_shot = False
    enemy_bullet2_shot = False 
    enemy_missile_shot = False
    enemy_bomb_shot = False
    explode_true = False
    deadP = True


    #Create the screen object
    #The size is determined by the constant WIDTH and HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.RESIZABLE)
    textfont = pygame.font.SysFont("monospace", 50) 
    pygame.display.set_caption("Last Stand")


    class Player(pygame.sprite.Sprite):
        def __init__(self):
            super(Player, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame1.png")).convert(),
                (player_size_w, player_size_h))
            self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT - player_size_h/2 - sprite_gap_to_border)

        # Move the sprite based on user keypresses
        def update(self, pressed_keys):

            global enemy_time, LorR_Enemy, LorR_Calc, sprite_timer

            if sprite_timer == 100:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame1.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            
            elif sprite_timer == 80:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame2.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            
            elif sprite_timer == 60:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame3.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            
            elif sprite_timer == 40:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame4.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)

            elif sprite_timer == 20:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Frame5.png")).convert(),
                    (player_size_w, player_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)

            if pressed_keys[K_w]:
                self.rect.move_ip(0, -player_speed)
            if pressed_keys[K_s]:
                self.rect.move_ip(0, player_speed)
            if pressed_keys[K_a]:
                self.rect.move_ip(-player_speed, 0)
            if pressed_keys[K_d]:
                self.rect.move_ip(player_speed, 0)
            
            # Keep player on the screen
            if self.rect.left < sprite_gap_to_left:
                self.rect.left = sprite_gap_to_left
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH

            if self.rect.top <= SCREEN_HEIGHT - player_size_h*1.5 - sprite_gap_to_border*2:
                self.rect.top = SCREEN_HEIGHT - player_size_h*1.5 - sprite_gap_to_border*2
            if self.rect.bottom >= SCREEN_HEIGHT-5:
                self.rect.bottom = SCREEN_HEIGHT-5

    class Bullet(pygame.sprite.Sprite):

        def __init__(self):
            super(Bullet, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame1.png")).convert(),
                (bullet_size_w, bullet_size_h))
            self.surf.set_colorkey((255, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (player.rect.x  + player_size_h/2, player.rect.y + bullet_size_h/2)   

        def update(self):
            
            global sprite_timer, bullet1_shot, bullet2_shot

            if sprite_timer == 100:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame1.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            elif sprite_timer == 80:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame2.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            elif sprite_timer == 60:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame3.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            elif sprite_timer == 40:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame4.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            elif sprite_timer == 20:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bullet", "Frame5.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if bullet1_shot == True:
                bullet1.rect.move_ip(0, -bullet_speed)
            if bullet1_shot == False:
                bullet1.rect.x = (player.rect.x+33)
                bullet1.rect.y = (player.rect.y)
                bullet1.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if bullet1.rect.bottom <= 0:
                bullet1_shot = False

            if bullet2_shot == True:
                bullet2.rect.move_ip(0, -bullet_speed)
            if bullet2_shot == False:
                bullet2.rect.x = (player.rect.x+33)
                bullet2.rect.y = (player.rect.y)
                bullet2.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if bullet2.rect.bottom <= 0:
                bullet2_shot = False
    class Missile(pygame.sprite.Sprite):

        def __init__(self):
            super(Missile, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame1.png")).convert(),
                (missile_size_w, missile_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (player.rect.x  + player_size_h/2, player.rect.y + missile_size_h/2)   

        def update(self):
            
            global sprite_timer, missile_shot

            if missile_shot == True:
                missile1.rect.move_ip(0, -missile_speed)

                if sprite_timer == 100:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame1.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame2.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame3.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame4.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Missiles", "Frame5.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if missile_shot == False:
                missile1.rect.x = (player.rect.x + 30)
                missile1.rect.y = (player.rect.y)
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (missile_size_w, missile_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if missile1.rect.bottom <= 0:
                missile_shot = False
    class Bomb(pygame.sprite.Sprite):

        def __init__(self):
            super(Bomb, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame1.png")).convert(),
                (bomb_size_w, bomb_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (player.rect.x  + player_size_h/2, player.rect.y + bomb_size_h/2)   

        def update(self):
            
            global sprite_timer, bomb_shot

            if bomb_shot == True:
                bomb1.rect.move_ip(0, -bomb_speed)

                if sprite_timer == 100:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame1.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                if sprite_timer == 80:
                    self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame1.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                if sprite_timer == 60:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame3.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                if sprite_timer == 40:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame4.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                if sprite_timer == 20:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "Bombs", "Frame5.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if bomb_shot == False:
                bomb1.rect.x = (player.rect.x + 32)
                bomb1.rect.top = (player.rect.top)

                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (missile_size_w, missile_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if bomb1.rect.bottom <= 0:
                bomb_shot = False

    class Enemy(pygame.sprite.Sprite):

        def __init__(self):
            super(Enemy, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 5", "9", "Frame1.png")).convert(),
                (enemy_size_w, enemy_size_h))
            self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, enemy_size_h/2 + sprite_gap_to_border)

        def update(self):
            
            global enemy_time, LorR_Enemy, LorR_Calc, sprite_timer

            if sprite_timer == 100:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 5", "9", "Frame1.png")).convert(),
                    (enemy_size_w, enemy_size_h))
                self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            
            elif sprite_timer == 75:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 5", "9", "Frame2.png")).convert(),
                    (enemy_size_w, enemy_size_h))
                self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            
            elif sprite_timer == 50:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 5", "9", "Frame3.png")).convert(),
                    (enemy_size_w, enemy_size_h))
                self.surf.set_colorkey((255, 0, 255), RLEACCEL)
            
            elif sprite_timer == 25:
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Level 5", "9", "Frame4.png")).convert(),
                    (enemy_size_w, enemy_size_h))
                self.surf.set_colorkey((255, 0, 255), RLEACCEL)

            

            #Enemy Movement
            if enemy_time > 0:
                enemy_time -= 1

                #timer runs out
                if LorR_Enemy >= LorR_Calc:  
                    self.rect.move_ip(-enemy_speed, 0)   #left
                elif LorR_Enemy < LorR_Calc: 
                    self.rect.move_ip(enemy_speed, 0)   #right

            else:
                #Reset
                enemy_time = random.randint(25, 30)
                LorR_Enemy = (enemy1.rect.x - 241.5) / 1437 * 100
                
                #1920 - 483 = 1437

                LorR_Calc = random.randint(0, 100) 
                
            # Keep enemy on the screen
            if self.rect.left < sprite_gap_to_left:
                self.rect.left = sprite_gap_to_left
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH

            if self.rect.top <= 0:
                self.rect.top = 0
            if self.rect.bottom >= SCREEN_HEIGHT:
                self.rect.bottom = SCREEN_HEIGHT

    class Enemy_Bullet(pygame.sprite.Sprite):

        def __init__(self):
            super(Enemy_Bullet, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (bullet_size_w, bullet_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.x = (enemy1.rect.x+25)
            self.rect.y = (enemy1.rect.y)

        def update(self):
            
            global sprite_timer, enemy_bullet1_shot, enemy_bullet2_shot
            
            if enemy_bullet1.rect.top >= SCREEN_HEIGHT:
                enemy_bullet1_shot = False
                enemy_bullet1.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                enemy_bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if enemy_bullet2.rect.top >= SCREEN_HEIGHT:
                enemy_bullet2_shot = False
                enemy_bullet2.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                enemy_bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)

            if enemy_bullet1_shot == True:
                enemy_bullet1.rect.move_ip(0, +bullet_speed)
                if sprite_timer == 100:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame1.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame2.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame3.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame4.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    enemy_bullet1.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame5.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet1.surf.set_colorkey((255, 255, 255), RLEACCEL)
            if enemy_bullet2_shot == True:
                enemy_bullet2.rect.move_ip(0, +bullet_speed)
                if sprite_timer == 100:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame1.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame2.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame3.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame4.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    enemy_bullet2.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bullet", "Frame5.png")).convert(),
                        (bullet_size_w, bullet_size_h))
                    enemy_bullet2.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if enemy_bullet1_shot == False:
                enemy_bullet1.rect.x = (enemy1.rect.x+25)
                enemy_bullet1.rect.y = (enemy1.rect.y)   
                enemy_bullet1.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                enemy_bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)      
            if enemy_bullet2_shot == False:
                enemy_bullet2.rect.x = (enemy1.rect.x+25)
                enemy_bullet2.rect.y = (enemy1.rect.y)  
                enemy_bullet2.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (bullet_size_w, bullet_size_h))
                enemy_bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)           
    class Enemy_Missile(pygame.sprite.Sprite):

        def __init__(self):
            super(Enemy_Missile, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (missile_size_w, missile_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.x = (enemy1.rect.x + 24)
            self.rect.bottom = (enemy1.rect.top)     

        def update(self):
            
            global sprite_timer, enemy_missile_shot

            if enemy_missile_shot == True:
                enemy_missile1.rect.move_ip(0, +missile_speed)

                if sprite_timer == 100:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Missiles", "Frame1.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Missiles", "Frame2.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Missiles", "Frame3.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Missiles", "Frame4.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Missiles", "Frame5.png")).convert(),
                        (missile_size_w, missile_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if enemy_missile_shot == False:
                enemy_missile1.rect.x = (enemy1.rect.x + 24)
                enemy_missile1.rect.bottom = (enemy1.rect.top)
                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (missile_size_w, missile_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
                
            if enemy_missile1.rect.top >= SCREEN_HEIGHT:
                enemy_missile_shot = False
    class Enemy_Bomb(pygame.sprite.Sprite):

        def __init__(self):
            super(Enemy_Bomb, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (bomb_size_w, bomb_size_h))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.x = (enemy1.rect.x + 24)
            self.rect.top = (enemy1.rect.bottom)

        def update(self):
            
            global sprite_timer, enemy_bomb_shot

            if enemy_bomb_shot == True:
                enemy_bomb1.rect.move_ip(0, +bomb_speed)

                if sprite_timer == 100:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bombs", "Frame1.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 80:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bombs", "Frame2.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 60:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bombs", "Frame3.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 40:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bombs", "Frame4.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

                elif sprite_timer == 20:
                    self.surf = pygame.transform.scale(
                        pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons", "Bombs", "Frame5.png")).convert(),
                        (bomb_size_w, bomb_size_h))
                    self.surf.set_colorkey((255, 255, 255), RLEACCEL)

            if enemy_bomb_shot == False:
                enemy_bomb1.rect.x = (enemy1.rect.x + 24)
                enemy_bomb1.rect.top = (enemy1.rect.bottom)

                self.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Enemies", "Weapons","SetAs'00FFFF'.png")).convert(),
                    (bomb_size_w, bomb_size_h))
                self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            if enemy_bomb1.rect.top >= SCREEN_HEIGHT:
                enemy_bomb_shot = False

    class Explode(pygame.sprite.Sprite):

        def __init__(self):
            super(Explode, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH, SCREEN_HEIGHT)   

        def update(self):
            
            global sprite_timer, explode_true

            explode_sleep = 0.05

            bullet1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            bullet2.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)
            missile1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            missile1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            bomb1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            bomb1.surf.set_colorkey((0, 255, 255), RLEACCEL)

            enemy_bullet1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            enemy_bullet1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            enemy_bullet2.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            enemy_bullet2.surf.set_colorkey((0, 255, 255), RLEACCEL)
            enemy_missile1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            enemy_missile1.surf.set_colorkey((0, 255, 255), RLEACCEL)
            enemy_bomb1.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (150, 150))
            enemy_bomb1.surf.set_colorkey((0, 255, 255), RLEACCEL)




            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-1.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-2.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-3.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-4.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-5.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-6.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-7.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-8.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-9.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-10.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-11.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-12.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-13.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-14.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            if deadP == True:
                player.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (150, 150))
                player.surf.set_colorkey((0, 255, 255), RLEACCEL)
            elif deadP == False:
                enemy1.surf = pygame.transform.scale(
                    pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                    (150, 150))
                enemy1.surf.set_colorkey((0, 255, 255), RLEACCEL)

            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-15.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-16.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-17.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-18.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-19.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-20.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-21.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-22.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-23.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Explosion", "Explosion-24.png.png")).convert(),
                (150, 150))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
    class Game_over(pygame.sprite.Sprite):

        def __init__(self):
            super(Game_over, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)    

        def update(self):

            explode_sleep = 0.05
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over--1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(1.2)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-0.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(0.14)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over--1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(0.7)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-0.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(1.2)

            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-2.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-3.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-4.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-5.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-6.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-7.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-8.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-9.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-10.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-11.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-12.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-13.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-14.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-15.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-16.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-17.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-18.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-19.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-20.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "game_over-21.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()

            menu(BASE_DIR)   
    class Success(pygame.sprite.Sprite):

        def __init__(self):
            super(Success, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)    

        def update(self):

            explode_sleep = 0.05
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(1.2)

            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-2.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-3.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-4.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-5.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-6.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-7.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-8.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-9.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-10.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-11.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-12.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-13.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-14.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-15.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-16.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-17.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-18.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-19.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-20.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-21.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-22.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-23.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-24.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-25.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            time.sleep(explode_sleep)
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-26.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()

            menu(BASE_DIR)   


    explode1 = Explode()
    game_over = Game_over()
    success = Success()

    # Instantiate sprites
    player = Player()

    bullet1 = Bullet()
    bullet2 = Bullet()
    missile1 = Missile()
    bomb1 = Bomb()

    enemy1 = Enemy()

    enemy_bullet1 = Enemy_Bullet()
    enemy_bullet2 = Enemy_Bullet()
    enemy_missile1 = Enemy_Missile()
    enemy_bomb1 = Enemy_Bomb()

    #Groups
    players = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    missiles = pygame.sprite.Group()
    bombs = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    enemy_missiles = pygame.sprite.Group()
    enemy_bombs = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()

    players.add(player
                )
    enemies.add(enemy1,
                )
    bullets.add(bullet1,
                bullet2
                )
    missiles.add(missile1
                 )
    bombs.add(bomb1
              )
    enemy_bullets.add(enemy_bullet1,
                enemy_bullet2
                )
    enemy_missiles.add(enemy_missile1
                 )
    enemy_bombs.add(enemy_bomb1
              )
    all_sprites.add(bullet1,
                    bullet2,
                    missile1,
                    bomb1, 
                    enemy_bullet1,
                    enemy_bullet2,
                    enemy_missile1,
                    enemy_bomb1,
                    player, 
                    enemy1,
                    explode1,
                    game_over,
                    success
                    )
    
    bullet_delay_time = 0
    bullet_delay_base = 20
    missile_delay_time = 0
    missile_delay_base = 75
    bomb_delay_time = 0
    bomb_delay_base = 75

    enemy_bullet_delay_time = 0
    enemy_bullet_delay_base = 20
    enemy_missile_delay_time = 0
    enemy_missile_delay_base = 75
    enemy_bomb_delay_time = 0
    enemy_bomb_delay_base = 75

    def bullets_updating():
        bullet1.update()
        bullet2.update()

    #GAME LOOP ITSELF
    while running:
        true = True
        for event in pygame.event.get():            
            if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
                game_to_menu(BASE_DIR)

        # Get all the keys currently pressed
        pressed_keys = pygame.key.get_pressed()
        Thread1 = threading.Thread(player.update(pressed_keys))
        Thread2 = threading.Thread(enemy1.update())
        Thread3 = threading.Thread(target = bullets_updating)
        Thread5 = threading.Thread(missile1.update())
        Thread6 = threading.Thread(bomb1.update())
        Thread7 = threading.Thread(enemy_bullet1.update())
        Thread8 = threading.Thread(enemy_bullet2.update())
        Thread9 = threading.Thread(enemy_missile1.update())
        Thread10 = threading.Thread(enemy_bomb1.update())

        Thread1.start()
        Thread2.start()
        Thread3.start()
        Thread5.start()
        Thread6.start()
        Thread7.start()
        Thread8.start()
        Thread9.start()
        Thread10.start()

        
        if sprite_timer == 0:
            sprite_timer = 100 
        else:
            sprite_timer -= 5

        #Kills player bullets
        if pygame.sprite.spritecollideany(bullet1, enemies):
            bullet1_shot = False
            enemy1_health -= player_bullet_damage
        if pygame.sprite.spritecollideany(bullet2, enemies):
            bullet2_shot = False
            enemy1_health -= player_bullet_damage
        if pygame.sprite.spritecollideany(missile1, enemies):
            missile_shot = False
            enemy1_health -= player_missile_damage
        if pygame.sprite.spritecollideany(bomb1, enemies):
            bomb_shot = False
            enemy1_health -= player_bomb_damage
        #Kills enemy bullets
        if pygame.sprite.spritecollideany(enemy_bullet1, players):
            enemy_bullet1_shot = False
            player_health -= enemy1_bullet_damage
        if pygame.sprite.spritecollideany(enemy_bullet2, players):
            enemy_bullet2_shot = False
            player_health -= enemy1_bullet_damage
        if pygame.sprite.spritecollideany(enemy_missile1, players):
            enemy_missile_shot = False
            player_health -= enemy1_missile_damage
        if pygame.sprite.spritecollideany(enemy_bomb1, players):
            enemy_bomb_shot = False
            player_health -= enemy1_bomb_damage
    
        #Kills player
        if player_health <= 0:
            player.kill()
            screen.blit(background_image, (0, 0))
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)
            pygame.display.flip()
            explode1.rect.center = player.rect.center
            deadP = True
            explode1.update()
            time.sleep(1.5)
            game_over.update()
            score0 += 200 * enemy_multiplier
            next_level(BASE_DIR)        
        #kills enemy
        if enemy1_health <= 0:
            if pygame.sprite.spritecollideany(enemy1, bullets):
                enemy1.kill()
                screen.blit(background_image, (0, 0))
                for entity in all_sprites:
                    screen.blit(entity.surf, entity.rect)
                pygame.display.flip()
                explode1.rect.center = enemy1.rect.center
                deadP = False
                explode1.update()
                time.sleep(1.5)
                success.update()
                score0 += enemy_strength
                menu(BASE_DIR)
            if pygame.sprite.spritecollideany(enemy1, missiles):
                enemy1.kill()
                screen.blit(background_image, (0, 0))
                for entity in all_sprites:
                    screen.blit(entity.surf, entity.rect)
                pygame.display.flip()
                explode1.rect.center = enemy1.rect.center
                deadP = False
                explode1.update()
                time.sleep(1.5)
                success.update()
                score0 += enemy_strength
                menu(BASE_DIR)
            if pygame.sprite.spritecollideany(enemy1, bombs):
                enemy1.kill()
                screen.blit(background_image, (0, 0))
                for entity in all_sprites:
                    screen.blit(entity.surf, entity.rect)
                pygame.display.flip()
                explode1.rect.center = enemy1.rect.center
                deadP = False
                explode1.update()
                time.sleep(1.5)
                success.update()
                score0 += enemy_strength
                menu(BASE_DIR)

        enemy_bullet_chance = random.randint(1,50)
        enemy_missile_chance = random.randint(1,50)
        enemy_bomb_chance = random.randint(1,50)

        if enemy_bullet_chance == 5:
            if enemy_bullet_delay_time <= 0:
                if enemy_bullet1_shot == False:
                    enemy_bullet1_shot = True
                    enemy_bullet_delay_time = enemy_bullet_delay_base
                elif enemy_bullet1_shot and enemy_bullet2_shot == False:
                    enemy_bullet2_shot = True
                    enemy_bullet_delay_time = enemy_bullet_delay_base

        if enemy_missile_chance == 5:
            if enemy_missile_delay_time <= 0:
                if enemy_missile_shot == False:
                    enemy_missile_shot = True
                    enemy_missile_delay_time = enemy_missile_delay_base

        if enemy_bomb_chance == 5:
            if enemy_bomb_delay_time <= 0:
                if enemy_bomb_shot == False:
                    enemy_bomb_shot = True
                    enemy_bomb_delay_time = enemy_bomb_delay_base
        

        enemy_bullet_delay_time -= 2
        enemy_missile_delay_time -= 2
        enemy_bomb_delay_time -= 2

        pressed_keys = pygame.key.get_pressed()
        mouse_button = pygame.mouse.get_pressed()

        if mouse_button[0]:
            if bullet_delay_time <= 0:
                if bullet1_shot == False:
                    bullet1_shot = True
                    bullet_delay_time = bullet_delay_base
                elif bullet1_shot and bullet2_shot == False:
                    bullet2_shot = True
                    bullet_delay_time = bullet_delay_base

        if mouse_button[2]:
            if missile_delay_time <= 0:
                if missile_shot == False:
                    missile_shot = True
                    missile_delay_time = missile_delay_base

        if pressed_keys[K_SPACE]:
            if bomb_delay_time <= 0:
                if bomb_shot == False:
                    bomb_shot = True
                    bomb_delay_time = bomb_delay_base
        
        bullet_delay_time -= 2
        missile_delay_time -= 2
        bomb_delay_time -= 2

        Health_Player = textfont.render(f" {player_health}", 1, (255,255,255))
        Health_Enemy = textfont.render(f" {enemy1_health}", 1, (255,255,255))

        
        #space.update() idk if i like this or if it can be made to be perfect in near future

        Thread1.join()
        Thread2.join()
        Thread3.join()
        Thread5.join()
        Thread6.join()
        Thread7.join()
        Thread8.join()
        Thread9.join()
        Thread10.join()

        #Cirtical Screen Stuff
        screen.blit(background_image, (0, 0))
        for entity in all_sprites:
            screen.blit(entity.surf, entity.rect)
        screen.blit(Health_Player, (60, 175))
        screen.blit(Health_Enemy, (60, 500))
        pygame.display.flip()
        clock.tick(hz)

    pygame.quit()
    sys.exit()

def add_score():
    if score0 == 0:
        pass

#Next Level
def next_level(BASE_DIR):
    #ESSENTIAL CODE DO NOT TOUCH
    global SCREEN_HEIGHT, SCREEN_WIDTH
    global background_image1
    pygame.init()
    pygame.joystick.init()
    clock = pygame.time.Clock()
    running = True
    #variables
    hz = 24
    placeholder = "" #can be changed with no effect
    menu_choice = ""
    settings_choice = ""
    sprite_timer = 100
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
    background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level Select", "next_level-1.png.png")), (SCREEN_WIDTH, SCREEN_HEIGHT))
    menu_in_use = 1
    details_sent = False

    if score0 == 510 or score0 == 1530 or score0 == 3570: #level 0/7 boss
        # success
        pass
    elif score0 == 8670:
        # game complete
        pass

    #Create the screen object
    #The size is determined by the constant WIDTH and HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.RESIZABLE) 
    pygame.display.set_caption("Last Stand")
    
    class Menu(pygame.sprite.Sprite):
        def __init__(self):
            super(Menu, self).__init__()
            self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

        def update(self, pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR):

            if pressed_keys[K_UP]:
                menu_in_use = 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level Select", f"next_level-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            if pressed_keys[K_DOWN]:
                menu_in_use = 2 
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level Select", f"next_level-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 1:
                
                if   score0 == 10 or score0 == 530 or score0 == 1570 or score0 == 3670: #level 2
                    game2()
                elif score0 == 30 or score0 == 570 or score0 == 1650 or score0 == 3870: #level 2
                    game3()
                elif score0 == 70 or score0 == 650 or score0 == 1810 or score0 == 4270: #level 3
                    game4()
                elif score0 == 130 or score0 == 770 or score0 == 2040 or score0 == 4870: #level 4
                    game5()
                elif score0 == 210 or score0 == 930 or score0 == 2370 or score0 == 5670: #level 5
                    game6()
                elif score0 == 310 or score0 == 1130 or score0 == 2770 or score0 == 6670: #level 6
                    game7()
                elif score0 == 510 or score0 == 1530 or score0 == 3570 or score0 == 8670: #level 0/7 boss
                    if   enemy_multiplier == 1:
                        enemy_multiplier = 2
                    elif enemy_multiplier == 2:
                        enemy_multiplier = 4
                    elif enemy_multiplier == 4:
                        enemy_multiplier = 10
                    elif enemy_multiplier == 10:
                        enemy_multiplier = 100
                    if enemy_multiplier == 100:
                        menu(BASE_DIR)
                    else:
                        game1()
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 2:
                menu(BASE_DIR)
            
            return menu_in_use, sprite_timer, background_image1, 

    Menu1 = Menu()

    #GAME LOOP ITSELF
    while running:
        true = True
        for event in pygame.event.get():            
            pressed_keys = pygame.key.get_pressed()
            menu_in_use, sprite_timer, background_image1,  = Menu1.update(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
             
        
        #Cirtical Screen Stuff
        screen.blit(Menu1.surf, Menu1.rect)        
        pygame.display.flip()
        clock.tick(10)

    pygame.quit()
    sys.exit()

#Victory
def victory(BASE_DIR):
    #ESSENTIAL CODE DO NOT TOUCH
    global SCREEN_HEIGHT, SCREEN_WIDTH  # Returns Size(width=1920, height=1080) []

    global background_image1
    pygame.init()
    pygame.joystick.init()
    clock = pygame.time.Clock()
    running = True
    #variables
    hz = 24
    placeholder = "" #can be changed with no effect
    menu_choice = ""
    settings_choice = ""
    sprite_timer = 100
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
    background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level Select", "next_level-1.png.png")), (SCREEN_WIDTH, SCREEN_HEIGHT))
    menu_in_use = 1
    details_sent = False

    #Create the screen object
    #The size is determined by the constant WIDTH and HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.RESIZABLE) 
    pygame.display.set_caption("Last Stand")
    
    class Success(pygame.sprite.Sprite):

        def __init__(self):
            super(Success, self).__init__()
            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Player", "Weapons", "SetAs'00FFFF'.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)   

        def update(self):

            explode_sleep = 0.05

            self.surf = pygame.transform.scale(
                pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Game over", "Success-1.png.png")).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.surf.set_colorkey((0, 255, 255), RLEACCEL)
            screen.blit(background_image, (0, 0))
            screen.blit(Menu1.surf, Menu1.rect)
            pygame.display.flip()
            time.sleep(1.2)

            pygame.display.flip()

            menu(BASE_DIR)

    class Menu(pygame.sprite.Sprite):
        def __init__(self):
            super(Menu, self).__init__()
            self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.rect = self.surf.get_rect()
            self.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

        def update(self, pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR):

            if pressed_keys[K_UP]:
                menu_in_use = 1
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level Select", f"next_level-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            if pressed_keys[K_DOWN]:
                menu_in_use = 2 
                background_image1 = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "Sprites", "Other", "Level Select", f"next_level-{menu_in_use}.png.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.surf = pygame.transform.scale(background_image1.convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 1:
                
                if   score0 == 10 or score0 == 530 or score0 == 1570 or score0 == 3670: #level 2
                    game1()
                elif score0 == 30 or score0 == 570 or score0 == 1650 or score0 == 3870: #level 2
                    game2()
                elif score0 == 70 or score0 == 650 or score0 == 1810 or score0 == 4270: #level 3
                    game3()
                elif score0 == 130 or score0 == 770 or score0 == 2040 or score0 == 4870: #level 4
                    game4()
                elif score0 == 210 or score0 == 930 or score0 == 2370 or score0 == 5670: #level 5
                    game5()
                elif score0 == 310 or score0 == 1130 or score0 == 2770 or score0 == 6670: #level 6
                    game6()
                elif score0 == 510 or score0 == 1530 or score0 == 3570 or score0 == 8670: #level 0/7 boss
                    victory() # win the dificulty
                else:
                    pass #competed all
            if event.type == KEYDOWN and pressed_keys[K_RETURN] and menu_in_use == 2:
                menu(BASE_DIR)
            
            return menu_in_use, sprite_timer, background_image1, 

    Menu1 = Menu()

    #GAME LOOP ITSELF
    while running:
        true = True
        for event in pygame.event.get():            
            pressed_keys = pygame.key.get_pressed()
            menu_in_use, sprite_timer, background_image1,  = Menu1.update(pressed_keys, menu_in_use, sprite_timer, background_image1, BASE_DIR)
             
        
        #Cirtical Screen Stuff
        screen.blit(Menu1.surf, Menu1.rect)        
        pygame.display.flip()
        clock.tick(10)

    pygame.quit()
    sys.exit()

get_storage_data()

game6()

menu(BASE_DIR)
