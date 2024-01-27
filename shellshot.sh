# Saving entered commands
LCMD=""
CCMD=""
preexec () {
  LCMD=$CCMD
  CCMD=$1
}

record(){
  if [[ -z $SCRIPT ]];then
    dir="$HOME/.shellshot"
    mkdir -p $dir
    file="$dir/$(uuidgen)"
    SCRIPT=$file exec script -qf $file
  fi
}

if [[ -n $SCRIPT ]];then
  echo "recording..."

  zshexit(){
    rm $SCRIPT
  }

  # Path to save .svg and .png shellshots at:
  SHELLSHOT_EXPORT_DIR="$(xdg-user-dir PICTURES)/shellshot"

  mkdir -p $SHELLSHOT_EXPORT_DIR
  alias shot='shellshot.py "$SCRIPT" -c 1 -p "$LCMD" -o "$SHELLSHOT_EXPORT_DIR/shellshot $(date +"%Y-%m-%d %H:%M:%S").png" --png --open'

fi

record # comment this line to disable automatic recording
