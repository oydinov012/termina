import os

def execute_command(workspace, command):
    parts = command.split()
    if not parts: return ""
    
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else None
    
    current = workspace.current_dir
    root = workspace.root_dir

    try:
        if cmd == "pwd":
            return current.replace(root, "~")
        
        elif cmd == "ls":
            files = os.listdir(current)
            return "\n".join(files) if files else "Bo'sh"

        elif cmd == "mkdir" and arg:
            path = os.path.join(current, arg)
            os.mkdir(path)
            return f"Papka yaratildi: {arg}"

        elif cmd == "touch" and arg:
            path = os.path.join(current, arg)
            open(path, "w").close()
            return f"Fayl yaratildi: {arg}"

        elif cmd == "cd" and arg:
            if arg == "..":
                new_dir = os.path.dirname(current)
            else:
                new_dir = os.path.abspath(os.path.join(current, arg))
            
            # Xavfsizlik: Rootdan chiqib ketmaslik
            if not new_dir.startswith(root):
                return "Ruxsat yo'q!"
            
            if os.path.isdir(new_dir):
                workspace.current_dir = new_dir
                workspace.save()
                return new_dir.replace(root, "~")
            return "Papka topilmadi"

        elif cmd == "cat" and arg:
            path = os.path.join(current, arg)
            with open(path, "r") as f:
                return f.read()

        return f"Noma'lum buyruq: {cmd}"
    except Exception as e:
        return str(e)