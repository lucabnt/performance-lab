"""Run via Python inside the Android app, never use host success as Android proof."""
import io
import json
import sys


def check():
    if sys.platform != 'android' and not hasattr(sys, 'getandroidapilevel'):
        raise RuntimeError('This check must run inside the Android Python runtime')
    from PIL import Image, ImageDraw, ImageFont, features
    import PIL
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen.canvas import Canvas
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib import get_data_path
    from pathlib import Path
    assert PIL.__version__ == '13.0.0', PIL.__version__
    assert features.check('jpg') and features.check('zlib') and features.check('freetype2')
    image = Image.new('RGB', (240, 80), 'white')
    font = ImageFont.truetype(str(Path(get_data_path()) / 'fonts/ttf/DejaVuSans.ttf'), 18)
    ImageDraw.Draw(image).text((8, 8), 'Fuorigiri — città', font=font, fill='black')
    for fmt in ['PNG', 'JPEG']:
        encoded = io.BytesIO()
        image.save(encoded, format=fmt)
        encoded.seek(0)
        with Image.open(encoded) as decoded:
            decoded.load()
            assert decoded.size == image.size
    figure = Figure(figsize=(3, 2))
    FigureCanvasAgg(figure)
    figure.add_subplot().plot([0, 1, 2], [1, 3, 2])
    plot = io.BytesIO()
    figure.savefig(plot, format='png')
    plot.seek(0)
    pdf = io.BytesIO()
    canvas = Canvas(pdf)
    canvas.drawImage(ImageReader(plot), 30, 500, width=240, height=160)
    canvas.save()
    assert pdf.getvalue().startswith(b'%PDF-') and len(pdf.getvalue()) > 1000
    result = {'pillow': PIL.__version__, 'android_api': sys.getandroidapilevel(),
              'codecs': {name: features.version(name) for name in ['jpg', 'zlib', 'freetype2']},
              'png_jpeg_font_matplotlib_reportlab': 'passed', 'pdf_bytes': len(pdf.getvalue()),
              'limits': 'No UI export/open, app update, archive or device qualification'}
    print(json.dumps(result))
    return result


if __name__ == '__main__':
    check()
