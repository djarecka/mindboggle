#!/usr/bin/python
"""
Functions that call the legacy ANTs package created by PICSL at UPenn.

Authors:
Arno Klein, 2011-2013  .  arno@mindboggle.info  .  www.binarybottle.com

Copyright 2013,  Mindboggle team (http://mindboggle.info), Apache v2.0 License

"""


def ImageMath(volume1, volume2, operator='m', output_file=''):
    """
    Use the ImageMath function in ANTS to perform operation on two volumes::

        m         : Multiply ---  use vm for vector multiply
        +         : Add ---  use v+ for vector add
        -         : Subtract ---  use v- for vector subtract
        /         : Divide
        ^         : Power
        exp       : Take exponent exp(imagevalue*value)
        addtozero : add image-b to image-a only over points where image-a has zero values
        overadd   : replace image-a pixel with image-b pixel if image-b pixel is non-zero
        abs       : absolute value
        total     : Sums up values in an image or in image1*image2 (img2 is the probability mask)
        mean      :  Average of values in an image or in image1*image2 (img2 is the probability mask)
        vtotal    : Sums up volumetrically weighted values in an image or in image1*image2 (img2 is the probability mask)
        Decision  : Computes result=1./(1.+exp(-1.0*( pix1-0.25)/pix2))
        Neg       : Produce image negative


    Parameters
    ----------
    volume1 : string
        nibabel-readable image volume
    volume2 : string
        nibabel-readable image volume
    operator : string
        ImageMath string corresponding to mathematical operator
    output_file : string
        nibabel-readable image volume

    Returns
    -------
    output_file : string
        name of output nibabel-readable image volume

    Examples
    --------
    >>> import os
    >>> from mindboggle.utils.ants import ImageMath
    >>> from mindboggle.utils.plots import plot_volumes
    >>> path = os.path.join(os.environ['MINDBOGGLE_DATA'])
    >>> volume1 = os.path.join(path, 'arno', 'mri', 't1weighted.nii.gz')
    >>> volume2 = os.path.join(path, 'arno', 'mri', 'mask.nii.gz')
    >>> operator = 'm'
    >>> output_file = ''
    >>> output_file = ImageMath(volume1, volume2, operator, output_file)
    >>> # View
    >>> plot_volumes(output_file)

    """
    import os
    from mindboggle.utils.utils import execute

    if not output_file:
        output_file = os.path.join(os.getcwd(), 'ImageMath.nii.gz')

    cmd = ['ImageMath', '3', output_file, operator, volume1, volume2]
    execute(cmd, 'os')
    if not os.path.exists(output_file):
        raise(IOError(output_file + " not found"))

    return output_file


def ANTS(source, target, iterations='30x99x11', output_stem=''):
    """
    Use ANTs to register a source image volume to a target image volume.

    This program uses the ANTs SyN registration method.

    Parameters
    ----------
    source : string
        file name of source image volume
    target : string
        file name of target image volume
    iterations : string
        number of iterations ("0" for affine, "30x99x11" default)
    output_stem : string
        file name stem for output transform matrix

    Returns
    -------
    affine_transform : string
        file name for affine transform matrix
    nonlinear_transform : string
        file name for nonlinear transform nifti file
    nonlinear_inverse_transform : string
        file name for nonlinear inverse transform nifti file
    output_stem : string
        file name stem for output transform matrix

    Examples
    --------
    >>> import os
    >>> from mindboggle.utils.ants import ANTS
    >>> path = os.environ['MINDBOGGLE_DATA']
    >>> source = os.path.join(path, 'arno', 'mri', 't1weighted_brain.nii.gz')
    >>> target = os.path.join(path, 'atlases', 'MNI152_T1_1mm_brain.nii.gz')
    >>> iterations = "0"
    >>> output_stem = ""
    >>> #
    >>> ANTS(source, target, iterations, output_stem)

    """
    import os
    from mindboggle.utils.utils import execute

    if not output_stem:
        src = os.path.basename(source).split('.')[0]
        tgt = os.path.basename(target).split('.')[0]
        output_stem = os.path.join(os.getcwd(), src+'_to_'+tgt)

    cmd = ['ANTS', '3', '-m CC[' + target + ',' + source + ',1,2]',
            '-r Gauss[2,0]', '-t SyN[0.5] -i', iterations,
            '-o', output_stem, '--use-Histogram-Matching',
            '--number-of-affine-iterations 10000x10000x10000x10000x10000']
    execute(cmd, 'os')

    affine_transform = output_stem + 'Affine.txt'
    nonlinear_transform = output_stem + 'Warp.nii.gz'
    nonlinear_inverse_transform = output_stem + 'InverseWarp.nii.gz'

    if not os.path.exists(affine_transform):
        raise(IOError(affine_transform + " not found"))
    if not os.path.exists(nonlinear_transform):
        raise(IOError(nonlinear_transform + " not found"))
    if not os.path.exists(nonlinear_inverse_transform):
        raise(IOError(nonlinear_inverse_transform + " not found"))

    return affine_transform, nonlinear_transform,\
           nonlinear_inverse_transform, output_stem


