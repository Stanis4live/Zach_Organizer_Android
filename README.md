# ZACH Organizer

## Beta version

ZACH is a time management organizer app. It integrates calendar functions, event planning, to-do lists, shopping lists, 
and notes. A distinctive feature is the capability to set up SMS and email reminders. The aim of this project is to provide 
users with an intuitive tool for efficient time management.
To run the application, you need to create a configuration.py file and add variables there:
WAK=""
CONFIG={}
The variables need to be obtained from the firebase service. You also need to set the following privacy settings in firebase in
rules section:
{
  "rules": {
    ".read": false,
    ".write": false,
    "$localId": {
      ".read": "auth != null && auth.uid === $localId && auth.token.email_verified == true",
      ".write": "auth != null && auth.uid === $localId && auth.token.email_verified == true",
    }
  }
}

The beta version of the product can be downloaded from Google Play at the link:
https://play.google.com/store/apps/details?id=infinitedreams.zach.zach01

ZACH — это органайзер для управления вашим временем. В приложении интегрированы функции календаря, планировщика событий, 
списков дел, покупок и заметок. Особенностью является возможность подключения СМС и электронных напоминаний. 
Цель проекта — предоставить пользователям интуитивный инструмент для эффективного тайм-менеджмента.
Для запуска приложения необходимо создать файл configuration.py и добавить туда переменные:
WAK = ""
CONFIG = {}
Переменные нужно получить из сервиса firebase. Также необходимо задать следующие настройки приватности в firebase в 
разделе rules:
{
  "rules": {
    ".read": false,
    ".write": false,
    "$localId": {
      ".read": "auth != null && auth.uid === $localId && auth.token.email_verified == true",
      ".write": "auth != null && auth.uid === $localId && auth.token.email_verified == true",
    }
  }
}

Бета-версию продукта можно скачать с Google Play по ссылке:
https://play.google.com/store/apps/details?id=infinitedreams.zach.zach01