import json
from ..helper.clear import clear


class CourseJson:
    def __init__(self, response):
        raw_data = response.body

        if len(raw_data) == 0:
            raise ValueError("Body is empty or none")
            return

        data = json.loads(raw_data)

        if (
            data is None
            or data["content"] is None
            or "_componentOrders" not in data["content"]
        ):
            raise ValueError("Body is empty or none")
            return

        components = data["content"]["_componentOrders"]

        self.setComponentsId(components)

        self.contents = data["content"]

    def setComponentsId(self, components):
        self.reviews_id = []
        self.descriptions_id = []
        self.course_modules_id = []

        for component in components:
            if "studentsReviews" in component:
                self.reviews_id.append(component)
            if "courseDescriptionText" in component:
                self.descriptions_id.append(component)
            if "programModule" in component:
                self.course_modules_id.append(component)

    def getReviews(self):
        reviews = []
        for review in self.reviews_id:
            if review in self.contents:
                reviews += [
                    {
                        "name": clear(x["name"]),
                        "text": clear(x["text"]),
                    }
                    for x in self.contents[review]["reviews"]
                ]
        return reviews

    def getDescriptions(self, descriptions):
        for description in self.descriptions_id:
            if description in self.contents:
                text = clear(
                    self.contents[description]["text"]
                    + self.contents[description]["title"]
                )
                if text is None:
                    continue
                descriptions.append(text)
        return descriptions

    def getProgramModules(self):
        modules = []
        for course_module in self.course_modules_id:
            if (
                course_module in self.contents
                and "blocks" in self.contents[course_module]
            ):
                module = {"title": "", "lessons": "", "description": ""}
                for block in self.contents[course_module]["blocks"]:
                    if "title" in block and len(block["title"]) > 0:
                        module["title"] = clear(block["title"])

                    if "lessons" in block and len(block["lessons"]) > 0:
                        module["lessons"] = block["lessons"]

                    if "description" in block and len(block["description"]) > 0:
                        module["description"] = clear(block["description"])

                if module != {"title": "", "lessons": "", "description": ""}:
                    modules.append(module)

        return modules
