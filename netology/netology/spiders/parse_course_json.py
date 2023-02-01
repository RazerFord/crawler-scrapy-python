import json
import html2text


def clear(text_):
    if text_ is None:
        return ""
    h = html2text.HTML2Text()
    h.ignore_links = True
    return h.handle(text_)


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
        self.course_features_id = []
        self.course_modules_id = []

        for component in components:
            if "studentsReviews" in component:
                self.reviews_id.append(component)
            if "courseDescriptionText" in component:
                self.descriptions_id.append(component)
            if "courseFeaturesWithImages" in component:
                self.course_features_id.append(component)
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

    def getCourseFeatures(self):
        course_features = []
        for course_feature in self.course_features_id:
            if course_feature in self.contents:
                course_features.append(
                    [
                        {
                            "title": clear(item["title"]),
                            "description": clear(item["description"]),
                        }
                        for item in self.contents[course_feature]["items"]
                    ]
                )
        return course_features

    def getProgramModules(self):
        modules = []
        for course_module in self.course_modules_id:
            if (
                course_module in self.contents
                and "blocks" in self.contents[course_module]
            ):
                module = {}
                for block in self.contents[course_module]["blocks"]:
                    if "title" in block:
                        module["title"] = clear(block["title"])

                    if "lessons" in block:
                        module["lessons"] = ""
                        for lesson in block["lessons"]:
                            module["lessons"] += clear(
                                lesson["title"] + "\n" if "title" in lesson else ""
                            ) + clear(
                                lesson["description"] if "description" in lesson else ""
                            )

                    if "description" in block:
                        module["description"] = clear(block["description"])
                if module != {}:
                    modules.append(module)

        return modules
