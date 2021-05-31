# MSPainter
Picture generator using MS Paint in Python

![Screenshot](https://github.com/James-P-D/MSPainter/blob/master/screenshot.gif)

(Note image has been sped-up. Actual process above generating a version of [David Hockney's 1966 painting The Splash](https://en.wikipedia.org/wiki/The_Splash) took 15 minutes)

## Usage

To use the program, first open MS Paint. Then run the `MSPainter.py` script, passing the full path to the image you wish to recreate:

```
python MSPainter.py c:\splash_small.jpg
```

The console will prompt you to first click on the top-left color icon (black) in MS Paint, then the bottom-right colour icon (light purple), and then finally click on the top-left corner of the empty canvas.

The program will then automatically move the mouse across the MS Paint palette and read the twenty possible colours. It will then slowly analyse the inputted image file and generate a 2D array mapping the colours of the original image to the closest possible colours available in the MS Paint palette. Once this process is complete, it will begin to paint the picture.