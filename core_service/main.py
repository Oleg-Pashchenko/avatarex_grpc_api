import amocrm_connect_service.client as amocrm
import database_connect_service.src.client as database
import prompt_mode_service.client as prompt_mode
import qualification_mode_service.src.client as qualification_mode


def main():
    while True:
        settings = database.get_settings()
        for setting in settings:
            chats = amocrm.get_chats(setting)
            for chat in chats:
                if not chat.qualification_passed:
                    answer = qualification_mode.get_answer(setting, chat)

                if chat.qualification_passed:
                    answer = prompt_mode.get_answer(setting, chat)
                    amocrm.send_message(setting, chat, answer)


if __name__ == "__main__":
    main()
