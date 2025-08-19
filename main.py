import pygame
import math
import random
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# Installiere mit: pip install pygame PyOpenGL

class Vector3:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def distance_to(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)

class Player3D:
    def __init__(self):
        self.position = Vector3(0, -3, 0)
        self.speed = 5
        self.size = 0.3
        
    def update(self, keys, dt):
        if keys[K_LEFT] or keys[K_a]:
            self.position.x -= self.speed * dt
        if keys[K_RIGHT] or keys[K_d]:
            self.position.x += self.speed * dt
        if keys[K_UP] or keys[K_w]:
            self.position.y += self.speed * dt
        if keys[K_DOWN] or keys[K_s]:
            self.position.y -= self.speed * dt
            
        # Bildschirmgrenzen
        self.position.x = max(-4, min(4, self.position.x))
        self.position.y = max(-3, min(3, self.position.y))
    
    def draw(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glColor3f(1.0, 1.0, 1.0)  # Weiß
        
        # Spieler als Pyramide zeichnen (Raumschiff-Form)
        glBegin(GL_TRIANGLES)
        # Vorderseite
        glVertex3f(0, self.size, 0)      # Spitze
        glVertex3f(-self.size, -self.size, 0)  # Links unten
        glVertex3f(self.size, -self.size, 0)   # Rechts unten
        
        # Rechte Seite
        glVertex3f(0, self.size, 0)
        glVertex3f(self.size, -self.size, 0)
        glVertex3f(0, -self.size, -self.size)
        
        # Linke Seite
        glVertex3f(0, self.size, 0)
        glVertex3f(0, -self.size, -self.size)
        glVertex3f(-self.size, -self.size, 0)
        
        # Boden
        glVertex3f(-self.size, -self.size, 0)
        glVertex3f(0, -self.size, -self.size)
        glVertex3f(self.size, -self.size, 0)
        glEnd()
        
        glPopMatrix()

class Laser3D:
    def __init__(self, start_pos):
        self.position = Vector3(start_pos.x, start_pos.y, start_pos.z)
        self.speed = 10
        self.alive = True
        
    def update(self, dt):
        self.position.z += self.speed * dt
        
        if self.position.z > 10:
            self.alive = False
            
    def draw(self):
        if self.alive:
            glPushMatrix()
            glTranslatef(self.position.x, self.position.y, self.position.z)
            glColor3f(1.0, 0.0, 0.0)  # Rot
            
            # Laser als kleine Kugel
            quadric = gluNewQuadric()
            gluSphere(quadric, 0.05, 8, 8)
            gluDeleteQuadric(quadric)
            
            glPopMatrix()

class Enemy3D:
    def __init__(self, enemy_type='red'):
        self.position = Vector3(
            random.uniform(-4, 4),
            random.uniform(2, 4),
            8
        )
        self.enemy_type = enemy_type
        self.alive = True
        
        if enemy_type == 'red':
            self.health = 1
            self.speed = 2
            self.points = 10
            self.size = 0.2
            self.color = (1.0, 0.0, 0.0)  # Rot
            self.side_speed = 0
        elif enemy_type == 'green':
            self.health = 1
            self.speed = 1.5
            self.points = 30
            self.size = 0.25
            self.color = (0.0, 1.0, 0.0)  # Grün
            self.side_speed = random.choice([-2, 2])
        elif enemy_type == 'yellow':
            self.health = 3
            self.max_health = 3
            self.speed = 3
            self.points = 100
            self.size = 0.3
            self.color = (1.0, 1.0, 0.0)  # Gelb
            self.side_speed = 0
            
    def update(self, dt):
        if not self.alive:
            return
            
        # Nach unten bewegen
        self.position.z -= self.speed * dt
        
        # Seitliche Bewegung für grüne Gegner
        if self.enemy_type == 'green':
            self.position.x += self.side_speed * dt
            if self.position.x > 4 or self.position.x < -4:
                self.side_speed *= -1
        
        # Farbe basierend auf Gesundheit für gelbe Gegner
        if self.enemy_type == 'yellow':
            if self.health == 3:
                self.color = (1.0, 1.0, 0.0)  # Gelb
            elif self.health == 2:
                self.color = (1.0, 0.5, 0.0)  # Orange
            else:
                self.color = (1.0, 0.0, 0.0)  # Rot
        
        # Entfernen wenn außerhalb des Bildschirms
        if self.position.z < -5:
            self.alive = False
            
    def take_damage(self):
        self.health -= 1
        return self.health <= 0
        
    def draw(self):
        if not self.alive:
            return
            
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glColor3f(*self.color)
        
        if self.enemy_type == 'red':
            # Rote Gegner als umgedrehte Pyramide
            glBegin(GL_TRIANGLES)
            glVertex3f(0, -self.size, 0)     # Spitze unten
            glVertex3f(-self.size, self.size, 0)   # Links oben
            glVertex3f(self.size, self.size, 0)    # Rechts oben
            glEnd()
            
        elif self.enemy_type == 'green':
            # Grüne Gegner als Kugel
            quadric = gluNewQuadric()
            gluSphere(quadric, self.size, 12, 12)
            gluDeleteQuadric(quadric)
            
        elif self.enemy_type == 'yellow':
            # Gelbe Gegner als Würfel
            glBegin(GL_QUADS)
            # Vorderseite
            glVertex3f(-self.size, -self.size, self.size)
            glVertex3f(self.size, -self.size, self.size)
            glVertex3f(self.size, self.size, self.size)
            glVertex3f(-self.size, self.size, self.size)
            # Rückseite
            glVertex3f(-self.size, -self.size, -self.size)
            glVertex3f(-self.size, self.size, -self.size)
            glVertex3f(self.size, self.size, -self.size)
            glVertex3f(self.size, -self.size, -self.size)
            glEnd()
            
        glPopMatrix()

class Star3D:
    def __init__(self):
        self.position = Vector3(
            random.uniform(-8, 8),
            random.uniform(-5, 5),
            random.uniform(5, 20)
        )
        self.speed = random.uniform(1, 3)
        self.brightness = random.uniform(0.3, 1.0)
        
    def update(self, dt):
        self.position.z -= self.speed * dt
        if self.position.z < -5:
            self.position.z = 20
            self.position.x = random.uniform(-8, 8)
            self.position.y = random.uniform(-5, 5)
            
    def draw(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glColor3f(self.brightness, self.brightness, self.brightness)
        
        glBegin(GL_POINTS)
        glVertex3f(0, 0, 0)
        glEnd()
        
        glPopMatrix()

class SpaceDefender3D:
    def __init__(self):
        pygame.init()
        self.screen_size = (800, 600)
        self.screen = pygame.display.set_mode(self.screen_size, DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Space Defender 3D")
        
        # OpenGL Setup
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (self.screen_size[0]/self.screen_size[1]), 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)
        
        # Spiel-Objekte
        self.player = Player3D()
        self.lasers = []
        self.enemies = []
        self.stars = [Star3D() for _ in range(100)]
        
        # Spiel-Status
        self.score = 0
        self.laser_level = 1
        self.max_laser_level = 5
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Timer
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 2000  # Millisekunden
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.shoot()
                    
    def shoot(self):
        # Mehrere Laser basierend auf Level
        positions = []
        if self.laser_level == 1:
            positions = [Vector3(0, 0.3, 0)]
        elif self.laser_level == 2:
            positions = [Vector3(-0.2, 0.3, 0), Vector3(0.2, 0.3, 0)]
        elif self.laser_level == 3:
            positions = [Vector3(-0.2, 0.3, 0), Vector3(0, 0.3, 0), Vector3(0.2, 0.3, 0)]
        elif self.laser_level == 4:
            positions = [Vector3(-0.3, 0.3, 0), Vector3(-0.1, 0.3, 0), 
                        Vector3(0.1, 0.3, 0), Vector3(0.3, 0.3, 0)]
        else:  # Level 5
            positions = [Vector3(-0.3, 0.3, 0), Vector3(-0.15, 0.3, 0), Vector3(0, 0.3, 0),
                        Vector3(0.15, 0.3, 0), Vector3(0.3, 0.3, 0)]
            
        for pos in positions:
            laser_pos = Vector3(
                self.player.position.x + pos.x,
                self.player.position.y + pos.y,
                self.player.position.z + pos.z
            )
            self.lasers.append(Laser3D(laser_pos))
    
    def spawn_enemy(self):
        # Gegnertyp basierend auf Score
        if self.score < 200:
            enemy_type = 'red'
        elif self.score < 2000:
            enemy_type = random.choice(['red', 'green'])
        else:
            enemy_type = random.choice(['red', 'green', 'yellow'])
            
        self.enemies.append(Enemy3D(enemy_type))
    
    def update(self, dt):
        keys = pygame.key.get_pressed()
        
        # Spieler updaten
        self.player.update(keys, dt)
        
        # Laser updaten
        self.lasers = [laser for laser in self.lasers if laser.alive]
        for laser in self.lasers:
            laser.update(dt)
            
        # Gegner updaten
        self.enemies = [enemy for enemy in self.enemies if enemy.alive]
        for enemy in self.enemies:
            enemy.update(dt)
            
        # Sterne updaten
        for star in self.stars:
            star.update(dt)
            
        # Gegner spawnen
        current_time = pygame.time.get_ticks()
        if current_time - self.enemy_spawn_timer > self.enemy_spawn_delay:
            self.spawn_enemy()
            self.enemy_spawn_timer = current_time
            
        # Kollisionen prüfen
        self.check_collisions()
        
    def check_collisions(self):
        # Laser vs Gegner
        for laser in self.lasers[:]:
            for enemy in self.enemies[:]:
                if laser.position.distance_to(enemy.position) < 0.5:
                    if enemy.take_damage():
                        self.score += enemy.points
                        enemy.alive = False
                    laser.alive = False
                    break
        
        # Spieler vs Gegner (Game Over)
        for enemy in self.enemies:
            if self.player.position.distance_to(enemy.position) < 0.5:
                print(f"Game Over! Final Score: {self.score}")
                self.running = False
                
    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Kamera positionieren
        gluLookAt(0, 0, -8,  # Kamera Position
                 0, 0, 0,    # Blickpunkt
                 0, 1, 0)    # Up-Vektor
        
        # Sterne zeichnen
        for star in self.stars:
            star.draw()
            
        # Spieler zeichnen
        self.player.draw()
        
        # Laser zeichnen
        for laser in self.lasers:
            laser.draw()
            
        # Gegner zeichnen
        for enemy in self.enemies:
            enemy.draw()
            
        pygame.display.flip()
        
    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # Delta time in Sekunden
            
            self.handle_events()
            self.update(dt)
            self.draw()
            
        pygame.quit()

if __name__ == "__main__":
    game = SpaceDefender3D()
    game.run()
    