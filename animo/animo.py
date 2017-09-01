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
        if {'fig', 'ax'} <= set(kwargs.keys()):
            self.f, self.ax = kwargs['fig'], kwargs['ax']
        else:
            self.f, self.ax = plt.subplots(figsize=self.figsize)
        
    def frame(self, iframe):
        if self.fixed == 'x':
            self.lines, = self.ax.plot(self.x[0,:], self.y[iframe,:])
        elif self.fixed == 'y':
            self.lines, = self.ax.plot(self.x[iframe,:], self.y[0,:])
        elif self.fixed is None:
            self.lines, = self.ax.plot(self.x[iframe,:], self.y[iframe,:])
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
            _, self.nr, self.nc = self.data.shape
            self.interval = kwargs.get('interval', 100)
            self.nframes = kwargs.get('nframes', data.shape[axis])
            self.x = kwargs.get('x', range(self.nr))
            self.y = kwargs.get('y', range(self.nc))
            self.figsize = kwargs.get('figsize', (5,6))
            self.xgrid, self.ygrid = np.meshgrid(self.y, self.x)
            self.cmap = kwargs.get('cmap', 'terrain_r')
            self.vmin = kwargs.get('vmin', None)
            self.vmax = kwargs.get('vmax', None)
            if {'fig', 'ax'} <= set(kwargs.keys()):
                self.f, self.ax = kwargs['fig'], kwargs['ax']
            else:
                self.f, self.ax = plt.subplots(figsize=self.figsize)
    
    def frame(self, iframe):
        imgframe = self.data[iframe,:,:]
        self.qmesh = self.ax.pcolormesh(self.xgrid, self.ygrid, np.flipud(imgframe), \
              cmap=self.cmap, vmin=self.vmin, vmax=self.vmax)
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
        return self.f
    
    def view_anim(self, backend):
        self.anim = animation.FuncAnimation(self.f, self.animator,\
               frames=self.nframes, interval=self.interval)
        if backend == 'JS':
            return display_animation(self.anim)