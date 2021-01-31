"""
Component classes, part of the glGA SDK ECS
    
glGA SDK v2020.1 ECS (Entity Component System)
@Coopyright 2020 George Papagiannakis
    
The Compoment class is the dedicated to a specific type of data container in the glGA ECS.

The following is example restructured text doc example
:param file_loc: The file location of the spreadsheet
:type file_loc: str
:returns: a list of strings representing the header columns
:rtype: list

"""

from __future__ import annotations
from abc        import ABC, abstractmethod
from typing     import List

from System     import *
from utilities  import *

class Component(ABC):
    """
    The Interface Component class of our ECS.
    
    Based on the Composite pattern, it is a data collection of specific
    class of data. Subclasses typically are e.g. Transform, RenderMesh, Shader, RigidBody etc.
    """
    
    def __init__(self, name=None, type=None, id=None):
        self._name = name
        self._type = type
        self._id = id
        self._parent = None
    
    #define properties for id, name, type, parent
    @property #name
    def name(self) -> str:
        """ Get Component's name """
        return self._name
    @name.setter
    def name(self, value):
        self._name = value
        
    @property #type
    def type(self) -> str:
        """ Get Component's type """
        return self._type
    @type.setter
    def type(self, value):
        self._type = value
        
    @property #id
    def id(self) -> int:
        """ Get Component's id """
        return self._id
    @id.setter
    def id(self, value):
        self._id = value
        
    @property #parent
    def parent(self) -> Component:
        """ Get Component's parent """
        return self._parent
    @parent.setter
    def parent(self, value):
        self._parent = value
    
    @classmethod
    def getClassName(cls):
        return cls.__name__
    
    #@abstractmethod
    def init(self):
        """
        abstract method to be subclassed for extra initialisation
        """
        pass
    
    #@abstractmethod
    def update(self):
        """
        method to be subclassed for debuging purposes only, 
        in case we need some behavioral or logic computation within te Component. 
        This violates the ECS architecture and should be avoided.
        """
        pass
    
    #@abstractmethod
    def accept(self, system: System):
        """
        Accepts a class object to operate on the Component, based on the Visitor pattern.

        :param system: [a System object]
        :type system: [System]
        """
        system.update()
        
    def print(self):
        #print out name, type, id of this Component
        print(f"\n {self.getClassName()} name: {self._name}, type: {self._type}, id: {self._id}, parent: {self._parent._name}")
        print(f" ______________________________________________________________")
        
    def __str__(self):
        return f"\n {self.getClassName()} name: {self._name}, type: {self._type}, id: {self._id}, parent: {self._parent._name}"

class BasicTransform(Component):
    """
    An example of a concrete Component Transform class
    
    Contains a basic Euclidean Translation, Rotation and Scale Homogeneous matrices
    all-in-one TRS 4x4 matrix
    
    :param Component: [description]
    :type Component: [type]
    """
   
    def __init__(self, name=None, type=None, id=None):
        self._name = name
        self._type = type
        self._id = id
        self._trs = identity()
         
    @property #trs
    def trs(self):
        """ Get Component's transform: translation, rotation ,scale """
        return self._trs
    @trs.setter
    def trs(self, value):
        self._trs = value
                 
    
    def update(self):
        pass
    
    
    def accept(self, system: System):
        """
        Accepts a class object to operate on the Component, based on the Visitor pattern.

        :param system: [a System object]
        :type system: [System]
        """
        system.update()
    
    
    def init(self):
        """
        abstract method to be subclassed for extra initialisation
        """
        pass


class RenderMesh(Component):
    """
    A concrete RenderMesh class

    :param Component: [description]
    :type Component: [type]
    """
    def draw(self):
        print(self.getClassName(), ": draw() called")
        
    def update(self):
        self.draw()
   
    def accept(self, system: System):
        """
        Accepts a class object to operate on the Component, based on the Visitor pattern.

        :param system: [a System object]
        :type system: [System]
        """
        system.update()
    
    def init(self):
        """
        abstract method to be subclassed for extra initialisation
        """
        pass
    