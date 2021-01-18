import pygame
import random
import math
from os import path

img_dir = path.join(path.dirname(__file__), 'data')
snd_dir = path.join(path.dirname(__file__), 'data')

mobs_hp = (30, 100)
WIDTH = 700
HEIGHT = 900
FPS = 60
POWERUP_TIME = 5000

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Космонарды!")
clock = pygame.time.Clock()

font_name = pygame.font.match_font('BatmanForeverAlternate')


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)


def draw_shield_bar(surf, x, y, hp, max_hp):
    if hp < 0:
        hp = 0
    BAR_LENGTH = 250
    BAR_HEIGHT = 20
    fill = (hp / max_hp) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)


def show_go_screen():
    st = open("data/high_score.txt").read()
    screen.blit(background, background_rect)
    screen.blit(background2, background_rect2)
    screen.blit(background3, background_rect3)
    screen.blit(logo, logo_rect)
    screen.blit(menu, menu_rect)
    screen.blit(highscore, highscore_rect)
    draw_text(screen, st, 32, WIDTH / 2, HEIGHT - 32)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(-1)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.armour = 0.3
        self.infinite_lvl = True
        self.power_time = pygame.time.get_ticks()
        self.damage = 15
        self.max_lvl = False
        self.shield_activated = True
        self.shield_active = pygame.time.get_ticks()
        self.last_armour = self.armour
        self.shield_lenght = 1000
        self.shield_cd = 5000
        self.max_shield = 100

    def update(self):
        if not self.infinite_lvl:
            if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
                self.power -= 1
                self.power_time = pygame.time.get_ticks()

        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.activate_shield()
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10
            self.image.set_alpha(1000)

        if self.hidden and pygame.time.get_ticks() - self.hide_timer <= 1000:
            self.rect.x = 1000
            self.rect.y = 1000

        self.speedx = 0
        self.speedy = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        if keystate[pygame.K_UP]:
            self.speedy = -8
        if keystate[pygame.K_DOWN]:
            self.speedy = 8
        if keystate[pygame.K_SPACE]:
            self.shoot()
        if keystate[pygame.K_LCTRL]:
            if not self.shield_activated and pygame.time.get_ticks() - self.shield_active >= self.shield_cd:
                self.activate_shield()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if not self.hidden:
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.bottom > HEIGHT:
                self.rect.bottom = HEIGHT
            if self.rect.top < 0:
                self.rect.top = 0
        if self.shield_activated and pygame.time.get_ticks() - self.shield_active >= self.shield_lenght:
            self.armour = self.last_armour
            self.shield_activated = False

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    def one_bullet(self):
        bullet = Bullet(self.rect.centerx, self.rect.top, 0, -10)
        all_sprites.add(bullet)
        bullets.add(bullet)

    def update_shield(self, last, new, sh):
        return sh * (new / last)

    def two_bullet(self):
        bullet1 = Bullet(self.rect.left, self.rect.centery, 0, -10)
        bullet2 = Bullet(self.rect.right, self.rect.centery, 0, -10)
        all_sprites.add(bullet1)
        all_sprites.add(bullet2)
        bullets.add(bullet1)
        bullets.add(bullet2)

    def three_bullet(self):
        bullet1 = Bullet(self.rect.left, self.rect.centery, -1, -9)
        bullet2 = Bullet(self.rect.right, self.rect.centery, 1, -9)
        bullet3 = Bullet(self.rect.centerx, self.rect.centery, 0, -10)
        all_sprites.add(bullet1)
        all_sprites.add(bullet2)
        all_sprites.add(bullet3)
        bullets.add(bullet1)
        bullets.add(bullet2)
        bullets.add(bullet3)

    def five_bullet(self):
        bullet1 = Bullet(self.rect.left, self.rect.centery, -1, -9)
        bullet2 = Bullet(self.rect.right, self.rect.centery, 1, -9)
        bullet3 = Bullet(self.rect.centerx, self.rect.centery, 0, -10)
        bullet4 = Bullet(self.rect.left - 6, self.rect.centery, -3, -8)
        bullet5 = Bullet(self.rect.right + 6, self.rect.centery, 3, -8)
        all_sprites.add(bullet1)
        all_sprites.add(bullet2)
        all_sprites.add(bullet3)
        all_sprites.add(bullet4)
        all_sprites.add(bullet5)
        bullets.add(bullet1)
        bullets.add(bullet2)
        bullets.add(bullet3)
        bullets.add(bullet4)
        bullets.add(bullet5)

    def shoot(self):
        if not self.shield_activated:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shoot_delay:
                # self.shoot_delay = 250
                self.last_shot = now
                if self.power == 1:
                    self.one_bullet()
                if self.power == 2:
                    self.two_bullet()
                if self.power == 3:
                    self.three_bullet()
                if self.power == 4:
                    self.five_bullet()
                if self.power == 5:
                    self.new_max_shield = 150
                    self.shield = self.update_shield(self.max_shield, self.new_max_shield, self.shield)
                    self.max_shield = self.new_max_shield
                    self.one_bullet()
                    self.damage = 40
                    self.shoot_delay = 225
                if self.power == 6:
                    self.two_bullet()
                if self.power == 7:
                    self.three_bullet()
                if self.power == 8:
                    self.five_bullet()
                if self.power == 9:
                    self.new_max_shield = 200
                    self.shield = self.update_shield(self.max_shield, self.new_max_shield, self.shield)
                    self.max_shield = self.new_max_shield
                    self.damage = 80
                    self.shoot_delay = 200
                    self.one_bullet()
                if self.power == 10:
                    self.two_bullet()
                if self.power == 11:
                    self.three_bullet()
                if self.power == 12:
                    self.five_bullet()
                if self.power == 13:
                    self.new_max_shield = 250
                    self.shield = self.update_shield(self.max_shield, self.new_max_shield, self.shield)
                    self.max_shield = self.new_max_shield
                    self.damage = 120
                    self.shoot_delay = 175
                    self.one_bullet()
                if self.power == 14:
                    self.two_bullet()
                if self.power == 15:
                    self.three_bullet()
                if self.power == 16:
                    self.five_bullet()
                if self.power == 17:
                    self.new_max_shield = 400
                    self.shield = self.update_shield(self.max_shield, self.new_max_shield, self.shield)
                    self.max_shield = self.new_max_shield
                    self.damage = 160
                    self.shoot_delay = 175
                    self.one_bullet()
                if self.power == 18:
                    self.two_bullet()
                if self.power == 19:
                    self.three_bullet()
                if self.power == 20:
                    self.five_bullet()
                if self.power == 21:
                    self.new_max_shield = 600
                    self.shield = self.update_shield(self.max_shield, self.new_max_shield, self.shield)
                    self.max_shield = self.new_max_shield
                    self.damage = 250
                    self.shoot_delay = 100
                    self.one_bullet()
                if self.power == 22:
                    self.two_bullet()
                if self.power == 23:
                    self.three_bullet()
                if self.power == 24:
                    self.damage = 250
                    self.shoot_delay = 100
                    self.five_bullet()
                    self.new_max_shield = 850
                    self.shield = self.update_shield(self.max_shield, self.new_max_shield, self.shield)
                    self.max_shield = self.new_max_shield
                    # self.max_lvl = True
                if self.power == 25:
                    self.damage = 450
                    self.shoot_delay = 50
                    self.one_bullet()
                if self.power == 26:
                    self.two_bullet()
                if self.power == 27:
                    self.three_bullet()
                if self.power >= 28:
                    self.five_bullet()
                    self.new_max_shield = 1250
                    self.shield = self.update_shield(self.max_shield, self.new_max_shield, self.shield)
                    self.max_shield = self.new_max_shield
                    self.max_lvl = True
                shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)

    def activate_shield(self):
        self.armour = 0
        self.shield_activated = True
        self.shield_active = pygame.time.get_ticks()


