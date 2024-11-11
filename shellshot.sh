add_prefix() {
    echo -en "\033]prefix\007"
}

add_suffix() {
    echo -en "\033]suffix\007"
}

autoload -Uz add-zsh-hook
add-zsh-hook preexec add_prefix
add-zsh-hook precmd add_suffix

record(){
  if [[ -z $SHELLSHOT ]];then
    dir="$HOME/.shellshot"
    mkdir -p $dir
    file="$dir/$(uuidgen)"
    SHELLSHOT=$file exec script -qf $file
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
  : ${SHELLSHOT_EXPORT_DIR:="$(xdg-user-dir PICTURES)/shellshot"} # Define SHELLSHOT_EXPORT_DIR as env var to override
  mkdir -p $SHELLSHOT_EXPORT_DIR

  shot(){
    CMDS=$(fc -lIn 0)
    local sanitize() { echo "${1:0:20}" | tr -dc '[:alnum:] -'; }
    local SANITIZED_FILENAME=$(sanitize "$(fc -lIn -1)")_$(date +%s) # to use the last ran command as filename
    #local SANITIZED_FILENAME="shellshot $(date +"%Y-%m-%d %Hh%Mm%S")" # to use date as filename
    if [ $# -eq 0 ]; then
      local default=1
    else
      local default=($@)
    fi
    shellshot.py "$SHELLSHOT" $default -c "$CMDS" -o "$SHELLSHOT_EXPORT_DIR/$SANITIZED_FILENAME" --png --open --clipboard
  }

fi

record # comment this line to disable automatic recording
