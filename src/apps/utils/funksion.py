import os
import re
import shutil
from apps.task.models import Task
from apps.utils.tasks import async_check_task

class TerminalEngine:
    MAX_FILE_BYTES = 100_000  # bitta fayl uchun maksimal hajm

    def __init__(self, workspace):
        self.workspace = workspace
        self.user = workspace.user

    # ============================================
    # XAVFSIZ ABSOLUTE PATH
    # ============================================

    def is_inside_root(self, abs_path):
        root = os.path.abspath(self.workspace.root_dir)
        try:
            return os.path.commonpath([root, abs_path]) == root
        except ValueError:
            return False

    def safe_path(self, path):
        abs_path = os.path.abspath(
            os.path.join(self.workspace.current_dir, path)
        )

        if not self.is_inside_root(abs_path):
            raise Exception("Ruxsat yo'q!")

        return abs_path

    # ============================================
    # EXECUTE
    # ============================================

    def execute_command(self, command, content_to_write=""):
        # Split qilishdan oldin umumiy komandani tozalaymiz
        command_clean = command.strip()
        parts = command_clean.split()

        if not parts:
            return {
                "type": "output",
                "output": ""
            }

        cmd = parts[0].lower()
        args = parts[1:]

        # ---------------------------------------------------------
        # RUXSAT ETILGAN BUYRUQLAR RO'YXATI (Whitelist)
        # ---------------------------------------------------------
        ALLOWED_COMMANDS = ["pwd", "ls", "mkdir", "touch", "cat", "cd", "rm", "cp", "mv", "nano", "start", "check"]

        if cmd not in ALLOWED_COMMANDS:
            return self.error(f"Noma'lum yoki taqiqlangan buyruq: '{cmd}'  Iltimos qo'llanma ilan tanishib chiqing")
            
        
        # ====================================
        # START (Taskni boshlash)
        # ====================================
        
        try:
            if cmd == "start":
                match = re.search(r'start(?:\s+|\()(\d+)\)?', command_clean)
                if not match:
                    return self.error("Xato format! Ishlatish: start <task_id>")

                task_id = int(match.group(1))
                try:
                    task = Task.objects.get(id=task_id, user=self.user)
                except Task.DoesNotExist:
                    return self.error(f"Sizga tegishli bunday ID dagi topshiriq topilmadi.")

                if task.status == "completed":
                    return self.success("Bu topshiriqni allaqachon muvaffaqiyatli bajargansiz!")

                # Bazada saqlamaymiz, shunchaki o'zgaruvchi sifatida yaratamiz
                folder_name = f"task_{task.id}_papkasi"
                task_dir_abs = os.path.join(self.workspace.root_dir, folder_name)

                if not os.path.exists(task_dir_abs):
                    os.makedirs(task_dir_abs)

                # task.workspace_path = task_dir_abs  <-- BU QATORNI OLIB TASHLADIK
                task.status = "in_progress"
                task.save()

                self.workspace.current_dir = task_dir_abs
                self.workspace.save()

                return {
                    "type": "start",
                    "output": f"Topshiriq boshlandi! '{folder_name}' yaratildi va siz uning ichidasiz. Vazifani bajaring va tugatgach 'check' deb yozing.",
                    "file_path": folder_name
                }

            # ====================================
            # CHECK (joriy topshiriq papkasini tekshirish)
            # ====================================
            elif cmd == "check":
                # Qaysi topshiriq papkasi ichida turganingizga qarab aniqlaymiz
                rel = os.path.relpath(self.workspace.current_dir, self.workspace.root_dir)
                match = re.match(r"task_(\d+)_papkasi$", rel.split(os.sep)[0])
                if not match:
                    return self.error(
                        "Avval `start <id>` bilan topshiriqni boshlang va uning papkasida turing."
                    )

                task = Task.objects.filter(
                    id=int(match.group(1)),
                    user=self.user,
                    status__in=["in_progress", "failed"],
                ).first()
                if not task:
                    return self.error(
                        "Bu topshiriq faol emas yoki allaqachon bajarilgan. Yangi topshiriq uchun `start <id>` yozing."
                    )

                task_path = os.path.join(self.workspace.root_dir, f"task_{task.id}_papkasi")

                # Faqat BIR marta yuboramiz va ID ni shu taskka bog'laymiz
                celery_result = async_check_task.delay(self.user.id, task.id, task_path)
                task.check_job_id = celery_result.id
                task.save(update_fields=["check_job_id"])

                return {
                    "type": "check_queued",
                    "celery_task_id": celery_result.id,  # Frontend shu ID bilan holatni so'raydi
                    "output": "Topshiriq tekshirishga topshirildi... Natija yuklanmoqda.",
                }

            # ====================================
            # PWD
            # ====================================
            elif cmd == "pwd":
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
            # ====================================
            # MKDIR
            # ====================================
            elif cmd == "mkdir":
                current_items = len(os.listdir(self.workspace.current_dir))
                if current_items >= 20:  # bitta papka ichida ko'pi bilan 20 ta element
                    return self.error("Siz ajratilgan limitdan ko'p obyekt yarata olmaysiz!")
                
                # 1. Birinchi navbatda argument borligini tekshiramiz
                if not args:
                    return self.error("Papka nomi yozilmadi")

                # 2. Endi xavfsiz yo'lni olamiz va 'path' o'zgaruvchisini yaratamiz
                path = self.safe_path(args[0])

                # 3. 'path' yaratilgandan keyingina uning mavjudligini tekshiramiz
                if os.path.exists(path):
                    return self.error(f"mkdir: '{args[0]}' papkasini yaratib bo'lmadi: Fayl yoki papka allaqachon mavjud.")

                # 4. Hammasi joyida bo'lsa, papkani yaratamiz
                os.mkdir(path)

                return self.success(f"Papka yaratildi: {args[0]}")
            # ====================================
            # TOUCH
            # ====================================
            elif cmd == "touch":
                if not args:
                    return self.error("Fayl nomi yozilmadi")

                path = self.safe_path(args[0])
                open(path, "w").close()

                return self.success(f"Fayl yaratildi: {args[0]}")

            # ====================================
            # CAT
            # ====================================
            elif cmd == "cat":
                if not args:
                    return self.error("Fayl nomi yozilmadi")

                path = self.safe_path(args[0])
                if not os.path.isfile(path):
                    return self.error("Fayl topilmadi")

                with open(path, "r", encoding="utf-8") as f:
                    return self.success(f.read())

            # ====================================
            # CD
            # ====================================
            elif cmd == "cd":
                if not args:
                    return self.error("Papka nomi yozilmadi")

                if args[0] == "..":
                    new_dir = os.path.dirname(
                        self.workspace.current_dir
                    )
                else:
                    new_dir = self.safe_path(args[0])

                if not self.is_inside_root(new_dir):
                    return self.error("Ruxsat yo'q")

                if not os.path.isdir(new_dir):
                    return self.error("Papka topilmadi")

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
                    return self.error("Fayl nomi yozilmadi")

                path = self.safe_path(args[0])

                if path == os.path.abspath(self.workspace.root_dir):
                    return self.error("Bosh papkani o'chirib bo'lmaydi")

                if os.path.isfile(path):
                    os.remove(path)
                    return self.success("Fayl o'chirildi")

                elif os.path.isdir(path):
                    shutil.rmtree(path)
                    return self.success("Papka o'chirildi")

                return self.error("Topilmadi")

            # ====================================
            # CP
            # ====================================
            elif cmd == "cp":
                if len(args) < 2:
                    return self.error("cp source target")

                src = self.safe_path(args[0])
                dst = self.safe_path(args[1])

                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                else:
                    shutil.copytree(src, dst)

                return self.success("Copy qilindi")

            # ====================================
            # MV
            # ====================================
            elif cmd == "mv":
                if len(args) < 2:
                    return self.error("mv source target")

                src = self.safe_path(args[0])
                dst = self.safe_path(args[1])

                shutil.move(src, dst)
                return self.success("Move qilindi")

            # ====================================
            # NANO (Kontent tahrirlash va saqlash)
            # ====================================
            elif cmd == "nano":
                if not args:
                    return self.error("Fayl nomi yozilmadi")

                file_name = args[0]
                path = self.safe_path(file_name)

                # Agar Front-end'dan content kelgan bo'lsa -> Faylni SAQLAYMIZ
                if content_to_write:
                    if len(content_to_write.encode("utf-8")) > self.MAX_FILE_BYTES:
                        return self.error("Fayl juda katta (maksimum 100 KB)")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(content_to_write)
                    return {
                        "type": "nano_save",
                        "output": "Fayl muvaffaqiyatli saqlandi.",
                        "file_path": file_name
                    }

                # Agar shunchaki faylni OCHISH bo'lsa (content yo'q bo'lsa)
                current_content = ""
                if os.path.isfile(path):
                    with open(path, "r", encoding="utf-8") as f:
                        current_content = f.read()

                return {
                    "type": "nano",
                    "file_path": file_name,
                    "content": current_content
                }

            # ====================================
            # UNKNOWN
            # ====================================
            return self.error("Noma'lum buyruq")

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