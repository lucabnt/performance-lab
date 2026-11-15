"""Numeric and native-provider checks for the rebuilt Android stack, not host proof."""

import ctypes
import json
import sys


def check():
    if not hasattr(sys, 'getandroidapilevel'):
        raise RuntimeError('Run inside the Android Python runtime')
    import numpy as np
    import matplotlib
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure
    from PIL import Image
    import io

    ft = ctypes.CDLL('libfreetype.so')
    ft.FT_Init_FreeType.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
    ft.FT_Init_FreeType.restype = ctypes.c_int
    ft.FT_Library_Version.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
    ]
    ft.FT_Done_FreeType.argtypes = [ctypes.c_void_p]
    library = ctypes.c_void_p()
    assert ft.FT_Init_FreeType(ctypes.byref(library)) == 0
    try:
        values = [ctypes.c_int() for _ in range(3)]
        ft.FT_Library_Version(library, *(ctypes.byref(v) for v in values))
        freetype_version = '.'.join(str(v.value) for v in values)
    finally:
        ft.FT_Done_FreeType(library)
    assert freetype_version == '2.15.0', freetype_version
    png = ctypes.CDLL('libpng16.so')
    png.png_get_libpng_ver.argtypes = [ctypes.c_void_p]
    png.png_get_libpng_ver.restype = ctypes.c_char_p
    png_version = png.png_get_libpng_ver(None).decode()
    assert png_version == '1.6.59', png_version
    blas = ctypes.CDLL('libopenblas.so')
    blas.openblas_get_config.restype = ctypes.c_char_p
    blas_config = blas.openblas_get_config().decode()
    assert 'OpenBLAS 0.3.34' in blas_config and 'USE64BITINT' not in blas_config, blas_config

    np.testing.assert_array_equal(
        np.array([[1.0, 2.0], [3.0, 4.0]]) @ np.array([[5.0, 6.0], [7.0, 8.0]]), [[19.0, 22.0], [43.0, 50.0]]
    )
    np.testing.assert_allclose(np.linalg.solve([[3.0, 1.0], [1.0, 2.0]], [9.0, 8.0]), [2.0, 3.0], rtol=0, atol=1e-12)
    np.testing.assert_allclose(
        np.linalg.solve([[1 + 1j, 2], [0, 2 - 1j]], [-1 + 1j, -1 - 2j]), [1 + 2j, -1j], rtol=0, atol=1e-12
    )
    np.testing.assert_allclose(np.linalg.eigvalsh([[2.0, 1.0], [1.0, 2.0]]), [1.0, 3.0], rtol=0, atol=1e-12)
    design = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    coefficients, *_ = np.linalg.lstsq(design, [2.0, 3.0, 5.0], rcond=None)
    np.testing.assert_allclose(coefficients, [2.0, 3.0], rtol=0, atol=1e-12)
    np.testing.assert_allclose(
        np.polyfit([0.0, 1.0, 2.0, 3.0], [1.0, 6.0, 19.0, 40.0], 2), [4.0, 1.0, 1.0], rtol=0, atol=1e-12
    )
    u, s, vh = np.linalg.svd(design, full_matrices=False)
    np.testing.assert_allclose((u * s) @ vh, design, rtol=0, atol=1e-12)
    figure = Figure(figsize=(3, 2))
    FigureCanvasAgg(figure)
    axis = figure.add_subplot()
    axis.plot([0, 1, 2], [0, 1, 0])
    axis.set_title('Verifica città')
    encoded = io.BytesIO()
    figure.savefig(encoded, format='png')
    encoded.seek(0)
    with Image.open(encoded) as image:
        image.load()
        assert image.width > 0 and image.height > 0
    result = {
        'numpy': np.__version__,
        'matplotlib': matplotlib.__version__,
        'shared_freetype': freetype_version,
        'shared_libpng': png_version,
        'openblas': blas_config,
        'numeric_vectors': 'passed',
        'matplotlib_font_png': 'passed',
        'limits': 'Does not certify all scientific methods, historical equivalence, or 16KB runtime',
    }
    print(json.dumps(result))
    return result


if __name__ == '__main__':
    check()
