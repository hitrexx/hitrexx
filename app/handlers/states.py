from aiogram.fsm.state import State, StatesGroup

SURVEY_QUESTIONS: list[tuple[str, str]] = [
    ("project_type", "Что строим? (например: жилой дом, баня, гараж)"),
    ("area", "Какая общая площадь объекта, м²?"),
    ("floors", "Количество этажей?"),
    ("wall_material", "Материал стен?"),
    ("foundation_type", "Тип фундамента?"),
    ("roof_type", "Тип кровли?"),
    ("ceiling_height", "Высота потолков, м?"),
    ("region", "Регион строительства?"),
    ("extra_wishes", "Дополнительные пожелания? (если нет — напишите \"нет\")"),
]


class EstimateStates(StatesGroup):
    waiting_price_list = State()
    survey = State()
    waiting_project_files = State()
    processing = State()
