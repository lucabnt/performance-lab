"""Run via Python inside the Android app, never use host success as Android proof."""
import io
import json
import sys


def check(output_directory=None, logo_path=None):
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
    assert features.version('freetype2') == '2.14.3', features.version('freetype2')
    assert features.version('libjpeg_turbo') == '3.2.0', features.version('libjpeg_turbo')
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
    if logo_path is not None:
        with Image.open(logo_path) as logo:
            logo.load()
            assert logo.width > 0 and logo.height > 0
        canvas.drawImage(logo_path, 30, 700, width=100, height=60,
                         preserveAspectRatio=True, mask='auto')
    canvas.save()
    assert pdf.getvalue().startswith(b'%PDF-') and len(pdf.getvalue()) > 1000
    pdf_path = None
    if output_directory is not None:
        import uuid
        destination = Path(output_directory) / f'pillow-native-{uuid.uuid4().hex}.pdf'
        with destination.open('xb') as stream:
            stream.write(pdf.getvalue())
        pdf_path = str(destination)
    result = {'pillow': PIL.__version__, 'python_build_api': sys.getandroidapilevel(),
              'codecs': {name: features.version(name) for name in ['jpg', 'libjpeg_turbo', 'zlib', 'freetype2']},
              'png_jpeg_font_matplotlib_reportlab': 'passed', 'pdf_bytes': len(pdf.getvalue()),
              'pdf_path': pdf_path, 'fixed_logo': 'passed' if logo_path is not None else 'not-tested',
              'limits': 'No UI export/open, app update, archive or device qualification'}
    print(json.dumps(result))
    return result


if __name__ == '__main__':
    check()
