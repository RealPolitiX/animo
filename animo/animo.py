#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: R. Patrick Xian
"""

from __future__ import print_function, division
from abc import ABCMeta, abstractmethod
from JSAnimation.IPython_display import display_animation
from matplotlib import animation
import numpy as np
import matplotlib.pyplot as plt


class PlotAnimate(object):
    """
    The animator metaclass
    """
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def animator(self, iframe):
        """
        Construct animation
        """
        return
    
    @abstractmethod
    def view_frame(self, iframe):
        """
        Display a single frame of animation
        """
        return
        
    @abstractmethod
    def view_anim(self, backend):
        """
        Display the entire animation
        """
        return
    

class LineAnimate(PlotAnimate):
    """
    Class for 1D line animation
    """
    
    def __init__(self, x, y, nframes, fixed='x', **kwargs):
        self.x = x
        self.y = y
        self.nframes = nframes
        self.fixed = fixed
        self.figsize = kwargs.get('figsize', (6,4))
        self.interval = kwargs.get('interval', 100)
        self.zorder = kwargs.get('zorder', 0)
        if {'fig', 'ax'} <= set(kwargs.keys()):
            self.f, self.ax = kwargs['fig'], kwargs['ax']
        else:
            self.f, self.ax = plt.subplots(figsize=self.figsize)
        
    def frame(self, iframe):
        if self.fixed == 'x':
            self.lines, = self.ax.plot(self.x[0,:], self.y[iframe,:], zorder=self.zorder)
        elif self.fixed == 'y':
            self.lines, = self.ax.plot(self.x[iframe,:], self.y[0,:], zorder=self.zorder)
        elif self.fixed is None:
            self.lines, = self.ax.plot(self.x[iframe,:], self.y[iframe,:], zorder=self.zorder)
        return self.lines
    
    def view_frame(self, iframe):
        _ = self.frame(iframe)
        return
        
    def animator(self, iframe):
        if not hasattr(self, 'lines'):
            self.lines = self.frame(0)
        else:
            if self.fixed == 'x':
                self.lines.set_data(self.x, self.y[iframe,:])
            elif self.fixed == 'y':
                self.lines.set_data(self.x[iframe,:], self.y)
            elif self.fixed is None:
                self.lines.set_data(self.x[iframe,:], self.y[iframe,:])
        return self.f
    
    def view_anim(self, backend):
        anim = animation.FuncAnimation(self.f, self.animator,\
                frames=self.nframes, interval=self.interval)
        if backend == 'JS':
            return display_animation(anim)
            

class ImageAnimate(PlotAnimate):
    """
    Class for 2D image animation
    """
    
    def __init__(self, data, axis=0, **kwargs):
        if np.ndim(data) != 3:
            raise Exception('The input array needs to have dimension 3.')
        else:
            self.axis = axis
            self.data = np.rollaxis(data, axis)
            self.nl, self.nr, self.nc = self.data.shape
            self.interval = kwargs.get('interval', 100)
            self.nframes = kwargs.get('nframes', data.shape[axis])
            self.xaxis = kwargs.get('imx', range(self.nr))
            self.yaxis = kwargs.get('imy', range(self.nc))
            self.figsize = kwargs.get('figsize', (5,6))
            self.xgrid, self.ygrid = np.meshgrid(self.yaxis, self.xaxis)
            self.cmap = kwargs.get('cmap', 'terrain_r')
            self.text = kwargs.get('text', ['']*self.nl)
            self.textpos = kwargs.get('textpos', (0.9, 0.9))
            self.textsize = kwargs.get('textsize', 15)
            self.textcolor = kwargs.get('textcolor', 'k')
            self.vmin = kwargs.get('vmin', None)
            self.vmax = kwargs.get('vmax', None)
            self.zorder = kwargs.get('zorder', 0)
            if {'fig', 'ax'} <= set(kwargs.keys()):
                self.f, self.ax = kwargs['fig'], kwargs['ax']
            else:
                self.f, self.ax = plt.subplots(figsize=self.figsize)
    
    def frame(self, iframe):
        imgframe = self.data[iframe,:,:]
        self.qmesh = self.ax.pcolormesh(self.xgrid, self.ygrid, np.flipud(imgframe), \
              cmap=self.cmap, vmin=self.vmin, vmax=self.vmax, zorder=self.zorder)
        self.txt = self.ax.text(self.textpos[0], self.textpos[1], self.text[iframe], \
                     fontsize=self.textsize, color=self.textcolor, \
                     zorder=1, transform=self.ax.transAxes)
        return self.f, self.qmesh
        
    def view_frame(self, iframe):
        _ = self.frame(iframe)
        return
        
    def animator(self, iframe):
        if not hasattr(self, 'qmesh'):
            self.qmesh = self.frame(0)[1]
        else:
            imgcurr = np.flipud(self.data[iframe,:,:])
            self.qmesh.set_array(imgcurr[:-1,:-1].flatten())
            self.txt.set_text(self.text[iframe])
        return self.f
    
    def view_anim(self, backend):
        self.anim = animation.FuncAnimation(self.f, self.animator,\
               frames=self.nframes, interval=self.interval)
        if backend == 'JS':
            return display_animation(self.anim)

            
class CompositePlotAnimate(LineAnimate, ImageAnimate):
    """
    Class for composite image and line animation
    """
    
    def __init__(self, x, y, data, fixed='x', axis=0, **kwargs):
        
        # Construct figure and axes objects
        self.figsize = kwargs.get('figsize', (5,6))
        if {'fig', 'ax'} <= set(kwargs.keys()):
            self.f, self.ax = kwargs['fig'], kwargs['ax']
        else:
            self.f, self.ax = plt.subplots(figsize=self.figsize)
        
        # Initiate animation with existing figure and axes handles
        ImageAnimate.__init__(self, data, axis=axis, fig=self.f, \
                ax=self.ax, figsize=self.figsize, zorder=0, **kwargs)
        LineAnimate.__init__(self, x, y, self.nframes, fixed=fixed, \
                fig=self.f, ax=self.ax, figsize=self.figsize, zorder=1, **kwargs)
    
    def frame(self, iframe):
        self.lines = LineAnimate.frame(self, iframe)
        self.qmesh = ImageAnimate.frame(self, iframe)[1]
        return self.lines, self.qmesh
    
    def view_frame(self, iframe):
        _ = self.frame(iframe)
        return
    
    def animator(self, iframe):
        LineAnimate.animator(self, iframe)
        ImageAnimate.animator(self, iframe)
        return self.f
    
    def view_anim(self, backend):
        self.anim = animation.FuncAnimation(self.f, self.animator,\
               frames=self.nframes, interval=self.interval)
        if backend == 'JS':
            return display_animation(self.anim)