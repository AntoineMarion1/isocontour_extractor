# Tools

The main project code is in the `contour.py` and `stitch.py` file. [`contour.py`](#contourpy) compute the isocontour of the scalar field. Once this tool has been used, the [`stitch.py`](#stitchpy) tool can be used to stitch these isocontours. The execution time logs are available in the file `data/log`.


The other tools can be run after the previous tools were used: 

- [`visualise.py`](#visualisepy)
- [`tosvg.py`](#tosvgpy)


## `contour.py`

Extract the isocontours of a scalar field. 

### Input

- **input_file_path**: path to a .npy file containing the data for a scalar field. 
- **output_file_name**: name of the file containing the graph data. 

### Output
- `data/np/<output_file_name>_contour.npz` .npz file describing the isolines of the scalar field.

### Usage 

```
python tools/contour.py input_file_path output_file_name
```

### Example 

```
python tools/contour.py data/fields/bunny.npy bunny 
```


## `stitch.py`

Stitch the isocontours that have been extracted. 

### Input

- **input_file_path**: path to a .npy file containing the data for a scalar field. 
- **neighbours**: (optionnal argument) distance from the reference edge to compute the neighbours. The distance is defined as a number of edges in the grid. 


### Output
- `data/np/<output_file_name>_cycle.npz` .npz file describing a single stitched cycle. 


### Usage 

```
python tools/stitch.py input_file_name neighbours
```

### Example 

```
python tools/stitch.py data/bunny.npy 10 
```





## `visualise.py`

Display the results of isocontour extraction in a window. The graph lines are blue for the single cycle, green for the isocontours. 

### Input 

- **input_file_path**: .npy file containing the data for a scalar field
- **datatosee**: 
    - _scalar_ to display the scalar field 
    - _contour_ to display the isocontours of the scalar field 
    - _cycle_ to display the print path 
    - _both_ to display the isocontours and press 'space' to dispaly the stitched cycle 



### Usage 
To be entered in the repository root console. 

```
python tools/visualise.py input_file_path datatosee
```

### Example 
```
python tools/visualise.py data/bunny.npy contour
```



## `tosvg.py`
Exports the isocontours or cycle as an SVG file. Please open the exported file with Inkscape. 

### Input 

- **input_file_path**: .npy file containing scalar field data

- **datatosee**: 
    - _contour_ to export the isocontours of the scalar field
    - _cycle_ to export the print trajectory 


### Output
 
- `data/svg_files/<output_file_name>_<datatosee>.svg` SVG file containing the cycle(s) of the graph. 


### Usage 
```
python tools/tosvg.py input_file_path datatosee
```

### Example 
```
python tools/tosvg.py data/bunny.npy contour
```

## Troubleshooting
- If isocontour extraction doesn't work, try reshaping the scalar field by inverting the x and y axes. If this still doesn't work, check that your scalar field has a border with the same sign everywhere. If not, try adding a border of 1. 

- Sometimes the stitching doesn't work. Please try changing the optional neighbours argument. If the sacalr field resolution is high, it should generally be increased, and decreased if the resolution is low. 

