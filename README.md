# animo
OOP-style custom animations for IPython using matplotlib and JSAnimation


#### Install animo  
```
pip install git+https://github.com/RealPolitiX/animo.git
```


#### Explanation of simple use cases
```
from animo import LineAnimate, ImageAnimate
```
1. Construct animation of line series
```anm = LineAnimate(x, y, nframes, fixed='x')```

to view a single frame,
```anm.view_frame(frame_number)```

to view the whole animation,
```anm.view_anim(backend='JS')```


2. Construct animation of image series
```anm = ImageAnimate(data, axis=0)```

to view a single frame,
```anm.view_frame(frame_number)

to view the whole animation,
```anm.view_anim(backend='JS')```


3. Construct a composite animation (with both lines and images)