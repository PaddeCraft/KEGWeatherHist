if [ -z "$DISPLAY" ] && [ $(tty) == /dev/tty1 ]; then
   exec i3
fi
