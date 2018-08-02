from django.core.management.base import BaseCommand
from planner.models import Task, Employee, IntTask
from django.conf import settings
from django.core import mail
from datetime import date


class Command(BaseCommand):
    help = 'Sending notifications to tasks owners and executors'

    def handle(self, *args, **options):

        employees = Employee.objects.filter(user__is_active=True)
        tasks = Task.objects.exclude(exec_status=Task.Sent).\
                             exclude(deal__expire_date__gte=date.today(),
                                     planned_finish__isnull=True).\
                             exclude(deal__expire_date__gte=date.today(),
                                     planned_finish__gte=date.today())
        inttasks = IntTask.objects.exclude(exec_status=IntTask.Done)\
                                  .exclude(planned_finish__gte=date.today())

        emails = []

        for employee in employees:
            otasks = tasks.filter(owner=employee)
            etasks = tasks.filter(executors=employee)
            einttasks = inttasks.filter(executor=employee)

            message = '<html><body>Шановний(а) {}.<br><br>'\
                      .format(employee.user.first_name)

            if otasks.exists():
                index = 0
                message += 'Протерміновані наступні проекти, в яких Ви відповідальна особа:<br>\
                           <table border="1">\
                           <th>&#8470;</th><th>Шифр об\'єкту</th><th>Адреса об\'єкту</th>\
                           <th>Тип проекту</th><th>Статус</th><th>Планове закінчення</th><th>Попередження</th>'

                for task in otasks:
                    index += 1
                    message += '<tr>\
                               <td>{}</td>\
                               <td><a href="http://erp.itel.rv.ua/admin/planner/task/{}/change/">{}</a></td>\
                               <td>{:.80}</td>\
                               <td>{}</td>\
                               <td>{!s}</td>\
                               <td>{}</td>\
                               <td>{!s}</td>\
                               </tr>'.\
                               format(index, task.pk, task.object_code, task.object_address,
                                      task.project_type, task.get_exec_status_display(),
                                      task.planned_finish, task.overdue_status())

                message += '</table><br>'

            if etasks.exists():
                index = 0
                message += 'Протерміновані наступні проекти, в яких Ви виконуєте роботи:<br>\
                           <table border="1">\
                           <th>&#8470;</th><th>Шифр об\'єкту</th><th>Адреса об\'єкту</th>\
                           <th>Тип проекту</th><th>Статус</th><th>Планове закінчення</th><th>Попередження</th>'

                for task in etasks:
                    index +=1
                    message += '<tr>\
                               <td>{}</td>\
                               <td><a href="http://erp.itel.rv.ua/admin/planner/task/{}/change/">{}</a></td>\
                               <td>{:.80}</td>\
                               <td>{}</td>\
                               <td>{!s}</td>\
                               <td>{}</td>\
                               <td>{!s}</td>\
                               </tr>'\
                               .format(index, task.pk, task.object_code, task.object_address,
                                       task.project_type, task.get_exec_status_display(),
                                       task.planned_finish, task.overdue_status())

                message += '</table></body></html><br>'

            if einttasks.exists():
                index = 0
                message += 'Ви протермінували наступні завдання:<br>\
                           <table border="1">\
                           <th>&#8470;</th><th>Завдання</th><th>Статус</th><th>Планове закінчення</th>'

                for task in einttasks:
                    index += 1
                    message += '<tr>\
                               <td>{}</td>\
                               <td><a href="http://erp.itel.rv.ua/admin/planner/inttask/{}/change/">{}</a></td>\
                               <td>{!s}</td>\
                               <td>{}</td>\
                               </tr>'\
                               .format(index, task.pk, task.task_name, task.get_exec_status_display(),
                                       task.planned_finish)
                message += '</table></body></html><br>'

            if otasks.exists() or etasks.exists() or einttasks.exists():
                emails.append(mail.EmailMessage(
                              'Протерміновані проекти',
                              message,
                              settings.DEFAULT_FROM_EMAIL,
                              [employee.user.email],
                              ['s.kozlyuk@itel.rv.ua', 'm.kozlyuk@itel.rv.ua'],
                ))

        for email in emails:
            email.content_subtype = "html"

        connection = mail.get_connection()
        connection.open()
        connection.send_messages(emails)
        connection.close()
