IMPORTANT INSTRUCTIONS FOR CURSOR AGENT = INTEGRATOR AGENT (YOU, THE CONTROLLING AI):
1. AFTER YOU HAVE COMPLETED THE INTEGRATION OF INSTRUCTIONS, YOU MUST RUN THE Integrator Agent SCRIPT (agent_trigger.sh) AGAIN. This puts it back in waiting mode.
2. YOUR PRIMARY ROLE IS TO PERFORM THE INTEGRATION. After doing so, always be ready for the next set of instructions by restarting the Integrator Agent's waiting mode as per step 6.

WORKFLOW:
1. Run the Instruct Agent (Another agent, not you) script `cd agents && python instruct_agent.py` and move it to the background. This agent listens for voice notes, transcribes them, and generates integration instruction files.
2. Then run the Integrator Agent script `cd agents && ./agent_trigger.sh` in another terminal. This script WAITS INDEFINITELY for a trigger from the Instruct Agent.
3. When the Instruct Agent creates an instruction file, it will trigger the Integrator Agent script (`agent_trigger.sh`). The Integrator Agent script will then display a message indicating:
    a. That a trigger was received.
    b. The **full path** to the newly created integration instructions file.
    c. A clear message that **ACTION IS REQUIRED BY YOU (THE CONTROLLING AI/CURSOR)** to:
        i. Read and process the instructions in the specified file.
        ii. Perform the actual integration into the PKM system (Obsidian vault at $PROJECT_DIR).
        iii. Once integration is complete, re-run `agent_trigger.sh` (as per step 6).
4. **YOUR ACTION:** Carefully read and understand the instructions from the file path provided by the Integrator Agent script in the previous step.
5. **YOUR ACTION:** Follow rigorously those instructions and integrate them into your Obsidian vault located at `$PROJECT_DIR`. When integrating instructions, please, write down in the chat what you're doing in a markdown headers (concise)
6. **YOUR ACTION (After successful integration):** Run `cd agents && ./agent_trigger.sh` again in a terminal. DO NOT CLOSE THE SHELL SESSION. This resets the Integrator Agent script to its waiting mode, ready for the next trigger from the Instruct Agent.

## TOOLS
### ARXIV PAPER TOOL:
When an ArXiv-specific search is needed (e.g., for academic papers), use ArXiv MCP tool.