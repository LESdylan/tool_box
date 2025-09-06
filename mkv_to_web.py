#!/usr/bin/env python3
"""
Simple MKV to WebP Converter using FFmpeg only
No Python dependencies required except standard library

This script uses FFmpeg directly to convert MKV to WebP
"""

import os
import sys
import subprocess
import argparse
import shutil


def check_ffmpeg():
    """Check if FFmpeg is available"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return True
    except FileNotFoundError:
        pass
    return False


def install_ffmpeg_suggestion():
    """Suggest how to install FFmpeg"""
    print("FFmpeg not found. To install:")
    print("• Ubuntu/Debian: apt install ffmpeg")
    print("• CentOS/RHEL: yum install ffmpeg")
    print("• macOS: brew install ffmpeg")
    print("• Or download from: https://ffmpeg.org/download.html")


def convert_mkv_to_webp(input_file, output_file=None,
                       start_time=0, duration=None,
                       fps=12, width=None, height=None,
                       quality=80, lossless=False,
                       loop=True, verbose=False):
    """
    Convert MKV to WebP using FFmpeg
    """
    
    # Check if FFmpeg is available
    if not check_ffmpeg():
        print("❌ FFmpeg not found!")
        install_ffmpeg_suggestion()
        return None
    
    # Validate input
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return None
    
    # Generate output filename
    if not output_file:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_algorithm_viz.webp"
    
    print(f"Converting {input_file} to {output_file}...")
    
    # Build FFmpeg command
    cmd = ['ffmpeg']
    
    # Input file
    cmd.extend(['-i', input_file])
    
    # Time constraints
    if start_time > 0:
        cmd.extend(['-ss', str(start_time)])
    if duration:
        cmd.extend(['-t', str(duration)])
    
    # Video filters
    filters = []
    
    # Resize
    if width and height:
        filters.append(f'scale={width}:{height}')
    elif width:
        filters.append(f'scale={width}:-1')
    elif height:
        filters.append(f'scale=-1:{height}')
    
    # Frame rate
    cmd.extend(['-r', str(fps)])
    
    # Apply filters
    if filters:
        cmd.extend(['-vf', ','.join(filters)])
    
    # WebP options
    if lossless:
        cmd.extend(['-lossless', '1'])
    else:
        cmd.extend(['-quality', str(quality)])
    
    # Loop (0 = infinite)
    if loop:
        cmd.extend(['-loop', '0'])
    
    # Overwrite output file
    cmd.extend(['-y', output_file])
    
    # Verbose output
    if not verbose:
        cmd.extend(['-loglevel', 'error'])
    
    try:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Check if file was created
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file) / (1024 * 1024)
                print(f"✅ Conversion successful!")
                print(f"📁 Output: {output_file}")
                print(f"📊 Size: {file_size:.2f} MB")
                return output_file
            else:
                print("❌ Output file was not created")
                return None
        else:
            print(f"❌ FFmpeg error:")
            print(result.stderr)
            return None
            
    except Exception as e:
        print(f"❌ Error running FFmpeg: {e}")
        return None


def get_video_info(input_file):
    """Get video information using FFprobe"""
    try:
        cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', 
               '-show_format', '-show_streams', input_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            
            # Find video stream
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    duration = float(stream.get('duration', 0))
                    width = stream.get('width', 0)
                    height = stream.get('height', 0)
                    fps = eval(stream.get('r_frame_rate', '0/1'))
                    
                    print(f"📹 Video Info:")
                    print(f"   Duration: {duration:.2f} seconds")
                    print(f"   Resolution: {width}x{height}")
                    print(f"   Frame rate: {fps:.2f} fps")
                    return duration, width, height, fps
                    
    except Exception as e:
        print(f"Could not get video info: {e}")
    
    return None, None, None, None


def batch_convert(input_dir, output_dir=None, **kwargs):
    """Batch convert MKV files"""
    if not os.path.isdir(input_dir):
        print(f"❌ Directory not found: {input_dir}")
        return
    
    if not output_dir:
        output_dir = input_dir
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Find MKV files
    mkv_files = [f for f in os.listdir(input_dir) 
                 if f.lower().endswith('.mkv')]
    
    if not mkv_files:
        print("No MKV files found")
        return
    
    print(f"Found {len(mkv_files)} MKV files")
    
    success_count = 0
    for mkv_file in mkv_files:
        input_path = os.path.join(input_dir, mkv_file)
        output_name = os.path.splitext(mkv_file)[0] + '_algorithm_viz.webp'
        output_path = os.path.join(output_dir, output_name)
        
        print(f"\n--- Converting {mkv_file} ---")
        result = convert_mkv_to_webp(input_path, output_path, **kwargs)
        if result:
            success_count += 1
    
    print(f"\n🎉 Converted {success_count}/{len(mkv_files)} files")


def main():
    parser = argparse.ArgumentParser(description='Convert MKV to WebP using FFmpeg')
    parser.add_argument('input', help='Input MKV file or directory')
    parser.add_argument('-o', '--output', help='Output WebP file or directory')
    parser.add_argument('-s', '--start', type=float, default=0, 
                       help='Start time in seconds')
    parser.add_argument('-d', '--duration', type=float, 
                       help='Duration in seconds')
    parser.add_argument('-f', '--fps', type=int, default=12, 
                       help='Frame rate (default: 12)')
    parser.add_argument('-w', '--width', type=int, help='Width in pixels')
    parser.add_argument('-H', '--height', type=int, help='Height in pixels')
    parser.add_argument('-q', '--quality', type=int, default=80, 
                       help='Quality 0-100 (default: 80)')
    parser.add_argument('--lossless', action='store_true', 
                       help='Use lossless compression')
    parser.add_argument('--no-loop', action='store_true', 
                       help='Disable looping')
    parser.add_argument('--batch', action='store_true', 
                       help='Batch process directory')
    parser.add_argument('-v', '--verbose', action='store_true', 
                       help='Verbose output')
    parser.add_argument('--info', action='store_true', 
                       help='Show video info only')
    
    args = parser.parse_args()
    
    # Show video info only
    if args.info:
        if os.path.isfile(args.input):
            get_video_info(args.input)
        else:
            print("❌ Please provide a video file for --info")
        return
    
    # Conversion parameters
    params = {
        'start_time': args.start,
        'duration': args.duration,
        'fps': args.fps,
        'width': args.width,
        'height': args.height,
        'quality': args.quality,
        'lossless': args.lossless,
        'loop': not args.no_loop,
        'verbose': args.verbose
    }
    
    try:
        if args.batch or os.path.isdir(args.input):
            batch_convert(args.input, args.output, **params)
        else:
            # Show video info first
            print("📹 Analyzing input video...")
            get_video_info(args.input)
            print()
            
            # Convert
            result = convert_mkv_to_webp(args.input, args.output, **params)
            
            if result:
                # Show file size comparison
                original_size = os.path.getsize(args.input) / (1024 * 1024)
                webp_size = os.path.getsize(result) / (1024 * 1024)
                compression = (1 - webp_size / original_size) * 100
                
                print(f"\n📊 Compression:")
                print(f"   Original: {original_size:.2f} MB")
                print(f"   WebP: {webp_size:.2f} MB")
                print(f"   Saved: {compression:.1f}%")
                
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == '__main__':
    print("🎬 Simple MKV to WebP Converter")
    print("=" * 40)
    
    if len(sys.argv) == 1:
        print("Usage examples:")
        print("  python3 mkv_to_web.py video.mkv")
        print("  python3 mkv_to_web.py video.mkv -f 15 -w 800 -q 90")
        print("  python3 mkv_to_web.py video.mkv --info")
        print("  python3 mkv_to_web.py ./videos --batch")
        print("\nThis version uses FFmpeg directly (no Python deps needed)")
        sys.exit(1)
    
    main()
