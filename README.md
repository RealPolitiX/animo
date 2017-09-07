# animo
OOP-style custom animations for IPython using matplotlib and JSAnimation


### Install animo  
```
pip install git+https://github.com/RealPolitiX/animo.git
```


### A quick guide to standard use cases
```
from animo import LineAnimate, ImageAnimate
```  
##### 1. Animation of line series  
(1) Construct the animation
```
anm = LineAnimate(x, y, nframes, fixed='x')
```  
(2) To view a single frame,
```
anm.view_frame(frame_number)
```  
(3) To view the whole animation,
```
anm.view_anim(backend='JS')
```


##### 2. Animation of image series  
(1) Construct the animation
```
anm = ImageAnimate(data, axis=0)
```  
(2) To view a single frame,
```
anm.view_frame(frame_number)
```  
(3) To view the whole animation,
```
anm.view_anim(backend='JS')
```


##### 3. Animation with mixed static and dynamic components  
(1) Construct the static figure  
(2) Pass the figure and axes handle to an instance of an animator class (such as LineAnimate or ImageAnimate) upon instantiation  
(3) Execute animation command as explained before


##### 4. Animate both lines and images  
Use the CompositePlotAnimate class in a similar way as LineAnimate and ImageAnimate