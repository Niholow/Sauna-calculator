from flask import Flask, render_template_string, request
import os
import datetime

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Калькулятор сауны</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial; background: #f5f5f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0 }
        .calculator { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); width: 100%; max-width: 400px; text-align: center }
        input[type=text] { width: 60px; text-align: center; font-size: 1.2em; padding: 10px; margin: 10px 5px; border: 1px solid #ccc }
        button { width: 100%; padding: 12px; font-size: 1em; background: #007AFF; color: white; border: none; border-radius: 6px; cursor: pointer }
        .result { margin-top: 20px; font-size: 1.3em; color: #007AFF; font-weight: bold }
    </style>
</head>
<body>
<div class="calculator">
    <h1>Калькулятор стоимости сауны</h1>

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
    return hour >= 17 or hour < 9

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
                "weekday": {"day": 800, "night": 1400},
                "weekend": {"day": 1200, "night": 1800}
            }

            total_cost = 0.0
            current = start_time

            while current < end_time:
                next_hour = current.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
                hour = current.hour
                is_night = is_night_time(hour)
                rate = tariffs[day_type]["night" if is_night else "day"]

                delta = (min(next_hour, end_time) - current).total_seconds() / 3600
                total_cost += rate * delta
                current = next_hour

            result = f"{total_cost:.2f}"
        except:
            result = "Ошибка ввода"

    return render_template_string(HTML_TEMPLATE, result=result, day_type=day_type)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))