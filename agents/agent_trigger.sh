#!/usr/bin/env bash
PIPE=/tmp/cursor_agent_pipe

# Colors
RESET="\033[0m"
CYAN="\033[0;36m"
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[1;33m" # Bold Yellow
BLUE="\033[0;34m"   # Blue for filepath

# Make sure the pipe exists
if [[ ! -p "$PIPE" ]]; then
  mkfifo "$PIPE" || { echo -e "${RED}Error: Could not create pipe $PIPE${RESET}"; exit 1; }
fi

# Spinner function
spinner() {
    local chars=("◢" "◣" "◤" "◥")
    local i=0
    tput civis # Hide cursor
    while true; do
        # Print over the same line. Ensure -e is used. -n suppresses newline.
        echo -e -n "${chars[$i]}${RESET} \r${CYAN}Integrator: waiting"
        i=$(( (i+1) % ${#chars[@]} ))
        sleep 0.2
    done
}

# Start spinner in background
spinner &
SPINNER_PID=$!

# Cleanup function to kill spinner and restore cursor
cleanup() {
    if ps -p $SPINNER_PID > /dev/null; then
        kill $SPINNER_PID >/dev/null 2>&1
        wait $SPINNER_PID 2>/dev/null
    fi
    # Clear the spinner line thoroughly and restore cursor
    echo -e -n "\r\033[K"
    tput cnorm
}

# Trap exit signals to ensure cleanup runs
trap cleanup EXIT INT TERM

# Read from pipe
if read -r cmd filepath < "$PIPE"; then
  # Kill spinner and clear its line immediately
  if ps -p $SPINNER_PID > /dev/null; then
      kill $SPINNER_PID &>/dev/null
      wait $SPINNER_PID 2>/dev/null
  fi
  echo -e -n "\r\033[K" # Clear spinner line

  # Process command
  if [[ "$cmd" == "integration_instructions_created" ]]; then # Only this command is supported
    echo -e "${YELLOW}▶ Trigger Received!${RESET}"
    echo -e "  Instructions for integration are now available in:"
    echo -e "  ${BLUE}${filepath}${RESET}" # Display full filepath
    echo -e "${CYAN}☞ ACTION REQUIRED (by controlling agent/Cursor):${RESET}"
    echo -e "  1. Read and process the instructions in the file above."
    echo -e "  2. Perform the integration into the PKM system."
    echo -e "  3. Once integration is complete, re-run this script (agent_trigger.sh) to await the next trigger."
  else
    echo -e "${RED}❓ Unknown command: '$cmd'. Exiting.${RESET}" >&2
    exit 1
  fi
else
  # This block executes if read fails
  echo -e "\r\033[K${RED}❌ Failed to read from pipe $PIPE. Was it closed?${RESET}" >&2
  exit 1
fi

# Explicitly restore cursor before exiting normally (trap EXIT handles other cases)
tput cnorm
exit 0