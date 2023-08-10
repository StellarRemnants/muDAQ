#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 11:23:27 2023

@author: stellarremnants
"""

import numpy as np
import matplotlib.pyplot as plt

"""
Wrapper for creating random values (to create artificial inputs for the plotter)
"""
def random_data_generator(*array_size):
    """
    Generates an array of random values in the range [0, 1)

    Parameters
    ----------
    *array_size : integers
        d0, d1, ..., dn
        Integers corresponding to the dimensions of the returned array
        (e.g. 10, 2, 3 produces an array with shape (10, 2, 3))

    Returns
    -------
    output_array : numpy.ndarray
        An array with shape (d0, d1, ..., dn).

    """
    return np.random.rand(*array_size)


"""
Wrapper for creating a figure with a set shape
"""
def create_figure(
        *args,
        ylim=None,
        xlim=None,
        **kwargs,
        ):
    """
    Creates a figure with the given parameters with the matplotlib backend

    Parameters
    ----------
    *args : arguments
        Arguments to be passed to plt.subplots().
    ylim : list, optional
        An iterable with length 2. Sets the vertical limits of the plot 
        [ymin, ymax]. The default is None.
    xlim : list, optional
        An iterable with length 2. Sets the horizontal limits of the plot 
        [xmin, xmax]. The default is None.
    **kwargs : keyword arguments
        Keyword arguments to be passed to plt.subplots().

    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure handle.
    ax : matplotlib.axes._subplots.AxesSubplot
        Axis handle.

    """
    fig, ax = plt.subplots(*args, **kwargs)
    if not (ylim is None):
        ax.set_ylim(ylim)
    if not (xlim is None):
        ax.set_xlim(xlim)
        
    return fig, ax

"""
Utility function for appending two arrays of arbitrary shape along their first
axis. new_data may be the same number of dimensions or one shorter.
Must match in all other dimensions. Used for appending new data onto the 
existing displayed data.
"""
def smart_append(orig_data, new_data):
    """
    Intelligently appends new_data onto orig_data.
    Constraints:
        new_data must have the same shape as orig_data.shape[1:]
        (i.e. new_data must have one fewer dimensions than orig_data and have 
         the same dimensions on all axes but the first)
       OR
        new_data.shape[1:] must be the same as orig_data.shape[1:]
        (i.e. new_data must have the same number of dimensions as orig_data and 
         have the same dimensions on all axes but the first)

    Parameters
    ----------
    orig_data : numpy.ndarray
        An array of arbitrary shape.
    new_data : numpy.ndarray
        An array of the same number of dimensions as orig_data and sharing all 
        dimensions except for the first.
       OR
        An array of one fewer dimensions than orig_data and sharing all 
        dimensions with the dimensions of orig_data following its first.
    Returns
    -------
    numpy.ndarray
        An appended array with the same dimensions as orig_data save for being 
        longer in the first dimension according to new_data.

    """
    
    if not(orig_data.shape[1:] == new_data.shape):
        if not(len(orig_data.shape) == len(new_data.shape)):
            pass # Cannot be coerced
        else:
            if not(orig_data.shape[1:] == new_data.shape[1:]):
                pass # cannot be coerced
            else:
                return np.append(orig_data, new_data, axis=0) # append along axis 0
    else:
        return np.append(orig_data, [new_data], axis=0) # append along axis 0 using list wrap around new_data
    
    
"""
Utility function for appending new_data onto orig_data while maintaining the
original array shape. Deletes 'oldest' data first.
"""
def smart_queue_rotate(orig_data, new_data, max_length=None):
    """
    Adds new_data onto orig_data and removes the corresponding number of entries
    from the beginning of the returned array to maintain a length of max_length 
    in the first dimension (if specified) otherwise the original length of the 
    first dimension of orig_data

    Parameters
    ----------
    orig_data : numpy.ndarray
        An array of arbitrary shape.
    new_data : numpy.ndarray
        An array of the same number of dimensions as orig_data and sharing all 
        dimensions except for the first.
       OR
        An array of one fewer dimensions than orig_data and sharing all 
        dimensions with the dimensions of orig_data following its first.
    max_length : int, optional
        An integer which caps the length of the returned array, otherwise uses 
        the original first dimension of orig_data. The default is None.

    Returns
    -------
    numpy.ndarray
        An appended array with the same dimensions as orig_data, or the same 
        except for having length max_length in the first dimension

    """
    if max_length is None:
        max_length = orig_data.shape[0]
        
    appended_data = smart_append(orig_data, new_data)
    new_length = appended_data.shape[0]
    return appended_data[new_length-max_length:]

# %%
if __name__ == "__main__":
    # Instantiate image
    fig, ax = create_figure()
    
    #Create initial data
    data_shape = [20, 2]
    x_vals = np.arange(0, data_shape[0])
    data = random_data_generator(*data_shape)
    
    #Plot initial data
    line_list = []
    for i in range(data_shape[1]):
        # Plot each line and hold a reference to each in a list
        line_list.append(
            ax.plot(
                x_vals, data[:,i], label=f"Line: {i+1}",
                marker="o", ls="--"    
                    )
            )
    
    #Add labels, flairs, etc.
    fig.suptitle("Example Live Plot")
    ax.legend(loc="lower left")
    ax.set_ylabel("Y Axis")
    ax.set_xlabel("X Axis")
    
    # %%
    for i in range(15):
        for j in range(len(line_list)):
            # Get the current data from the line objects
            x, y = line_list[j][0].get_data()
            
            #Create the new datapoints and rotate them into the displayed data
            b = smart_queue_rotate(y, random_data_generator(1))
            line_list[j][0].set_data(x, b)
        
        #Non-blocking flag is important to allow figure to be shown after being updated
        plt.show(block=False)
        
        #Pause for one second between frames - could instead be read from file, etc.
        plt.pause(1)
        
    #Blocking show - if run from commandline, keeps plot open until manually closed
    plt.show()