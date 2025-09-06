#!/bin/bash

echo "🎬 Enter the path to your input video file (.mp4, .mkv, etc.):"
read input_file

echo "📂 Enter the output .webp file path (example: output.webp):"
read output_file

echo "📐 Choose size (example: 640x480). Press Enter for default 640x480:"
read size
if [ -z "$size" ]; then
    size="640x480"
fi

echo "🚀 Converting '$input_file' to '$output_file' at size $size..."

ffmpeg -i "$input_file" -vcodec libwebp \
-filter:v fps=15 -lossless 0 -compression_level 6 -q:v 50 \
-loop 0 -preset default -an -vsync 0  "$output_file"

echo "✅ Done! Output saved as $output_file"

