"""frames.py: decode a film into small numpy frames, and grab single frames. Shared by the pipeline scripts.

decode(video, fps, width, gray)  -> (frames uint8 array (N, h, w) or (N, h, w, 3), fps)
grab(video, t, height)           -> PIL.Image or None
probe(video)                     -> {"duration", "w", "h", "fps"}
Needs ffmpeg/ffprobe, numpy, Pillow.
"""
import io, json, subprocess
import numpy as np
from PIL import Image


def probe(video):
    p = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type,width,height,r_frame_rate',
                                            '-of', 'json', video]))
    v = next(s for s in p['streams'] if s['codec_type'] == 'video')
    n, d = v['r_frame_rate'].split('/')
    return {'duration': float(p['format']['duration']), 'w': v['width'], 'h': v['height'], 'fps': round(float(n) / float(d), 3)}


def decode(video, fps=15, width=160, gray=True):
    info = probe(video)
    h = int(round(info['h'] * width / info['w'] / 2) * 2)
    fmt, ch = ('gray', 1) if gray else ('rgb24', 3)
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', video, '-vf', f'fps={fps},scale={width}:{h}:flags=area,format={fmt}',
                          '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    shape = (-1, h, width) if gray else (-1, h, width, 3)
    return np.frombuffer(raw, np.uint8).reshape(shape), fps


def grab(video, t, height=360):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{max(t, 0):.3f}', '-i', video, '-frames:v', '1', '-vf', f'scale=-2:{height}',
                          '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True).stdout
    return Image.open(io.BytesIO(raw)).convert('RGB') if raw else None