def WarpImageMultiTransform(source, target, output='',
                            interp='--use-NN', xfm_stem='',
                            affine_transform='', nonlinear_transform='',
                            inverse=False, affine_only=False):
    """
    Use ANTs to transform a source image volume to a target image volume.

    This program uses the ANTs WarpImageMultiTransform function.

    Parameters
    ----------
    source : string
        file name of source image volume
    target : string
        file name of target (reference) image volume
    output : string
        file name of output image volume
    interp : string
        interpolation type ("--use-NN" for nearest neighbor)
    xfm_stem : string
        file name stem for output transform
    affine_transform : string
        file containing affine transform
    nonlinear_transform : string
        file containing nonlinear transform
    inverse : Boolean
        apply inverse transform?
    affine_only : Boolean
        apply only affine transform?

    Returns
    -------
    output : string
        output label file name

    """
    import os
    import sys
    from mindboggle.utils.utils import execute

    if xfm_stem:
        affine_transform = xfm_stem + 'Affine.txt'
        if inverse:
            nonlinear_transform = xfm_stem + 'InverseWarp.nii.gz'
        else:
            nonlinear_transform = xfm_stem + 'Warp.nii.gz'
    elif not affine_transform and not nonlinear_transform:
        sys.exit('Provide either xfm_stem or affine_transform and '
                 'nonlinear_transform.')

    if not output:
        output = os.path.join(os.getcwd(), 'WarpImageMultiTransform.nii.gz')

    if not os.path.exists(nonlinear_transform):
        affine_only = True

    if affine_only:
        if inverse:
            cmd = ['WarpImageMultiTransform', '3', source, output, '-R',
                   target, interp, '-i', affine_transform]
        else:
            cmd = ['WarpImageMultiTransform', '3', source, output, '-R',
                   target, interp, affine_transform]
    else:
        if inverse:
            cmd = ['WarpImageMultiTransform', '3', source, output, '-R',
                   target, interp, '-i', affine_transform, nonlinear_transform]
        else:
            cmd = ['WarpImageMultiTransform', '3', source, output, '-R',
                   target, interp, nonlinear_transform, affine_transform]
    execute(cmd, 'os')

    if not os.path.exists(output):
        raise(IOError(output + " not found"))

    return output


