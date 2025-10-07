<div align="center">
<img src="miniform/assets/images/icon.png" alt="miniform Logo"/>  

<h3>Miniform</h3>

![Version](https://img.shields.io/pypi/v/miniform?style=for-the-badge&logo=pypi&logoColor=white&label=miniform&labelColor=black&color=white&link=https%3A%2F%2Fpypi.org%2Fproject%2Fminiform%2F2025.0.2%2F)  
![GitHub Stars](https://img.shields.io/github/stars/r3shape/miniform?style=for-the-badge&label=stars&labelColor=black&color=white)
![License](https://img.shields.io/badge/mit-badge?style=for-the-badge&logo=mit&logoColor=white&label=License&labelColor=black&color=white)  
![Build](https://github.com/r3shape/miniform/actions/workflows/miniform.yml/badge.svg)  

</div>

## What?
**miniform** is a game development framework designed to help developers **create more with less hassle**. It provides a structured foundation for handling Worlds, objects, UI, input, and rendering, so you can focus on making games instead of reinventing the wheel.

## Why?
- **Save Time** – No need to build a game structure from scratch.
- **Better Organization** – Worlds, assets, and objects are neatly managed.
- **Pygame, but Better** – All the flexibility of Pygame, with added convenience.

## Content?
- **Modularity** – Manage your game with a clean and modular API.
- **World & Object Management** – Easily define and swap worlds.
- **Custom UI System** – Interface-scripting made simple.
- **Asset Loading** – Load sprites and animations efficiently.
- **Input Handling** – Keyboard and mouse events with built-in support.
- **Partitioning Systems** – Efficient object management for game worlds of any size.

## Download?
Install **miniform** via pip:

```sh
pip install miniform
```

## Getting Started?
After youv'e installed `miniform` go ahead and create a script named `main.py` somwhere and paste in the following code:

```python
import miniform

class MyWorld(miniform.resource.world.MiniWorld):
    def __init__(self, app):
        super().__init__(
            app,
            miniform.resource.world.MiniTileMap(self, [32, 32]),
            miniform.resource.world.MiniGridPartition(app, self, [32, 32])
        )

    def init(self) -> None:
        self.player = self.load_object("player-1", size=[16, 16], pos=[100, 100], mass=800, static=0)

    def update_hook(self, dt: float) -> None:
        if self.app.events.mouse_wheel_up:
            self.app.camera_proc.zoom(-2.5)
        elif self.app.events.mouse_wheel_down:
            self.app.camera_proc.zoom(2.5)
        
        speed = 200.0
        if self.app.events.key_held(self.app.keyboard.W): self.player.set_velocity(vy=-speed)
        if self.app.events.key_held(self.app.keyboard.A): self.player.set_velocity(vx=-speed)
        if self.app.events.key_held(self.app.keyboard.S): self.player.set_velocity(vy=speed)
        if self.app.events.key_held(self.app.keyboard.D): self.player.set_velocity(vx=speed)
        
        self.app.camera_proc.move_to(self.player.pos)

    def render_hook(self) -> None:
        if self.app.events.mouse_held(self.app.mouse.LeftClick):
            self.app.render_proc.draw_line(self.player.center, self.app.mouse.pos.world, [0, 0, 255])
            self.app.render_proc.draw_circle(self.player.center, 4, [0, 0, 255])
            self.tile_map.set_tile(0, self.app.mouse.pos.world, 0, 0)
        elif self.app.events.mouse_held(self.app.mouse.RightClick):
            self.app.render_proc.draw_line(self.player.center, self.app.mouse.pos.world, [255, 0, 0])
            self.app.render_proc.draw_circle(self.player.center, 4, [255, 0, 0])
            self.tile_map.rem_tile(0, self.app.mouse.pos.world)

class MyApp(miniform.app.MiniApp):
    def __init__(self) -> None:
        super().__init__("PlayGround")

    def init(self) -> None:
        self.set_world(MyWorld)

    def exit(self) -> None: pass

    def update_hook(self, dt: float) -> None: pass
    def render_hook(self) -> None: pass

MyApp().run()
```
| NOTE: The methods `init()`, `exit()` must be defined for any instance of `MiniApp`; a `NotImplementedError` is raised otherwise.

Above is a simple `MiniApp` + `MiniWorld` set up for topdown movement/runtime tilemap edits. From here you can explore the `MiniStaticObject`, `MiniDynamicObject` and the other classes provided in `miniform.core.resource` and `miniform.core.resource.interface`.

## Contributions?  
Want to help improve **miniform**? Feel free to contribute by submitting issues, suggesting features, or making pull requests!  

## License  
**miniform** is open-source under the **MIT License.**
</div>
