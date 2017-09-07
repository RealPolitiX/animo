# animo
OOP-style custom animations for IPython using matplotlib and JSAnimation


### Install animo  
```
pip install git+https://github.com/RealPolitiX/animo.git
```


### A quick guide to simple use cases
```
from animo import LineAnimate, ImageAnimate
```  
1. Animation of line series  
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


2. Animation of image series  
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


3. Construct a composite animation (with both lines and images)