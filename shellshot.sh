add_prefix() {
    echo -en "\033]prefix\007"
}

add_suffix() {
    echo -en "\033]suffix\007"
}

autoload -Uz add-zsh-hook
add-zsh-hook preexec add_prefix
add-zsh-hook precmd add_suffix

# Saving entered commands
LCMD=""
CCMD=""
logcmd () {
  LCMD=$CCMD
  CCMD=$1
}

autoload -Uz add-zsh-hook
add-zsh-hook preexec logcmd

record(){
  if [[ -z $SHELLSHOT ]];then
    dir="$HOME/.shellshot"
    mkdir -p $dir
    file="$dir/$(uuidgen)"
    SHELLSHOT=$file exec script -qf $file
    echo "test" > $SHELLSHOT
  fi
}

if [[ -n $SHELLSHOT ]];then
  
  # Unexport $SHELLSHOT to prevent children for inheriting
  local file=$SHELLSHOT
  unset SHELLSHOT
  SHELLSHOT=$file
  
  echo "recording..."

  zshexit(){
    rm $SHELLSHOT
  }

  # Path to save .svg and .png shellshots at:
  SHELLSHOT_EXPORT_DIR="$(xdg-user-dir PICTURES)/shellshot"

  mkdir -p $SHELLSHOT_EXPORT_DIR
  alias shot='shellshot.py "$SHELLSHOT" -c 1 -p "$LCMD" -o "$SHELLSHOT_EXPORT_DIR/shellshot" --png --open --clipboard'

fi

record # comment this line to disable automatic recording
