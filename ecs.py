from uuid import uuid4
from collections import namedtuple
import pprint
from io import StringIO

Event = namedtuple('Event', ['name', 'value'])
Component = namedtuple('Component', ['name', 'value'])


class Entity:
    eindex = {} # map entity IDs to entity objects
    cindex = {} # map component names to entity objects

    def __init__(self, hid=None):
        self.uid = uuid4()
        self.components = {}
        self.eindex[self.uid] = self 
        self.hid=hid
        if hid != None:
            self.bind(Component(name='id', value=hid))

    
    def add_component(self, component):
        self.components[component.name] = component.value
        if component.name not in self.cindex:
            self.cindex[component.name] = []
        self.cindex[component.name].append(self)
        return 0
    
    def bind(self, component):
        self.add_component(component)


    def remove_component(self, component):
        if component.name not in self.components.keys(): return None
        del self.components[component.name]
        return 0


    @classmethod
    def filter(cls, component_name, where=None):
        entities = cls.cindex.get(component_name)
        def filter_values(entity):
            for name in entity.components:
                if entity.components[name] == where: return True
            return False
        if where != None and entities != None: entities = list(filter(lambda e: filter_values(e), entities))
        return entities if entities is not None else []


    @classmethod
    def get(cls, eid):
        return cls.eindex.get(eid)


    def __str__(self):
        buff = StringIO()
        buff.write('Component id: ' + str(self.uid if self.hid is None else self.hid) + '\n')
        buff.write(pprint.pformat(self.components))
        return buff.getvalue()


    def __repr__(self):
        return str(self.__str__())


class System(object):
    systems = []
    subscriptions = {}
    def __init__(self):
        self.events = []
        self.systems.append(self)


    def subscribe(self, event_type):
        if event_type not in self.subscriptions:
            self.subscriptions[event_type] = []
        self.subscriptions[event_type].append(self)
        self.subscriptions[event_type] = list(set(self.subscriptions[event_type])) # remove possible duplicates


    def pending(self):
        events = self.events
        self.events = []
        return events


    @classmethod
    def inject(cls, event):
        if event.name not in cls.subscriptions:
            return
        for subscriber in cls.subscriptions[event.name]:
            subscriber.events.append(event)


    def update(self):
        pass


    @classmethod
    def update_all(cls):
        for system in cls.systems:
            system.update()

    def __str__(self):
        pass


    def __repr__(self):
        pass