class Shield(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(shield_image, (50, 38))
        self.rect = self.image.get_rect()
        self.image.set_alpha(0)
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10

    def update(self, x, y, alpha):
        self.image.set_alpha(alpha)
        self.rect.x = x
        self.rect.y = y


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = pygame.image.load(path.join(img_dir, 'meteorBrown_med1.png')).convert_alpha()
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.hit_point = random.randint(*mobs_hp)
        self.image_orig = pygame.transform.scale(self.image_orig,
                                                 (43 * self.hit_point // (mobs_hp[0] * 2),
                                                  43 * self.hit_point // (mobs_hp[0] * 2)))
        self.score = self.hit_point
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot).convert_alpha()
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 100 or self.rect.left < -100 or self.rect.right > WIDTH + 100:
            self.kill()
            newmob()
        if self.hit_point <= 0:
            self.kill()
            expl = Explosion(hit.rect.center, 'lg')
            all_sprites.add(expl)
            if random.random() > spawn_pow_chance:
                pow = Pow(hit.rect.center)
                all_sprites.add(pow)
                powerups.add(pow)
            newmob()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speedx, speedy):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedx = speedx
        self.speedy = speedy
        self.rotate()

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.bottom < 0 or self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

    def rotate(self):
        rot = (math.sin(self.speedx / self.speedy) / math.pi) * 180
        new_image = pygame.transform.rotate(self.image, rot).convert_alpha()
        old_center = self.rect.center
        self.image = new_image
        self.rect = self.image.get_rect()
        self.rect.center = old_center


class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        if player.max_lvl:
            self.type = 'shield'
        else:
            self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50
        random.choice(expl_sounds).play()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


bg_name = 'starfield.png'
logo = pygame.image.load(path.join(img_dir, 'logo.png')).convert_alpha()
logo_rect = logo.get_rect()
logo_rect.y = 100
highscore = pygame.image.load(path.join(img_dir, 'highscore.png')).convert_alpha()
highscore_rect = highscore.get_rect()
highscore_rect.y = HEIGHT - highscore_rect.height
menu = pygame.image.load(path.join(img_dir, 'menu.png')).convert_alpha()
menu_rect = menu.get_rect()
menu_rect.x = WIDTH // 2 - menu_rect.width // 2
menu_rect.y = HEIGHT - menu_rect.height

background = pygame.image.load(path.join(img_dir, bg_name)).convert()
background_rect = background.get_rect()
background2 = pygame.image.load(path.join(img_dir, bg_name)).convert()
background_rect2 = background2.get_rect()
background3 = pygame.image.load(path.join(img_dir, bg_name)).convert()
background_rect3 = background3.get_rect()
background_rect2.top = background_rect.bottom
background_rect3.bottom = background_rect.top
player_img = pygame.image.load(path.join(img_dir, "playerShip1_orange.png")).convert_alpha()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
bullet_img = pygame.image.load(path.join(img_dir, "laserRed16.png")).convert()
meteor_images = []

shield_image = pygame.image.load(path.join(img_dir, "shield.png")).convert_alpha()

explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)
powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'hp.png')).convert_alpha()
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'bolt_gold.png')).convert_alpha()

