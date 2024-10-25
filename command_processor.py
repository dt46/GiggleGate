def process_command(command):
    if command:
        if "turn on the light" in command.lower():
            print("Executing: Turning on the light.")
            # Implement the actual action here.
        elif "open browser" in command.lower():
            print("Executing: Opening browser.")
            # Implement the actual action here.
        else:
            print("Command not recognized.")
