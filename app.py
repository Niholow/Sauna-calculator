from flask import Flask, render_template_string, request
import datetime

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <title>Калькулятор сауны</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial; background: #f5f5f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .calculator { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); width: 100%; max-width: 400px; text-align: center; }
        input[type=text] { width: 60px; text-align: center; font-size: 1.2em; padding: 10px; margin: 10px 5px; border: 1px solid #ccc; }
        button { width: 100%; padding: 12px; font-size: 1em; background: #007AFF; color: white; border: none; border-radius: 6px; cursor: pointer; }
        .result { margin-top: 20px; font-size: 1.3em; color: #007AFF; font-weight: bold; }
    </style>
</head>
<body>
<div class="calculator">
    <h1>Калькулятор стоимости сауны</h3>

    <form method="post">
        <label>Время начала:</label><br>
        <input type="text" name="start_hour" placeholder="16" maxlength="2" value="{{ request.form['start_hour'] if request.form.get('start_hour') else '' }}">
        :
        <input type="text" name="start_min" placeholder="00" maxlength="2" value="{{ request.form['start_min'] if request.form.get('start_min') else '' }}"><br><br>

        <label>Длительность:</label><br>
        <input type="text" name="duration_hour" placeholder="5" maxlength="2" value="{{ request.form['duration_hour'] if request.form.get('duration_hour') else '' }}">
        :
        <input type="text" name="duration_min" placeholder="00" maxlength="2" value="{{ request.form['duration_min'] if request.form.get('duration_min') else '' }}"><br><br>

        <label><input type="radio" name="day" value="weekday" {% if day_type != 'weekend' %}checked{% endif %}> Будний день</label>
        <label><input type="radio" name="day" value="weekend" {% if day_type == 'weekend' %}checked{% endif %}> Выходной</label><br><br>

        <button type="submit">Рассчитать</button>
    </form>

    {% if result %}
        <p class="result">Итого стоимость: {{ result }} ₽</p>
    {% endif %}
</div>
</body>
</html>
'''

def is_night_time(hour):
    return hour >= 20 or hour < 9

@app.route('/', methods=['GET', 'POST'])
def home():
    result = None
    day_type = "weekday"

    if request.method == 'POST':
        try:
            sh = int(request.form['start_hour'])
            sm = int(request.form['start_min'])
            dh = int(request.form['duration_hour'])
            dm = int(request.form['duration_min'])
            day_type = request.form['day']

            start_time = datetime.datetime.now().replace(second=0, microsecond=0, hour=sh, minute=sm)
            end_time = start_time + datetime.timedelta(hours=dh, minutes=dm)

            tariffs = {
                "weekday": {"day": 800, "night": 1000},
                "weekend": {"day": 1000, "night": 1200}
            }

            current = start_time
            total_cost = 0.0

            while current < end_time:
                current_hour = current.hour
                is_night_current = is_night_time(current_hour)

                # Определяем, сколько осталось до следующего целого часа
                next_hour = current.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
                delta_to_next_hour = (min(next_hour, end_time) - current).total_seconds() / 3600
                rate = tariffs[day_type]["night" if is_night_current else "day"]

                # Учитываем, что начальное время может быть не строго на часе, а в середине
                if current.minute >= 30 and current < end_time:
                    # Разделяем на две части, если это переход через 30 минут
                    part_1 = (current.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(minutes=30)) - current
                    part_1_min = part_1.total_seconds() / 60
                    part_1_hour_fraction = part_1.total_seconds() / 3600
                    rate_1 = rate
                    total_cost += rate_1 * part_1_hour_fraction

                    current = current.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(minutes=30)

                    if current >= end_time:
                        break

                # После 30 минут — обычная почасовая логика
                delta = (min(next_hour, end_time) - current).total_seconds() / 3600
                total_cost += rate * delta
                current = next_hour

            result = f"{total_cost:.2f}"
        except Exception as e:
            result = f"Ошибка: {str(e)}"

    return render_template_string(HTML_TEMPLATE, result=result, day_type=day_type)