shoot_sound = pygame.mixer.Sound(path.join(snd_dir, 'pew.wav'))
shield_sound = pygame.mixer.Sound(path.join(snd_dir, 'pow1.wav'))
power_sound = pygame.mixer.Sound(path.join(snd_dir, 'buzz.ogg'))
expl_sounds = []
for snd in ['expl3.wav', 'expl6.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(snd_dir, snd)))
player_expl_sound = pygame.mixer.Sound(path.join(snd_dir, 'explosion.wav'))

all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()
shields = pygame.sprite.Group()
shield = Shield()
player = Player()
shields.add(shield)
all_sprites.add(player)
for i in range(8):
    newmob()
score = 0

game_over = True
running = True
last_spawn = pygame.time.get_ticks()
spawn_stones = 10000
spawn_pow_chance = 0.5
if __name__ == '__main__':
    while running:
        if game_over:
            game_over = False
            all_sprites = pygame.sprite.Group()
            mobs = pygame.sprite.Group()
            bullets = pygame.sprite.Group()
            powerups = pygame.sprite.Group()
            player = Player()
            all_sprites.add(player)
            for i in range(8):
                newmob()
            score = 0
            show_go_screen()

        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        all_sprites.update()

        hits = pygame.sprite.groupcollide(mobs, bullets, False, True)
        for hit in hits:
            score += 50 + hit.score // 8

            hit.hit_point -= player.damage

        hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
        for hit in hits:
            score += 50 + hit.score // 8
            player.shield -= hit.score * 2 * player.armour
            expl = Explosion(hit.rect.center, 'sm')
            all_sprites.add(expl)
            newmob()
            if player.shield <= 0:
                death_explosion = Explosion(player.rect.center, 'player')
                player_expl_sound.play()
                all_sprites.add(death_explosion)
                player.hide()
                player.lives -= 1
                player.shield = player.max_shield

        hits = pygame.sprite.spritecollide(player, powerups, True)
        for hit in hits:
            if hit.type == 'shield':
                player.shield += 30
                shield_sound.play()
                if player.shield > player.max_shield:
                    player.shield = player.max_shield
            if hit.type == 'gun':
                player.powerup()
                power_sound.play()

        if player.lives == 0:
            st = int(open("data/high_score.txt").read())
            if score > st:
                file = open("data/high_score.txt", 'w')
                file.write(str(score))
                file.close()
            game_over = True

        screen.fill(BLACK)
        screen.blit(background, background_rect)
        screen.blit(background2, background_rect2)
        screen.blit(background3, background_rect3)
        all_sprites.draw(screen)
        draw_text(screen, str(score), 18, WIDTH / 2, 10)
        draw_shield_bar(screen, 5, 5, player.shield, player.max_shield)
        draw_lives(screen, WIDTH - 100, 5, player.lives,
                   player_mini_img)
        background_rect.y += 1
        background_rect2.y += 1
        background_rect3.y += 1
        if background_rect.top >= HEIGHT:
            background_rect.bottom = HEIGHT - background_rect.height * 2
        if background_rect2.top >= HEIGHT:
            background_rect2.bottom = HEIGHT - background_rect.height * 2
        if background_rect3.top >= HEIGHT:
            background_rect3.bottom = HEIGHT - background_rect.height * 2
        if player.shield_activated:
            shields.update(player.rect.x, player.rect.y, 500)
        else:
            shields.update(player.rect.x, player.rect.y, 0)
        if pygame.time.get_ticks() - last_spawn >= spawn_stones:
            newmob()
            last_spawn = pygame.time.get_ticks()

        if player.damage == 15:
            spawn_pow_chance = 0.5
            bullet_img = pygame.image.load(path.join(img_dir, "laserRed16.png")).convert()
        if player.damage == 40:
            spawn_pow_chance = 0.85
            bullet_img = pygame.image.load(path.join(img_dir, "LaserOrange.png")).convert()
        if player.damage == 80:
            spawn_pow_chance = 0.9
            bullet_img = pygame.image.load(path.join(img_dir, "LaserBlue.png")).convert()
        if player.damage == 120:
            spawn_pow_chance = 0.95
            bullet_img = pygame.image.load(path.join(img_dir, "LaserGreen.png")).convert()
        if player.damage == 160:
            spawn_pow_chance = 0.95
            bullet_img = pygame.image.load(path.join(img_dir, "LaserPurple.png")).convert()
        if player.damage == 250:
            spawn_pow_chance = 0.985
            bullet_img = pygame.image.load(path.join(img_dir, "LaserDarkBlue.png")).convert()
        if player.damage == 450:
            spawn_pow_chance = 0.995
            bullet_img = pygame.image.load(path.join(img_dir, "LaserRainbow.png")).convert_alpha()

        mobs_hp = ((score // 400) + 30, (score // 400) + 100)
        shields.draw(screen)
        pygame.display.flip()

    pygame.quit()
    exit(-1)
