from aiogram import Router
from handlers.commands_handler import router as commands_router
from handlers.random_fact import router as random_fact_router
from handlers.gpt_chat import router as gpt_router
from handlers.talk import router as talk_router
from handlers.quiz import router as quiz_router


router = Router()
# Создаем главный роутер, который будет объединять все остальные роутеры
# Если его не подключить к диспетчеру, ни один обработчик работать не будет

router.include_routers(commands_router, random_fact_router, gpt_router, talk_router, quiz_router)
# Объединяем все подроутеры в главный router