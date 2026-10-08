import { Config } from '@remotion/cli/config';

// PNG frames keep gradients clean; JPEG frames band before the encoder ever sees them.
Config.setVideoImageFormat('png');
Config.setConcurrency(null);
