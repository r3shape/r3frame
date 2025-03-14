from r3frame.utils import damp_lin, math
from r3frame.globals import pg, os, re, time

# ------------------------------------------------------------ #
class Clock:
    FPS:int=0
    maxFPS:int=60
    last:float=0.0
    delta:float=0.0
    current:float=0.0

    def update(self) -> None:
        self.current = time.time()

        if self.last == 0.0:
            self.delta = 0.0
        else: self.delta = self.current - self.last

        self.last = self.current

        if self.delta > 0: self.FPS = 1 / self.delta

    def rest(self) -> None:
        time.sleep(max(1 / self.maxFPS - self.delta, 0))
# ------------------------------------------------------------ #

# ------------------------------------------------------------ #
class Window:
    def __init__(self, size: list[int], display_size: list[int], color: list[int]=[25, 25, 25]) -> None:
        self.icon = None
        self.title = None
        self.size = size
        self.color = color
        self.clip_range = [1, 1]
        self.display_size = display_size
        self.window = pg.display.set_mode(size)
        self.display = pg.Surface(self.display_size)

        self.draw_line = lambda start, end, color, width: pg.draw.line(self.display, color, start, end, width=width)
        self.draw_rect = lambda size, location, color, width: pg.draw.rect(self.display, color, pg.Rect(location, size), width=width)
        self.draw_circle = lambda center, radius, color, width: pg.draw.circle(self.display, color, [*map(int, center)], radius, width)
        
        self.blit_rect = lambda rect, color, width: self.draw_rect(rect.size, rect.topleft, color, width)

    def set_title(self, title: str) -> None: self.title = title
    def set_icon(self, icon: pg.Surface) -> None: self.icon = icon

    def configure(self) -> None:
        self.display = pg.Surface(self.display_size)
        if isinstance(self.title, str): pg.display.set_caption(self.title)
        if isinstance(self.icon, pg.Surface): pg.display.set_icon(self.icon)

    def clear(self) -> None:
        self.display.fill(self.color)
        self.window.fill(self.color)

    def blit(self, surface: pg.Surface, location: list[int], offset: list[int]=[0, 0]) -> None:
        # display-culling
        if ((location[0] + surface.size[0]) - self.clip_range[0] < 0 or location[0] + self.clip_range[0] > self.display_size[0]) \
        or ((location[1] + surface.size[1]) - self.clip_range[1] < 0 or location[1] + self.clip_range[1] > self.display_size[1]):
            return
        self.display.blit(surface, [location[0] - offset[0], location[1] - offset[1]])

    def update(self) -> None:
        pg.display.flip()
# ------------------------------------------------------------ #

