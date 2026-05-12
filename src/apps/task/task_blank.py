TASK_BANK = {
    1: {
        "level_name": "beginner",
        "tasks": [
            {
                "id": "L1_T1",
                "title": "Basic folder",
                "description": "1 ta papka yarating",
                "structure": {
                    "test/": {}
                },
                "xp": 1,
                "type": "folder"
            },
            {
                "id": "L1_T2",
                "title": "File create",
                "description": "1 ta fayl yarating",
                "structure": {
                    "test.txt": None
                },
                "xp": 1,
                "type": "file"
            },
            {
                "id": "L1_T3",
                "title": "Simple structure",
                "description": "folder + file",
                "structure": {
                    "test/": {
                        "a.txt": None
                    }
                },
                "xp": 1,
                "type": "mixed"
            },
        ]
    },

    2: {
        "level_name": "intermediate",
        "tasks": [
            {
                "id": "L2_T1",
                "title": "2 folder structure",
                "description": "2 ta papka yarating",
                "structure": {
                    "folder1/": {},
                    "folder2/": {}
                },
                "xp": 2,
                "type": "folder"
            },
            {
                "id": "L2_T2",
                "title": "Nested files",
                "description": "har papkada file",
                "structure": {
                    "folder1/": {
                        "a.txt": 'None'
                    },
                    "folder2/": {
                        "b.txt": None
                    }
                },
                "xp": 2,
                "type": "nested"
            },
        ]
    }
}



class TaskEngine:

    @staticmethod
    def generate(user):

        profile, _ = Profile.objects.get_or_create(user=user)
        level = profile.level

        tasks = TaskTemplate.objects.filter(
            level=level,
            is_active=True
        )

        if not tasks.exists():
            tasks = TaskTemplate.objects.filter(level=1)

        task_template = random.choice(list(tasks))

        return Task.objects.create(
            user=user,
            level=level,
            title=task_template.title,
            description=task_template.description,
            target_structure=task_template.structure,
            xp=task_template.xp
        )