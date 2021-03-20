"""
VertexArray classes, extension of the glGA SDK ECSS
    
glGA SDK v2021 ECSS (Entity Component System in a Scenegraph)
@Coopyright 2020-2021 George Papagiannakis
    
The VertexArray Compoment class is the dedicated to a specific type of data container in the pyglGA ECSS
that of assembling, using and destroying OpenGL API vertex array and buffer objects

Based on the Composite and Iterator design patterns:
	• https://refactoring.guru/design-patterns/composite
    • https://github.com/faif/python-patterns/blob/master/patterns/structural/composite.py
    • https://refactoring.guru/design-patterns/iterator
    • https://github.com/faif/python-patterns/blob/master/patterns/behavioral/iterator.py


"""

from __future__         import annotations
from abc                import ABC, abstractmethod
from typing             import List
from collections.abc    import Iterable, Iterator

import OpenGL.GL as gl
from OpenGL.GL import shaders
import numpy as np

import pyglGA.ECSS.System
from pyglGA.ECSS.Component import Component, BasicTransform, Camera, RenderMesh, CompNullIterator, BasicTransformDecorator
import uuid  
import pyglGA.ECSS.utilities as util


class VertexArray(Component):
    """
    A concrete VertexArray class

    :param Component: [description]
    :type Component: [type]
    """
    def __init__(self, name=None, type=None, id=None, attributes=None, index=None, usage=gl.GL_STATIC_DRAW):
        super().__init__(name, type, id)
        
        self._trs = util.identity()
        self._parent = self
        self._children = []
        self._glid = None
        self._buffers = [] #store all GL buffers
        self._draw_command = None
        self._arguments = (0,0)
        self.init(attributes, index, usage)
        
    def __del__(self):
        gl.glDeleteVertexArrays(1, [self._glid])
        gl.glDeleteBuffers(len(self._buffers), self._buffers)
    
    def draw(self, primitive = None):
        # draw a vertex Array as direct array or index array
        print(self.getClassName(), ": draw() called")
        
        gl.glBindVertexArray(self._glid)
        self._draw_command(primitive, *self._arguments)
        
    def update(self, primitive = None):
        print(self.getClassName(), ": update() called")
        self.draw(primitive)
   
    def accept(self, system: pyglGA.ECSS.System):
        """
        Accepts a class object to operate on the Component, based on the Visitor pattern.

        :param system: [a System object]
        :type system: [System]
        """
        system.apply2VertexArray(self)
    
    def init(self, attributes, index, usage):
        """
        extra method for extra initialisation pf VertexArray
        Vertex array from attributes and optional index array. 
        Vertex Attributes should be list of arrays with one row per vertex. 
        """
        # create and bind(use) a vertex array object
        self._glid = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self._glid)
        nb_primitives, size = 0, 0
        
        # load buffer per vertex attribute (in a list with index = shader layout)
        for loc, data in enumerate(attributes):
            if data is not None:
                # bind a new VBO, upload it to GPU, declare size and type
                self._buffers.append(gl.glGenBuffers(1))
                data = np.array(data, np.float32, copy=False)
                nb_primitives, size = data.shape
                gl.glEnableVertexAttribArray(loc)
                gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._buffers[-1])
                gl.glBufferData(gl.GL_ARRAY_BUFFER, data, usage)
                gl.glVertexAttribPointer(loc, size, gl.GL_FLOAT, False, 0, None)
        
        #optionally create and upload an index buffer for this VBO         
        self._draw_command = gl.glDrawArrays
        self._arguments = (0, nb_primitives)
        if index is not None:
            self._buffers += [gl.glGenBuffers(1)]
            index_buffer = np.array(index, np.int32, copy=False)
            gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self._buffers[-1])
            self._draw_command = gl.glDrawElements
            self._arguments = (index_buffer.size, gl.GL_UNSIGNED_INT, None)
    
    
    def __iter__(self) ->CompNullIterator:
        """ A component does not have children to iterate, thus a NULL iterator
        """
        return CompNullIterator(self) 