# This game file is not the game logic, it's the handling of the game and the rendering part.
import pygame, pytmx, pyscroll
from utils.storageHandler import param_get
from utils.sceneHandler import scene

from player import *

class Game:

    def __init__(self):
        """
        This is the game init function. It's called at the beginning of the game.
        """
        self.clock = pygame.time.Clock()

        # Get variables
        self.window_name = param_get("window_name")

        # Renderer part
        self.screen = pygame.display.set_mode(param_get("screen_size"))
        pygame.display.set_caption(self.window_name)

        # TODO: Make it configurable with saved files.
        self.player = Player()
        self.player.position = (755, 670)
        
        self.update_map("testa", "scene1")

    def update_map(self, map_name=None, scene_name=None):
        if scene_name is None:
            scene_name = self.selected_scene
        if map_name is None:
            map_name = self.selected_map

        scene.change_map(map_name, scene_name)
        scene.scene_cleanup()

        self.group = pyscroll.PyscrollGroup(map_layer=scene.get_map_layer(map_name, scene_name), default_layer=4)
        self.group.add(self.player)

    def run(self):
        """
        Update the player position and make a draw call.
        """

        # Update the player movement. TODO: Dispatch it to the player class
        self.clock.tick(60)
        try:
            dt = 50 / self.clock.get_fps()
        except:
            dt = 0
        self.player.update(dt)

        # Teleport the player if he collide with a portal
        for portal in scene.get_portals():
            if self.player.feet.colliderect(scene.get_portals()[portal]["rect"]) == True:
                self.player.position = (scene.get_portal_exit(scene.get_portals()[portal]).x, scene.get_portal_exit(scene.get_portals()[portal]).y)
                self.update_map(scene.get_portals()[portal]["targeted_map_name"], scene.get_portals()[portal]["targeted_scene_name"])

        # Recenter and draw
        self.group.center(self.player.rect.center)
        self.group.draw(self.screen)
        pygame.display.flip()

    def quit(self):
        """
        This is empty for the moment.
        """
        ...