def PropagateLabelsThroughMask(mask_volume, label_volume, mask_index=None,
                               output_file='', binarize=True):
    """
    Use ANTs to fill a binary volume mask with initial labels.

    This program uses ThresholdImage and the ImageMath
    PropagateLabelsThroughMask functions in ANTS.

    ThresholdImage ImageDimension ImageIn.ext outImage.ext
        threshlo threshhi <insideValue> <outsideValue>

    PropagateLabelsThroughMask: Final output is the propagated label image.
        ImageMath ImageDimension Out.ext PropagateLabelsThroughMask
        speed/binaryimagemask.nii.gz initiallabelimage.nii.gz ...

    Parameters
    ----------
    mask_volume : string
        nibabel-readable image volume
    label_volume : string
        nibabel-readable image volume with integer labels
    mask_index : integer (optional)
        mask with just voxels having this value
    output_file : string
        nibabel-readable labeled image volume
    binarize : Boolean
        binarize mask_volume?

    Returns
    -------
    output_file : string
        name of labeled output nibabel-readable image volume

    Examples
    --------
    >>> import os
    >>> from mindboggle.utils.ants import PropagateLabelsThroughMask
    >>> from mindboggle.utils.plots import plot_volumes
    >>> path = os.path.join(os.environ['MINDBOGGLE_DATA'])
    >>> label_volume = os.path.join(path, 'arno', 'labels', 'labels.DKT25.manual.nii.gz')
    >>> mask_volume = os.path.join(path, 'arno', 'mri', 't1weighted_brain.nii.gz')
    >>> mask_index = None
    >>> output_file = ''
    >>> binarize = True
    >>> output_file = PropagateLabelsThroughMask(mask_volume, label_volume, mask_index, output_file, binarize)
    >>> # View
    >>> plot_volumes(output_file)

    """
    import os
    from mindboggle.utils.utils import execute

    if not output_file:
        output_file = os.path.join(os.getcwd(),
                                   'PropagateLabelsThroughMask.nii.gz')

    # Binarize image volume:
    if binarize:
        temp_file = os.path.join(os.getcwd(),
                                 'PropagateLabelsThroughMask.nii.gz')
        cmd = ['ThresholdImage', '3', mask_volume, temp_file, '0 1 0 1']
        execute(cmd, 'os')
        mask_volume = temp_file

    # Mask with just voxels having mask_index value:
    if mask_index:
        mask = os.getcwd('temp.nii.gz')
        cmd = 'ThresholdImage 3 {0} {1} {2} {3} 1 0'.format(mask_volume, mask,
               mask_index, mask_index)
        execute(cmd)
    else:
        mask = mask_volume

    # Propagate labels:
    cmd = ['ImageMath', '3', output_file, 'PropagateLabelsThroughMask',
            mask, label_volume]
    execute(cmd, 'os')
    if not os.path.exists(output_file):
        raise(IOError(output_file + " not found"))

    return output_file


def fill_volume_with_surface_labels(volume_mask, surface_files,
                                    mask_index=None, output_file='',
                                    binarize=False):
    """
    Use ANTs to fill a volume mask with surface mesh labels.

    This program uses PropagateLabelsThroughMask in ANTS's ImageMath function.

    Note ::
        Partial volume information is lost when mapping the surface
        to the volume.

    Parameters
    ----------
    volume_mask : string
        nibabel-readable image volume
    surface_files : string or list of strings
        VTK file(s) containing surface mesh(es) with labels as scalars
    mask_index : integer (optional)
        mask with just voxels having this value
    output_file : string
        name of output file
    binarize : Boolean
        binarize volume_mask?

    Returns
    -------
    output_file : string
        name of labeled output nibabel-readable image volume

    Examples
    --------
    >>> import os
    >>> from mindboggle.utils.ants import fill_volume_with_surface_labels
    >>> from mindboggle.utils.plots import plot_volumes
    >>> path = os.path.join(os.environ['MINDBOGGLE_DATA'])
    >>> surface_files = [os.path.join(path, 'arno', 'labels',
    >>>     'lh.labels.DKT25.manual.vtk'), os.path.join(path, 'arno', 'labels',
    >>>     'rh.labels.DKT25.manual.vtk')]
    >>> volume_mask = os.path.join(path, 'arno', 'mri', 't1weighted_brain.nii.gz')
    >>> mask_index = None
    >>> output_file = ''
    >>> binarize = True
    >>> output_file = fill_volume_with_surface_labels(volume_mask, surface_files, mask_index, output_file, binarize)
    >>> # View
    >>> plot_volumes(output_file)

    """
    import os

    from mindboggle.utils.io_vtk import transform_to_volume
    from mindboggle.labels.relabel import overwrite_volume_labels
    from mindboggle.utils.ants import PropagateLabelsThroughMask
    from mindboggle.utils.utils import execute

    if isinstance(surface_files, str):
        surface_files = [surface_files]

    # Transform vtk coordinates to voxel index coordinates in a target
    # volume by using the header transformation:
    surface_in_volume = transform_to_volume(surface_files[0], volume_mask)

    # Do the same for additional vtk surfaces:
    if len(surface_files) == 2:
        surfaces_in_volume = os.path.join(os.getcwd(), 'surfaces.nii.gz')
        surface_in_volume2 = transform_to_volume(surface_files[1], volume_mask)

        overwrite_volume_labels(surface_in_volume, surface_in_volume2,
                                surfaces_in_volume, ignore_labels=[0])
        surface_in_volume = surfaces_in_volume

    # Use ANTs to fill a binary volume mask with initial labels:
    output_file = PropagateLabelsThroughMask(volume_mask, surface_in_volume,
                                             mask_index, output_file,
                                             binarize)
    if not os.path.exists(output_file):
        raise(IOError(output_file + " not found"))

    return output_file  # surface_in_volume
