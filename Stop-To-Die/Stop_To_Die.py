import pygame, sys,os
import random, math
from pygame import mixer

pygame.init()
mixer.init()
pygame.display.init()
vec = pygame.math.Vector2
pygame.event.get()
#Creating the screen

Width = 1920
Height = 1200
screen_center = [Width/2,Height/2]
#Variables
pygame.init()
done = False
clock = pygame.time.Clock()
pygame.event.set_grab(True)
game_paused = False
create_enemy = True
is_firing = False
menu_state = "main"
sould_create_enemy = 0
difficulty = 1
max_enem = 200
cr_enem = 0
change_frame = 0
frame_cycle = 0
level_up_progress = 0
level_up_max = 100
all_player_projectiles = []
sfx = "Sfx"
sourceFileDir = os.path.dirname(os.path.abspath(__file__))


#Menu screen stuff

    #Defining fonts
font = pygame.font.SysFont("Pixelated Regular", 40)

    #Defining colours
white = (255, 255, 255)


enemy_hurt_sound = pygame.mixer.Sound(os.path.join("Sfx" , 'Damaged.mp3'))
enemy_hurt_sound.set_volume(0.5)

pickup_sound = pygame.mixer.Sound(os.path.join("Sfx" , 'Pick_up.mp3'))
pickup_sound.set_volume(0.5)

