"""
Shader classes, extension of the glGA SDK ECSS
    
glGA SDK v2021 ECSS (Entity Component System in a Scenegraph)
@Coopyright 2020-2021 George Papagiannakis
    
The Shader Compoment class is the dedicated to a specific type of data container in the pyglGA ECSS
that of assembling, using and destroying OpenGL API shader programs

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
import os  
import sys

import OpenGL.GL as gl
from OpenGL.GL import shaders

from pyglGA.ECSS.System import System, RenderSystem, SystemDecorator
from pyglGA.ECSS.Component import Component, BasicTransform, Camera, ComponentDecorator, RenderMesh, CompNullIterator, BasicTransformDecorator
import uuid  
import pyglGA.ECSS.utilities as util
from pyglGA.ext.VertexArray import VertexArray

class Shader(Component):
    """
    A concrete OpenGL-GLSL Shader container Component class

    """
    
    # ---------------------------------------------------
    #  basic pass-through Vertex-Fragment Shader examples
    # ---------------------------------------------------
    COLOR_VERT = """#version 410
        layout (location=0) in vec4 position;
        layout (location=1) in vec4 colour;
        out vec4 theColour;
        void main()
        {
            gl_Position = position;
            theColour = colour;
        }
    """
    COLOR_FRAG = """#version 410
        in vec4 theColour;
        out vec4 outputColour;
        void main()
        {
            //outputColour = vec4(1, 0, 0, 1);
            outputColour = theColour;
        }
    """
    COLOR_VERT_MVP = """#version 410
        layout (location=0) in vec4 position;
        layout (location=1) in vec4 colour;
        out     vec4 theColour;
        uniform mat4 modelViewProj;
        
        void main()
        {
            gl_Position = modelViewProj * position;
            theColour = colour;
        }
    """
    
    def __init__(self, name=None, type=None, id=None, vertex_source=None, fragment_source=None):
        super().__init__(name, type, id)
        
        self._parent = self
        
        self._glid = None
        self._mat4fDict = {}
        self._mat3fDict = {}
        self._float1fDict = {}
        self._float3fDict = {}
        self._float4fDict = {}
        
        if not vertex_source:
            self._vertex_source = Shader.COLOR_VERT
        else:
            self._vertex_source = vertex_source
            
        if not fragment_source:
            self._fragment_source = Shader.COLOR_FRAG
        else:
            self._fragment_source = fragment_source
        #self.init(vertex_source, fragment_source) #init Shader under a valid GL context
    
    @property
    def glid(self):
        return self._glid
    
    @property
    def vertex_source(self):
        return self._vertex_source
    
    @vertex_source.setter
    def vertex_source(self, value):
        self._vertex_source = value
    
    @property
    def fragment_source(self):
        return self._fragment_source
    
    @fragment_source.setter
    def fragment_source(self, value):
        self._fragment_source = value
        
    @property
    def mat4fDict(self):
        return self._mat4fDict
    @mat4fDict.setter
    def mat4fDict(self, value):
        self._mat4fDict = value
        
    @property
    def mat3fDict(self):
        return self._mat3fDict
    @mat3fDict.setter
    def mat3fDict(self, value):
        self._mat3fDict = value
    
    @property
    def float1fDict(self):
        return self._float1fDict
    @float1fDict.setter
    def float1fDict(self, value):
        self._float1fDict = value
    
    @property
    def float3fDict(self):
        return self._float3fDict
    @float3fDict.setter
    def float3fDict(self, value):
        self._float3fDict = value
        
    @property
    def float4fDict(self):
        return self._float4fDict
    @float4fDict.setter
    def float4fDict(self, value):
        self._float4fDict = value
    
    def __del__(self):
        gl.glUseProgram(0)
        if self._glid:
            gl.glDeleteProgram(self._glid)
    
    def disableShader(self):
        gl.glUseProgram(0)
    
    def enableShader(self):
        gl.glUseProgram(self._glid)
        if self._mat4fDict is not None:
            for key, value in self._mat4fDict.items():
                loc = gl.glGetUniformLocation(self._glid, key)
                gl.glUniformMatrix4fv(loc, 1, True, value) 
        if self._mat3fDict is not None:
            for key, value in self._mat3fDict.items():
                loc = gl.glGetUniformLocation(self._glid, key)
                gl.glUniformMatrix3fv(loc, 1, True, value)
        if self._float1fDict is not None:
            for key, value in self._float1fDict.items():
                loc = gl.glGetUniformLocation(self._glid, key)
                gl.glUniform1fv(loc, 1, True, value)
        if self._float3fDict is not None:
            for key, value in self._float3fDict.items():
                loc = gl.glGetUniformLocation(self._glid, key)
                gl.glUniform3fv(loc, 1, True, value)
        if self._float4fDict is not None:
            for key, value in self._float4fDict.items():
                loc = gl.glGetUniformLocation(self._glid, key)
                gl.glUniform4fv(loc, 1, True, value)
            
    @staticmethod
    def _compile_shader(src, shader_type):
        src = open(src, 'r').read() if os.path.exists(src) else src
        #src = src.decode('ascii') if isinstance(src, bytes) else src.decode
        shader = gl.glCreateShader(shader_type)
        gl.glShaderSource(shader, src)
        gl.glCompileShader(shader)
        status = gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS)
        src = ('%3d: %s' % (i+1, l) for i,l in enumerate(src.splitlines()) ) 
        print('Compile shader success for %s\n%s\n%s' % (shader_type, status, src))
        if not status:
            log = gl.glGetShaderInfoLog(shader).decode('ascii')
            gl.glDeleteShader(shader)
            src = '\n'.join(src)
            print('Compile failed for %s\n%s\n%s' % (shader_type, log, src))
            return None
        return shader
        
    
    def update(self):
        print(self.getClassName(), ": update() called")
        
   
    def accept(self, system: System):
        """
        Accepts a class object to operate on the Component, based on the Visitor pattern.

        :param system: [a System object]
        :type system: [System]
        """
        system.apply2Shader(self)
    
    def init(self):
        """
        shader extra initialisation from raw strings or source file names
        """
        vert = self._compile_shader(self._vertex_source, gl.GL_VERTEX_SHADER)
        frag = self._compile_shader(self._fragment_source, gl.GL_FRAGMENT_SHADER)
        
        if vert and frag:
            self._glid = gl.glCreateProgram()
            gl.glAttachShader(self._glid, vert)
            gl.glAttachShader(self._glid, frag)
            gl.glLinkProgram(self._glid)
            gl.glDeleteShader(vert)
            gl.glDeleteShader(frag)
            status = gl.glGetProgramiv(self._glid, gl.GL_LINK_STATUS)
            if not status:
                print(gl.glGetProgramInfoLog(self._glid).decode('ascii'))
                gl.glDeleteProgram(self._glid)
                self._glid = None
    
    def __iter__(self) ->CompNullIterator:
        """ A component does not have children to iterate, thus a NULL iterator
        """
        return CompNullIterator(self) 
    
    
class ShaderGLDecorator(ComponentDecorator):
    """A decorator of the Shader Compoment to decorate it with custom standard pass-through 
    shader attributes

    :param ComponentDecorator: [description]
    :type ComponentDecorator: [type]
    """
    def init(self):
        self.component.init()
    
    def update(self):
        self.component.update()
        # add here custom shader draw calls, e.g. glGetUniformLocation(), glUniformMatrix4fv() etc.add()
        # e.g.  loc = GL.glGetUniformLocation(shid, 'projection')
        #       GL.glUniformMatrix4fv(loc, 1, True, projection)
        
    def setUniformVariable(self,key, value, mat4=False, mat3=False, float1=False, float3=False, float4=False):
        if mat4:
            self.component.mat4fDict[key]=value
        if mat3:
            self.component.mat3fDict[key]=value
        if float1:
            self.component.float1fDict[key]=value
        if float3:
            self.component.float3fDict[key]=value
        if float4:
            self.component.float4fDict[key]=value
            
    def enableShader(self):
        self.component.enableShader()
    
    def disableShader(self):
        self.component.disableShader()
    
    def get_glid(self):
        return self.component.glid

    def accept(self, system: System):
        """
        Accepts a class object to operate on the Component, based on the Visitor pattern.

        :param system: [a System object]
        :type system: [System]
        """
        system.apply2ShaderGLDecorator(self)
    
    def __iter__(self) ->CompNullIterator:
        """ A concrete component Decorator does not have children to iterate, thus a NULL iterator
        """
        return CompNullIterator(self) 

class InitGLShaderSystem(System):
    """Initialise outside of the rendering loop RenderMesh, Shader, VertexArray, ShaderGLDecorator classes

    """
    def init(self):
        pass
    
    def update(self):
        """
        """
        #add here custom Shader render calls
    
        
    def apply2RenderMesh(self, renderMesh:RenderMesh):
        """
        method to be subclassed for  behavioral or logic computation 
        when visits Components.
        
        """
        print(f'\n{renderMesh} accessed within {self.getClassName()}::apply2RenderMesh() \n')
        self.update()
        
    def apply2VertexArray(self, vertexArray:VertexArray):
        """
        method to be subclassed for  behavioral or logic computation 
        when visits Components.
        
        """
        print(f'\n{vertexArray} accessed within {self.getClassName()}::apply2RenderMesh() \n')
        # Access parent Entity's RenderMesh
        parentEntity = vertexArray.parent
        parentRenderMesh = parentEntity.getChildByType(RenderMesh.getClassName())
        if parentRenderMesh:
            # Copy RenderMesh::vertex_attributes and vertex_indices to vertexArray
            vertexArray.attributes = parentRenderMesh.vertex_attributes
            vertexArray.index = parentRenderMesh.vertex_index
            vertexArray.init()
        else:
            print("\n no RenderMesh to copy vertex attributes from! \n")
        # Init vertexArray
        
    def apply2Shader(self, shader:Shader):
        """
        method to be subclassed for  behavioral or logic computation 
        when visits Components.
        
        """
        # if there is no ShaderGLDecorator, init Shader
        # for the moment assume that the user will not be directly adding both a shader and shaderDecorator at scenegraph level
        # we can prevent this at ECSSManager level, but not at scenegraph direct access level
        shader.init()
        print(f'\n{shader} accessed within {self.getClassName()}::apply2Shader() \n')
    
    def apply2ShaderGLDecorator(self, shaderGLDecorator:ShaderGLDecorator):
        """
        method to be subclassed for  behavioral or logic computation 
        when visits Components.
        
        """
        #init ShaderGLDecorator if there is such a node
        shaderGLDecorator.init()
        print(f'\n{shaderGLDecorator} accessed within {self.getClassName()}::apply2ShaderGLDecorator() \n')


class RenderGLShaderSystem(System):
    """A RenderSystem specifically for GL vertex and fragment Shaders and associated 
    VertexArray components attached to a specific Entity

    """
    def init(self):
        pass
        
    def apply2VertexArray(self, vertexArray:VertexArray):
        """
        Main GPU rendering is initiated when a vertexArray node is encountered and if a Shader/Shaderdecorator 
        and RenderMesh components are present 

        method to be subclassed for  behavioral or logic computation 
        when visits RenderMesh Components of the parent EntityNode. 
        Separate SystemDecorator is needed for each case, e.g. for rendering with GL 
        vertex and fragment Shaders: RenderShaderSystem
        
        Actuall RenderShaderSystem rendering is initiated in this update call, according to following pseudocode:
        """
        parentEntity = vertexArray.parent
        compRenderMesh = parentEntity.getChildByType(RenderMesh.getClassName())
        compShader = parentEntity.getChildByType(Shader.getClassName())
        if not compShader:
            compShader = parentEntity.getChildByType(ShaderGLDecorator.getClassName())
        
        if (vertexArray and compRenderMesh and compShader):
            self.render(vertexArray, compRenderMesh, compShader)
    
    
    def render(self, vertexArray:VertexArray = None, compRenderMesh:RenderMesh = None, compShader=None):
        """
        - Shader-based main draw():
            - retrive ShaderDecorator glid
            - useShaderProgram(ShaderDecorator.glid)
            - call ShaderDecorator::update to pass on uniform shader parameters to GPU
            - renderMeshVertexArray.execute(gl.GL_TRIANGLES)
            - userShaderProgram(0) #clean GL state
        """
        # retrieve L2C matrix here to pass it as uniform to shader
        
        #add here custom Shader render calls
        compShader.enableShader()
        
        #call main draw from VertexArray
        vertexArray.update()
        compShader.disableShader()
        
        print(f'\nMain shader GL render within {self.getClassName()}::render() \n')