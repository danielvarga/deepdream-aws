from cStringIO import StringIO
import numpy as np
import scipy.ndimage as nd
import PIL.Image
from google.protobuf import text_format
import sys

import caffe

def saveImage(a, filename):
    b = np.uint8(np.clip(a, 0, 255))
    PIL.Image.fromarray(b).save(filename)


# a couple of utility functions for converting to and from Caffe's input image layout
def preprocess(net, img):
    # m = net.transformer.mean['data']
    m = 110.0
    return np.float32(np.rollaxis(img, 2)[::-1]) - m
def deprocess(net, img):
    # m = net.transformer.mean['data']
    m = 110.0
    return np.dstack((img + m)[::-1])

def smoothed(img, sigma=5):
    # This is not correct, it smoothes between colors, so turns it into grayscale:
    # But we are fine with that in this application.
    vis = nd.gaussian_filter(img, sigma=sigma)

    # This would be the correct way:
    # vis = np.concatenate([nd.gaussian_filter(img[...,x,np.newaxis], sigma=sigma) for x in xrange(img.shape[2])], axis=2)
    return vis

def make_step(net, step_size=1.5, end='inception_4c/output', jitter=32, clip=True, shift=True, mask=None):
    '''Basic gradient ascent step.'''

    src = net.blobs['data'] # input image is stored in Net's 'data' blob
    dst = net.blobs[end]

    if shift:
	ox, oy = np.random.randint(-jitter, jitter+1, 2)
	src.data[0] = np.roll(np.roll(src.data[0], ox, -1), oy, -2) # apply jitter shift
	mask = np.roll(np.roll(mask, ox, -1), oy, -2)

    net.forward(end=end)
    dst.diff[:] = dst.data  # specify the optimization objective

    net.backward(start=end)
    g = src.diff[0]

    # apply normalized ascent step to the input image
    if mask is not None:
	factor = (1.0*(mask<0))
#	print factor.shape,
	factor[:] = smoothed(factor[0], sigma=10)
	factor += 0.3
#	print factor.shape
#	print factor[0,::20,::20]
#	import sys
#	sys.exit()
#	vis = deprocess(net, 128.0*factor[:,::10,::10])
#	saveImage(vis, "tmp_factor.jpg")
	src.data[:] += step_size/np.abs(g).mean() * g * factor
    else :
        src.data[:] += step_size/np.abs(g).mean() * g

    if shift:
	src.data[0] = np.roll(np.roll(src.data[0], -ox, -1), -oy, -2) # unshift image
	# I don't think that's necessary:
	if mask is not None:
	    mask = np.roll(np.roll(mask, -ox, -1), -oy, -2)

    if clip:
        # bias = net.transformer.mean['data']
        bias = 110.0
        src.data[:] = np.clip(src.data, -bias, 255-bias)

def deepdream(net, base_img, iter_n=20, octave_n=4, octave_scale=1.4, end='inception_4c/output', clip=True, filename="vis.jpg", mask_img=None, **step_params):

    # prepare base images for all octaves
    octaves = [preprocess(net, base_img)]
    if mask_img is not None:
	masks = [preprocess(net, mask_img)]
    else:
	masks = [preprocess(net, np.ones_like(octaves[0]))]

    for i in xrange(octave_n-1):
        octaves.append(nd.zoom(octaves[-1], (1, 1.0/octave_scale,1.0/octave_scale), order=1))
        masks  .append(nd.zoom(masks  [-1], (1, 1.0/octave_scale,1.0/octave_scale), order=1))

    for octave, (octave_base, mask) in enumerate(reversed(zip(octaves,masks))):
	print octave_base.shape, mask.shape

    src = net.blobs['data']
    detail = np.zeros_like(octaves[-1]) # allocate image for network-produced details
    for octave, (octave_base, mask) in enumerate(reversed(zip(octaves,masks))):
        h, w = octave_base.shape[-2:]
        if octave > 0:
            # upscale details from the previous octave
            h1, w1 = detail.shape[-2:]
            detail = nd.zoom(detail, (1, 1.0*h/h1,1.0*w/w1), order=1)

        src.reshape(1,3,h,w) # resize the network's input image size
        src.data[0] = octave_base+detail
        for i in xrange(iter_n):
            make_step(net, end=end, clip=clip, mask=mask, **step_params)

            # visualization
            vis = deprocess(net, src.data[0])
            if not clip: # adjust image contrast if clipping is disabled
                vis = vis*(255.0/np.percentile(vis, 99.98))
            saveImage(vis, filename)
            print octave, i, end, vis.shape

        # extract details produced on the current octave
        detail = src.data[0]-octave_base
    # returning the resulting image
    return vis

def main():
    inImageFilename = sys.argv[1]
    base,ext = inImageFilename.rsplit(".",1)
    end = sys.argv[2]
    outImageFilename = ".".join((base, end.replace("/","-"), ext))

    img = np.float32(PIL.Image.open(inImageFilename))
    try:
	dumbPath = inImageFilename.split("/")
	maskImageFilename = "/".join(dumbPath[:-1]+["mask_"+dumbPath[-1]])
	print maskImageFilename
	mask_img = np.float32(PIL.Image.open(maskImageFilename))
	assert img.shape==mask_img.shape, "Input image and mask differ in size or color channel count." 
    except:
	print "Mask file not found, no masking."
	mask_img = None
    else:
	print "Mask file found, masking will be applied."

    model_path = 'caffe/models/bvlc_googlenet/' # substitute your path here
    net_fn   = model_path + 'deploy.prototxt'
    param_fn = model_path + 'bvlc_googlenet.caffemodel'

    # Patching model to be able to compute gradients.
    # Note that you can also manually add "force_backward: true" line to "deploy.prototxt".
    model = caffe.io.caffe_pb2.NetParameter()
    text_format.Merge(open(net_fn).read(), model)
    model.force_backward = True
    open('tmp.prototxt', 'w').write(str(model))

    net = caffe.Classifier('tmp.prototxt', param_fn)
    #net.set_channel_swap('data',(2,1,0))
    #net.set_mean('data', np.float32([104.0, 116.0, 122.0]))

    vis = deepdream(net, img, iter_n=20, octave_n=4, end=end, mask_img=mask_img, filename=outImageFilename)
    saveImage(vis, outImageFilename)

main()
