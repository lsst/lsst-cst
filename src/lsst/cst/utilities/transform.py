from abc import ABC, abstractmethod

import numpy as np
from astropy.visualization import AsinhStretch, ZScaleInterval


class ImageTransform(ABC):
    """Interface to make modifications on an image
    before rendering into a plot.
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def transform(self, image_array: np.ndarray):
        """Transform an image executing a series of actions over it.

        Parameters
        ----------
        image_array: `np.array`
            Array to be transformed

        Return
        ------
        transformed_image_array: `np.array`
            Array modified after all transformation has been applied.
        """
        raise NotImplementedError


class NoImageTransform(ImageTransform):
    """No transformation class, mainly used when no transformation
    is wanted on the image array.
    """

    def __init__(self):
        super().__init__()

    def transform(self, image_array: np.ndarray) -> np.ndarray:
        """Do no transformation on image_array.

        Parameters
        ----------
        image_array: `np.ndarray`
            array to no transform

        Returns
        -------
        image_array: `np.array`
            Same array passaed as argument
        """
        return image_array


class RGBImageTransform(ImageTransform):
    """Standard RGB Image modificacions. When executing transform the image
    will be fliped vertically.
    """

    def __init__(self):
        super().__init__()
        self._transformation = [self._flip_columns]

    def transform(self, image_array: np.ndarray) -> np.ndarray:
        """Transform an image executing vertical flip
        and dynamic range reduction.

        Parameters
        ----------
        image_array: `np.array`
            Array to be transformed.

        Returns
        -------
        transformed_image_array: `np.array`
            Array modified after all transformation has been applied.
        """
        for transformation_function in self._transformation:
            image_array = transformation_function(image_array)
        return image_array

    def _flip_columns(self, image_array: np.ndarray) -> None:
        """Flips vertically an image array.

        Parameters
        ----------
        image_array: `np.ndarray`
            Array to be vertically flip.

        Returns
        -------
        transformed_image_array: `np.array`
            Array vertically flipped.
        """
        return np.flipud(image_array)


class StandardImageTransform(ImageTransform):
    """Standard Image modificacions. When executing transform the image will be
    fliped vertically and dynamic range will be reduced.
    """

    def __init__(self):
        super().__init__()
        self._transformation = [self._scale_image, self._flip_columns]

    def transform(self, image_array: np.ndarray) -> np.ndarray:
        """Transform an image executing vertical flip
        and dynamic range reduction.

        Parameters
        ----------
        image_array: `np.array`
            Array to be transformed.

        Returns
        -------
        transformed_image_array: `np.array`
            Array modified after all transformation has been applied.
        """
        for transformation_function in self._transformation:
            image_array = transformation_function(image_array)
        return image_array

    def _flip_columns(self, image_array: np.ndarray) -> None:
        """Flips vertically an image array.

        Parameters
        ----------
        image_array: `np.ndarray`
            Array to be vertically flip.

        Returns
        -------
        transformed_image_array: `np.array`
            Array vertically flipped.
        """
        return np.flipud(image_array)

    def _scale_image(self, image_array: np.ndarray) -> None:
        """Reduce dynamic range of an image array.

        Parameters
        ----------
        image_array: `np.ndarray`
            Array to reduce dynamic range.

        Returns
        -------
        transformed_image_array: `np.array`
            Array with dynamic range reduced
        """
        transform = AsinhStretch() + ZScaleInterval()
        return transform(image_array)
