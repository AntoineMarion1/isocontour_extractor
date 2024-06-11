# Tools

The main project code is in the `main.py` file. This tool computes the isolines of the scalar field using the marching square algorithm, then stitch them to create one trajectory.

The other tools can be run after [`main.py`](#mainpy) was used: 

- [`visualise.py`](#visualisepy)
- [`tosvg.py`](#tosvgpy)


## `main.py`

Extract the isocontours of a scalar field, then stitch them into a single cycle. 

### Input


- **input_file_path**: .npy file containing the data for a scalar field. 

### Output
- `data/np/<input_file_path>_cycle.npz` .npz file describing a single stitched cycle. 
- `data/np/<input_file_path>_contour.npz` .npz file describing the isolines of the scalar field.


### Usage 
To be entered in the repository root console. 

```
python tools/main.py input_file_path
```

### Example 
```

python tools/main.py bunny 
```


## `visualise.py`

Display the results of isocontour extraction in a window. The graph lines are blue for the single cycle, green for the isocontours. 

### Input 

- **input_file_path**: .npy file containing the data for a scalar field
- **datatosee**: 
    - _scalar_ to display the scalar field 
    - _contour_ to display the isocontours of the scalar field (press ‘space’ to display the stitched cycle)
    - _cycle_ to display the print path (press ‘space’ to display the contours)



### Usage 
To be entered in the repository root console. 

```
python tools/visualise.py input_file_path datatosee
```

### Example 
```
python tools/visualise.py bunny contour
```



## `tosvg.py`
Exports the isocontours or cycle as an SVG file. Please open the exported file with Inkscape. 

### Input 

- **input_file_path**: .npy file containing scalar field data

- **datatosee**: 
    - _contour_ to export the isocontours of the scalar field
    - _cycle_ to export the print trajectory 



### Output
 
- `data/svg_files/<input_file_path>_<datatosee>.svg` SVG file containing the cycle(s) of the graph. 


### Usage 
To be entered in the repository root console. 
```
python tools/tosvg.py input_file_name datatosee
```

### Example 
```
python tools/tosvg.py bunny contour
```