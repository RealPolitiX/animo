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
import matplotlib as mpl
import matplotlib.colors as colors


# ===== Utility functions ===== #

class MidpointNormalize(colors.Normalize):

    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))


def parse_norm(data, cscale):
    """
    Parser of string for color normalization
    """
    if isinstance(cscale, str):
        if cscale == 'log':  # log scale
            return mpl.colors.LogNorm()
        elif cscale == 'linear':  # linear scale (default)
            return mpl.colors.Normalize()
    elif isinstance(cscale, dict):
        mp = cscale.pop('midpoint', 0.)
        cvmin = cscale.pop('vmin', np.min(data))
        cvmax = cscale.pop('vmax', np.max(data))
        return MidpointNormalize(vmin=cvmin, vmax=cvmax, midpoint=mp)


# ===== Animator classes ===== #

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
        self.label = kwargs.get('label', '')
        self.legend = kwargs.get('legend', False)
        self.lgdloc = kwargs.get('legendloc', 'upper right')
        self.lgdttl = kwargs.get('legendtitle', '')
        self.linewidth = kwargs.get('linewidth', 2)
        self.linecolor = kwargs.get('linecolor', 'k')
        self.linestyle = kwargs.get('linestyle', '-')
        if {'fig', 'ax'} <= set(kwargs.keys()):
            self.f, self.ax = kwargs['fig'], kwargs['ax']
        else:
            self.f, self.ax = plt.subplots(figsize=self.figsize)

    def set_param(self, prop_statement):
        exec("self." + prop_statement)

    def frame(self, iframe):
        if self.fixed == 'x':
            self.lines, = self.ax.plot(self.x[0,:], self.y[iframe,:], linewidth=self.linewidth, \
                        color=self.linecolor, linestyle=self.linestyle, label=self.label, \
                        zorder=self.zorder)
        elif self.fixed == 'y':
            self.lines, = self.ax.plot(self.x[iframe,:], self.y[0,:], linewidth=self.linewidth, \
                        color=self.linecolor, linestyle=self.linestyle, label=self.label, \
                        zorder=self.zorder)
        elif self.fixed is None:
            self.lines, = self.ax.plot(self.x[iframe,:], self.y[iframe,:], linewidth=self.linewidth, \
                        color=self.linecolor, linestyle=self.linestyle, label=self.label, \
                        zorder=self.zorder)
        if self.legend == True:
            self.ax.legend(title=self.lgdttl, loc=self.lgdloc)
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
    
    def view_anim(self, backend=None):
        anim = animation.FuncAnimation(self.f, self.animator,\
                frames=self.nframes, interval=self.interval)
        if backend == 'JS':
            return display_animation(anim)
        elif backend is None:
            return self.anim
            

