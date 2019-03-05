/**
 * The first step is pretty clear: The captcha is copied into the canvas and then converted
 * to grayscale.
 */

function convert_grey(image_data){
	for (var x = 0; x < image_data.width; x++) {
		for (var y = 0; y < image_data.height; y++) {
			var i = x*4 + y*4*image_data.width;
			var luma = Math.floor(image_data.data[i] * 299/1000 + image_data.data[i+1] * 587/1000
								+ image_data.data[i+2] * 114/1000);
			image_data.data[i] = luma;
			image_data.data[i+1] = luma;
			image_data.data[i+2] = luma;
			image_data.data[i+3] = 255;
		}
	}
}

/**
 * The canvas is then broken apart into three separate pixel matrices - each containing an
 * individual character (this is quite easy to do - since each character is a separate color,
 * they're broken apart just based upon the different colors used).
 */

filter(image_data[0], 105);
filter(image_data[1], 120);
filter(image_data[2], 135);

function filter(image_data, colour){
	for (var x = 0; x < image_data.width; x++) {
		for (var y = 0; y < image_data.height; y++) {
			var i = x*4 + y*4*image_data.width;
			// Turn all the pixels of the certain colour to white
			if (image_data.data[i] == colour) {
				image_data.data[i] = 255;
				image_data.data[i+1] = 255;
				image_data.data[i+2] = 255;
			}
			// Everything else to black
			else {
				image_data.data[i] = 0;
				image_data.data[i+1] = 0;
				image_data.data[i+2] = 0;
			}
		}
	}
}

/**
 * Finally any extraneous noisy pixels are removed from the image (providing a clear character).
 * This is done by looking for white pixels (ones that've been matched) that are surrounded
 * (above and below) by black, un-matched, pixels. If that's the case then the matching pixel
 * is simply removed.
 */

var i = x*4+y*4*image_data.width;
var above = x*4+(y-1)*4*image_data.width;
var below = x*4+(y+1)*4*image_data.width;
if (image_data.data[i] == 255 && image_data.data[above] == 0 && image_data.data[below] == 0) {
	image_data.data[i] = 0;
	image_data.data[i+1] = 0;
	image_data.data[i+2] = 0;
}

/**
 * We're getting really close to having a shape that we can feed into the neural network, but
 * it's not completely there yet. The script then goes on to do some very crude edge detection
 * on the shape. The script looks for the top, left, right, and bottom-most pixels in the shape
 * and turns it into a rectangle - and converts that shape back into a 20 by 25 pixel matrix.
 */

cropped_canvas.getContext("2d").fillRect(0, 0, 20, 25);
var edges = find_edges(image_data[i]);
cropped_canvas.getContext("2d").drawImage(canvas, edges[0], edges[1], edges[2]-edges[0],
				edges[3] - edges[1], 0, 0, edges[2] - edges[0], edges[3] - edges[1]);
image_data[i] = cropped_canvas.getContext("2d").getImageData(0, 0, cropped_canvas.width,
				cropped_canvas.height);

/**
 * So - after all this work, what do we have? A 20 by 25 matrix containing a single rectangle,
 * drawn in black and white. Terribly exciting. That rectangle is then reduced even further.
 * A number of strategically-chosen points are then extracted from the matrix in the form of
 * "receptors" (these will feed the neural network). For example a receptor might be to look at
 * the pixel at position 9x6 and see if it's "on" or not. A whole series of these states are
 * computed (much less than the full 20x25 grid - a mere 64 states) and fed into the neural
 * network. The question that you should be asking yourself now is: Why not just do a straight
 * pixel comparison? Why all this mess with the neural network? Well, the problem is, with all
 * of reduction of information a lot ambiguity exists.
 * If you run <a href="http://herecomethelizards.co.uk/mu_captcha/">the online demo</a> of this
 * script you’re more likely to find the occasional failure from the straight pixel comparison
 * than from running it through the network. That being said, for most users, a straight pixel
 * comparison would probably be sufficient.
 */