# ------------------------------------------------------------ #
class Asset_Manager:
    def __init__(self) -> None:
        self.font:dict = {}
        self.image:dict = {}
        self.audio:dict = {}

        self.create_surface = lambda size, color: pg.Surface(size)
        self.create_rect = lambda location, size: pg.Rect(location, size)

        self.fill_surface = lambda surface, color: surface.fill(color)
        self.flip_surface = lambda surface, x, y: pg.transform.flip(surface, x, y)
        self.scale_surface = lambda surface, scale: pg.transform.scale(surface, scale)
        self.rotate_surface = lambda surface, angle: pg.transform.rotate(surface, angle)

    def flip_image(self, key: str, x: bool, y: bool) -> None:
        try:
            image = self.image[key]
            if isinstance(image, pg.Surface):
                self.image[key] = self.flip_surface(image, x, y)
            elif isinstance(image, list):
                self.image[key] = [self.flip_surface(i, x, y) for i in image]
        except (KeyError) as err: print(err)

    def get_image(self, key:str) -> pg.Surface|pg.Surface:
        return self.image.get(key, None)
    
    def set_image(self, key:str, image:pg.Surface) -> pg.Surface|None:
        try:
            self.image[key] = image
        except (KeyError) as err: print(err)

    def load_image(self, key:str, path:str, scale:list=None, colorKey:list=None) -> pg.Surface:
        try:
            image:pg.Surface = pg.image.load(path).convert_alpha()
            image.set_colorkey(colorKey)
            if scale: image = self.scale_surface(image, scale)
            self.image[key] = image
            return self.image[key]
        except (FileNotFoundError) as err: print(err)
    
    def load_image_dir(self, key:str, path:str, scale:list=None, colorKey:list=None) -> list:
        try:
            images:list = []
            for _, __, image in os.walk(path):
                sorted_images = sorted(image, key=lambda string_: [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)])
                for image in sorted_images:
                    full_path = path + '/' + image
                    image_surface = self.load_image(full_path, scale, colorKey)
                    if self.image_visible(image_surface):
                        images.append(image_surface)
            self.image[key] = images
            return self.image[key]
        except (FileNotFoundError) as err: ...
    
    def load_image_sheet(self, key: str, path: str, frameSize: list[int], colorKey: list=None) -> list:
        try:
            sheet = self.load_image(key, path)
            frame_x = int(sheet.get_size()[0] / frameSize[0])
            frame_y = int(sheet.get_size()[1] / frameSize[1])
            
            frames = []
            for row in range(frame_y):
                for col in range(frame_x):
                    x = col * frameSize[0]
                    y = row * frameSize[1]
                    frame = pg.Surface(frameSize, pg.SRCALPHA).convert_alpha()
                    frame.set_colorkey(colorKey)
                    frame.blit(sheet, (0,0), pg.Rect((x, y), frameSize))   # blit the sheet at the desired coords (texture mapping)
                    if self.image_visible(frame):
                        frames.append(frame)
            self.image[key] = frames
            return self.image[key]
        except (FileNotFoundError) as err: ...

    def image_visible(self, image:pg.Surface, threshold:int=1) -> bool:
        result = False
        pixels, noPixels = 0, 0
        for y in range(image.size[1]):
            for x in range(image.size[0]):
                pixel = image.get_at([x, y])
                if pixel[3] == 0:
                    noPixels += 1
                pixels += 1
        if pixels-noPixels >= threshold:
            result = True
        return result
# ------------------------------------------------------------ 

