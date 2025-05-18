import json
import os

class ManageData:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self.load_data()

    def load_data(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                return json.load(file)
        else:
            return []
        
    def create_story_data(self,story_name,story_description,):
        story_data = {
            "name": story_name,
            "description": story_description,
            "chapters": []
        }
        self.data.append(story_data)
        return print(f"Story '{story_name}' created successfully!")