class MultiLineAnimate(LineAnimate):
    """
    Create multiline animation
    """
    
    def __init__(self, dataset, fixed, nframes, figsize=(6,4), **kwargs):
        self.f, self.ax = plt.subplots(figsize=figsize)
        self.dataset = dataset
        self.dscount = len(dataset)
        self.nframes = nframes
        self.labels = kwargs.get('labels', ['']*self.dscount)
        self.linewidths = kwargs.get('linewidths', [2]*self.dscount)
        self.linestyles = kwargs.get('linestyles', ['-']*self.dscount)
        self.linecolors = kwargs.get('linecolors', ['k']*self.dscount)
        self.zorders = kwargs.get('zorders', range(self.dscount))
        self.inst = []
        for i in range(self.dscount):
            self.inst.append(LineAnimate(*dataset[i], fixed=fixed, nframes=nframes,\
                fig=self.f, ax=self.ax, linewidth=self.linewidths[i], linecolor=self.linecolors[i], \
                linestyle=self.linestyles[i], label=self.labels[i], zorder=self.zorders[i], **kwargs))

    def set_inst_param(self, n_inst, prop_statement):
        exec("self.inst[n_inst]." + prop_statement)

    def frame(self, iframe):
        for i in range(self.dscount):
            self.inst[i].frame(iframe)
        return
    
    def view_frame(self, iframe):
        _ = self.frame(iframe)
        return
    
    def animator(self, iframe):
        for i in range(self.dscount):
            self.inst[i].animator(iframe)
        return self.f
    
    def view_anim(self, backend=None):
        anim = animation.FuncAnimation(self.f, self.animator,\
                frames=self.nframes, interval=self.inst[0].interval)
        if backend == 'JS':
            return display_animation(anim)
        elif backend is None:
            return self.anim
            

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
            self.colorbar = kwargs.get('colorbar', False)
            self.cscale = kwargs.get('cscale', 'linear')
            self.nframes = kwargs.get('nframes', data.shape[axis])
            self.xaxis = kwargs.get('imx', range(self.nc))
            self.yaxis = kwargs.get('imy', range(self.nr))
            self.xlabel = kwargs.get('xlabel', '')
            self.ylabel = kwargs.get('ylabel', '')
            self.axlabelsize = kwargs.get('axlabelsize', 15)
            self.figsize = kwargs.get('figsize', (5,6))
            self.xgrid, self.ygrid = np.meshgrid(self.xaxis, self.yaxis)
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
            self.ax.set_xlabel(self.xlabel, fontsize=self.axlabelsize)
            self.ax.set_ylabel(self.ylabel, fontsize=self.axlabelsize)
            
    def set_param(self, prop_statement):
        exec("self." + prop_statement)
    
    def frame(self, iframe):
        imgframe = self.data[iframe,:,:]
        self.qmesh = self.ax.pcolormesh(self.xgrid, self.ygrid, imgframe, \
              cmap=self.cmap, vmin=self.vmin, vmax=self.vmax, zorder=self.zorder)
        self.qmesh.set_norm(parse_norm(imgframe, self.cscale))
        self.txt = self.ax.text(self.textpos[0], self.textpos[1], self.text[iframe], \
                     fontsize=self.textsize, color=self.textcolor, \
                     zorder=1, transform=self.ax.transAxes)
        if self.colorbar == True:
            self.f.colorbar(self.qmesh)
        return self.f, self.qmesh
        
    def view_frame(self, iframe):
        _ = self.frame(iframe)
        return
        
    def animator(self, iframe):
        if not hasattr(self, 'qmesh'):
            self.qmesh = self.frame(0)[1]
        else:
            imgcurr = self.data[iframe,:,:]
            self.qmesh.set_array(imgcurr[:-1,:-1].flatten())
            self.txt.set_text(self.text[iframe])
        return self.f
    
    def view_anim(self, backend=None):
        self.anim = animation.FuncAnimation(self.f, self.animator,\
               frames=self.nframes, interval=self.interval)
        if backend == 'JS':
            return display_animation(self.anim)
        elif backend is None:
            return self.anim


class MultiImageAnimate(ImageAnimate):
    """
    Create connected multi-image animation
    """
    
    def __init__(self, dataset, axis=0, nrow=1, ncol=2, figsize=(12, 4), **kwargs):
        self.f, axs = plt.subplots(nrow, ncol, figsize=figsize)
        if np.ndim(axs) > 1:
            self.axs = axs.flatten()
        else:
            self.axs = axs
        self.dataset = dataset
        self.dscount = len(dataset)
        self.inst = []
        for i in range(self.dscount):
            self.inst.append(ImageAnimate(dataset[i], axis=axis, \
                            fig=self.f, ax=self.axs[i], **kwargs))

    def set_inst_param(self, n_inst, prop_statement):
        exec("self.inst[n_inst]." + prop_statement)
    
    def frame(self, iframe):
        for i in range(self.dscount):
            self.inst[i].frame(iframe)
        
    def view_frame(self, iframe):
        _ = self.frame(iframe)
        return
    
    def animator(self, iframe):
        for i in range(self.dscount):
            self.inst[i].animator(iframe)
        return self.f
    
    def view_anim(self, backend):
        self.anim = animation.FuncAnimation(self.f, self.animator,\
               frames=self.inst[0].nframes, interval=self.inst[0].interval)
        if backend == 'JS':
            return display_animation(self.anim)
        elif backend is None:
            return self.anim

            
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
    
    def view_anim(self, backend=None):
        self.anim = animation.FuncAnimation(self.f, self.animator,\
               frames=self.nframes, interval=self.interval)
        if backend == 'JS':
            return display_animation(self.anim)
        elif backend is None:
            return self.anim