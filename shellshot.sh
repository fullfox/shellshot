# Fileshot
fileshot() {
  local filename="$1"
  shift
  batcat --color=always --style=plain "$filename" --theme="Visual Studio Dark+" | pipeshot.py -t "$filename" "$@"
}

# Shellshot
record(){
  if [[ -z $SHELLSHOT ]];then
    local file=$(mktemp -t shellshot.XXXXXXXX)
    SHELLSHOT=$file exec script -qf $file -c zsh
  fi
}

if [[ -n $SHELLSHOT ]];then
  
  # Unexport $SHELLSHOT to prevent children for inheriting
  local file=$SHELLSHOT
  unset SHELLSHOT
  SHELLSHOT=$file
  
  echo "recording..."

  zshexit(){
    rm -f $SHELLSHOT
  }
  # Interactive zsh ignores SIGTERM, so on shutdown/logout `script` would end up
  # SIGKILLing us and the transcript would be left behind. Delete it ourselves.
  TRAPTERM(){
    rm -f $SHELLSHOT
    exit
  }

  # Don't edit these defaults, override them in your .zshrc before sourcing this file:
  #   SHELLSHOT_EXPORT_DIR=~/screenshots   # where .png/.svg are saved
  #   SHELLSHOT_ARGS=()                     # flags passed to shellshot.py (default: --open --clipboard)
  : ${SHELLSHOT_EXPORT_DIR:="$(xdg-user-dir PICTURES)/shellshot"}
  (( ${+SHELLSHOT_ARGS} )) || SHELLSHOT_ARGS=(--open --clipboard)
  mkdir -p $SHELLSHOT_EXPORT_DIR

  shot(){
    local sanitize() { echo "${1:0:40}" | tr -dc '[:alnum:] -'; }
    local BASE_FILENAME=$(sanitize "$(fc -lIn -1)") # to use the last ran command as filename
    #local BASE_FILENAME="shellshot_$(date +"%Y-%m-%d %Hh%Mm%S")" # to use date as filename
    local FILENAME="$BASE_FILENAME"
    local i=1
    while [[ -e "$SHELLSHOT_EXPORT_DIR/$FILENAME.png" || -e "$SHELLSHOT_EXPORT_DIR/$FILENAME.svg" ]]; do
      FILENAME="${BASE_FILENAME}_$i"
      ((i++))
    done
    shellshot.py -o "$SHELLSHOT_EXPORT_DIR/$FILENAME" "${SHELLSHOT_ARGS[@]}" "$SHELLSHOT" "$@"
  }

fi

record # comment this line to disable automatic recording
