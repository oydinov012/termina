# terminal_engine.py

import os
import shutil


class TerminalEngine:

    def __init__(self, workspace):

        self.workspace = workspace

    # ============================================
    # XAVFSIZ ABSOLUTE PATH
    # ============================================

    def safe_path(self, path):

        abs_path = os.path.abspath(
            os.path.join(
                self.workspace.current_dir,
                path
            )
        )

        if not abs_path.startswith(
            self.workspace.root_dir
        ):
            raise Exception("Ruxsat yo'q!")

        return abs_path

    # ============================================
    # EXECUTE
    # ============================================

    def execute_command(self, command):

        parts = command.split()

        if not parts:
            return {
                "type": "output",
                "output": ""
            }

        cmd = parts[0].lower()

        args = parts[1:]

        try:

            # ====================================
            # PWD
            # ====================================

            if cmd == "pwd":

                return {
                    "type": "output",
                    "output":
                        self.workspace.current_dir.replace(
                            self.workspace.root_dir,
                            "~"
                        )
                }

            # ====================================
            # LS
            # ====================================

            elif cmd == "ls":

                files = os.listdir(
                    self.workspace.current_dir
                )

                return {
                    "type": "output",
                    "output":
                        "   ".join(files)
                        if files else "Bo'sh"
                }

            # ====================================
            # MKDIR
            # ====================================

            elif cmd == "mkdir":

                if not args:
                    return self.error(
                        "Papka nomi yozilmadi"
                    )

                path = self.safe_path(args[0])

                os.mkdir(path)

                return self.success(
                    f"Papka yaratildi: {args[0]}"
                )

            # ====================================
            # TOUCH
            # ====================================

            elif cmd == "touch":

                if not args:
                    return self.error(
                        "Fayl nomi yozilmadi"
                    )

                path = self.safe_path(args[0])

                open(path, "w").close()

                return self.success(
                    f"Fayl yaratildi: {args[0]}"
                )

            # ====================================
            # CAT
            # ====================================

            elif cmd == "cat":

                if not args:
                    return self.error(
                        "Fayl nomi yozilmadi"
                    )

                path = self.safe_path(args[0])

                if not os.path.isfile(path):

                    return self.error(
                        "Fayl topilmadi"
                    )

                with open(
                    path,
                    "r",
                    encoding="utf-8"
                ) as f:

                    return self.success(
                        f.read()
                    )

            # ====================================
            # CD
            # ====================================

            elif cmd == "cd":

                if not args:
                    return self.error(
                        "Papka nomi yozilmadi"
                    )

                if args[0] == "..":

                    new_dir = os.path.dirname(
                        self.workspace.current_dir
                    )

                else:

                    new_dir = self.safe_path(
                        args[0]
                    )

                if not new_dir.startswith(
                    self.workspace.root_dir
                ):

                    return self.error(
                        "Ruxsat yo'q"
                    )

                if not os.path.isdir(new_dir):

                    return self.error(
                        "Papka topilmadi"
                    )

                self.workspace.current_dir = new_dir

                self.workspace.save()

                return self.success(
                    new_dir.replace(
                        self.workspace.root_dir,
                        "~"
                    )
                )

            # ====================================
            # RM
            # ====================================

            elif cmd == "rm":

                if not args:
                    return self.error(
                        "Fayl nomi yozilmadi"
                    )

                path = self.safe_path(args[0])

                if os.path.isfile(path):

                    os.remove(path)

                    return self.success(
                        "Fayl o'chirildi"
                    )

                elif os.path.isdir(path):

                    shutil.rmtree(path)

                    return self.success(
                        "Papka o'chirildi"
                    )

                return self.error(
                    "Topilmadi"
                )

            # ====================================
            # CP
            # ====================================

            elif cmd == "cp":

                if len(args) < 2:

                    return self.error(
                        "cp source target"
                    )

                src = self.safe_path(args[0])

                dst = self.safe_path(args[1])

                if os.path.isfile(src):

                    shutil.copy2(src, dst)

                else:

                    shutil.copytree(src, dst)

                return self.success(
                    "Copy qilindi"
                )

            # ====================================
            # MV
            # ====================================

            elif cmd == "mv":

                if len(args) < 2:

                    return self.error(
                        "mv source target"
                    )

                src = self.safe_path(args[0])

                dst = self.safe_path(args[1])

                shutil.move(src, dst)

                return self.success(
                    "Move qilindi"
                )

            # ====================================
            # NANO
            # ====================================

            elif cmd == "nano":

                if not args:

                    return self.error(
                        "Fayl nomi yozilmadi"
                    )

                return {
                    "type": "nano",
                    "file_path": args[0]
                }

            # ====================================
            # UNKNOWN
            # ====================================

            return self.error(
                "Noma'lum buyruq"
            )

        except Exception as e:

            return self.error(str(e))

    # ============================================
    # RESPONSE HELPERS
    # ============================================

    def success(self, text):

        return {
            "type": "output",
            "output": text
        }

    def error(self, text):

        return {
            "type": "error",
            "output": text
        }