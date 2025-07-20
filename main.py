from ursina import *

app = Ursina()
cube = Entity(model='cube', color=color.orange, scale=2)

def update():
    cube.rotation_y += time.dt * 50
    cube.rotation_x += time.dt * 50
    cube.rotation_z += time.dt * 50

app.run()
