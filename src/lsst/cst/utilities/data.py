import warnings

from astropy.visualization import make_lupton_rgb

_lsst_stack_ready = False
try:
    import lsst.geom as geom
except ImportError:
    warnings.warn("Unable to import lsst.geom")
    _lsst_stack_ready = True


__all__ = ["create_rgb", "cutout_coadd"]


def create_rgb(image, bgr="gri", stretch=1, Q=10, scale=None):
    """Create an RGB color composite image.

    Parameters
    ----------
    image : `MultibandExposure`
        `MultibandExposure` to display.
    bgr : `sequence`, optional
        A 3-element sequence of filter names (i.e., keys of the exps dict)
        indicating what band to use for each channel. If `image` only has
        three filters then this parameter is ignored and the filters
        in the image are used.
    stretch: `int`, optional
        The linear stretch of the image.
    Q: `int`, optional
        The Asinh softening parameter.
    scale: `List[float]`, optional
        list of 3 floats, each less than 1.
        Re-scales the RGB channels.

    Returns
    -------
    rgb: `ndarray`
        RGB (integer, 8-bits per channel) colour
        image as an NxNx3 numpy array.
    """
    # If the image only has 3 bands, reverse
    # the order of the bands
    # to produce the RGB image
    if len(image) == 3:
        bgr = image.filters

    # Extract the primary image component
    # of each Exposure with the
    #   .image property, and use .array
    # to get a NumPy array view.

    if scale is None:
        r_im = image[bgr[2]].array  # numpy array for the r channel
        g_im = image[bgr[1]].array  # numpy array for the g channel
        b_im = image[bgr[0]].array  # numpy array for the b channel
    else:
        # manually re-scaling the images here
        r_im = image[bgr[2]].array * scale[0]
        g_im = image[bgr[1]].array * scale[1]
        b_im = image[bgr[0]].array * scale[2]

    rgb = make_lupton_rgb(
        image_r=r_im, image_g=g_im, image_b=b_im, stretch=stretch, Q=Q
    )
    # "stretch" and "Q" are parameters to
    # stretch and scale the pixel values

    return rgb


def cutout_coadd(
    butler,
    ra,
    dec,
    band="r",
    dataset_type="deepCoadd",
    skymap=None,
    cutout_side_length=51,
    **kwargs,
):
    """Produce a cutout from a coadd at the given ra, dec position.
    Adapted from DC2 tutorial notebook by Michael Wood-Vasey.

    Parameters
    ----------
    butler: `lsst.daf.persistence.Butler`
        Helper object providing access to a data repository
    ra: `float`
        Right ascension of the center of the cutout, in degrees
    dec: `float`
        Declination of the center of the cutout, in degrees
    band: `string`, optional
        Filter of the image to load
    dataset_type: `string [deepCoadd]`, optional
        Which type of coadd to load.  Doesn't support 'calexp'
    skymap: `lsst.afw.skyMap.SkyMap`, optional
        Pass in to avoid the Butler read.
        Useful if you have lots of them.
    cutout_side_length: `float`, optional
        Size of the cutout region in pixels.

    Returns
    -------
    image: `MaskedImage`
        Cutout image.
    """
    if not _lsst_stack_ready:
        raise Exception(
            "Cannot use this cutout_coadd " "if lsst stack is not loaded"
        )
    radec = geom.SpherePoint(ra, dec, geom.degrees)
    cutout_size = geom.ExtentI(cutout_side_length, cutout_side_length)

    if skymap is None:
        skymap = butler.get("skyMap")

    # Look up the tract, patch for the RA, Dec
    tractInfo = skymap.findTract(radec)
    patchInfo = tractInfo.findPatch(radec)
    xy = geom.PointI(tractInfo.getWcs().skyToPixel(radec))
    bbox = geom.BoxI(xy - cutout_size // 2, cutout_size)
    patch = tractInfo.getSequentialPatchIndex(patchInfo)

    coaddId = {"tract": tractInfo.getId(), "patch": patch, "band": band}
    parameters = {"bbox": bbox}

    cutout_image = butler.get(
        dataset_type, parameters=parameters, dataId=coaddId
    )

    return cutout_image
