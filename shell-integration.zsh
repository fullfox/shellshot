# Slightly modified version of
# https://gitlab.freedesktop.org/Per_Bothner/specifications/-/blob/master/proposals/prompts-data/shell-integration.zsh

urlencode() {
  local LC_ALL=C s="$1" out="" i c
  for (( i=1; i<=${#s}; i++ )); do
    c="${s[i]}"
    [[ $c == [A-Za-z0-9._~-] ]] || printf -v c '%%%02X' "'$c"
    out+="$c"
  done
  print -r -- "$out"
}

_prompt_executing=""
function __prompt_precmd() {
    local ret="$?"
    if test "$_prompt_executing" != "0"
    then
      _PROMPT_SAVE_PS1="$PS1"
      _PROMPT_SAVE_PS2="$PS2"
      PS1=$'%{\e]133;P;k=i\a%}'$PS1$'%{\e]133;B\a\e]122;> \a%}'
      PS2=$'%{\e]133;P;k=s\a%}'$PS2$'%{\e]133;B\a%}'
    fi
    if test "$_prompt_executing" != ""
    then
       printf "\033]133;D;%s;aid=%s\007" "$ret" "$$"
    fi
    printf "\033]133;A;cl=m;aid=%s\007" "$$"
    _prompt_executing=0
}
function __prompt_preexec() {
    PS1="$_PROMPT_SAVE_PS1"
    PS2="$_PROMPT_SAVE_PS2"
    printf "\033]133;C;cmd=%s\007" "$(urlencode "$1")"
    _prompt_executing=1
}
preexec_functions+=(__prompt_preexec)
precmd_functions+=(__prompt_precmd)