# ------------------------------------------------------------ #
class Camera:
    class MODES:
        CENTER_ON: int = 1

    def __init__(self, window: Window):
        self.window = window
        self.mode = 0
        self.drag = 18
        self.speed = 100
        self.location = [0, 0]
        self.velocity = [0.0, 0.0]
        self.last_location = self.location

        self.bounds = window.display_size
        self.viewport_size = window.display_size
        self.viewport_scale = [
            self.window.size[0] / self.viewport_size[0],
            self.window.size[1] / self.viewport_size[1]
        ]
        self.center = [self.location[0] + self.viewport_size[0] / 2, self.location[1] + self.viewport_size[1] / 2]
        self.mod_viewport(-self.viewport_size[0] - self.viewport_size[1])

    def get_center(self, size: list[int]) -> pg.Rect:
        return pg.Rect([self.center[0] - size[0] / 2, self.center[1] - size[1] / 2], size)

    def get_viewport(self) -> pg.Rect:
        return pg.Rect(self.location, self.viewport_size)

    def set_velocity(self, vx: float=0.0, vy: float=0.0) -> None:
        if vx: self.velocity[0] = vx
        if vy: self.velocity[1] = vy

    def mod_viewport(self, delta: float) -> list[int]:
        delta *= (min(self.viewport_size) * 0.05)  # scale the delta by 5% of the viewport size
        aspect_ratio = self.viewport_size[0] / self.viewport_size[1]

        new_width = min(self.bounds[0], max(260, self.viewport_size[0] + delta))
        new_height = min(self.bounds[1], max(260, self.viewport_size[1] + delta))

        if new_width / new_height != aspect_ratio:
            if new_width == self.bounds[0]:
                new_height = new_width / aspect_ratio
            if new_height == self.bounds[1]:
                new_width = new_height * aspect_ratio

        self.viewport_size = [new_width, new_height]
        self.center = [self.location[i] + self.viewport_size[i] / 2 for i in (0, 1)]

        return self.viewport_size

    def center_on(self, size: list[int], location: list[int|float]) -> None:
        if self.mode != self.MODES.CENTER_ON: self.mode = self.MODES.CENTER_ON
        target_center = [
            (location[0] + self.viewport_size[0] / 2) + size[0] / 2,
            (location[1] + self.viewport_size[1] / 2) + size[1] / 2
        ]

        dist = [
            (self.center[0] - target_center[0]) + self.viewport_size[0] / 2,
            (self.center[1] - target_center[1]) + self.viewport_size[1] / 2
        ]
    
        self.velocity = [
            (-dist[0] * self.speed) * (1 / self.drag),
            (-dist[1] * self.speed) * (1 / self.drag)
        ]

    def update(self, delta_time: float) -> None:
        self.viewport_scale = [
            self.window.size[0] / self.viewport_size[0],
            self.window.size[1] / self.viewport_size[1]
        ]
        self.last_location = self.location
        self.velocity = [damp_lin(v, self.speed, 3, delta_time) for v in self.velocity]
        self.location[0] = max(0, min(self.bounds[0] - self.viewport_size[0], self.location[0] + self.velocity[0] * delta_time))
        self.location[1] = max(0, min(self.bounds[1] - self.viewport_size[1], self.location[1] + self.velocity[1] * delta_time))
        self.center = [self.location[0] + self.viewport_size[0] / 2, self.location[1] + self.viewport_size[1] / 2]
# ------------------------------------------------------------ #

