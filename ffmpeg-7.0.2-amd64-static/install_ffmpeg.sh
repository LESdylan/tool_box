wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
tar -xf ffmpeg-release-amd64-static.tar.xz
./ffmpeg-*-amd64-static/ffmpeg -version
ln -s ~/tool_box/ffmpeg-*-amd64-static/ffmpeg ~/tool_box/ffmpeg
ln -s ~/tool_box/ffmpeg-*-amd64-static/ffprobe ~/tool_box/ffprobe
export PATH=$PATH:~/tool_box
