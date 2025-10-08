from __future__ import annotations
from typing import Any
import math

from ... import util
from .. import Object

__all__: list[str] = [
    "RotSurface",
    "RotTriangle",
    "LightSource",
]


class RotSurface(Object):
    def __init__(self, x: float, y: float, direction: float, surf: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.x = x
        self.y = y
        self.direction = direction
        self.surf = surf
        self.speed = 0

    def step(self) -> None:
        dx = self.speed * math.cos(self.direction)
        dy = self.speed * math.sin(self.direction)
        self.x += dx
        self.y += dy

    def draw(self, viewer: Any) -> None:
        import pygame
        degrees = math.degrees(self.direction)
        rotated_surf = pygame.transform.rotate(self.surf, degrees)
        rot_rect = rotated_surf.get_rect()
        rot_rect.center = (self.x, self.y)
        viewer.v.blit(rotated_surf, rot_rect)


class RotTriangle(RotSurface):
    def __init__(self, x: float, y: float, size: int, color_fg: Any, color_bg: Any, direction: float) -> None:
        self.size = size
        self.color_fg = color_fg
        self.color_bg = color_bg
        import pygame
        self.surf = pygame.Surface((size, size))
        self.surf.fill(color_bg)
        self.surf.set_colorkey(color_bg)

        # vertices with direction 0
        x1 = 0
        y1 = size / 4
        x2 = 0
        y2 = 0.75 * size
        x3 = size
        y3 = size / 2

        v1 = [x1, y1]
        v2 = [x2, y2]
        v3 = [x3, y3]

        # print([v1, v2, v3])

        import pygame
        pygame.draw.polygon(self.surf, self.color_fg, [v1, v2, v3])

        super().__init__(x, y, direction, self.surf)


class LightSource(RotSurface):
    def __init__(
        self,
        x: float,
        y: float,
        emitting_power: int,
        color_fg: Any = util.Color.YELLOW,
        color_bg: Any = util.Color.BLACK,
        **kwargs: Any,
    ) -> None:
        self.emitting_power = emitting_power
        self.color_fg = color_fg
        self.color_bg = color_bg
        self.size = emitting_power
        self.label = None
        import pygame
        self.surf = pygame.Surface((self.size, self.size))
        self.surf.fill(color_bg)
        self.surf.set_colorkey(color_bg)

        pygame.draw.circle(
            self.surf,
            color_fg,
            [int(round(self.size / 2)), int(round(self.size / 2))],
            int(round(self.size / 2)),
        )

        super().__init__(x, y, 0, self.surf, **kwargs)

    def get_saved_scene_repr(self) -> str:
        return (
            self.__class__.__name__
            + " "
            + str(self.x)
            + " "
            + str(self.y)
            + " "
            + str(self.emitting_power)
        )
