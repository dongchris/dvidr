import cv2
import numpy as np
import os
import skimage.io as skio


def get_image(url):
    """
    Get image array from url.
    """
    img = skio.imread(url)
    return img


def transform(pos):
    """
    Find corners and dimensions of the object.
    """
    pts=[]
    n=len(pos)
    for i in range(n):
        pts.append(list(pos[i][0]))
    sums={}
    diffs={}
    tl=tr=bl=br=0
    for i in pts:
        x=i[0]
        y=i[1]
        sum=x+y
        diff=y-x
        sums[sum]=i
        diffs[diff]=i
    sums=sorted(sums.items())
    diffs=sorted(diffs.items())
    n=len(sums)
    #      top-left   top-right   bottom-left   bottom-right
    rect=[sums[0][1],diffs[0][1],diffs[n-1][1],sums[n-1][1]]

    # height of left side
    h1=np.sqrt((rect[0][0]-rect[2][0])**2 + (rect[0][1]-rect[2][1])**2)
    # height of right side
    h2=np.sqrt((rect[1][0]-rect[3][0])**2 + (rect[1][1]-rect[3][1])**2)
    h=max(h1,h2)

    #width of upper side
    w1=np.sqrt((rect[0][0]-rect[1][0])**2 + (rect[0][1]-rect[1][1])**2)
    #width of lower side
    w2=np.sqrt((rect[2][0]-rect[3][0])**2 + (rect[2][1]-rect[3][1])**2)
    w=max(w1,w2)

    return int(w),int(h),rect


def process(img):
    """
    Main process of straighten image.
    Return a straightened image in gray-scale.
    """
    # resize image
    r = 500.0 / img.shape[1]
    dim = (500, int(img.shape[0] * r))
    img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

    # convert BGR to gray-scale
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    # Blur twice to remove noise
    gray = cv2.GaussianBlur(gray,(11,11),0)
    gray = cv2.GaussianBlur(gray,(11,11),0)

    # Canny edge detection
    edge = cv2.Canny(gray,10,200)
    edge = cv2.dilate(edge, None)
    edge = cv2.erode(edge, None)

    # find contours with biggest area
    _, contours, _ = cv2.findContours(edge.copy(),
                                      cv2.RETR_LIST,
                                      cv2.CHAIN_APPROX_NONE)
    n=len(contours)
    max_area=0
    pos=0
    for c in contours:
        area=cv2.contourArea(c)
        if area>max_area:
            max_area=area
            pos=c

    peri=cv2.arcLength(pos,True)
    approx=cv2.approxPolyDP(pos,0.01*peri,True)
    size=img.shape

    # get corners from transform function defined above
    w,h,arr=transform(approx)

    pts2=np.float32([[0,0],[w,0],[0,h],[w,h]])
    pts1=np.float32(arr)
    M=cv2.getPerspectiveTransform(pts1,pts2)
    dst=cv2.warpPerspective(img,M,(w,h))
    image=cv2.cvtColor(dst,cv2.COLOR_BGR2GRAY)
    image = cv2.resize(image,(w,h),interpolation = cv2.INTER_AREA)

    return image  # gray-scale


def straighten(url):
    """
    Straighten the image;
    Return straightened image in gray scale.
    """
    # get RGB image from url
    img = skio.imread(url)
    # convrt from RGB to BGR
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    # straighten image
    img = process(img)
    return img