''' -------- Classes  -------- '''
class Button():
    def __init__(self, x, y, image):
        self.width = image.get_width()
        self.height = image.get_height()
        self.image = pygame.transform.scale(image, (self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
    def draw(self, surface):
        #get mouse position
        pos = pygame.mouse.get_pos()

        #check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
            #self.image = pygame.transform.smoothscale(self.image(1.1,1.1))

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        #draw button on screen
        surface.blit(self.image, (self.rect.x, self.rect.y))


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        # camera offset
        self.offset = pygame.math.Vector2()
        self.half_w = self.display_surface.get_size()[0] // 2
        self.half_h = self.display_surface.get_size()[1] // 2

        # box setup
        self.camera_borders = {'left': 200 , 'right': 200 , 'top': 100 , 'bottom': 100}
        l = self.camera_borders['left']
        t = self.camera_borders['top']
        w = self.display_surface.get_size()[0] - (self.camera_borders['left'] + self.camera_borders['right'])
        h = self.display_surface.get_size()[1] - (self.camera_borders['top'] + self.camera_borders['bottom'])
        self.camera_rect = pygame.Rect(l, t, w, h)

        # ground
        self.ground_surf = pygame.image.load('Sprites/BG.png').convert()
        self.ground_surf = pygame.transform.scale(self.ground_surf, (9000,9000))
        self.ground_rect = self.ground_surf.get_rect(topleft=(-2500 , -2500))

        # zoom
        self.zoom_scale = 0.5

        """""REMEMBER TO USE WHEN ADDING INTERFACE THANK ME LATER OK BYE NOW"""
        self.internal_surf_size = (4000, 3000)
        self.internal_surf = pygame.Surface(self.internal_surf_size , pygame.SRCALPHA)
        self.internal_rect = self.internal_surf.get_rect(center=(self.half_w , self.half_h))
        self.internal_surface_size_vector = pygame.math.Vector2(self.internal_surf_size)
        self.internal_offset = pygame.math.Vector2()
        self.internal_offset.x = self.internal_surf_size[0] // 2 - self.half_w
        self.internal_offset.y = self.internal_surf_size[1] // 2 - self.half_h

    def center_target_camera(self , target):
        self.offset.x = target.rect.centerx - self.half_w
        self.offset.y = target.rect.centery - self.half_h

    def custom_draw(self,player):

        self.center_target_camera(player)

        self.internal_surf.fill('#71ddee')

        ground_offset = self.ground_rect.topleft - self.offset + self.internal_offset
        self.internal_surf.blit(self.ground_surf, ground_offset)

        # active elements
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset + self.internal_offset
            self.internal_surf.blit(sprite.image_selected, offset_pos)
        scaled_surf = pygame.transform.scale(self.internal_surf, self.internal_surface_size_vector * self.zoom_scale)
        scaled_rect = scaled_surf.get_rect(center=(self.half_w, self.half_h))

        #self.display_surface.blit(scaled_surf, scaled_rect)

        self.display_surface.blit(scaled_surf, scaled_rect)


#class Upgrade(pygame.sprite.Sprite):
    #def __init__(self,group, image_group):
        #super().__init__(group)


        #setting a variable for the image and the upgrade's purpose
        #self.upgrade_do = random.randint(0,0)
        #self.image_selected = image_group[self.upgrade_do]
        #self.rect = self.image_selected.get_rect()
        #self.rect.topleft = (0,0)
        #self.clicked = False

    def update(self, surface,pos):
        self.rect.topleft = pos
        #self.image_selected = pygame.transform.smoothscale(self.image_selected, (50,75))
        #get mouse position
        pos = pygame.mouse.get_pos()

        #check mouseover and clicked conditions

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if self.rect.collidepoint(pos):
                    if pygame.mouse.get_pressed()[0] == 1:
                        return self.upgrade_do

        #if pygame.mouse.get_pressed()[0] == 0:
            #self.clicked = False

        #draw button on screen
        surface.blit(self.image_selected, (self.rect.x, self.rect.y))


class Player(pygame.sprite.Sprite):
    def __init__(self, pos ,group,image_lists):
        super().__init__(group)
        self.pos = vec(pos)
        self.image_lists = image_lists
        self.image_regular = self.image_lists[0][0]
        self.image_selected = self.image_regular
        self.rect = self.image_selected .get_rect(center = pos)
        self.direction = pygame.math.Vector2()
        self.speed = 7
        self.base_damage = 15
        self.Max_HP = 100
        self.HP = 100
        self.iframes = 0
        self.frame = 0
        self.reload_cr = 0
        self.looking = "left"
    def frame_change(self,bullet_spawn_timer):
        if self.direction.x == 0 and self.direction.y == 0 and bullet_spawn_timer > 50:
            self.selected_list = self.image_lists[1]
        elif self.direction.x == 0 and self.direction.y == 0 and bullet_spawn_timer <= 50:
            self.selected_list = self.image_lists[2]
        else:
            self.selected_list = self.image_lists[0]



        self.frame += 0.25
        if self.frame >= float(len(self.selected_list)):
            self.frame = 0
        self.image_selected = self.selected_list[int(self.frame)]


        #if self.looking == "right":
            #self.image_selected = self.image_regular
        #elif self.looking == "left":
            #self.image_selected = self.image_fliped

    def update(self,bullet_spawn_timer):
        keys = pygame.key.get_pressed()
        # Y change
        if keys[pygame.K_w]:    self.direction.y = -1
        elif keys[pygame.K_s]:  self.direction.y = 1
        else:   self.direction.y = 0
        # X change
        if keys[pygame.K_d]:
            self.direction.x = 1
            self.looking = "right"
        elif keys[pygame.K_a]:
            self.direction.x = -1
            self.looking = "left"

        else:   self.direction.x = 0


        self.frame_change(bullet_spawn_timer)

        # I frames
        if self.iframes > 0: self.iframes -= 1
        self.rect.center += self.direction * self.speed
        self.pos = vec(self.rect.center)

class Bullet_type_1(pygame.sprite.Sprite):
    def __init__(self, group, start_x, start_y, dest_x, dest_y,player,images,accuracy):
        super().__init__(group)
        self.selected_list = images
        self.image_selected = images[0]
        self.rect = self.image_selected.get_rect()
        self.damage = player.base_damage * 1
        self.speed = 15
        self.frame = 0
        self.rect = self.image_selected.get_rect()
        #how accuret the projectiles will be
        self.accuracy = accuracy
        #How many enemies the bullet can pass though
        self.piercing = 2
        # Move the bullet to our starting location
        self.rect.x = start_x
        self.rect.y = start_y


        # Because rect.x and rect.y are automatically converted
        # to integers, we need to create different variables that
        # store the location as floating point numbers. Integers
        # are not accurate enough for aiming.
        self.floating_point_x = start_x
        self.floating_point_y = start_y

        #fixing mouse pos
        dest_x += start_x - 960
        dest_y += start_y - 600

        #changinng the accuracy depending on the spawn bullet timer
        if self.accuracy >= 800:
            self.accuracy = 1
        elif self.accuracy < 800 and self.accuracy > 500:
            self.accuracy = random.uniform(0.95, 1.05)
        else:
            self.accuracy = random.uniform(0.9, 1.1)


        # Calculation the angle in radians between the start points
        # and end points. This is the angle the bullet will travel.
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        self.angle = math.atan2(y_diff , x_diff) * self.accuracy

        #rotating the image
        self.selected_list = [pygame.transform.rotate(self.selected_list[0],self.angle * -60),
                              pygame.transform.rotate(self.selected_list[1],self.angle * -60),
                              pygame.transform.rotate(self.selected_list[2],self.angle * -60),
                              pygame.transform.rotate(self.selected_list[3],self.angle * -60),
                              pygame.transform.rotate(self.selected_list[4],self.angle * -60),
                              pygame.transform.rotate(self.selected_list[5],self.angle * -60)]

        # Taking into account the angle, calculate our change_x
        # and change_y. Velocity is how fast the bullet travels.
        self.change_x = math.cos(self.angle) * self.speed
        self.change_y = math.sin(self.angle) * self.speed


    def update(self,player):
        """ Move the bullet. """

        # The floating point x and y hold our more accurate location.
        self.floating_point_y += self.change_y
        self.floating_point_x += self.change_x

        # The rect.x and rect.y are converted to integers.
        self.rect.y = int(self.floating_point_y)
        self.rect.x = int(self.floating_point_x)


        #frame changing
        self.frame += 0.25
        if self.frame >= float(len(self.selected_list)):
            self.frame = 0
        self.image_selected = self.selected_list[int(self.frame)]

        #delete self if out of screen
        #Top
        if self.rect.y < player.rect.y - 1100:
            self.kill()
        #Down
        if self.rect.y > player.rect.y + 1100:
            self.kill()
        #Left
        if self.rect.x >player.rect.x + 2000:
            self.kill()
        #Right
        if self.rect.x < player.rect.x - 2000:
            self.kill()
    def hit(self):
        self.piercing -=1
        if self.piercing > 0:
            return
        if self.piercing >= 0:
            self.kill()

class Enemy_type_1(pygame.sprite.Sprite):
    def __init__(self,group,images):
        super().__init__(group)
        self.pos = vec(0,0)
        self.speed = 5
        self.damage = 10
        self.HP = 20
        self.iframes = 0
        self.frame = 0
        self.animate = False
        self.frame_cycle = 0
        self.image_lists = images
        self.image_selected = self.image_lists[0][0]
        self.rect = self.image_selected.get_rect(center=self.pos)
    def spawn(self,player):
        self.spawn_dir = random.randint(1,4)
        #Top
        if self.spawn_dir == 1:
            self.spawn_loc = [random.randint(int(player.rect.x- 2250),int(player.rect.x +2250)),player.rect.y - 1100]
        #Down
        if self.spawn_dir == 2:
            self.spawn_loc = [random.randint(int(player.rect.x- 2250),int(player.rect.x +2250)), player.rect.y + 1100]
        #Left
        if self.spawn_dir == 3:
            self.spawn_loc = [player.rect.x + 2000, random.randint(int(player.rect.y - 1100),int(player.rect.y +1100))]
        #Right
        if self.spawn_dir == 4:
            self.spawn_loc = [player.rect.x - 2000, random.randint(int(player.rect.y - 1100),int(player.rect.y +1100))]
        self.pos = vec(self.spawn_loc)
        self.rect = self.image_selected.get_rect(center = self.spawn_loc)
    def update(self,player,x,y):

        if x != 0:
            return self.pos.x
        if y != 0:
            return  self.pos.y
        #reduce iframes
        if self.iframes > 0:
            self.iframes -= 1

        if self.HP >= 0:
            self.frame_change()
            # locate player
            angle_radians = (math.atan2(self.pos.y - player.pos.y , self.pos.x - player.pos.x))
            self.pos.y -= math.sin(angle_radians) * self.speed
            self.pos.x -= math.cos(angle_radians) * self.speed
        else:
            self.death_animation()


        self.rect = self.image_selected.get_rect(center=self.pos)
    def frame_change(self):
        if self.iframes > 0:
            self.selected_list = self.image_lists[1]
            self.frame +=1
        else:
            self.selected_list = self.image_lists[0]
            self.frame += 0.25



        if self.frame >= float(len(self.selected_list)):
            self.frame = 0
        self.image_selected = self.selected_list[int(self.frame)]
    def hit(self,damage):
        self.HP -= damage
        self.iframes = 20
    def death_animation(self):

        self.selected_list = self.image_lists[2]
        self.frame += 0.25
        if self.frame >= float(len(self.selected_list)):
            self.frame = 0
            self.kill()
        self.image_selected = self.selected_list[int(self.frame)]

class Pick_up_1(pygame.sprite.Sprite):
    def __init__(self,group,image_lists):
        super().__init__(group)
        self.image_lits = image_lists
        self.image_selected = self.image_lits[0]
        self.image_selected = pygame.transform.scale(self.image_selected, (60, 60))
        self.rect = self.image_selected.get_rect()
    def spawn(self,pos):
        self.pos = vec(pos)
        self.rect = self.image_selected.get_rect(center=self.pos)
    #def collision(self):
        #self.kill()


''' -------- GAME  -------- '''

class Game_loop():
    def __init__(self):
        self.screen = pygame.display.set_mode((Width, Height))
        self.screen.fill('#1c0818')
        self.camera_group = CameraGroup()
        self.images()
        self.Player = Player((960, 600), self.camera_group,self.images_Player_all_lists)
        pygame.display.flip()
        pygame.mouse.set_visible(False)
        self.update_hp_bar()
        self.level_up_progress = 0
        self.level_up_max = 100
        self.game_paused = False
        self.level_up = False
        ''' ---- Variables ---- '''
            #for enemies
        self.create_enemy = False
        self.cr_enem = 0
        self.sould_create_enemy = 0
        self.spawn_bullet_timer = 1000

            #for player
        self.spawn_bullet_cr = False
        ''' ---- Groups ---- '''
        self.all_enemies = pygame.sprite.Group()
        self.all_pick_ups = pygame.sprite.Group()
        self.all_player_projectiles = pygame.sprite.Group()
        self.all_players = pygame.sprite.Group()
        #self.all_players.add(self.Player)
        ''' ---- Buttons ---- '''
        #Start
        self.start_button = Button(Width / 2 - 175, 400, self.menu_button_start_image)
        self.resume_button = Button(Width / 2 - 175, 400, self.menu_button_resume_image)
        self.quit_button = Button(Width / 2 - 175, 800, self.menu_button_quit_image)
        self.back_button = Button(Width / 2 - 175, 600, self.menu_button_back_image)
        self.menu_buttons = [self.start_button, self.quit_button]
        self.paused_buttons = [self.resume_button, self.back_button, self.quit_button]
        #Upgrades
        #self.upgrade_btn_1 = Upgrade(self.camera_group,self.all_upgrades)
        #self.upgrade_btns = [self.upgrade_btn_1]
        ''' ---- User Events ---- '''
        self.spawn_bullet: int = pygame.USEREVENT + 0
        self.spawn_bullet_request = pygame.USEREVENT + 1
        self.spawn_enemy: int = pygame.USEREVENT + 2
        #self.spawn_pick_up: int = pygame.USEREVENT + 3

        ''' ---- User Event Activation---- '''

        pygame.time.set_timer(self.spawn_enemy, 1000)
    #def upgrade_updates(self):
        #pos1 = vec(500 , 500)
        #for sprite in self.upgrade_btns:
            #if sprite.update(self.screen, pos1) != "None":
                #print("e")
                #self.level_up = False


       # for event in pygame.event.get():
           # if event.type == pygame.QUIT:
               # pygame.quit()
                #s#ys.exit()
            #if event.type == pygame.MOUSEBUTTONUP:
                #pos = pygame.mouse.get_pos()

                # get a list of all sprites that are under the mouse cursor
                #clicked_sprites = [s for s in sprites if s.rect.collidepoint(pos)]

    def updates(self):
        self.screen.fill((255, 255, 255))
        self.Player.update(self.spawn_bullet_timer)
        self.Player_bullet_charging()
        self.camera_group.custom_draw(self.Player)
        self.update_hp_bar()
        self.update_exp_bar()
        self.screen.blit(self.exp_png, (600, 0))
        self.screen.blit(self.Hp, self.HpRect)


        self.all_enemies.update(self.Player,0,0)
        self.all_player_projectiles.update(self.Player)

        self.update_cursor(self.cursor_image1_rect,self.cursor_image1)

        #Collisions
        #   i) Collision Player - Enemies
        if pygame.sprite.spritecollideany(self.Player, self.all_enemies) and self.Player.iframes <= 0:
            self.Player.HP -= 10
            self.Player.iframes = 20
        # ii) Collisions Player - Pickups
        player_pick_up_collision =  pygame.sprite.groupcollide(self.all_players, self.all_pick_ups,False , False)
        for player, pick_up in player_pick_up_collision.items():
            pick_up[0].kill()
            print("e")
            #self.level_up_progress += 10



        # iii) Collision Player projectile - Enemies
        player_projectile_enemy_hit = pygame.sprite.groupcollide(self.all_enemies, self.all_player_projectiles ,False ,False)
        for enemy, bullet in player_projectile_enemy_hit.items():
            if enemy.iframes <= 0:
                enemy.hit(bullet[0].damage)
                bullet[0].hit()
                if enemy.HP <= 0:
                    #spawn pick ups
                    enemy.update(self.Player,0,0)
                    #self.Pick_up = Pick_up_1(self.camera_group , self.images_Pick_ups)
                    #self.Pick_up.spawn(enemy.pos)
                    #self.all_pick_ups.add(self.Pick_up)
    def images(self):
        # Button images

        self.menu_button_back_image = pygame.image.load('Sprites/Menu/button_back.png').convert_alpha()
        self.menu_button_back_image = pygame.transform.scale(self.menu_button_back_image, (350, 100))

        self.menu_button_start_image = pygame.image.load("Sprites/Menu/start_image.png").convert_alpha()
        self.menu_button_start_image = pygame.transform.scale(self.menu_button_start_image, (300, 75))

        self.menu_button_quit_image = pygame.image.load("Sprites/Menu/Quit button.png").convert_alpha()
        self.menu_button_quit_image = pygame.transform.scale(self.menu_button_quit_image, (300, 75))

        self.menu_button_resume_image = pygame.image.load("Sprites/Menu/button_resume.png").convert_alpha()
        self.menu_button_resume_image = pygame.transform.scale(self.menu_button_resume_image, (300, 75))

        # General imagry

        self.health_BG = pygame.image.load('Sprites/HP_Bar_BG.png').convert_alpha()
        self.health_BG = pygame.transform.scale(self.health_BG, (250, 150))

        self.exp_bar_BG = pygame.image.load('Sprites/EXP_bar.png').convert_alpha()
        self.exp_bar_BG = pygame.transform.scale(self.exp_bar_BG, (750,100))

        self.title_image = pygame.image.load('Sprites/Menu/Main_title.png').convert_alpha()
        self.title_image = pygame.transform.scale(self.title_image , (500 , 100))

        self.cursor_image1 = pygame.image.load('Sprites/Cursor_1.png').convert_alpha()
        self.cursor_image1 = pygame.transform.scale(self.cursor_image1 , (32 , 32))
        self.cursor_image1_rect = self.cursor_image1.get_rect()

        self.cursor_image2 = pygame.image.load('Sprites/Cursor_2.png').convert_alpha()
        self.cursor_image2 = pygame.transform.scale(self.cursor_image2, (32, 32))
        self.cursor_image2_rect = self.cursor_image2.get_rect()

        ''' ---- Upgrades ---- '''

        self.image_Upgrade_1= pygame.image.load("Sprites/Upgrades/Upgrade_1.png").convert_alpha()
        self.image_Upgrade_1 = pygame.transform.scale(self.image_Upgrade_1, (120, 130))


        self.all_upgrades = [self.image_Upgrade_1]

        ''' ---- Enemy Animations ---- '''

            #Enemy 1
                #Walking
        self.image_Enemy1_walking_F1 = pygame.image.load(
            "Sprites/Enemy_1/Walking/Enemy_1_walking_F1.png").convert_alpha()
        self.image_Enemy1_walking_F1 = pygame.transform.scale(self.image_Enemy1_walking_F1, (120, 130))

        self.image_Enemy1_walking_F2 = pygame.image.load(
            "Sprites/Enemy_1/Walking/Enemy_1_walking_F2.png").convert_alpha()
        self.image_Enemy1_walking_F2 = pygame.transform.scale(self.image_Enemy1_walking_F2, (120, 130))

        self.image_Enemy1_walking_F3 = pygame.image.load(
            "Sprites/Enemy_1/Walking/Enemy_1_walking_F3.png").convert_alpha()
        self.image_Enemy1_walking_F3 = pygame.transform.scale(self.image_Enemy1_walking_F3, (120, 130))

        self.image_Enemy1_walking_F4 = pygame.image.load(
            "Sprites/Enemy_1/Walking/Enemy_1_walking_F4.png").convert_alpha()
        self.image_Enemy1_walking_F4 = pygame.transform.scale(self.image_Enemy1_walking_F4, (120, 130))

        self.image_Enemy1_walking_F5 = pygame.image.load(
            "Sprites/Enemy_1/Walking/Enemy_1_walking_F5.png").convert_alpha()
        self.image_Enemy1_walking_F5 = pygame.transform.scale(self.image_Enemy1_walking_F5, (120, 130))

        self.images_Enemy1_walking = [self.image_Enemy1_walking_F1,self.image_Enemy1_walking_F2,self.image_Enemy1_walking_F3,
                                   self.image_Enemy1_walking_F4,self.image_Enemy1_walking_F5]

                #hurt
        self.image_Enemy1_hurt_F1 = pygame.image.load("Sprites/Enemy_1/Hurt/Enemy_1_hurt_F1.png").convert_alpha()
        self.image_Enemy1_hurt_F1 = pygame.transform.scale(self.image_Enemy1_hurt_F1, (120, 130))

        self.image_Enemy1_hurt_F2 = pygame.image.load("Sprites/Enemy_1/Hurt/Enemy_1_hurt_F2.png").convert_alpha()
        self.image_Enemy1_hurt_F2 = pygame.transform.scale(self.image_Enemy1_hurt_F2, (120, 130))

        self.images_Enemy1_hurt = [self.image_Enemy1_hurt_F1,self.image_Enemy1_hurt_F2]



        self.image_Enemy1_crumble_F1 = pygame.image.load(
            "Sprites/Enemy_1/Crumble/Enemy_1_Crumble_F1.png").convert_alpha()
        self.image_Enemy1_crumble_F1 = pygame.transform.scale(self.image_Enemy1_crumble_F1, (120, 130))

        self.image_Enemy1_crumble_F2 = pygame.image.load(
            "Sprites/Enemy_1/Crumble/Enemy_1_Crumble_F2.png").convert_alpha()
        self.image_Enemy1_crumble_F2 = pygame.transform.scale(self.image_Enemy1_crumble_F2, (120, 130))

        self.image_Enemy1_crumble_F3 = pygame.image.load(
            "Sprites/Enemy_1/Crumble/Enemy_1_Crumble_F3.png").convert_alpha()
        self.image_Enemy1_crumble_F3 = pygame.transform.scale(self.image_Enemy1_crumble_F3, (120, 130))

        self.image_Enemy1_crumble_F4 = pygame.image.load(
            "Sprites/Enemy_1/Crumble/Enemy_1_Crumble_F4.png").convert_alpha()
        self.image_Enemy1_crumble_F4 = pygame.transform.scale(self.image_Enemy1_crumble_F4, (120, 130))

        self.image_Enemy1_crumble_F5 = pygame.image.load(
            "Sprites/Enemy_1/Crumble/Enemy_1_Crumble_F5.png").convert_alpha()
        self.image_Enemy1_crumble_F5 = pygame.transform.scale(self.image_Enemy1_crumble_F5, (120, 130))

        self.image_Enemy1_crumble_F6 = pygame.image.load(
            "Sprites/Enemy_1/Crumble/Enemy_1_Crumble_F6.png").convert_alpha()
        self.image_Enemy1_crumble_F6 = pygame.transform.scale(self.image_Enemy1_crumble_F6, (120, 130))

        self.images_Enemy1_crumble = [self.image_Enemy1_crumble_F1,self.image_Enemy1_crumble_F2,self.image_Enemy1_crumble_F3,
                                      self.image_Enemy1_crumble_F4,self.image_Enemy1_crumble_F5,self.image_Enemy1_crumble_F6]


        self.images_Enemy1_all_lists = [self.images_Enemy1_walking,self.images_Enemy1_hurt,self.images_Enemy1_crumble]


        ''' ---- Projectile Animations ---- '''

        self.image_Projectile1_F1 = pygame.image.load("Sprites/Bullet_1/Bullet1_F1.png").convert_alpha()
        self.image_Projectile1_F1 = pygame.transform.scale(self.image_Projectile1_F1, (80, 50))

        self.image_Projectile1_F2 = pygame.image.load("Sprites/Bullet_1/Bullet1_F2.png").convert_alpha()
        self.image_Projectile1_F2 = pygame.transform.scale(self.image_Projectile1_F2,(80, 50))

        self.image_Projectile1_F3 = pygame.image.load("Sprites/Bullet_1/Bullet1_F3.png").convert_alpha()
        self.image_Projectile1_F3 = pygame.transform.scale(self.image_Projectile1_F3, (80, 50))

        self.image_Projectile1_F4 = pygame.image.load("Sprites/Bullet_1/Bullet1_F4.png").convert_alpha()
        self.image_Projectile1_F4 = pygame.transform.scale(self.image_Projectile1_F4, (80, 50))

        self.image_Projectile1_F5 = pygame.image.load("Sprites/Bullet_1/Bullet1_F5.png").convert_alpha()
        self.image_Projectile1_F5 = pygame.transform.scale(self.image_Projectile1_F5, (80, 50))

        self.image_Projectile1_F6 = pygame.image.load("Sprites/Bullet_1/Bullet1_F6.png").convert_alpha()
        self.image_Projectile1_F6 = pygame.transform.scale(self.image_Projectile1_F6, (80, 50))

        self.images_Projectile1_moving = [self.image_Projectile1_F1,self.image_Projectile1_F2,self.image_Projectile1_F3
                                          ,self.image_Projectile1_F4,self.image_Projectile1_F5,self.image_Projectile1_F6]

        # Player related

        self.exp_png = pygame.image.load("Sprites/EXP_bar.png").convert_alpha()
        self.exp_png= pygame.transform.scale(self.exp_png, (0, 0))
        ''' ---- Pick -  Ups ---- '''


        self.image_Pick_up_1_F1 = pygame.image.load("Sprites/Pick_Up_1.png").convert_alpha()
        self.image_Pick_up_1_F1 = pygame.transform.scale(self.image_Pick_up_1_F1, (150, 150))

        self.images_Pick_ups = [self.image_Pick_up_1_F1]

        ''' ---- Player Animations ---- '''

            #Firing
        self.image_Player_firing_F1 = pygame.image.load(
            'Sprites/Player_1/Firing/Player_1_Firing_F1.png').convert_alpha()
        self.image_Player_firing_F1 = pygame.transform.scale(self.image_Player_firing_F1,(200,200))

        self.image_Player_firing_F2 = pygame.image.load(
            'Sprites/Player_1/Firing/Player_1_Firing_F2.png').convert_alpha()
        self.image_Player_firing_F2 = pygame.transform.scale(self.image_Player_firing_F2,(200,200))

        self.image_Player_firing_F3 = pygame.image.load(
            'Sprites/Player_1/Firing/Player_1_Firing_F3.png').convert_alpha()
        self.image_Player_firing_F3 = pygame.transform.scale(self.image_Player_firing_F3,(200,200))

        self.image_Player_firing_F4 = pygame.image.load(
            'Sprites/Player_1/Firing/Player_1_Firing_F4.png').convert_alpha()
        self.image_Player_firing_F4 = pygame.transform.scale(self.image_Player_firing_F4,(200,200))

        self.image_Player_firing_F5 = pygame.image.load(
            'Sprites/Player_1/Firing/Player_1_Firing_F5.png').convert_alpha()
        self.image_Player_firing_F5 = pygame.transform.scale(self.image_Player_firing_F5,(200,200))

        self.images_Player_firing = [self.image_Player_firing_F1,self.image_Player_firing_F2,
                                     self.image_Player_firing_F3,self.image_Player_firing_F4,self.image_Player_firing_F5]

            #Charging
        self.image_Player_charging_F1 = pygame.image.load(
            'Sprites/Player_1/Charging/Player_1_Charge_F1.png').convert_alpha()
        self.image_Player_charging_F1 = pygame.transform.scale(self.image_Player_charging_F1 , (200 , 200))

        self.image_Player_charging_F2 = pygame.image.load(
            'Sprites/Player_1/Charging/Player_1_Charge_F2.png').convert_alpha()
        self.image_Player_charging_F2 = pygame.transform.scale(self.image_Player_charging_F2 , (200 , 200))

        self.image_Player_charging_F3 = pygame.image.load(
            'Sprites/Player_1/Charging/Player_1_Charge_F3.png').convert_alpha()
        self.image_Player_charging_F3 = pygame.transform.scale(self.image_Player_charging_F3 , (200 , 200))

        self.image_Player_charging_F4 = pygame.image.load(
            'Sprites/Player_1/Charging/Player_1_Charge_F4.png').convert_alpha()
        self.image_Player_charging_F4 = pygame.transform.scale(self.image_Player_charging_F4 , (200 , 200))

        self.image_Player_charging_F5 = pygame.image.load(
            'Sprites/Player_1/Charging/Player_1_Charge_F5.png').convert_alpha()
        self.image_Player_charging_F5 = pygame.transform.scale(self.image_Player_charging_F5 , (200 , 200))

        self.images_Player_charging = [self.image_Player_charging_F1,self.image_Player_charging_F2,
                                       self.image_Player_charging_F3,self.image_Player_charging_F4,self.image_Player_charging_F5]

            #Charged

        self.image_Player_charged_F1 = pygame.image.load(
            'Sprites/Player_1/Charged/Player_1_Charged_F1.png').convert_alpha()
        self.image_Player_charged_F1 = pygame.transform.scale(self.image_Player_charged_F1, (200, 200))

        self.image_Player_charged_F2 = pygame.image.load(
            'Sprites/Player_1/Charged/Player_1_Charged_F2.png').convert_alpha()
        self.image_Player_charged_F2 = pygame.transform.scale(self.image_Player_charged_F2, (200, 200))

        self.image_Player_charged_F3 = pygame.image.load(
            'Sprites/Player_1/Charged/Player_1_Charged_F3.png').convert_alpha()
        self.image_Player_charged_F3 = pygame.transform.scale(self.image_Player_charged_F3, (200, 200))

        self.image_Player_charged_F4 = pygame.image.load(
            'Sprites/Player_1/Charged/Player_1_Charged_F4.png').convert_alpha()
        self.image_Player_charged_F4 = pygame.transform.scale(self.image_Player_charged_F4, (200, 200))

        self.image_Player_charged_F5 = pygame.image.load(
            'Sprites/Player_1/Charged/Player_1_Charged_F5.png').convert_alpha()
        self.image_Player_charged_F5 = pygame.transform.scale(self.image_Player_charged_F5, (200, 200))

        self.images_Player_charged = [self.image_Player_charged_F1,self.image_Player_charged_F2,
                                       self.image_Player_charged_F3,self.image_Player_charged_F4,self.image_Player_charged_F5]


        self.images_Player_all_lists = [self.images_Player_firing,self.images_Player_charging,self.images_Player_charged]
    def update_hp_bar(self):
        self.Hp = font.render(str(self.Player.HP)+"/"+str(self.Player.Max_HP),True,('#621221'))
        self.HpRect = self.Hp.get_rect()
        self.HP_ratio = self.Player.HP / self.Player.Max_HP
        self.HpRect.center = (160,120)
        self.health_FG = pygame.draw.rect(self.screen, (53, 13, 36),pygame.Rect(82, 103, 153 * self.HP_ratio, 36))
        self.screen.blit(self.health_BG, (0, 50))
    def update_exp_bar(self):
        self.Exp_ratio = self.level_up_progress / self.level_up_max
        self.Exp_FG = pygame.draw.rect(self.screen, (53, 13, 36),pygame.Rect(725, 92, 530* self.Exp_ratio, 52))
        self.screen.blit(self.exp_bar_BG, (600, 60))
        if self.level_up_progress >= self.level_up_max:
            self.level_up = True
            self.level_up_progress = 0
            self.level_up_max += 10 * 1.1
    def Player_bullet_charging(self):
        if self.Player.direction.x != 0 or self.Player.direction.y != 0:
            if self.spawn_bullet_cr == True:
                if self.spawn_bullet_timer < 800:
                    self.spawn_bullet_timer += 15

            elif self.spawn_bullet_cr == False:
                self.spawn_bullet_cr = True
                pygame.time.set_timer(self.spawn_bullet, self.spawn_bullet_timer)
        else:
            self.spawn_bullet_cr = False
            pygame.time.set_timer(self.spawn_bullet, 0)
            if self.spawn_bullet_timer > 50:
                self.spawn_bullet_timer -= 20
    def update_cursor(self,cursor_image_rect,image):
        # Custom cursor
        # lag warning
        if pygame.mouse.get_rel() != 0:
            cursor_image_rect = pygame.mouse.get_pos()
            self.screen.blit(image, cursor_image_rect)

    def run(self):
        done = True

        ''' ----- Spawning Timers ----- '''

        while done == True:

            cursor_pos = pygame.mouse.get_pos()

            ''' -------- STR MENU  -------- '''
            if self.start_button.clicked == False:
                self.screen.fill('#1c0818')
                for sprite in self.menu_buttons:

                    sprite.draw(self.screen)
                self.screen.blit(self.title_image, (Width / 2 - 250, 100))
                self.update_cursor(self.cursor_image2_rect,self.cursor_image2)

            ''' -------- IN GAME  -------- '''
            if self.start_button.clicked and self.game_paused == False and self.level_up == False:

                ''' --- Debug--- '''


                ''' --- Updates --- '''
                self.updates()
                pygame.mouse.set_visible(False)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_DELETE:
                            pygame.quit()
                            sys.exit()

                        ''' --- User events --- '''

                    elif event.type == self.spawn_bullet:
                        mouse_x = cursor_pos[0]
                        mouse_y = cursor_pos[1]
                        self.Bullet = Bullet_type_1(self.camera_group, self.Player.pos.x, self.Player.pos.y, mouse_x, mouse_y,
                                                    self.Player,self.images_Projectile1_moving,self.spawn_bullet_timer)
                        self.all_player_projectiles.add(self.Bullet)
                        pygame.time.set_timer(self.spawn_bullet , self.spawn_bullet_timer)

                    elif event.type == self.spawn_enemy:
                        self.Enemy = Enemy_type_1(self.camera_group,self.images_Enemy1_all_lists)
                        self.Enemy.spawn(self.Player)
                        self.all_enemies.add(self.Enemy)

                    #elif event.type == self.spawn_pick_up:
                        #self.Pick_up = Pick_up_1(self.camera_group,self.images_Pick_ups)
                        #self.Pick_up.spawn()
                        #self.all_pick_ups.add(self.Pick_up)
                        #pygame.time.set_timer(self.spawn_pick_up, 0)


            ''' -------- IN LEVEL UP -------- '''
            #if self.level_up == True and self.game_paused == False:
                #pygame.mouse.set_visible(True)
                #self.upgrade_updates()
                #self.update_cursor(self.cursor_image2_rect,self.cursor_image2)



            pygame.display.flip()
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DELETE:
                        pygame.quit()
                        sys.exit()

            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    game = Game_loop()
    game.run()