import datetime


def year(request):

    """Добавляет переменную с текущим годом."""
    date_time = datetime.datetime.now()
    return {
        'date_time': date_time.year,
    }
