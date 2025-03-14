from r3frame.globals import pg
from r3frame.objects.game import Game_Object
from r3frame.application.ui import Interface
from r3frame.objects.world import Grid_Map, Quad_Map

class Scene:
    def __init__(self, name: str, partition: Grid_Map|Quad_Map):
        self.name = name
        self.partition = partition
        self.interfaces: dict[str, Interface] = {}

    def set_object(self, obj: Game_Object) -> None: self.partition.set_cell(*obj.location, obj)
    def get_object(self, location: list[int|float]) -> None: return self.partition.get_cell(*location)
    def rem_object(self, location: list[int|float]) -> Game_Object|None: return self.partition.rem_cell(*location)

    def rem_interface(self, key: str) -> None:
        if self.get_interface(key) is not None: del self.interfaces[key]
    def get_interface(self, key: str) -> Interface|None: return self.interfaces.get(key, None)
    def set_interface(self, interface: Interface) -> None: self.interfaces[interface.name] = interface

    def handle_update(self, event_manager) -> None:
        for interface in self.interfaces:
            self.interfaces[interface].update(event_manager)
    
    def handle_render(self) -> None:
        for interface in self.interfaces:
            self.interfaces[interface].render()
