"""lst.cst science data display utilities."""

import gc
import logging
from abc import ABC, abstractmethod

import holoviews as hv
import numpy as np
from holoviews.operation.datashader import rasterize

from lsst.cst.utilities.image import CalExpData
from lsst.cst.utilities.transform import (
    ImageTransform,
    RGBImageTransform,
    StandardImageTransform,
)

from .options import ImageOptions

_log = logging.getLogger(__name__)


__all__ = [
    "ImageDisplay",
    "CalExpImageDisplay",
    "ImageArrayDisplay",
    "RGBImageDisplay",
]


class ImageDisplay(ABC):
    """Plot interface image."""

    def __init__(self):
        super().__init__()
        self._img = None

    @abstractmethod
    def render(self):
        """Render the image."""
        raise NotImplementedError()

    @abstractmethod
    def show(self):
        """Show the image."""
        raise NotImplementedError()

    @abstractmethod
    def rasterize(self):
        """Rasterize the image."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def image(self):
        """Underlying image.

        Returns
        -------
        image: `np.ndarray`
            Underlying image used to create the plot.
        """
        raise NotImplementedError()

    @property
    def transformed_image(self):
        """Underlying transformed image.

        Returns
        -------
        image: `np.ndarray`
            Underlying transformed image shown in the plot.
        """
        raise NotImplementedError()

    def delete(self):
        """Delete underlying image."""
        assert self._img is not None
        del self._img
        gc.collect()

    @staticmethod
    def from_image_array(
        image: np.ndarray,
        bounds: tuple[float, float, float, float],
        title: str = "No title",
        xlabel: str = "X",
        ylabel: str = "Y",
        image_options: ImageOptions = ImageOptions(),
    ):
        """Create a Plot class for the exposureF image.

        Parameters
        ----------
        image: `numpy.array`
            image to be plotted.
        bounds: tuple[float]
            image bounds.
        title: `str`
            title of the plot.
        xlabel: `str`
            label for the x coordinates.
        ylabel: `str`
            label for the y coordinates.
        image_options: `ImageOptions`
            Options for the underlying plot object.

        Returns
        -------
        results: `Plot`
            Plot instance for the exposureF
        """
        return ImageArrayDisplay(
            image, bounds, title, xlabel, ylabel, image_options
        )

    @staticmethod
    def from_cal_exp_data(
        cal_exp_data: CalExpData,
        title: str = None,
        xlabel: str = "X",
        ylabel: str = "Y",
        show_detections: bool = True,
        image_options: ImageOptions = ImageOptions(),
    ):
        """Create a Plot class for CalExpData.

        Parameters
        ----------
        cal_exp_data: `CalExpData`
            exposure instance returned from butler.
        title: `str`
            title of the plot.
        xlabel: `str`
            label for the x coordinates.
        ylabel: `str`
            label for the y coordinates.
        image_options: `ImageOptions`
            Options for the underlying plot object.
        sources_options: `PointsOptions`
            Options for the underlying sources plot object.

        Returns
        -------
        results: `Plot`
            Plot instance for the exposureF including sources.
        """
        return CalExpImageDisplay(
            cal_exp_data, title, xlabel, ylabel, show_detections, image_options
        )


class ImageArrayDisplay(ImageDisplay):
    """Plot for an array as an image.

    Parameters
    ----------
    image: `numpy.ndarray`
        1D image array to be show in the plot.
    title: `str`
        title of the plot.
    xlabel: `str`
        label for the x coordinates.
    ylabel: `str`
        label for the y coordinates.
    options: `Options`
        Options for the underlying plot object.
    """

    options = ImageOptions

    def __init__(
        self,
        image: np.array,
        bounds: tuple[float],
        title: str = None,
        xlabel: str = "X",
        ylabel: str = "Y",
        options: ImageOptions = ImageOptions(),
    ):
        self._image = image
        self._title = title
        self._xlabel = xlabel
        self._ylabel = ylabel
        self._img = None
        self._options = options
        self._image_transform = StandardImageTransform()
        self._image_bounds = bounds
        self._transformed_image = None

    def _set_image_transform(self, image_transform: ImageTransform):
        """Setter to change the image transformer before rendering the image.

        Parameters
        ----------
        image_transform: `ImageTransform`
            New image transformation image to be applied when
            rendering the plot
        """
        assert isinstance(
            image_transform, ImageTransform
        ), "Non valid type of ImageTransform"
        self._image_transform = image_transform

    def render(self):
        if self._img is not None:
            return
        self._transformed_image = self._image_transform.transform(self._image)
        self._img = hv.Image(
            self._transformed_image,
            bounds=self._image_bounds,
            kdims=[self._xlabel, self._ylabel],
        ).opts(
            title=self._title,
            xlabel=self._xlabel,
            ylabel=self._ylabel,
            **self._options.to_dict(),
        )

    def show(self):
        assert self._img is not None
        return self._img

    def rasterize(self):
        assert self._img is not None
        return rasterize(self._img)

    @property
    def image(self):
        return self._image

    @property
    def transformed_image(self):
        return self._transformed_image

    image_transform = property(fget=None, fset=_set_image_transform)


class CalExpImageDisplay(ImageDisplay):
    """Plot using Calexp data, includes the
       image and also the sources.

    Parameters
    ----------
    cal_exp_data: `CalExpData`
        cal exp data to be plot
    title: `str`, Optional
        Plot title. Default value: CalExpId information.
    xlabel: `str`, Optional
        Plot xlabel. Default value: 'X'.
    ylabel: `str`, Optional
        Plot ylabel. Default value: 'Y'.
    show_detections: `bool`, Optional
        True if detections should be added to the plot. Default value: True.
    image_options: `ImageOptions`, Optional
        Image options.
    """

    options = ImageOptions

    def __init__(
        self,
        cal_exp_data: CalExpData,
        title: str = None,
        xlabel: str = "X",
        ylabel: str = "Y",
        show_detections: bool = True,
        options: ImageOptions = ImageOptions(),
    ):
        super().__init__()
        assert isinstance(
            options, ImageOptions
        ), "Not valid options type, should be ImageOptions"
        self._cal_exp_data = cal_exp_data
        self._title = title
        self._xlabel = xlabel
        self._ylabel = ylabel
        self._image_options = options
        self._detections = None
        self._show_detections = show_detections

    def render(self):
        if self._img is not None:
            return
        if self._title is None:
            self._title = self._cal_exp_data.cal_exp_id
        self._img = ImageDisplay.from_image_array(
            image=self._cal_exp_data.get_image(),
            bounds=self._cal_exp_data.get_image_bounds(),
            title=self._title,
            xlabel=self._xlabel,
            ylabel=self._ylabel,
            image_options=self._image_options,
        )
        self._img.render()

    def show(self):
        return self._img.show()

    def rasterize(self):
        return self._img.rasterize()

    def delete(self):
        super().delete()

    @property
    def image(self):
        return self._cal_exp_data.get_image()

    @property
    def transformed_image(self):
        return self._img.transformed_image


class RGBImageDisplay(ImageDisplay):
    """Plot RGB image.

    Parameters
    ----------
    image: `numpy.ndarray`
        3D image array to be show in the plot.
    title: `str`
        title of the plot.
    xlabel: `str`
        label for the x coordinates.
    ylabel: `str`
        label for the y coordinates.
    options: `Options`
        Options for the underlying plot object.
    """

    def __init__(
        self,
        image: np.array,
        title: str = "Untitled",
        xlabel: str = "X",
        ylabel: str = "Y",
        options: ImageOptions = ImageOptions(),
    ):
        super().__init__()
        assert isinstance(
            options, ImageOptions
        ), "Not valid options type, should be ImageOptions"
        self._image = image
        self._image_transform = None
        self._img = None
        self._transformed_image = None
        self._title = title
        self._xlabel = xlabel
        self._ylabel = ylabel
        self._image_options = options
        self._image_transform = RGBImageTransform()

    def render(self):
        """Render the image."""
        self._transformed_image = self._image_transform.transform(self._image)
        self._img = hv.RGB(self._transformed_image).options(
            title=self._title,
            xlabel=self._xlabel,
            ylabel=self._ylabel,
            **self._image_options.to_dict(),
        )

    def show(self):
        """Show the image."""
        assert self._img is not None
        return self._img

    def rasterize(self):
        """Rasterize the image."""
        raise NotImplementedError()

    def image(self):
        """Underlying image.

        Returns
        -------
        image: `np.ndarray`
            Underlying image used to create the plot.
        """
        return self._image

    def _set_image_transform(self, image_transform: ImageTransform):
        """Setter to change the image transformer before rendering the image.

        Parameters
        ----------
        image_transform: `ImageTransform`
            New image transformation image to be applied when
            rendering the plot
        """
        assert isinstance(
            image_transform, ImageTransform
        ), "Non valid type of ImageTransform"
        self._image_transform = image_transform

    image_transform = property(fget=None, fset=_set_image_transform)