# ------------------------------------------------------------ #
class Renderer:
    """
    Handles rendering of objects to the display, with support for different rendering strategies 
    optimized for small and large game worlds.
    """
    
    class FLAGS:
        SHOW_CAMERA: int = 1 << 0  # flag to display the camera's viewport boundaries.

    def __init__(self, camera: Camera) -> None:
        """
        Initializes the renderer with a target window and camera.

        :param window: The game window where rendering occurs.
        :param camera: The camera that defines the viewport.
        """
        self.camera = camera
        self.window = camera.window
        self.target = self.window.display
        self.flags = 0
        self.draw_calls = 0
        self._draw_calls = []  # draw_call layout : [surface, location]

        self.draw_line = lambda start, end, color, width: pg.draw.line(
            self.target, color,
            [start[0] - self.camera.location[0], start[1] - self.camera.location[1]],
            [end[0] - self.camera.location[0], end[1] - self.camera.location[1]], width=width
        )

        self.draw_rect = lambda size, location, color, width: pg.draw.rect(self.target, color, pg.Rect(
            [location[0] - self.camera.location[0], location[1] - self.camera.last_location[1]], size), width=width)
        
        self.draw_circle = lambda center, radius, color, width: pg.draw.circle(
            self.target, color, [*map(int, [center[0] - self.camera.location[0], center[1] - self.camera.location[1]])], radius, width)
        
        self.blit_rect = lambda rect, color, width: self.draw_rect(rect.size, [rect.topleft[0] - self.camera.location[0], rect.topleft[1] - self.camera.location[1]], color, width)

    def set_flag(self, flag: int) -> None:
        """Enables a rendering flag."""
        self.flags |= flag

    def rem_flag(self, flag: int) -> None:
        """Disables a rendering flag."""
        if (self.flags & flag) == flag:
            self.flags &= ~flag

    def pre_render(self) -> None: pass
    
    def post_render(self) -> None: pass

    def draw_call(self, surface: pg.Surface, location: list[int]) -> None:
        """
        Queues a draw call for rendering.

        :param surface: The image/surface to render.
        :param location: The world-space position of the surface.
        
        Performs frustum culling to avoid rendering objects outside of the viewport.
        """
        if self.draw_calls + 1 > 4096:  # prevent excessive draw calls.
            return

        # frustum culling
        if ((location[0] + surface.size[0]) - self.window.clip_range[0] < self.camera.location[0] or 
            location[0] + self.window.clip_range[0] > self.camera.location[0] + self.camera.viewport_size[0]) or \
           ((location[1] + surface.size[1]) - self.window.clip_range[1] < self.camera.location[1] or 
            location[1] + self.window.clip_range[1] > self.camera.location[1] + self.camera.viewport_size[1]):
            return

        self._draw_calls.append([surface, location])
        self.draw_calls += 1

    def renderSW(self) -> None:
        """
        Renders objects directly onto the display.
        
        Solves the **per-object transformation bottleneck** by applying view transformations 
        only to the display, making it efficient for **small game worlds**. Since transformations 
        are applied at the display level, object positions remain true to world coordinates.
        """
        self.window.clear()
        self.target = self.window.display

        # compute scaling factors based on the viewport and window size.
        display_size = [self.window.display_size[0] * self.camera.viewport_scale[0], self.window.display_size[1] * self.camera.viewport_scale[1]]

        self.pre_render()
        # render all objects
        for i in range(self.draw_calls):
            surface, location = self._draw_calls.pop(0)
            self.window.blit(surface, location)
        self.draw_calls = 0

        # optionally render the camera's viewport for debugging
        if (self.flags & self.FLAGS.SHOW_CAMERA):
            self.blit_rect(self.camera.get_viewport(), [255, 255, 255], 1)
            self.blit_rect(self.camera.get_center([10, 10]), [0, 255, 0], 1)

        self.post_render()
        # apply camera transformations at the display level (no per-object transformations)
        self.window.window.blit(
            pg.transform.scale(self.target, display_size),
            [-self.camera.location[0] * self.camera.viewport_scale[0], -self.camera.location[1] * self.camera.viewport_scale[1]]
        )

    def renderLW(self) -> None:
        """
        Renders objects to a viewport-sized surface before scaling it up to the display.
        
        Solves the **display transformation bottleneck** by limiting rendering to objects within 
        the camera's viewport, making it efficient for **large game worlds**. However, since 
        transformations are applied per-object within the viewport, their positions are offset 
        relative to the camera's location.
        """
        self.window.clear()
        self.target = pg.Surface(self.camera.viewport_size)  # create a surface matching the viewport size.
        self.target.fill(self.window.color)

        self.pre_render()
        # apply camera transformations on per-object basis (no display transformation)
        for i in range(self.draw_calls):
            surface, location = self._draw_calls.pop(0)
            self.target.blit(surface, (location[0] - self.camera.location[0], location[1] - self.camera.location[1]))
        self.draw_calls = 0

        if (self.flags & self.FLAGS.SHOW_CAMERA):
            viewport_rect = self.camera.get_viewport()
            viewport_rect.topleft = (viewport_rect.x - self.camera.location[0], viewport_rect.y - self.camera.location[1])

            center_rect = self.camera.get_center([10, 10])
            center_rect.topleft = (center_rect.x - self.camera.location[0], center_rect.y - self.camera.location[1])

            pg.draw.rect(self.target, [255, 255, 255], viewport_rect, 1)
            pg.draw.rect(self.target, [0, 255, 0], center_rect, 1)

        self.post_render()
        self.window.window.blit(
            pg.transform.scale(self.target, self.window.size),
            [0, 0]
        )

    def flush(self) -> None:
        """ Flushes the renderer draw call array, dynamically swapping between large-world rendering and small-world rendering based on view scale.
            - (zoom effects are applied via Camera.mod_viewport() calls which require more of the world to be rendered)
        """
        if any(map(lambda s: s >= 0.4, self.camera.viewport_scale)): self.renderLW()
        else: self.renderSW()
# ------------------------------------------------------------ #
